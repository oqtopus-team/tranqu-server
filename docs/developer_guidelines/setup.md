
# Development Environment Setup

## Prerequisites

Before starting development, you need to install the following tools:

### Development Environment

| Tool                                            | Version | Description                        |
|-------------------------------------------------|---------|------------------------------------|
| [Python](https://www.python.org/downloads/)     | >=3.12  | Python programming language        |
| [uv](https://docs.astral.sh/uv/)                | -       | Python package and project manager |
| [Buf CLI](https://buf.build/docs/installation/) | -       | developer tool that enables building and management of Protobuf APIs through the command line |

To start development, clone the repository:

```shell
git clone https://github.com/oqtopus-team/tranqu-server.git
cd tranqu-server
```

### Setting Up the Python Environment

To install dependencies:

```shell
uv sync
```

## Generate Python codes from *.proto file

If you modify a `*.proto file`, run the following commands to generate the gRPC-related codes.

```shell
cd spec/proto
make all
```

## Lint and test

### How to Format Code

To format the code, run the following command:

```shell
uv run ruff format
```

### How to Lint Code

To check the types, run the following command:

```shell
uv run ruff check
```

### How to Check Types

To check the types, run the following command:

```shell
uv run mypy
```

### How to Test Code

To test the code, run the following command:

```shell
uv run pytest
```

## Starting the Documentation Server

We are using [MkDocs](https://www.mkdocs.org/) to generate the HTML documentation and [mkdocstrings-python](https://mkdocstrings.github.io/python/) to generate the Python API reference.
To start the documentation server, run the following command:

```shell
uv run mkdocs serve
```

Then, check the documentation at [http://localhost:8000](http://localhost:8000).
