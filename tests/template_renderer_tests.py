import pytest

from faust_avro_model_codegen.template_renderer import TemplateRenderer
from faust_avro_model_codegen.types import (
    PythonEnumClass,
    PythonAvroModel,
    CodeGenResultData,
)


def test_template_renderer_from_current_directory_returns_instance_of_template_Renderer():
    renderer = TemplateRenderer.from_current_directory()

    assert isinstance(renderer, TemplateRenderer)


def test_template_renderer_render_returns_expected_rendered_template_with_python_enum_class(
    python_enum_class: PythonEnumClass,
):
    renderer = TemplateRenderer.from_current_directory()
    actual = renderer.render(python_enum_class)
    expected = (
        "class Color(str, enum.Enum):\n"
        '    RED = "RED"\n'
        '    GREEN = "GREEN"\n'
        '    BLUE = "BLUE"\n'
        "    "
    )
    assert actual == expected


def test_template_renderer_render_returns_expected_rendered_template_with_python_avro_model(
    python_avro_model: PythonAvroModel,
):
    renderer = TemplateRenderer.from_current_directory()
    actual = renderer.render(python_avro_model)
    expected = (
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
        '"default": null}, default=null)\n'
        "    \n"
        "\n"
        "    \n"
        "\n"
        "    class Meta:\n"
        '        namespace = "example.avro"\n'
        "    "
    )
    assert actual == expected


def test_template_renderer_renders_expected_value_when_provided_code_gen_result_data(
    codegen_result_from_avro_schema: CodeGenResultData,
) -> None:
    renderer = TemplateRenderer.from_current_directory()
    actual = renderer.render(codegen_result_from_avro_schema)
    expected = (
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
    )
    assert actual == expected


def test_template_renderer_render_raises_value_error_when_given_unhandled_value() -> (
    None
):
    renderer = TemplateRenderer.from_current_directory()
    with pytest.raises(ValueError):
        renderer.render("not a valid value")  # type: ignore
