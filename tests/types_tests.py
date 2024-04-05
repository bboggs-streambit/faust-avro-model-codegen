import pytest

from faust_avro_code_gen.types import (
    SchemaData,
    CodeGenResultData,
    PythonAvroModel,
    PythonAvroField,
    PythonEnumClass,
)


def test_schema_data_from_file(user_avro_json: str, user_avro_dict):
    file_stem = "user"
    actual = SchemaData.from_file(file_stem, user_avro_json)
    expected = SchemaData(name=file_stem, schema=user_avro_dict)
    assert actual == expected


def test_codegen_result_data_empty():
    actual = CodeGenResultData.empty()
    expected = CodeGenResultData(classes=[], dependencies=[], schemas={})
    assert actual == expected


def test_codegen_result_data_when_empty_is_added_to_another_empty_is_empty():
    actual = CodeGenResultData.empty() + CodeGenResultData.empty()
    expected = CodeGenResultData(classes=[], dependencies=[], schemas={})
    assert actual == expected


def test_codegen_result_data_when_empty_is_added_to_another_is_the_other():
    actual = CodeGenResultData.empty() + CodeGenResultData(
        classes=["class"], dependencies=["dependency"], schemas={"schema": "schema"}
    )
    expected = CodeGenResultData(
        classes=["class"], dependencies=["dependency"], schemas={"schema": "schema"}
    )
    assert actual == expected


def test_codegen_result_data_when_non_empty_is_added_to_empty_is_the_non_empty():
    actual = (
        CodeGenResultData(
            classes=["class"], dependencies=["dependency"], schemas={"schema": "schema"}
        )
        + CodeGenResultData.empty()
    )
    expected = CodeGenResultData(
        classes=["class"], dependencies=["dependency"], schemas={"schema": "schema"}
    )
    assert actual == expected


def test_codegen_result_data_is_associative_a_added_to_b_plus_c_equals_a_plus_b_added_to_c():
    a = CodeGenResultData(classes=["a"], dependencies=["a"], schemas={"a": "a"})
    b = CodeGenResultData(classes=["b"], dependencies=["b"], schemas={"b": "b"})
    c = CodeGenResultData(classes=["c"], dependencies=["c"], schemas={"c": "c"})
    assert a + (b + c) == (a + b) + c


def test_codegen_result_data_from_schema_data_returns_expected_value(
    user_schema_data: SchemaData,
):
    actual = CodeGenResultData.from_schema_data(user_schema_data)
    expected = CodeGenResultData(
        classes=[
            PythonAvroModel(
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
                        default=None,
                        has_default=True,
                    ),
                ],
            )
        ],
        dependencies=[
            PythonEnumClass(name="Color", values=["RED", "GREEN", "BLUE"]),
            PythonEnumClass(
                name="AdditionalColor", values=["YELLOW", "PURPLE", "ORANGE"]
            ),
        ],
        schemas={
            "user": {
                "fields": [
                    {"name": "name", "type": "string"},
                    {"name": "favorite_number", "type": ["int", "null"]},
                    {
                        "name": "favorite_colors",
                        "type": {
                            "items": {
                                "name": "Color",
                                "symbols": ["RED", "GREEN", "BLUE"],
                                "type": "enum",
                            },
                            "type": "array",
                        },
                    },
                    {"default": None, "name": "new_field", "type": ["null", "string"]},
                    {
                        "name": "additional_field",
                        "type": [
                            "null",
                            {
                                "items": {
                                    "name": "AdditionalColor",
                                    "symbols": ["YELLOW", "PURPLE", "ORANGE"],
                                    "type": "enum",
                                },
                                "type": "array",
                            },
                        ],
                    },
                    {
                        "name": "timestamp_field",
                        "type": {"logicalType": "timestamp-millis", "type": "long"},
                    },
                ],
                "name": "User",
                "namespace": "example.avro",
                "type": "record",
            }
        },
    )
    assert actual == expected


def test_avro_schema_raises_not_implemented_error_if_its_not_handled():
    avro_schema = {
        "namespace": "example.avro",
        "type": "record",
        "name": "User",
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "data", "type": "bytes"},
        ],
    }
    with pytest.raises(NotImplementedError):
        CodeGenResultData.from_schema_data(SchemaData(name="user", schema=avro_schema))
