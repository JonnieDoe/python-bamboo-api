#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""Module used to test if the API can download a plan build artifacts."""


def test_get_artifacts(test_app):
    """Test to see if we can get an artifact from a Bamboo plan build."""

    bamboo_api_client = test_app.get('bamboo_api_tests').bamboo_api_client
    artifacts_destination_dir = test_app.get('artifacts_destination_dir')
    artifacts_url = test_app.get('artifacts_url')

    for artifact_name, artifact_url in artifacts_url.items():
        print(f"Getting artifact '{artifact_name}': '{artifact_url}'")

        get_artifact = bamboo_api_client.get_artifact(
            url=artifact_url,
            destination_file=str(artifacts_destination_dir / artifact_name)
        )
        # Check if the API got a HTTP 200 response code
        assert get_artifact.get('status_code') == 200, get_artifact
