.PHONY: help backup restore backup-list

help:
	@echo "Available commands:"
	@echo "  make backup          - Create database backup"
	@echo "  make restore FILE=<backup_file>  - Restore database from backup file"
	@echo "  make backup-list     - List all backup files"

backup:
	@echo "Creating database backup..."
	@docker compose -f docker-compose.prod.yml exec -T db pg_dump -U ${DB_USERNAME} ${DB_NAME} > backup_$(shell date +%Y-%m-%d_%H-%M-%S).sql
	@echo "Backup created: backup_$(shell date +%Y-%m-%d_%H-%M-%S).sql"

restore:
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify backup file. Example: make restore FILE=backup_2025-05-28_06-14-52.sql"; \
		exit 1; \
	fi
	@echo "Restoring database from $(FILE)..."
	@docker compose -f docker-compose.prod.yml exec -T db psql -U ${DB_USERNAME} ${DB_NAME} < $(FILE)
	@echo "Database restored successfully from $(FILE)"

backup-list:
	@echo "Available backup files:"
	@ls -lh backup_*.sql 2>/dev/null || echo "No backup files found"
