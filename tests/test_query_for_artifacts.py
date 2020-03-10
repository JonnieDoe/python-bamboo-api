#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""Module used to test if the API can query for artifacts."""

import pytest


INVALID_BUILD_PLAN_KEY = "TEST-XXX-43"


def test_query_for_artifacts_ok(test_app):
    """Test to see if we can successful query a build run in order to get the artifacts from a stage."""

    bamboo_api_client = test_app.get('bamboo_api_tests').bamboo_api_client
    plan_build_key = test_app.get('plan_keys', {}).get('build_key', '')
    test_type = test_app.get('test_type')

    if test_type == "MOCK":
        plan_build_key = "TEST-123"
        job_name = "RESULT"
        artifact_names = ("Build-log",)
    else:
        plan_build_key = plan_build_key
        job_name = ""
        artifact_names = ("",)

    query_for_artifacts = bamboo_api_client.query_job_for_artifacts(
        plan_build_key=plan_build_key,
        job_name=job_name,
        artifact_names=artifact_names
    )

    # Check if the API got a HTTP 200 response code
    assert query_for_artifacts.get('status_code') == 200, query_for_artifacts

    artifacts = query_for_artifacts.get('artifacts')
    print(f"Found artifacts: {artifacts}")

    # Check if we could found any artifacts
    assert len(artifacts) != 0, artifacts


@pytest.mark.xfail(strict=True, reason="The test is expected to fail as the URL is not valid")
def test_query_for_artifacts_fail(test_app):
    """Test to see if the query for artifacts of a build run fails as expected."""

    bamboo_api_client = test_app.get('bamboo_api_tests').bamboo_api_client

    query_for_artifacts_status = bamboo_api_client.query_job_for_artifacts(
        plan_key=INVALID_BUILD_PLAN_KEY,
        job_name="TEST",
        artifact_names=("Build-log",)
    )

    # Check if the API got a HTTP 200 response code
    assert query_for_artifacts_status.get('status_code') == 200, query_for_artifacts_status
