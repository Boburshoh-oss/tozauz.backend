include .env
export

.PHONY: help backup restore backup-list

help:
	@echo "Available commands:"
	@echo "  make backup          - Create database backup"
	@echo "  make restore FILE=<backup_file>  - Restore database from backup file"
	@echo "  make backup-list     - List all backup files"

backup:
	@echo "Creating database backup..."
	@docker compose -f docker-compose.prod.yml exec -T db pg_dump -U $${POSTGRES_USER:-tozauz} $${POSTGRES_DB:-tozauz} > backup_$$(date +%Y-%m-%d_%H-%M-%S).sql
	@echo "Backup created successfully!"

restore:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify backup file. Example: make restore FILE=backup_2025-05-28_06-14-52.sql"; \
		exit 1; \
	fi
	@echo "Restoring database from $(FILE)..."
	@docker compose -f docker-compose.prod.yml exec -T db psql -U $${POSTGRES_USER:-tozauz} $${POSTGRES_DB:-tozauz} < $(FILE)
	@echo "Database restored successfully from $(FILE)"

backup-list:
	@echo "Available backup files:"
	@ls -lh backup_*.sql 2>/dev/null || echo "No backup files found"
