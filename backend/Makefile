.PHONY: dev test seed clean

dev:
	./scripts/dev.sh

seed:
	DATABASE_URL=sqlite+aiosqlite:///./dev.db APP_ENV=dev \
		python -m scripts.seed_dev

test:
	pytest -q

clean:
	rm -f dev.db
