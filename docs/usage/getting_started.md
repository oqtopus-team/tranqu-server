# Getting started

## Prerequisites

Before you start the installation of Tranqu Server, you need to install the following tools:

### Development Environment

| Tool                                        | Version | Description                        |
|---------------------------------------------|---------|------------------------------------|
| [Python](https://www.python.org/downloads/) | >=3.12  | Python programming language        |
| [uv](https://docs.astral.sh/uv/)            | -       | Python package and project manager |

To start installing Tranqu Server, clone the repository:

```shell
git clone https://github.com/oqtopus-team/tranqu-server.git
cd tranqu-server
```

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
