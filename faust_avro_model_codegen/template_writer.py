import pathlib

import isort
from plumbum.cmd import autoflake, black  # type: ignore
from faust_avro_model_codegen.template_renderer import RenderedTemplate


class TemplateWriter:
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
