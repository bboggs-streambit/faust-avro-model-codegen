import typing

import httpx
from dataclasses_avroschema import AvroModel
from rich import print

from faust_avro_model_codegen.types import SchemaName


class SchemaNotAbleToBeVerified(Exception):
    pass


class SchemaVerifier:
    def __init__(
        self,
        schema_registry_url: str,
        client: typing.Callable[[], httpx.Client],
    ) -> None:
        self.schema_registry_url = schema_registry_url
        self.client = client

    def check_schema_against_sr(
        self, subject_name: str, schema: str
    ) -> typing.Dict[str, typing.Any]:
        with self.client() as client:
            resp = client.post(
                f"{self.schema_registry_url}/subjects/{subject_name}-value",
                json={"schema": schema},
            )
            resp.raise_for_status()
            return resp.json()

    def verify(
        self, generated_classes: dict[SchemaName, typing.Type[AvroModel]]
    ) -> None:
        for name, cls in generated_classes.items():
            print(f"[blue]Checking [italic yellow]{name}[/]...[/]")
            try:
                result = self.check_schema_against_sr(
                    name,
                    cls.avro_schema(),
                )
            except httpx.HTTPStatusError:
                print(
                    f"[italic red]Schema [bold yellow]{name}[/] not found in SR[/italic red]"
                )
                raise SchemaNotAbleToBeVerified
            else:
                print(
                    f"[italic green]Schema [bold yellow]{name}[/]"
                    f" in SR with ID [bold]{result['id']}[/][/italic green]"
                )
