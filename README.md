# Faust Avro Code Generator

This is a Python library that generates Faust models from Avro schemas.

## Installation

You can install the library using pip:

```bash
pip install faust_avro_code_gen
```

## Configuration

You can configure the library for your application using either `pyproject.toml` or a standalone configuration file.

### Using `pyproject.toml`

Add the following section to your `pyproject.toml`:

```toml
[tool.faust_avro_code_gen]
schema_dir = "path/to/your/schemas"
outfile = "path/to/your/models.py"
schema_registry_url = "http://localhost:8081"
faust_app_models_module = "models"
```

### Using a standalone configuration file

Create a `faust_avro_code_gen.toml` file in your project root with the following content:

```toml
schema_dir = "path/to/your/schemas"
outfile = "path/to/your/models.py"
schema_registry_url = "http://localhost:8081"
faust_app_models_module = "models"
```

## Usage

You can use the library from the command line as follows:

```bash
python -m faust_avro_code_gen 
```

If you have already registered your schemas with a Schema Registry, you can also verify that the schemas are correctly rendered by running the following command:

```bash
python -m faust_avro_code_gen --verify
```

This will generate Faust models from the Avro schemas in the directory specified in your configuration.