#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""Requests specific settings."""

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


RETRY_STRATEGY = Retry(
    backoff_factor=1,
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "POST", "OPTIONS"]
)

DEFAULT_TIMEOUT = 5  # seconds


class TimeoutHTTPAdapter(HTTPAdapter):
    """Custom timeout adapter."""

    def __init__(self, max_retries=RETRY_STRATEGY, *args, **kwargs):
        """CTOR."""

        self.timeout = DEFAULT_TIMEOUT

        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]

        super().__init__(max_retries=max_retries, *args, **kwargs)

    def send(self, request, **kwargs):
        """Overwrite method from HTTPAdapter base class."""

        timeout = kwargs.get("timeout")
        if not timeout:
            kwargs["timeout"] = self.timeout

        return super().send(request, **kwargs)
