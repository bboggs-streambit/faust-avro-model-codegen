import importlib
import pathlib
import typing
from functools import reduce

import isort
from plumbum.cmd import autoflake, black  # type: ignore

from .schema_verifier import SchemaVerifier
from .template_renderer import TemplateRenderer, RenderedTemplate
from .template_writer import TemplateWriter
from .types import (
    CodeGenResultData,
    SchemaData,
)


class FaustAvroModelGen:

    def __init__(
        self,
        renderer: TemplateRenderer,
        verifier: SchemaVerifier,
        writer: TemplateWriter,
    ):
        self.renderer = renderer
        self.verifier = verifier
        self.writer = writer

    def generate_module(
        self, schemas: typing.Iterable[SchemaData], outfile: pathlib.Path
    ) -> None:
        codegen_results_from_schemas = (
            CodeGenResultData.from_schema_data(s) for s in schemas
        )
        accum_codegen_data = reduce(
            lambda s, t: s + t,
            codegen_results_from_schemas,
            CodeGenResultData.empty(),
        )
        self.write(outfile, self.renderer.render(accum_codegen_data))

    def write(self, outfile: pathlib.Path, rendered_text: RenderedTemplate) -> None:
        self.writer.write(outfile, rendered_text)

    def verify_schemas(
        self, schemas: typing.Iterable[SchemaData], module_name: str
    ) -> None:
        module = importlib.import_module(module_name)
        generated_classes = {
            schema.name: getattr(module, schema.schema["name"]) for schema in schemas
        }
        self.verifier.verify(generated_classes)
