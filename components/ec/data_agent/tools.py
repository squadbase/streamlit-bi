import base64
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox
from langchain_core.tools import tool

from .bigquery_utils import bigquery_client, dry_run_sql
from .utils import ExtendedBaseModel

load_dotenv()


OUTPUT_DIRECTORY = "tmp"


class ExecuteBigQuerySqlArgs(ExtendedBaseModel):
    sql: str
    output_file_name: str


class ExecuteBigQuerySqlSuccessResult(ExtendedBaseModel):
    output_file_path: str


class ExecuteBigQuerySqlErrorResult(ExtendedBaseModel):
    error_message: str


ExecuteBigQuerySqlResult = (
    ExecuteBigQuerySqlSuccessResult | ExecuteBigQuerySqlErrorResult
)


@tool
def execute_bigquery_sql(sql: str, output_file_name: str) -> ExecuteBigQuerySqlResult:
    """Execute BigQuery SQL.

    Args:
        sql: The SQL to execute
        output_file_name: Part of the CSV file name. The file will be saved in the format `tmp/{output_file_name}_{datetime_string}.csv`.

    Returns:
        The CSV file path of the result of the SQL execution
    """
    try:
        cost_mb = dry_run_sql(sql)

        cost_mb_limit = 100

        if cost_mb > cost_mb_limit:
            return ExecuteBigQuerySqlErrorResult(
                error_message=f"The cost of the SQL is too high: {cost_mb} MB"
            )

        output_file_path = os.path.join(
            OUTPUT_DIRECTORY,
            f"{output_file_name}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv",
        )

        bigquery_client.query(sql).to_dataframe().to_csv(
            index=False, encoding="utf-8", path_or_buf=output_file_path
        )

        return ExecuteBigQuerySqlSuccessResult(output_file_path=output_file_path)
    except Exception as e:
        return ExecuteBigQuerySqlErrorResult(error_message=str(e))


class ExecutePythonCodeArgs(ExtendedBaseModel):
    code: str
    packages: list[str]
    csv_file_paths: list[str] = []
    output_files: list[str] = []


class ExecutePythonCodeSuccessResult(ExtendedBaseModel):
    stdout: str
    stderr: str
    output_files: list[str]
    error_message: Optional[str] = None


class ExecutePythonCodeErrorResult(ExtendedBaseModel):
    error_message: str


ExecutePythonCodeResult = ExecutePythonCodeSuccessResult | ExecutePythonCodeErrorResult


@tool
def execute_python_code(
    code: str,
    packages: list[str],
    files: list[str] = [],
) -> ExecutePythonCodeResult:
    """Execute Python Code in a sandbox environment.

    Args:
        code: The Python code to execute
        packages: The packages to be installed. For each package, `pip install {package_name}` will be executed before running the code.
        upload_file_paths: A list of files to uploaded to the sandbox environment. The path must be in the format `tmp/{filename}.{ext}`.

    Note:
        - For visualization, use matplotlib and display graphs with `show()`. (Graphs displayed with `show()` will be automatically downloaded)
        - When reading CSV files or other files, you must specify the path in the files parameter.

    """

    sbx = Sandbox()

    for package in packages:
        execution = sbx.commands.run(f"pip install {package}")
        if execution.error:
            return ExecutePythonCodeErrorResult(
                error_message=f"Failed to install package: {package}. {execution.error}"
            )

    try:
        for file in files:
            with open(file, "rb") as f:
                sbx.files.write(file, f)

        execution = sbx.run_code(code)

        output_files: list[str] = []
        has_invalid_format_output = False

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        print(execution)

        for i, result in enumerate(execution.results):
            if result.png:
                output_file = f"tmp/python-result-{timestamp}-{i}.png"
                with open(output_file, "wb") as f:
                    f.write(base64.b64decode(result.png))

                output_files.append(output_file)
            else:
                has_invalid_format_output = True

        stdout = "".join(execution.logs.stdout)
        stderr = "".join(execution.logs.stderr)

        error_message = f"""
{"Warning: Unexpected output format file has been detected. Please check your code." if has_invalid_format_output else ""}
{f"Error: {execution.error.name} {execution.error.value} traceback: {execution.error.traceback}" if execution.error else ""}
"""
        if error_message.strip() == "":
            error_message = None

        return ExecutePythonCodeSuccessResult(
            stdout=stdout,
            stderr=stderr,
            output_files=output_files,
            error_message=error_message,
        )
    except Exception as e:
        return ExecutePythonCodeErrorResult(error_message=str(e))
