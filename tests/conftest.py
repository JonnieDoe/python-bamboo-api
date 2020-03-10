#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""BambooAPI REST client testing module."""

import configparser
import os
import pathlib
import psutil
import pytest
import subprocess
import time

# Add custom packages
from bamboo.api import BambooAPIClient


# Current working dir
CURRENT_DIR = pathlib.Path(__file__).resolve().parent

BAMBOO_USER = None
BAMBOO_PASS = None


class LiveTestBambooAPI:
    """Test the API against a live Bamboo server."""

    def __init__(
            self, server_url: str = None, username: str = None, password: str = None, verbose: bool = False
    ) -> None:
        """CTOR.
        :param server_url: Bamboo server URL [str]
        :param username: Bamboo username [str]
        :param password: Bamboo password [str]
        :param verbose: Get verbose [bool]
        """
        self.__bamboo_api_client = BambooAPIClient(
            server_url=server_url, username=username, password=password, verbose=verbose
        )

    @property
    def bamboo_api_client(self) -> object:
        """Get the API client handler."""
        return self.__bamboo_api_client


class LocalTestBambooAPI:
    """Test the API against a mock ("fake") Bamboo server."""

    def __init__(self, server_url: str = None, verbose: bool = False) -> None:
        """CTOR.
        :param server_url: Bamboo server URL [str]
        :param verbose: Get verbose [bool]
        """
        self.__bamboo_api_client = BambooAPIClient(server_url=server_url, verbose=verbose)
        self.__bamboo_api_client.is_auth_enabled = False

    @property
    def bamboo_api_client(self) -> object:
        """Get the API client handler."""
        return self.__bamboo_api_client


class BambooAPITests:
    """Tests to run."""

    def __init__(self, bamboo_api_client: object = None, **kwargs) -> None:
        """CTOR.
        :param bamboo_api_client: BambooAPIClient object handler [object]
        """
        self.__bamboo_api_client = bamboo_api_client

    @property
    def bamboo_api_client(self):
        """Get the API client handler."""
        return self.__bamboo_api_client

    @property
    def is_bamboo_api_set(self) -> bool:
        """Checks if the user supplied a Bamboo handler for server communication."""
        return self.bamboo_api_client or False


def get_config_options() -> dict:
    """Get the configuration options for running the test."""

    configuration = configparser.ConfigParser()
    configuration.read(str(pathlib.Path(CURRENT_DIR) / 'configuration.ini'))

    username = configuration['Bamboo']['username']
    password = configuration['Bamboo']['password']
    server_url = configuration['Bamboo']['server_url']
    test_type = configuration['Testing']['type']
    mock_server_url = configuration['Mock_Settings']['mock_server_url']

    return {
        "username": username,
        "password": password,
        "bamboo_server_url": server_url,
        "test_type": test_type,
        "mock_server_url": mock_server_url
    }


@pytest.fixture(scope='module')
def test_app():
    """Testing starts here."""

    config_opts = get_config_options()

    username = config_opts.get("username")
    if BAMBOO_USER:
        username = BAMBOO_USER

    password = config_opts.get("password")
    if BAMBOO_PASS:
        password = BAMBOO_PASS

    test_type = config_opts.get("test_type")
    if test_type == "LIVE":
        plan_key_trigger_build = ""
        build_key_to_query = ""
        artifacts_url = {
        }

        server_url = config_opts.get("bamboo_server_url")
        live_test_bamboo_api = LiveTestBambooAPI(
            server_url=server_url, username=username, password=password, verbose=True
        )
        bamboo_api_test_type = live_test_bamboo_api.bamboo_api_client
    elif test_type == "MOCK":
        plan_key_trigger_build = "TEST"
        build_key_to_query = "TEST-123"
        artifacts_url = {}

        mock_server_url = config_opts.get("mock_server_url")
        local_test_bamboo_api = LocalTestBambooAPI(server_url=mock_server_url, verbose=True)
        bamboo_api_test_type = local_test_bamboo_api.bamboo_api_client
    else:
        raise ValueError("Invalid internal test configuration")

    # ALL tests:
    #     "trigger_plan", "query_plan", "query_for_artifacts", "get_artifact", "stop_plan"
    bamboo_api_tests = BambooAPITests(bamboo_api_client=bamboo_api_test_type)

    assert bamboo_api_tests.is_bamboo_api_set, "No <BambooAPI> connection object supplied!"

    # Setup resources
    if test_type == "MOCK":
        print(f"{os.linesep}Setup the resources ...{os.linesep}")

        json_server_pid = subprocess.Popen(
            [
                "./node_modules/.bin/json-server",
                "--middlewares", str(pathlib.Path(CURRENT_DIR) / "middleware_json_server.js"),
                "--routes", str(pathlib.Path(CURRENT_DIR) / "routes.json"),
                "--watch", str(pathlib.Path(CURRENT_DIR) / "db.json")
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=CURRENT_DIR,
            universal_newlines=True
        ).pid

        time.sleep(5)

    yield {
        "bamboo_api_tests": bamboo_api_tests,
        "test_type": test_type,
        "json_reference_db": str(pathlib.Path(CURRENT_DIR) / 'reference_data.json'),
        "artifacts_destination_dir": pathlib.Path(CURRENT_DIR) / "artifacts",
        "artifacts_url": artifacts_url,
        "plan_keys": {
            "plan_key": plan_key_trigger_build,
            "build_key": build_key_to_query
        }
    }

    # Tear down
    if test_type == "MOCK":
        print(f"{os.linesep}Teardown has started ...{os.linesep}")

        # Kill JSON-Server process
        psutil_proc_to_kill = psutil.Process(json_server_pid)
        psutil_proc_to_kill.terminate()
        print(f"JSON server was killed (PID): {psutil_proc_to_kill}")

        print(f"{os.linesep}Teardown has ended!{os.linesep}")
