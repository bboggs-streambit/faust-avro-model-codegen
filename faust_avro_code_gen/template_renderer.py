import pathlib
from typing import Union, NewType

import jinja2
from jinja2 import Template

from .types import (
    PythonEnumClass,
    PythonAvroModel,
    CodeGenResultData,
)

RenderedTemplate = NewType("RenderedTemplate", str)


class TemplateRenderer:
    THIS_LIBRARY = "avro_code_gen"

    def __init__(
        self,
        enum_template: Template,
        avro_template: Template,
        models_template: Template,
    ):
        self.enum_template = enum_template
        self.avro_template = avro_template
        self.models_template = models_template

    @classmethod
    def from_current_directory(cls) -> "TemplateRenderer":
        this_dir = pathlib.Path(__file__).parent
        loader = jinja2.FileSystemLoader(searchpath=this_dir / "templates")
        tpls = jinja2.Environment(loader=loader)
        return cls(
            enum_template=tpls.get_template("enum.py.jinja2"),
            avro_template=tpls.get_template("faust_record.jinja2"),
            models_template=tpls.get_template("models.py.jinja2"),
        )

    def render(
        self,
        python_cls: Union[PythonAvroModel, PythonEnumClass, CodeGenResultData],
    ) -> RenderedTemplate:
        match python_cls:
            case PythonEnumClass() as enum:
                return RenderedTemplate(self.enum_template.render(c=enum))
            case PythonAvroModel() as model:
                return RenderedTemplate(self.avro_template.render(c=model))
            case CodeGenResultData() as code_gen_result:
                return RenderedTemplate(
                    self.models_template.render(
                        classes=[self.render(c) for c in code_gen_result.classes],
                        deps=[self.render(d) for d in code_gen_result.dependencies],
                        __name__=self.THIS_LIBRARY,
                    )
                )
            case _:
                raise ValueError("Nothing happening here.")
