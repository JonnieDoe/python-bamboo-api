#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""Validation module: used to check if the method input params were initialized with actual values."""

from functools import wraps
from inspect import getcallargs as ins_getcallargs


class Validation:
    """Used to validate method input arguments."""

    @staticmethod
    def check_input(func):
        """Wrapper validate mandatory arguments inside method(s) call."""
        @wraps(func)
        def inner(*args, **kwargs):
            # Get the method name
            func_name = func.__name__

            # Get all method arguments as a dict
            get_call_args = ins_getcallargs(func, *args, **kwargs)

            # Check if the method received the Bamboo server URL
            if not get_call_args['self'].server_url and not get_call_args['server_url']:
                return {'content': f"Error in <{func_name}> method: No Bamboo server supplied!"}

            # Check if the method received the Bamboo plan/build key
            if not any(get_call_args.get('plan_build_key', []) or get_call_args.get('plan_key', [])):
                return {'content': f"Error in <{func_name}> method: No Bamboo plan/build build key supplied!"}

            return func(*args, **kwargs)

        return inner
