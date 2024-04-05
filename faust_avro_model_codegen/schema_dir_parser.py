import pathlib
from typing import Iterable

from faust_avro_model_codegen.types import SchemaData


class AvroSchemaDirectoryParser:
    @staticmethod
    def parse_dir(schema_dir: pathlib.Path) -> Iterable[SchemaData]:
        return (
            SchemaData.from_file(schema_file.stem, schema_file.read_text())
            for schema_file in schema_dir.glob("*.avsc")
        )
