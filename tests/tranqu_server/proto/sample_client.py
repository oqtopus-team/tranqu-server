import json

import grpc  # type: ignore[import-untyped]

from tranqu_server.proto.v1 import tranqu_pb2, tranqu_pb2_grpc

program = """OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;

h q[0];
cx q[0], q[1];
"""

options = {"basis_gates": ["id", "sx", "x", "rz", "cx"]}

with grpc.insecure_channel("localhost:50051") as channel:
    stub = tranqu_pb2_grpc.TranspilerServiceStub(channel)

    request = tranqu_pb2.TranspileRequest(  # type: ignore[attr-defined]
        request_id="id",
        program=program,
        program_lib="openqasm3",
        transpiler_lib="qiskit",
        transpiler_options=json.dumps(options),
        # device="example_device",  # noqa: ERA001
        # device_lib=json.dumps({"optimization_level": 2}),  # noqa: ERA001
    )
    response = stub.Transpile(request)

    # show response
    print("Response from server:")  # noqa: T201
    print(f"  {response.status=}")  # noqa: T201
    print(f"  {response.transpiled_program=}")  # noqa: T201
    print(f"  {response.stats=}")  # noqa: T201
    print(f"  {response.virtual_physical_mapping=}")  # noqa: T201
