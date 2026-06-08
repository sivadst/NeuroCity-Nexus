# Compose command wrapper so we only define it once.
COMPOSE = docker compose

# Start the full NeuroCity Nexus stack in detached mode after rebuilding images.
up:
	$(COMPOSE) up --build -d

# Stop the stack and remove the containers while keeping named volumes intact.
down:
	$(COMPOSE) down

# Stream logs from every service in the stack.
logs:
	$(COMPOSE) logs -f

# Run schema setup and Timescale bootstrap inside the backend container.
migrate:
	$(COMPOSE) exec backend python scripts/migrate.py

# Seed the database with a realistic development telemetry sample.
seed:
	$(COMPOSE) exec backend python scripts/seed.py
