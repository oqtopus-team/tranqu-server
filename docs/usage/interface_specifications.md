# Interface Specifications

## Protocol Buffers

This section explains the Protocol Buffers specification for Tranqu Server.

Tranqu Server provides a single service, `TranspilerService`, which includes one method, `Transpile`. The `Transpile` method accepts a request of type `TranspileRequest` and returns a response of type `TranspileResponse`.

The `TranspileRequest` is designed to fit the arguments of Tranqu's [`transpiler` function](https://tranqu.readthedocs.io/stable/reference/tranqu/tranqu/#tranqu.tranqu.Tranqu.transpile). Similarly, the `TranspileResponse` is structured to align with the return value of the `transpiler` function, specifically the [`TranspileResult` class](https://tranqu.readthedocs.io/stable/reference/tranqu/transpile_result/#tranqu.transpile_result.TranspileResult).

The `*.proto` file is [here](https://github.com/oqtopus-team/tranqu-server/tree/main/spec/proto).

### Services: `TranspilerService`

#### Method: `Transpile`

- **Request**: [`TranspileRequest`](#message-transpilerequest)
- **Response**: [`TranspileResponse`](#message-transpileresponse)

### Message: `TranspileRequest`

Except for `request_id`, all fields correspond to the arguments of Tranqu's `transpiler` function.

| Field Name           | Type   | Tag | Description |
|----------------------|--------|-----|-------------|
| `request_id`         | string | 1   | An identifier for the request to the Tranqu Server. It is output to the Tranqu Server's logs and can be freely set by the caller. |
| `program`            | string | 2   | The program to be transformed. This corresponds to the `program` argument of the `transpiler` function. |
| `program_lib`        | string | 3   | The library or format of the program. This corresponds to the `program_lib` argument of the `transpiler` function. |
| `transpiler_lib`     | string | 4   | The name of the transpiler to be used. This corresponds to the `transpiler_lib` argument of the `transpiler` function. |
| `transpiler_options` | string | 5   | Options passed to the transpiler in JSON format. These options are converted to a `dict`, which corresponds to the `transpiler_options` argument of the `transpiler` function. |
| `device`             | string | 6   | Information about the device on which the program will be executed. Specified in JSON format and converted to a `dict`, which corresponds to the `device` argument of the `transpiler` function. |
| `device_lib`         | string | 7   | Specifies the type of the device. This corresponds to the `device_lib` argument of the `transpiler` function. |

### Message: `TranspileResponse`

Except for `status`, all fields correspond to the arguments of properties of the `TranspileRequest` class.

| Field Name                 | Type   | Tag | Description |
|----------------------------|--------|-----|-------------|
| `status`                   | uint32 | 1   | Returns 0 if the `Transpile` method executes successfully, otherwise returns 1. |
| `transpiled_program`       | string | 2   | The quantum program after transpilation. This corresponds to the `transpiled_program` property of the `TranspileRequest` class, converted to a string type. |
| `stats`                    | string | 3   | Statistical information before and after transpilation. This corresponds to the `stats` property (dict) of the `TranspileRequest` class, converted to JSON format. |
| `virtual_physical_mapping` | string | 4   | Mapping between virtual quantum bits and physical quantum bits. This corresponds to the `virtual_physical_mapping` property (dict) of the `TranspileRequest` class, converted to JSON format. |
