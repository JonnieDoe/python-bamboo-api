#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""Config module: holds data for authentication."""

import os

# Default attempt to get the credentials
BAMBOO_USER = os.getenv('BAMBOO_USER')
BAMBOO_PASS = os.getenv('BAMBOO_PASS', "NO_PASS")
