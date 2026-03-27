# Getting started

## Prerequisites

Before you start the installation of Tranqu Server, you need to install the following tools:

### Development Environment

| Tool                                        | Version | Description                        |
| ------------------------------------------- | ------- | ---------------------------------- |
| [Python](https://www.python.org/downloads/) | >=3.12  | Python programming language        |
| [uv](https://docs.astral.sh/uv/)            | -       | Python package and project manager |

To start installing Tranqu Server, clone the repository:

```shell
git clone https://github.com/oqtopus-team/tranqu-server.git
cd tranqu-server
```

!!! info
    To use [ouqu-tp](https://github.com/Qulacs-Osaka/ouqu-tp) as a transpiler,
    [staq](https://github.com/softwareQinc/staq/blob/main/INSTALL.md) is required.
    If staq is not installed, it will be automatically installed the first time you use ouqu-tp.
    The installation of staq takes several minutes.

### Setting Up the Python Environment

To install dependencies:

```shell
uv sync
```

## Configurations

Tranqu Server uses two configuration files:

- [config.yaml](#configyaml)
- [logging.yaml](#loggingyaml)

!!! info
    You can use environment variables as values in the above YAML files.

### config.yaml

This is the main configuration file for Tranqu Server.

```yaml
proto: # Settings for Tranqu Server as a gRPC server
  max_workers: ${WORKERS, 10} # Maximum number of workers (default: 10)
  address: ${ADDRESS, "localhost:52020"} # Address and port for RPCs (default: localhost:52020)
```

### logging.yaml

This is the logging configuration file for Tranqu Server.
It is written in YAML format.
Within Tranqu Server, it is loaded and applied via the `setup_logging` function from [oqtopus-util](https://github.com/oqtopus-team/oqtopus-util).

## Start Tranqu Server

To start Tranqu Server, run the following command:

```shell
uv run python -m tranqu_server.proto.service -c config/config.yaml -l config/logging.yaml
```

- `-c` or `--config`: Specifies the path to the main configuration file (default: `config/config.yaml`).
- `-l` or `--logging`: Specifies the path to the logging configuration file (default: `config/logging.yaml`).

The `WORKERS` and `ADDRESS` environment variables can be used to override the default values defined in `config.yaml`.

```shell
WORKERS=10 ADDRESS="localhost:52020" uv run python -m tranqu_server.proto.service -c config/config.yaml -l config/logging.yaml
```

## Run sample client

A sample client can call the Tranqu Server to try it out and check its functionality.

```bash
uv run python tests/tranqu_server/proto/sample_client.py
```

## Example

You can check Tranqu Server's with `grpcurl`:

### Install grpcurl

See the [grpcurl repository](https://github.com/fullstorydev/grpcurl)

### List services

```shell
grpcurl -plaintext localhost:52020 list
```

Alternatively, you can use the shortcut defined in the Makefile:

```shell
make grpcurl-list 
```

### Check supported methods

```shell
grpcurl -plaintext "localhost:52020" list tranqu_server.proto.v1.TranspilerService
```

### Request to transpile

To send a transpile request with a sample OpenQASM 3.0 program:

```shell
grpcurl -plaintext -d '{
  "program": "OPENQASM 3.0; include \"stdgates.inc\"; qubit[2] q; h q[0]; cx q[0], q[1];\n",
  "program_lib": "openqasm3",
  "transpiler_lib": "qiskit"
}' "localhost:52020" tranqu_server.proto.v1.TranspilerService.Transpile
```

You can also run this pre-defined test command via `make`:

```shell
make grpcurl-test 
```
