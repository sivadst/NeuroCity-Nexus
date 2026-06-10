from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.db.session import AsyncSessionLocal
from src.models.city import District, DistrictScore, WeatherReading
from src.services.digital_twin.scoring import DistrictScoringEngine

try:
    from redis.asyncio import Redis
except Exception:  # pragma: no cover
    Redis = None  # type: ignore[assignment]

WS_CHANNEL = "neurocity:twin:updates"
MAX_CONNECTIONS = 100
engine = DistrictScoringEngine()
settings = get_settings()
INSTANCE_ID = uuid4().hex


class TwinConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._subscriptions: dict[WebSocket, UUID | None] = {}
        self._lock = asyncio.Lock()
        self._publisher_task: asyncio.Task[None] | None = None
        self._subscriber_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        if self._publisher_task is None:
            self._publisher_task = asyncio.create_task(self._publisher_loop())
        if self._subscriber_task is None:
            self._subscriber_task = asyncio.create_task(self._subscriber_loop())

    async def connect(self, websocket: WebSocket) -> bool:
        if len(self._connections) >= MAX_CONNECTIONS:
            await websocket.close(code=1013, reason="Too many websocket connections")
            return False
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
            self._subscriptions[websocket] = None
        return True

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)
            self._subscriptions.pop(websocket, None)

    async def subscribe(self, websocket: WebSocket, district_id: UUID) -> None:
        async with self._lock:
            self._subscriptions[websocket] = district_id

    async def active_count(self) -> int:
        async with self._lock:
            return len(self._connections)

    async def send_personal(self, websocket: WebSocket, payload: dict[str, Any]) -> None:
        await websocket.send_text(json.dumps(payload, default=str))

    async def broadcast(self, payload: dict[str, Any]) -> None:
        message = json.dumps(payload, default=str)
        async with self._lock:
            targets = list(self._connections)
            subscriptions = dict(self._subscriptions)
        for websocket in targets:
            district_filter = subscriptions.get(websocket)
            if district_filter is not None:
                districts = payload.get("districts", [])
                filtered = [item for item in districts if str(item["id"]) == str(district_filter)]
                if not filtered:
                    continue
                payload_to_send = dict(payload)
                payload_to_send["districts"] = filtered
                await websocket.send_text(json.dumps(payload_to_send, default=str))
            else:
                await websocket.send_text(message)

    async def snapshot(self) -> dict[str, Any]:
        async with AsyncSessionLocal() as session:
            latest_scores_sq = (
                select(DistrictScore.district_id, func.max(DistrictScore.time).label("time"))
                .group_by(DistrictScore.district_id)
                .subquery()
            )
            rows = (
                await session.execute(
                    select(District, DistrictScore)
                    .join(DistrictScore, DistrictScore.district_id == District.id)
                    .join(
                        latest_scores_sq,
                        (DistrictScore.district_id == latest_scores_sq.c.district_id)
                        & (DistrictScore.time == latest_scores_sq.c.time),
                    )
                    .order_by(District.name)
                )
            ).all()
            # Fetch latest weather
            weather_stmt = select(WeatherReading).order_by(desc(WeatherReading.time)).limit(1)
            weather = (await session.execute(weather_stmt)).scalar_one_or_none()
            
            districts = []
            for district, score in rows:
                districts.append(
                    {
                        "id": district.id,
                        "name": district.name,
                        "scores": {
                            "traffic_score": float(score.traffic_score),
                            "energy_score": float(score.energy_score),
                            "pollution_score": float(score.pollution_score),
                            "carbon_score": float(score.carbon_score),
                            "sustainability_score": float(score.sustainability_score),
                        },
                        "composite_score": engine.composite_score(
                            {
                                "traffic": float(score.traffic_score),
                                "energy": float(score.energy_score),
                                "pollution": float(score.pollution_score),
                                "carbon": float(score.carbon_score),
                                "sustainability": float(score.sustainability_score),
                            }
                        ),
                        "changed": False,
                    }
                )
            return {
                "type": "score_update",
                "timestamp": datetime.now(UTC),
                "districts": districts,
                "weather": {
                    "temperature": weather.temperature,
                    "humidity": weather.humidity,
                    "condition": weather.condition,
                    "wind_speed": weather.wind_speed,
                    "precipitation": weather.precipitation,
                    "air_quality_index": weather.air_quality_index,
                } if weather else None,
                "source_instance": INSTANCE_ID,
            }

    async def _publisher_loop(self) -> None:
        redis = Redis.from_url(settings.redis_url, decode_responses=True) if Redis is not None else None
        try:
            while True:
                payload = await self.snapshot()
                if redis is not None:
                    await redis.publish(WS_CHANNEL, json.dumps(payload, default=str))
                await self.broadcast(payload)
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            raise
        finally:
            if redis is not None:
                await redis.aclose()

    async def _subscriber_loop(self) -> None:
        if Redis is None:
            return
        redis = Redis.from_url(settings.redis_url, decode_responses=True)
        pubsub = redis.pubsub()
        await pubsub.subscribe(WS_CHANNEL)
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message.get("type") == "message":
                    payload = json.loads(message["data"])
                    if payload.get("source_instance") == INSTANCE_ID:
                        continue
                    await self.broadcast(payload)
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            raise
        finally:
            await pubsub.close()
            await redis.aclose()


manager = TwinConnectionManager()


async def twin_websocket(websocket: WebSocket) -> None:
    """Stream live twin score updates to websocket clients.

    ws://localhost:8000/ws/twin
    """
    await manager.start()
    if not await manager.connect(websocket):
        return
    await manager.send_personal(websocket, await manager.snapshot())

    try:
        while True:
            message = await websocket.receive_text()
            payload = json.loads(message)
            if payload.get("action") == "subscribe_district":
                district_id = UUID(payload["district_id"])
                await manager.subscribe(websocket, district_id)
            await websocket.send_text(json.dumps({"type": "heartbeat", "timestamp": datetime.now(UTC)}, default=str))
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
