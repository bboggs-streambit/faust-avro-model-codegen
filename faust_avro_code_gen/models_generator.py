import importlib
import pathlib
import typing
from functools import reduce

import isort
from plumbum.cmd import autoflake, black  # type: ignore

from .schema_verifier import SchemaVerifier
from .template_renderer import TemplateRenderer, RenderedTemplate
from .types import (
    CodeGenResultData,
    SchemaData,
)


class FaustAvroModelGen:

    def __init__(
        self,
        renderer: TemplateRenderer,
        verifier: SchemaVerifier,
    ):
        self.renderer = renderer
        self.verifier = verifier

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

    @classmethod
    def write(cls, filepath: pathlib.Path, rendered_text: RenderedTemplate) -> None:
        if not filepath.parent.exists():
            filepath.parent.mkdir(parents=True)

        filepath.write_text(rendered_text)

        cls._post_process_output_file(filepath)

    @staticmethod
    def _post_process_output_file(file: pathlib.Path) -> None:
        isort.file(
            file,
            overwrite_in_place=True,
            remove_redundant_aliases=True,
            include_trailing_comma=True,
            group_by_package=True,
            float_to_top=True,
            dedup_headings=True,
            force_sort_within_sections=True,
            quiet=True,
        )
        autoflake(file.absolute(), "--in-place", "--remove-all-unused-imports")
        black(file.absolute())

    def verify_schemas(
        self, schemas: typing.Iterable[SchemaData], module_name: str
    ) -> None:
        module = importlib.import_module(module_name)
        generated_classes = {
            schema.name: getattr(module, schema.schema["name"]) for schema in schemas
        }
        self.verifier.verify(generated_classes)
