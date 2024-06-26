from pathlib import Path
from types import ModuleType
from unittest.mock import Mock, patch

from faust_avro_model_codegen.models_generator import FaustAvroModelGen
from faust_avro_model_codegen.template_renderer import TemplateRenderer
from faust_avro_model_codegen.types import SchemaData


def test_generate_module_passes_expected_arguments_to_write_method(
    all_schemas: list[SchemaData], outfile: Path, mock_code_gen: FaustAvroModelGen
):
    with patch.object(mock_code_gen, "write") as mock_write:
        mock_code_gen.generate_module(all_schemas, outfile)
        [(actual_out, actual_generated), _] = mock_write.call_args
        expected_generated = (
            '""" NOTICE!!\n'
            "This file is generated by: avro_code_gen\n"
            "Do not edit this file directly unless absolutely necessary!\n"
            '"""\n'
            "import typing, enum\n"
            "\n"
            "from dataclasses import dataclass, field\n"
            "from dataclasses_avroschema import types, AvroModel\n"
            "from dataclasses_avroschema.schema_generator import CT\n"
            "\n"
            "\n"
            "\n"
            "\n"
            "class Color(str, enum.Enum):\n"
            '    RED = "RED"\n'
            '    GREEN = "GREEN"\n'
            '    BLUE = "BLUE"\n'
            "    \n"
            "\n"
            "class AdditionalColor(str, enum.Enum):\n"
            '    YELLOW = "YELLOW"\n'
            '    PURPLE = "PURPLE"\n'
            '    ORANGE = "ORANGE"\n'
            "    \n"
            "\n"
            "\n"
            "\n"
            "import typing, enum, dataclasses, datetime\n"
            "\n"
            "from dataclasses import dataclass, field\n"
            "from dataclasses_avroschema.schema_generator import CT\n"
            "from dataclasses_avroschema.faust import AvroRecord\n"
            "\n"
            "\n"
            "@dataclass\n"
            "class User(AvroRecord):\n"
            "    def __post_init__(self) -> None:\n"
            "        for _field in dataclasses.fields(self):\n"
            "            value = getattr(self, _field.name)\n"
            "            if isinstance(value, dataclasses.Field):\n"
            "                setattr(self, _field.name, value.default)\n"
            "            if isinstance(value, typing.List):\n"
            "                item: enum.Enum\n"
            "                for index, item in enumerate(value):\n"
            "                    if issubclass(item.__class__, enum.Enum):\n"
            "                        value[index] = item.value\n"
            '    name: str = field(metadata={"doc": "None"})\n'
            '    favorite_number: typing.Union[types.Int32,None] = field(metadata={"doc": '
            '"None"})\n'
            '    favorite_colors: typing.List[Color] = field(metadata={"doc": "None"})\n'
            "    additional_field: typing.Union[None, typing.List[AdditionalColor]] = "
            'field(metadata={"doc": "None"})\n'
            '    timestamp_field: datetime.datetime = field(metadata={"doc": "None"})\n'
            '    new_field: typing.Union[None,str] = field(metadata={"doc": "None", '
            '"default": None}, default=None)\n'
            "    \n"
            "\n"
            "    \n"
            "\n"
            "    class Meta:\n"
            '        namespace = "example.avro"\n'
            "    \n"
            "\n"
            "import typing, enum, dataclasses, datetime\n"
            "\n"
            "from dataclasses import dataclass, field\n"
            "from dataclasses_avroschema.schema_generator import CT\n"
            "from dataclasses_avroschema.faust import AvroRecord\n"
            "\n"
            "\n"
            "@dataclass\n"
            "class BlogPost(AvroRecord):\n"
            "    def __post_init__(self) -> None:\n"
            "        for _field in dataclasses.fields(self):\n"
            "            value = getattr(self, _field.name)\n"
            "            if isinstance(value, dataclasses.Field):\n"
            "                setattr(self, _field.name, value.default)\n"
            "            if isinstance(value, typing.List):\n"
            "                item: enum.Enum\n"
            "                for index, item in enumerate(value):\n"
            "                    if issubclass(item.__class__, enum.Enum):\n"
            "                        value[index] = item.value\n"
            '    id: str = field(metadata={"doc": "None"})\n'
            '    title: str = field(metadata={"doc": "None"})\n'
            '    content: str = field(metadata={"doc": "None"})\n'
            '    author: str = field(metadata={"doc": "None"})\n'
            "    \n"
            "\n"
            "    \n"
            "\n"
            "    class Meta:\n"
            '        namespace = "example.avro"\n'
            "    \n"
        )
        assert actual_out is outfile
        assert actual_generated == expected_generated


def test_assert_outfile_precondition_and_post_condition_for_generate_module(
    mock_code_gen: FaustAvroModelGen, all_schemas: list[SchemaData], outfile: Path
) -> None:
    assert outfile.exists() is False

    mock_code_gen.generate_module(all_schemas, outfile)

    assert outfile.exists() is True


def test_verify_schemas_passes_expected_arguments_to_verify(
    mock_code_gen: FaustAvroModelGen,
    all_schemas: list[SchemaData],
    generated_module: ModuleType,
):

    mock_code_gen.verify_schemas(all_schemas, "fake_app.models")

    [[actual_call_args], _] = mock_code_gen.verifier.verify.call_args
    expected_call_args = {
        "blog_post": generated_module.BlogPost,
        "user": generated_module.User,
    }

    assert actual_call_args == expected_call_args
