import argparse
import json
import logging
import logging.config
import time
from concurrent import futures
from pathlib import Path
from typing import Any

import grpc  # type: ignore[import-untyped]
import yaml
from grpc_reflection.v1alpha import reflection  # type: ignore[import-untyped]
from tranqu import Tranqu  # type: ignore[import-untyped]

from tranqu_server.proto.v1 import tranqu_pb2, tranqu_pb2_grpc

logger = logging.getLogger("tranqu_server")


class TranspilerServiceImpl(tranqu_pb2_grpc.TranspilerServiceServicer):
    """Implementation of the TranspilerService gRPC service.

    This class provides the `Transpile` function, which handles requests to transpile
    quantum programs. It utilizes the `Tranqu` library to perform transpilation and
    prepares the response with the transpiled program, associated statistics, and
    virtual-physical qubit mapping.
    """

    def __init__(self) -> None:
        self._tranqu = Tranqu()

    def Transpile(  # noqa: N802
        self,
        request: tranqu_pb2.TranspileRequest,  # type: ignore[name-defined]
        context: grpc.ServicerContext,  # noqa: ARG002
    ) -> tranqu_pb2.TranspileResponse:  # type: ignore[name-defined]
        """Handle a gRPC request to transpile a quantum program.

        This method processes a transpilation request, parses the inputs, calls the
        `Tranqu` library to perform the transpilation, and constructs the response
        with the results. If an exception occurs during transpilation, an error
        response is returned.

        Args:
            request (tranqu_pb2.TranspileRequest): The gRPC request containing the
                program and related parameters for transpilation.
            context (grpc.ServicerContext): The gRPC context for the request.

        Returns:
            tranqu_pb2.TranspileResponse: The gRPC response containing the transpiled
                program, statistics, and virtual-physical qubit mapping.
                The `status` field indicates the result of the transpilation, where `0`
                represents a successful transpilation and `1` indicates an error
                occurred.

        """
        try:
            start_time = time.time()
            request_id = request.request_id
            logger.info("Transpile is started.", extra={"request_id": request_id})
            logger.debug(
                "received parameter",
                extra={
                    "request_id": request_id,
                    "program": request.program,
                    "program_lib": request.program_lib,
                    "transpiler_lib": request.transpiler_lib,
                    "transpiler_options": request.transpiler_options,
                    "device": request.device,
                    "device_lib": request.device_lib,
                },
            )

            # call Tranqu
            result = self._tranqu.transpile(
                program=parse_str(request.program),
                program_lib=parse_str(request.program_lib),
                transpiler_lib=parse_str(request.transpiler_lib),
                transpiler_options=parse_json(request.transpiler_options),
                device=parse_json(request.device),
                device_lib=parse_str(request.device_lib),
            )

            response = tranqu_pb2.TranspileResponse(  # type: ignore[attr-defined]
                status=0,
                transpiled_program=result.transpiled_program,
                stats=json.dumps(result.to_dict()["stats"]),
                virtual_physical_mapping=json.dumps(
                    result.to_dict()["virtual_physical_mapping"]
                ),
            )
        except:  # noqa: E722
            logger.exception(
                "Transpile failed. Exception occurred.",
                extra={"request_id": request_id},
            )
            response = tranqu_pb2.TranspileResponse(status=1)  # type: ignore[attr-defined]
        finally:
            elapsed_time = time.time() - start_time
            logger.info(
                "Transpile is finished.",
                extra={
                    "request_id": request_id,
                    "elapsed_time": elapsed_time,
                    "status": response.status,
                },
            )
            return response  # noqa: B012


def parse_str(raw_str: str) -> str | None:
    """Parse the input string and return a valid string or None.

    This function checks if the input string is empty or None-like. If the input
    is an empty string (`""`) or `None`, it returns `None`. Otherwise, it returns
    the input string as is.

    Args:
        raw_str (str): The input string to be parsed.

    Returns:
        str | None: The input string if it is valid, or `None` if the input is
        empty or None-like.

    """
    if raw_str in {"", None}:
        return None
    return raw_str


def parse_json(raw_str: str) -> dict[Any, Any] | None:
    """Parse a JSON string into a dictionary or return None if the input is invalid.

    This function takes a raw string and attempts to parse it as a JSON object.
    If the input string is empty or `None`, it returns `None`. Otherwise, it parses
    the string into a Python dictionary.

    Args:
        raw_str (str): The input JSON string to be parsed.

    Returns:
        dict[Any, Any] | None: A dictionary representation of the JSON string if
        parsing is successful, or `None` if the input is empty or `None`.

    """
    if raw_str in {"", None}:
        return None
    return json.loads(raw_str)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the gRPC server with configuration files."
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to the server configuration file (YAML format).",
    )
    parser.add_argument(
        "-l",
        "--logging",
        type=str,
        default="config/logging.yaml",
        help="Path to the logging configuration file (YAML format).",
    )
    return parser.parse_args()


def serve(config_yaml_path: str, logging_yaml_path: str) -> None:
    """Start the gRPC server with the specified configuration and logging settings.

    This function initializes and starts a gRPC server using the configuration
    provided in the YAML files for the server and logging. It sets up a
    transpiler service, configures the server's address and worker threads,
    and waits for the server to terminate.

    Args:
        config_yaml_path (str): Path to the YAML file containing the server's
            configuration. The file should define `proto.max_workers` and
            `proto.address` settings.
        logging_yaml_path (str): Path to the YAML file containing logging configuration.

    """
    with Path(config_yaml_path).open("r", encoding="utf-8") as file:
        config_yaml = yaml.safe_load(file)
    with Path(logging_yaml_path).open("r", encoding="utf-8") as file:
        logging_yaml = yaml.safe_load(file)
        logging.config.dictConfig(logging_yaml)

    max_workers = config_yaml["proto"].get("max_workers", 10)
    address = config_yaml["proto"].get("address", "[::]:50051")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers))
    tranqu_pb2_grpc.add_TranspilerServiceServicer_to_server(
        TranspilerServiceImpl(), server
    )
    service_names = (
        tranqu_pb2.DESCRIPTOR.services_by_name["TranspilerService"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)
    server.add_insecure_port(address)
    logger.info("Server is running on %s. max_workers=%d", address, max_workers)

    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    args = _parse_args()
    serve(args.config, args.logging)
