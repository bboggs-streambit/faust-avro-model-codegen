import dataclasses
import tomlkit
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    schema_dir: Path = Path("schemas")
    outfile: Path = Path("models.py")
    schema_registry_url: str = "http://localhost:8081"
    faust_app_models_module: str = "models"

    @classmethod
    def from_toml(cls) -> "Settings":
        pyproject_toml = Path("pyproject.toml")
        standalone_toml = Path("faust_avro_code_gen.toml")
        if cls.pyproject_config_exists(pyproject_toml):
            return cls(
                **tomlkit.loads(pyproject_toml.read_bytes())["tool"][
                    "faust_avro_code_gen"
                ]
            )
        if standalone_toml.exists():
            return cls(**tomlkit.loads(standalone_toml.read_bytes()).unwrap())
        return cls()

    @classmethod
    def pyproject_config_exists(cls, pyproject_toml: Path) -> bool:
        return (
            pyproject_toml.exists()
            and tomlkit.loads(pyproject_toml.read_bytes())
            .get("tool", {})
            .get("faust_avro_code_gen")
            is not None
        )
