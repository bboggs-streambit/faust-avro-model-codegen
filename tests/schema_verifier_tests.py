from typing import Type, cast
from unittest.mock import Mock, MagicMock

import pytest
from dataclasses_avroschema.faust import AvroRecord

from faust_avro_code_gen.schema_verifier import SchemaNotAbleToBeVerified


def test_verifier_raises_schema_not_able_to_be_verified_when_check_sr_fails(
    failed_verifier: Mock, generated_modules_dict: dict[str, Type[AvroRecord]]
):
    with pytest.raises(SchemaNotAbleToBeVerified):
        failed_verifier.verify(generated_modules_dict)


def test_verifier_passes_expected_args_to_http_client(
    successful_verifier: Mock,
    generated_modules_dict: dict[str, Type[AvroRecord]],
    mock_httpx_client_success: MagicMock,
):
    successful_verifier.verify(generated_modules_dict)
    [[[first_url], first_payload], [[second_url], second_payload]] = cast(
        MagicMock, mock_httpx_client_success.post
    ).call_args_list

    expected_args = [
        "http://localhost:8082/subjects/blog_post-value",
        {
            "json": {
                "schema": '{"type": "record", "name": "BlogPost", "fields": '
                '[{"doc": "None", "name": "id", "type": "string"}, '
                '{"doc": "None", "name": "title", "type": "string"}, '
                '{"doc": "None", "name": "content", "type": "string"}, '
                '{"doc": "None", "name": "author", "type": "string"}], '
                '"namespace": "example.avro"}'
            }
        },
        "http://localhost:8082/subjects/user-value",
        {
            "json": {
                "schema": '{"type": "record", "name": "User", "fields": [{"doc": '
                '"None", "name": "name", "type": "string"}, {"doc": '
                '"None", "name": "favorite_number", "type": ["int", '
                '"null"]}, {"doc": "None", "name": "favorite_colors", '
                '"type": {"type": "array", "items": {"type": "enum", '
                '"name": "Color", "symbols": ["RED", "GREEN", "BLUE"]}, '
                '"name": "favorite_color"}}, {"doc": "None", "name": '
                '"additional_field", "type": ["null", {"type": "array", '
                '"items": {"type": "enum", "name": "AdditionalColor", '
                '"symbols": ["YELLOW", "PURPLE", "ORANGE"]}, "name": '
                '"additional_field"}]}, {"doc": "None", "name": '
                '"timestamp_field", "type": {"type": "long", '
                '"logicalType": "timestamp-millis"}}, {"doc": "None", '
                '"default": null, "name": "new_field", "type": ["null", '
                '"string"]}], "namespace": "example.avro"}'
            }
        },
    ]
    assert [first_url, first_payload, second_url, second_payload] == expected_args
