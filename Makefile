SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

.PHONY: run test format lint grpcurl-list help

run: ## Run Tranqu Server
	@WORKERS=2 ADDRESS="localhost:52020" uv run python src/tranqu_server/proto/service.py -c config/config.yaml -l config/logging.yaml

test: ## Run tests
	@uv run pytest

format: ## Format code
	@uv run ruff format

lint: ## Lint code
	@uv run ruff check

grpcurl-list: ## List gRPC services via grpcurl
	@grpcurl -plaintext localhost:52020 list

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(filter-out .env,$(MAKEFILE_LIST)) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
