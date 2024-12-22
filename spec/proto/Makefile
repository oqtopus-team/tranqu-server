SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

.PHONY: all
all: lint generate

.PHONY: lint
lint:
	buf lint

.PHONY: generate
generate:
	buf generate

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all        - Run lint and generate"
	@echo "  lint       - Run buf lint"
	@echo "  generate   - Run buf generate"
	@echo "  help       - Show this help message"
