from pathlib import Path

import httpx
import typer

from faust_avro_code_gen.models_generator import FaustAvroModelGen
from faust_avro_code_gen.schema_verifier import SchemaVerifier
from faust_avro_code_gen.settings import Settings
from faust_avro_code_gen.template_renderer import TemplateRenderer
from faust_avro_code_gen.types import SchemaData


def main(
    verify: bool = typer.Option(
        False,
        "--verify",
        "-v",
        help="Verify schemas against Schema Registry",
        is_flag=True,
    )
):
    config = Settings.from_toml()
    schemas = [
        SchemaData.from_file(schema_file.stem, schema_file.read_text())
        for schema_file in Path(config.schema_dir).glob("*.avsc")
    ]

    app = FaustAvroModelGen(
        renderer=TemplateRenderer.from_current_directory(),
        verifier=SchemaVerifier(
            schema_registry_url=config.schema_registry_url,
            client=lambda: httpx.Client(),
        ),
    )
    app.generate_module(schemas, outfile=config.outfile)

    if verify:
        app.verify_schemas(schemas, config.faust_app_models_module)


typer.run(main)
