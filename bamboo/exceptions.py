#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""This module contains custom made exceptions."""


class HTTPErrorException(Exception):
    """Custom exception for HTTP requests."""

    def __init__(self, error_message: str) -> None:
        """CTOR.
        :param error_message: Error message to return
        """
        super(HTTPErrorException, self).__init__(error_message)


class EncodingJSONException(Exception):
    """Custom exception for JSON encoding errors."""

    def __init__(self, error_message: str) -> None:
        """CTOR.
        :param error_message: Error message to return
        """
        super(EncodingJSONException, self).__init__(error_message)


class DownloadErrorException(Exception):
    """Custom exception for Web downloading errors."""

    def __init__(self, error_message: str) -> None:
        """CTOR.
        :param error_message: Error message to return
        """
        super(DownloadErrorException, self).__init__(error_message)
