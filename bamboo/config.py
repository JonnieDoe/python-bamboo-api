#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""Config module: holds data for authentication."""

import logging.config
import os
import pathlib
import yaml

# Default attempt to get the credentials
BAMBOO_USER = os.getenv('BAMBOO_USER')
BAMBOO_PASS = os.getenv('BAMBOO_PASS', "NO_PASS")

# Current working dir
CURRENT_DIR = pathlib.Path(__file__).resolve().parent

with open(str(CURRENT_DIR / 'logging_config.yaml'), 'r') as fd_in:
    logging_config = yaml.safe_load(fd_in.read())
    logging.config.dictConfig(logging_config)

# Create a logger
LOGGER = logging.getLogger(__name__)
