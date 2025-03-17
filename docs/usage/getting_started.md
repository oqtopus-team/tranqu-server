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

### config.yaml

This is the main configuration file for Tranqu Server.

```yaml
proto: # Settings for Tranqu Server as a gRPC server
  max_workers: 10 # Maximum number of workers (default: 10)
  address: "[::]:50051" # Address and port for RPCs (default: "[::]:50051")
```

### logging.yaml

This is the logging configuration file for Tranqu Server.
It is written in YAML format.
Within Tranqu Server, it is loaded as a `dict`, and then the [logging.config.dictConfig function](https://docs.python.org/3/library/logging.config.html#logging.config.dictConfig) is called to apply the configuration.

If you use the default settings of `config.yaml`, the `logs` directory is required.

```shell
mkdir logs
```

## Start Tranqu Server

To start Tranqu Server, run the following command:

```shell
uv run python src/tranqu_server/proto/service.py -c config/config.yaml -l config/logging.yaml
```

- `-c` or `--config`: Specifies the path to the main configuration file.
- `-l` or `--logging`: Specifies the path to the logging configuration file.

## Run sample client

A sample client can call the Tranqu Server to try it out and check its functionality.

```bash
uv run python tests/tranqu_server/proto/sample_client.py
```

## Example

You can check Tranqu Server's with grpcurl:

### Install grpcurl

See the [grpcurl repository](https://github.com/fullstorydev/grpcurl)

### List services

```shell
grpcurl -plaintext [::]:50051 list
```

### Check supported methods

```shell
grpcurl -plaintext "[::]:50051" list tranqu_server.proto.v1.TranspilerService
```

### Request to transpile

```shell
grpcurl -plaintext -d '{
  "program": "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[2] q;\n\nh q[0];\ncx q[0], q[1];\n",
  "program_lib": "openqasm3",
  "transpiler_lib": "qiskit"
}' "[::]:50051" tranqu_server.proto.v1.TranspilerService.Transpile
```
