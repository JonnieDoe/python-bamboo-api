#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""Module used to test if the API can trigger a plan build."""

import pytest
from json import load


INVALID_BUILD_PLAN_KEY = "TEST-XYZ"


def test_trigger_plan_run_ok(test_app):
    """Test to see if we can trigger a successful Bamboo plan build."""

    bamboo_api_client = test_app.get('bamboo_api_tests').bamboo_api_client
    test_type = test_app.get('test_type')
    plan_key = test_app.get('plan_keys', {}).get('plan_key', '')

    trigger_plan = bamboo_api_client.trigger_plan_build(
        plan_key=plan_key,
        req_values=(True, {})
    )
    # Check if the API got a HTTP 200 response code
    assert trigger_plan.get('status_code') == 200, trigger_plan

    # Read the JSON used by the mocking server
    with open(test_app.get('json_reference_db', "")) as json_file:
        endpoint_data = load(json_file)

    request_content = trigger_plan.get('content', {})

    reference_data = dict()
    results_reference = endpoint_data.get('trigger_a_build', [])
    for result_reference in results_reference:
        if test_type == 'LIVE':
            del result_reference["id"]

        reference_data = result_reference

        break

    missing_items = request_content.keys() - reference_data.keys()
    assert len(missing_items) == 0, f"Items that differ between API call response and reference dict: {missing_items}"


@pytest.mark.xfail(strict=True, reason="The test is expected to fail as the URL is not valid")
def test_trigger_plan_run_fail(test_app):
    """Test to see if we fail to trigger a successful Bamboo plan build."""

    bamboo_api_client = test_app.get('bamboo_api_tests').bamboo_api_client

    trigger_plan = bamboo_api_client.trigger_plan_build(
        plan_key=INVALID_BUILD_PLAN_KEY,
        req_values=(
            True,
            {
                'release.platform': "TEST",
                'branch': "XYZ"
            }
        )
    )

    # Check if the API got a HTTP 200 response code
    assert trigger_plan.get('status_code') == 200, trigger_plan
