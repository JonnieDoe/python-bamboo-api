#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""Module used to test if the API can stop a plan build."""


def test_stop_plan_run_ok(test_app):
    """Test to see if we can stop a Bamboo plan build."""

    bamboo_api_client = test_app.get('bamboo_api_tests').bamboo_api_client
    plan_build_key = test_app.get('plan_keys', {}).get('build_key', '')

    stop_plan = bamboo_api_client.stop_build(plan_build_key=plan_build_key)

    # Check if the API got a HTTP 302/200 response code
    assert stop_plan.get('status_code') == 302, stop_plan
