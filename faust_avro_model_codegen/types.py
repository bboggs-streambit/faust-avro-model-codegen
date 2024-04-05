import dataclasses
import json
import typing

from dataclasses_avroschema import field_utils
from dataclasses_avroschema.model_generator.lang.python.avro_to_python_utils import (
    AVRO_TYPE_TO_PYTHON,
)

SchemaName: typing.TypeAlias = str
SchemaJson: typing.TypeAlias = dict[str, typing.Any]


@dataclasses.dataclass
class SchemaData:
    name: SchemaName
    schema: SchemaJson

    @classmethod
    def from_file(cls, file_stem: str, file_json: str) -> "SchemaData":
        return cls(name=file_stem, schema=json.loads(file_json))


@dataclasses.dataclass
class PythonEnumClass:
    name: str
    values: typing.List[str]


@dataclasses.dataclass
class PythonAvroField:
    name: str
    type: str
    doc: typing.Optional[str] = None
    default: typing.Optional[typing.Any] = None
    has_default: bool = False


@dataclasses.dataclass
class PythonAvroModel:
    name: str
    namespace: typing.Optional[str] = None
    example: typing.Optional[typing.Dict[str, typing.Any]] = None
    fields: typing.List[PythonAvroField] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class CodeGenResultData:
    classes: list[typing.Any]
    dependencies: list[typing.Any]
    schemas: dict[str, typing.Any]

    @classmethod
    def empty(cls) -> "CodeGenResultData":
        return cls(classes=[], dependencies=[], schemas={})

    def __add__(self, other: "CodeGenResultData") -> "CodeGenResultData":
        classes = [*self.classes, *other.classes]
        dependencies = [*self.dependencies, *other.dependencies]
        schemas = {**self.schemas, **other.schemas}
        return self.__class__(
            classes=classes, dependencies=dependencies, schemas=schemas
        )

    @classmethod
    def from_schema_data(cls, schema_data: SchemaData) -> "CodeGenResultData":
        c, deps = cls.parse_models_for_schema(schema_data.schema)
        schema = {schema_data.name: schema_data.schema}
        return cls(
            classes=[c],
            dependencies=deps,
            schemas=schema,
        )

    @classmethod
    def parse_models_for_schema(
        cls,
        schema: typing.Dict[str, typing.Any],
    ) -> typing.Tuple[PythonAvroModel, typing.List[typing.Any]]:
        fields = []
        dependencies = []
        for avro_field in schema["fields"]:
            python_field, python_deps = cls.convert_avro_field_to_python(avro_field)
            fields.append(python_field)
            dependencies += python_deps

        c = PythonAvroModel(
            name=schema["name"],
            namespace=schema.get("namespace"),
            example=schema.get("example"),
            # ensures that fields with defaults are at the end  of the class definition
            fields=sorted(
                [field for field in fields if field is not None],
                key=lambda x: x.has_default,
            ),
        )

        return c, dependencies

    @staticmethod
    def convert_avro_field_to_python(
        field: dict[str, typing.Any],
    ) -> typing.Tuple[PythonAvroField, typing.List[PythonEnumClass | None]]:
        match field["type"]:
            case (
                field_utils.STRING
                | field_utils.LONG
                | field_utils.INT
                | field_utils.BOOLEAN
                | field_utils.FLOAT
                | field_utils.DOUBLE
            ) as field_type:
                return (
                    PythonAvroField(
                        name=field["name"],
                        type=AVRO_TYPE_TO_PYTHON[field_type],
                        doc=field.get("doc"),
                        default=field.get("default"),
                        has_default="default" in field,
                    ),
                    [],
                )

            case {"type": field_utils.LONG, "logicalType": logical_type}:
                return (
                    PythonAvroField(
                        name=field["name"],
                        type=AVRO_TYPE_TO_PYTHON[logical_type],
                        doc=field.get("doc"),
                        default=field.get("default"),
                        has_default="default" in field,
                    ),
                    [],
                )

            case [
                "null",
                {
                    "type": field_utils.ARRAY,
                    "items": {
                        "type": field_utils.ENUM,
                        "name": name,
                        "symbols": symbols,
                    },
                },
            ]:
                e = PythonEnumClass(name=name, values=symbols)
                return (
                    PythonAvroField(
                        name=field["name"],
                        type=f"typing.Union[None, typing.List[{name}]]",
                        doc=field.get("doc"),
                        default=field.get("default"),
                        has_default="default" in field,
                    ),
                    [e],
                )
            case list(types):
                resolved_types = ",".join([AVRO_TYPE_TO_PYTHON[t] for t in types])
                displayed_types = f"typing.Union[{resolved_types}]"
                return (
                    PythonAvroField(
                        name=field["name"],
                        type=displayed_types,
                        doc=field.get("doc"),
                        default=field.get("default"),
                        has_default="default" in field,
                    ),
                    [],
                )

            case {
                "type": field_utils.ARRAY,
                "items": {"type": field_utils.ENUM, "name": name, "symbols": symbols},
            }:
                e = PythonEnumClass(name=name, values=symbols)  # type: ignore
                return (
                    PythonAvroField(
                        name=field["name"],
                        type=f"typing.List[{name}]",
                        doc=field.get("doc"),
                        default=field.get("default"),
                        has_default="default" in field,
                    ),
                    [e],
                )
            case _:
                raise NotImplementedError(field)
