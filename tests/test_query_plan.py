#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""Module used to test if the API can query a plan build."""

import pytest
from json import load


INVALID_BUILD_PLAN_KEY = "TEST-XXX-YZ"


def test_query_plan_run_ok(test_app):
    """Test to see if we can trigger a successful Bamboo plan build."""

    bamboo_api_client = test_app.get('bamboo_api_tests').bamboo_api_client
    test_type = test_app.get('test_type')
    plan_key = test_app.get('plan_keys', {}).get('build_key', '')

    query_plan = bamboo_api_client.query_plan(plan_key=plan_key)

    # Check if the API got a HTTP 200 response code
    assert query_plan.get('status_code') == 200, query_plan

    # Read the JSON used by the mocking server
    with open(test_app.get('json_reference_db', "")) as json_file:
        endpoint_data = load(json_file)

    # Get the data from the server
    request_content = query_plan.get('content', {})
    # We need to re-arrange the dict in case we use the MOCK testing, as the JSON-Server cannot serve the response
    # the way we need it
    if test_type == "MOCK":
        del request_content["id"]
        request_content = request_content.get("results", {})

    reference_data = dict()
    results_reference = endpoint_data.get('query_plan_reference', [])
    for result_reference in results_reference:
        if test_type not in result_reference["id"]:
            continue

        reference_data = result_reference['results']

        break

    missing_items = request_content.keys() - reference_data.keys()
    assert len(missing_items) == 0, f"Items that differ between API call response and reference dict: {missing_items}"


@pytest.mark.xfail(strict=True, reason="The test is expected to fail as the URL is not valid")
def test_query_plan_run_fail(test_app):
    """Test to see if we fail to trigger a successful Bamboo plan build."""

    bamboo_api_client = test_app.get('bamboo_api_tests').bamboo_api_client

    query_plan = bamboo_api_client.query_plan(plan_key=INVALID_BUILD_PLAN_KEY)

    # Check if the API got a HTTP 200 response code
    assert query_plan.get('status_code') == 200, query_plan
