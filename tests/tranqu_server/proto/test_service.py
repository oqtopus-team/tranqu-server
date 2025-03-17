import json

import pytest

from tranqu_server.proto.service import (
    TranspilerServiceImpl,
    assign_environ,
    parse_json,
    parse_str,
)
from tranqu_server.proto.v1 import tranqu_pb2


def test_parse_str():
    assert parse_str("") is None
    assert parse_str(None) is None
    assert parse_str("valid_string") == "valid_string"


def test_parse_json():
    assert parse_json("") is None
    assert parse_json(None) is None
    assert parse_json('{"key": "value"}') == {"key": "value"}
    with pytest.raises(json.JSONDecodeError):
        parse_json("invalid_json")


def test_assign_environ(mocker):  # noqa: ANN001
    # Arrange
    def expanduser_side_effect(arg):  # noqa: ANN202, ANN001
        if arg == "~":
            return "/home/testuser"
        return arg

    def expandvars_side_effect(arg):  # noqa: ANN202, ANN001
        if arg == "$MY_ENV":
            return "dummy_env"
        return arg

    mocker.patch("os.path.expanduser", side_effect=expanduser_side_effect)
    mocker.patch("os.path.expandvars", side_effect=expandvars_side_effect)
    config = {
        "key1": "~",
        "key2": {
            "key3": "$MY_ENV",
            "key4": "value",
        },
    }

    # Act
    actual = assign_environ(config)

    # Assert
    assert actual == {
        "key1": "/home/testuser",
        "key2": {
            "key3": "dummy_env",
            "key4": "value",
        },
    }


program = """OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;

h q[0];
cx q[0], q[1];
c = measure q;
"""


transpiler_options = json.dumps({
    "basis_gates": ["id", "sx", "x", "rz", "cx"],
})


oqtopus_device = json.dumps({
    "device_id": "fake_device",
    "qubits": [
        {
            "id": 0,
            "fidelity": 0.90,
            "meas_error": {
                "prob_meas1_prep0": 0.01,
                "prob_meas0_prep1": 0.02,
            },
            "gate_duration": {"x": 60.0, "sx": 30.0, "rz": 0},
        },
        {
            "id": 1,
            "meas_error": {
                "prob_meas1_prep0": 0.01,
                "prob_meas0_prep1": 0.02,
            },
            "gate_duration": {"x": 60.0, "sx": 30.0, "rz": 0},
        },
        {
            "id": 2,
            "fidelity": 0.99,
            "gate_duration": {"x": 60.0, "sx": 30.0, "rz": 0},
        },
        {
            "id": 3,
            "fidelity": 0.99,
            "meas_error": {
                "prob_meas1_prep0": 0.01,
                "prob_meas0_prep1": 0.02,
            },
        },
    ],
    "couplings": [
        {
            "control": 0,
            "target": 2,
            "fidelity": 0.8,
            "gate_duration": {"cx": 60.0},
        },
        {"control": 0, "target": 1, "fidelity": 0.8},
        {"control": 1, "target": 0, "fidelity": 0.25},
        {"control": 1, "target": 3, "fidelity": 0.25},
        {"control": 2, "target": 0, "fidelity": 0.25},
        {"control": 2, "target": 3, "fidelity": 0.25},
        {"control": 3, "target": 1, "fidelity": 0.9},
        {"control": 3, "target": 2, "fidelity": 0.9},
    ],
    "timestamp": "2024-10-31 14:03:48.568126",
})


class TestTranspilerServiceImpl:
    def test_transpile_success(self):
        # Arrange
        transpiler_service = TranspilerServiceImpl()
        request = tranqu_pb2.TranspileRequest(
            request_id="test_id",
            program=program,
            program_lib="openqasm3",
            transpiler_lib="qiskit",
            transpiler_options=transpiler_options,
            device=oqtopus_device,
            device_lib="oqtopus",
        )

        # Act
        actual = transpiler_service.Transpile(request, None)

        # Assert
        assert actual.status == 0
        assert (
            actual.transpiled_program
            == """OPENQASM 3.0;
include "stdgates.inc";
bit[2] c;
rz(pi/2) $0;
sx $0;
rz(pi/2) $0;
cx $0, $1;
c[0] = measure $0;
c[1] = measure $1;
"""
        )
        actual_stats = json.loads(actual.stats)
        assert actual_stats == {
            "before": {
                "n_qubits": 2,
                "n_gates": 4,
                "n_gates_1q": 3,
                "n_gates_2q": 1,
                "depth": 3,
            },
            "after": {
                "n_qubits": 4,
                "n_gates": 6,
                "n_gates_1q": 5,
                "n_gates_2q": 1,
                "depth": 5,
            },
        }
        actual_vp_mapping = json.loads(actual.virtual_physical_mapping)
        assert actual_vp_mapping == {
            "qubit_mapping": {
                "0": 0,
                "1": 1,
            },
            "bit_mapping": {
                "0": 0,
                "1": 1,
            },
        }

    def test_transpile_failure(self):
        # Arrange
        transpiler_service = TranspilerServiceImpl()
        request = tranqu_pb2.TranspileRequest(
            request_id="test_id",
            program=program,
            program_lib="openqasm3",
            transpiler_lib="qiskit",
            transpiler_options=transpiler_options,
            device=oqtopus_device,
            device_lib="invalid_device_lib",
        )

        # Act
        actual = transpiler_service.Transpile(request, None)

        # Assert
        assert actual.status == 1
        assert actual.transpiled_program == ""
        assert actual.stats == ""
        assert actual.virtual_physical_mapping == ""
