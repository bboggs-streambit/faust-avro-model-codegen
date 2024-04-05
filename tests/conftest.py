import importlib
import json
import shutil
from pathlib import Path
from types import ModuleType
from typing import Type, Any
from unittest.mock import Mock, MagicMock

import httpx
import pytest
import tomlkit
from dataclasses_avroschema.faust import AvroRecord

from faust_avro_code_gen.models_generator import FaustAvroModelGen
from faust_avro_code_gen.schema_verifier import SchemaVerifier
from faust_avro_code_gen.template_renderer import TemplateRenderer
from faust_avro_code_gen.types import (
    SchemaData,
    PythonAvroField,
    PythonAvroModel,
    PythonEnumClass,
    CodeGenResultData,
)


@pytest.fixture
def blog_post_avro_json() -> str:
    avro_file = Path(__file__).parent / "schemas" / "blog_post.avsc"
    return avro_file.read_text()


@pytest.fixture
def blog_post_avro_dict(blog_post_avro_json: str) -> dict:
    return json.loads(blog_post_avro_json)


@pytest.fixture
def blog_post_schema_data(blog_post_avro_dict: dict) -> SchemaData:
    return SchemaData(name="blog_post", schema=blog_post_avro_dict)


@pytest.fixture
def user_avro_json() -> str:
    avro_file = Path(__file__).parent / "schemas" / "user.avsc"
    return avro_file.read_text()


@pytest.fixture
def user_avro_dict(user_avro_json: str) -> dict:
    return json.loads(user_avro_json)


@pytest.fixture
def user_schema_data(user_avro_dict: dict) -> SchemaData:
    return SchemaData(name="user", schema=user_avro_dict)


@pytest.fixture
def all_schemas(
    user_schema_data: SchemaData, blog_post_schema_data: SchemaData
) -> list[SchemaData]:
    return [user_schema_data, blog_post_schema_data]


@pytest.fixture
def python_avro_field() -> PythonAvroField:
    return PythonAvroField(
        name="name",
        type="str",
        doc=None,
        default=None,
        has_default=False,
    )


@pytest.fixture
def python_avro_model() -> PythonAvroModel:
    return PythonAvroModel(
        name="User",
        namespace="example.avro",
        example=None,
        fields=[
            PythonAvroField(
                name="name",
                type="str",
                doc=None,
                default=None,
                has_default=False,
            ),
            PythonAvroField(
                name="favorite_number",
                type="typing.Union[types.Int32,None]",
                doc=None,
                default=None,
                has_default=False,
            ),
            PythonAvroField(
                name="favorite_colors",
                type="typing.List[Color]",
                doc=None,
                default=None,
                has_default=False,
            ),
            PythonAvroField(
                name="additional_field",
                type="typing.Union[None, " "typing.List[AdditionalColor]]",
                doc=None,
                default=None,
                has_default=False,
            ),
            PythonAvroField(
                name="timestamp_field",
                type="datetime.datetime",
                doc=None,
                default=None,
                has_default=False,
            ),
            PythonAvroField(
                name="new_field",
                type="typing.Union[None,str]",
                doc=None,
                default="null",
                has_default=True,
            ),
        ],
    )


@pytest.fixture
def python_enum_class() -> PythonEnumClass:
    return PythonEnumClass(name="Color", values=["RED", "GREEN", "BLUE"])


@pytest.fixture
def codegen_result_from_avro_schema(user_schema_data: SchemaData):
    return CodeGenResultData.from_schema_data(user_schema_data)


@pytest.fixture
def outfile():
    outfile = Path("fake_app") / "models.py"

    yield outfile

    if outfile.exists():
        shutil.rmtree(outfile.parent)


@pytest.fixture
def pyproject_toml(outfile: Path):
    # Define the configuration keys and example values
    config = {
        "tool": {
            "faust_avro_code_gen": {
                "schema_dir": "tests/schemas",
                "outfile": str(outfile),
                "schema_registry_url": "http://localhost:8082",
                "faust_app_models_module": "models",
            }
        }
    }

    # populate the pyproject.toml file with the configuration
    pyproject_toml = Path("pyproject.toml")
    original_pyproject_toml_config = tomlkit.loads(pyproject_toml.read_text())
    pyproject_toml.write_text(tomlkit.dumps(original_pyproject_toml_config | config))

    yield pyproject_toml

    pyproject_toml.write_text(tomlkit.dumps(original_pyproject_toml_config))


@pytest.fixture
def standalone_toml(outfile: Path):
    # Define the configuration keys and example values
    config = {
        "schema_dir": "tests/other_schemas",
        "outfile": str(outfile),
        "schema_registry_url": "http://localhost:8083",
        "faust_app_models_module": "models",
    }

    # Create a faust_avro_code_gen.toml file in the temporary directory
    standalone_toml = Path("faust_avro_code_gen.toml")
    standalone_toml.write_text(tomlkit.dumps(config))

    yield standalone_toml

    # Remove the file after the test
    if standalone_toml.exists():
        standalone_toml.unlink()


@pytest.fixture
def mock_verifier() -> Mock:
    return Mock()


@pytest.fixture
def mock_code_gen(mock_verifier: Mock) -> FaustAvroModelGen:
    return FaustAvroModelGen(
        renderer=TemplateRenderer.from_current_directory(), verifier=mock_verifier
    )


@pytest.fixture
def generated_module(
    mock_code_gen: FaustAvroModelGen, all_schemas: list[SchemaData], outfile: Path
):
    mock_code_gen.generate_module(all_schemas, outfile)
    generated_module = importlib.import_module("fake_app.models")

    yield generated_module


@pytest.fixture
def generated_modules_dict(generated_module: ModuleType) -> dict[str, Type[AvroRecord]]:
    return {
        "blog_post": generated_module.BlogPost,
        "user": generated_module.User,
    }


class FakeHttpResponse:
    def __init__(self, status_code: int, json: dict[str, Any]):
        self.status_code = status_code
        self._json = json

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("BOOM", request=Mock(), response=Mock())


@pytest.fixture
def mock_httpx_client_success() -> MagicMock:
    client = MagicMock()
    client.__enter__.return_value = client
    client.__exit__.return_value = None
    client.post.return_value = FakeHttpResponse(
        status_code=200,
        json={"id": 1},
    )
    return client


@pytest.fixture
def mock_httpx_client_failure() -> MagicMock:
    client = MagicMock()
    client.__enter__.return_value = client
    client.__exit__.return_value = None
    client.post.return_value = FakeHttpResponse(
        status_code=404,
        json={},
    )
    return client


@pytest.fixture
def successful_verifier(mock_httpx_client_success: MagicMock) -> SchemaVerifier:
    return SchemaVerifier(
        schema_registry_url="http://localhost:8082",
        client=lambda: mock_httpx_client_success,
    )


@pytest.fixture
def failed_verifier(mock_httpx_client_failure: MagicMock) -> SchemaVerifier:
    return SchemaVerifier(
        schema_registry_url="http://localhost:8082",
        client=lambda: mock_httpx_client_failure,
    )
