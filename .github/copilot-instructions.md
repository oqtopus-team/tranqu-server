# Copilot Instructions for Tranqu Server

## Project Overview

**Tranqu Server** is a Python gRPC service that wraps the [Tranqu](https://tranqu.readthedocs.io/) quantum circuit transpiler library, allowing clients to transpile quantum programs (e.g., OpenQASM 3) over the network. The sole gRPC service is `TranspilerService.Transpile`, defined in `spec/proto/` and implemented in `src/tranqu_server/proto/service.py`.

- **Language**: Python 3.12+
- **Package manager**: [`uv`](https://docs.astral.sh/uv/) — always use `uv` commands, never bare `pip`
- **Interface**: gRPC (Protobuf), port `52020` by default
- **License**: Apache-2.0

## Repository Layout

```
tranqu-server/
├── src/tranqu_server/          # Main package
│   └── proto/
│       ├── service.py          # gRPC servicer implementation (hand-written)
│       └── v1/                 # Generated Protobuf Python code (DO NOT edit)
│           ├── tranqu_pb2.py
│           └── tranqu_pb2_grpc.py
├── tests/tranqu_server/        # Mirrors src/ layout
│   └── proto/
│       ├── test_service.py     # pytest tests for service.py
│       └── sample_client.py    # Manual gRPC test client
├── spec/proto/tranqu_server/   # Protobuf source definitions
│   └── proto/                  # *.proto files
├── spec/proto/Makefile         # `make all` → buf lint + buf generate
├── config/
│   ├── config.yaml             # Server config (supports ${ENV_VAR, default} syntax)
│   └── logging.yaml            # JSON structured logging config
├── docs/                       # MkDocs documentation sources
├── pyproject.toml              # Project metadata, deps, ruff/mypy/pytest config
├── Makefile                    # Developer shortcuts (see below)
└── .github/                    # CI workflows, PR template, instructions
```

## Essential Commands

All common tasks are wrapped by `make`. Run these from the repo root:

| Goal | Command |
|---|---|
| Install all deps + configure git | `make install` |
| Run the gRPC server | `make run` |
| Auto-fix formatting | `make format` |
| Lint (ruff + mypy + lock check) | `make lint` |
| Run tests | `make test` |
| Format + lint + test (full verify) | `make verify` |
| Lint docs | `make docs-lint` |
| Build docs | `make docs-build` |
| Serve docs locally | `make docs-serve` |
| Regenerate Protobuf Python code | `cd spec/proto && make all` |

### Underlying tool invocations (when `make` is unavailable)

```bash
uv run ruff check --fix && uv run ruff format   # format
uv lock --check && uv run ruff check && uv run ruff format --check && uv run mypy  # lint
uv run pytest                                    # test
```

## Code Style and Linting

- **Formatter/Linter**: [Ruff](https://docs.astral.sh/ruff/) with `preview = true` and `lint.select = ["ALL"]`
- **Type checker**: [mypy](https://mypy.readthedocs.io/)
- **Exclusions**: `src/**/v1/**/*.py` (generated Protobuf code) is excluded from both ruff and mypy — never edit those files
- `tests/**` ignores several ruff rules (e.g., `S101` for `assert`, `PLR2004` for magic values, `ANN*` for annotations)
- Docstrings: follow Google style — `D203` (one-blank-line-before-class) and `D213` (multi-line-summary-second-line) are both **ignored**, meaning `D211` (no-blank-line-before-class) and `D212` (multi-line-summary-first-line) are enforced

## Protobuf / gRPC Workflow

1. Edit `.proto` files under `spec/proto/tranqu_server/proto/`
2. Run `cd spec/proto && make all` to regenerate Python stubs in `src/tranqu_server/proto/v1/`
3. The Buf CLI (`buf lint` + `buf generate`) handles code generation — config is in `spec/proto/buf.yaml` and `spec/proto/buf.gen.yaml`
4. Import generated code via `from tranqu_server.proto.v1 import tranqu_pb2, tranqu_pb2_grpc`

## Architecture Notes

- `TranspilerServiceImpl` (in `service.py`) is the only gRPC servicer; it wraps the `Tranqu` library
- A module-level `threading.Lock` (`_transpiler_lock`) serialises all transpilation calls — transpilation is not thread-safe in the underlying library
- `parse_str` / `parse_json` helpers normalise empty strings to `None` before passing to `Tranqu`
- The server runs with `grpc-reflection` enabled so `grpcurl` can introspect it
- Config is loaded from YAML at startup; environment variable interpolation uses `${VAR, default}` syntax (provided by `oqtopus-util`)
- Structured JSON logging is via `python-json-logger`; the `tranqu_server` logger writes to both stdout and a rotating file under `logs/`

## Testing

- Framework: `pytest` with `pytest-cov`
- Tests live under `tests/` mirroring the `src/` structure
- `pythonpath = ["src"]` is set in `pyproject.toml` — no install needed for imports
- Coverage reports are written as terminal, HTML, and XML (`htmlcov/`, `coverage.xml`)
- Tests use `Arrange / Act / Assert` pattern (see `test_service.py`)

## Git and PR Conventions

### Branch Naming
- `feature/xxx` — new features
- `bugfix/xxx` — bug fixes
- `hotfix/xxx` — urgent fixes targeting main
- All branches are cut from and merged back to `main`

### Commit Messages (Conventional Commits)
Format: `<type>(<scope>): <summary>` (≤72 chars, no trailing period, no emojis)

| Type | When |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, whitespace |
| `refactor` | Code restructure without behavior change |
| `test` | Adding or correcting tests |
| `ci` | CI/CD configuration changes |
| `chore` | Maintenance tasks |

Scope: use `api`, `docs`, `infra`, `repo` when clear; omit otherwise.

### Pull Requests
Follow `.github/pull_request_template.md` — sections are **Ticket**, **Summary**, **Changes**.
CI runs automatically on PRs to `main`: ruff lint/format, mypy type check, and pytest.

## Known Patterns and Gotchas

- **Never edit** files under `src/tranqu_server/proto/v1/` — they are generated and will be overwritten
- The `_transpiler_lock` must be preserved if refactoring the servicer; the Tranqu library is not thread-safe
- `request.transpiler_options`, `request.device` are JSON strings on the wire; use `parse_json()` to convert them
- `status=0` means success, `status=1` means error in `TranspileResponse`
- Documentation linting (`pymarkdownlnt`) only runs in CI when `docs/**` files change
- `make install` also configures the `.gitmessage` git commit template locally
