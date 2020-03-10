#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""Bamboo API client module used for communicating with the Bamboo server web service API."""

import json
import os
import requests

from abc import ABCMeta
# Third-party libs
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

# Add custom packages
from bamboo.config import BAMBOO_PASS, BAMBOO_USER
from bamboo.requests_utils import TimeoutHTTPAdapter
from bamboo.validation import Validation


# Mount it for both http and https usage
adapter = TimeoutHTTPAdapter(timeout=2.5)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

LINE_SEP = os.linesep


class BambooAccount(metaclass=ABCMeta):
    """Bamboo account info container.
    This is not intended to be instantiated. Please derive this class by using '<BambooAPIClient>' class.
    """

    __slots__ = ('__username', '__password')

    def __new__(cls, *args, **kwargs):
        if cls is BambooAccount:
            raise TypeError(f"{LINE_SEP * 2}BambooAccount class cannot be directly instantiated!{LINE_SEP * 2}")

        return object.__new__(cls)

    def __init__(self) -> None:
        """CTOR.
        Gets the credentials by loading them from the config module.
        """
        self.__username, self.__password = self.__load_credentials()

    @property
    def username(self) -> str:
        """Get the username."""
        return self.__username

    @username.setter
    def username(self, username):
        """Set the username to the desired value."""
        self.__username = username

    @property
    def password(self):
        """Get the password."""
        return self.__password

    @password.setter
    def password(self, password):
        """Set the password to the desired value."""
        self.__password = password

    @staticmethod
    def __load_credentials() -> tuple:
        if not all([BAMBOO_USER and BAMBOO_PASS]):
            print(
                "No credentials found while initializing the module! Please ensure you set them in explicitly!"
            )
            return None, None

        return BAMBOO_USER, BAMBOO_PASS


class BambooAPIClient(BambooAccount):
    """Bamboo API client interface with the Bamboo server API."""

    __slots__ = (
        '__trigger_plan_url_mask', '__stop_plan_url_mask', '__plan_results_url_mask', '__query_plan_url_mask',
        '__latest_queue_url_mask', '__artifact_url_mask', '__server_url', '__plan_key',
        '__verbose', '__http_header', '__is_auth_enabled'
    )

    def __init__(
            self, username: str = None, password: str = None, server_url: str = None, verbose: bool = False
    ) -> None:
        """CTOR.
        :param username: Bamboo username [str]
        :param password: Bamboo password [str]
        :param server_url: Bamboo server URL [str]
        :param verbose: Get verbose [bool]
        All the above params are optional.

        The <username> and <password> params are useful when we want to overwrite the BambooAccount credentials or we
        did not supplied any credentials so far.
        There might be cases when we work with a single user account that has permissions to interact with the
        Bamboo server API. But, in a cluster setup (multiple Bamboo servers) or multiple
        projects, there might be cases when we have to use several user accounts (probably different permissions per
        account). As so, the need to supply credentials when object is initialized does not exist.
        """
        super().__init__()

        if username:
            self.username = username

        if password:
            self.password = password

        # Useful when testing against a mock server or when there is no AUTH mechanism in place.
        self.__is_auth_enabled = True

        self.__plan_key = None

        self.__server_url = server_url
        self.__verbose = verbose

        self.__trigger_plan_url_mask = r'{server_url}/rest/api/latest/queue/'
        self.__stop_plan_url_mask = r'{server_url}/build/admin/stopPlan.action'
        self.__plan_results_url_mask = r'{server_url}/rest/api/latest/result/'
        self.__query_plan_url_mask = r'{server_url}/rest/api/latest/plan/'
        self.__latest_queue_url_mask = r'{server_url}/rest/api/latest/queue.json'
        self.__artifact_url_mask = r'{server_url}/browse/{plan_build_key}/artifact/{job_name}/{artifact_name}/'

        self.__http_header = {
            "Connection": "Keep-Alive",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "DNT": "1",
            "User-Agent": "Garbage browser: 5.6"
        }

    @property
    def auth(self):
        """Determine if we need to use AUTH or not."""
        if self.is_auth_enabled:
            return HTTPBasicAuth(self.username, self.password)

        return ()

    @property
    def is_auth_enabled(self) -> bool:
        """Perform authentication or not.
        Useful during testing against a mock server or when using no-auth at all.
        """
        return self.__is_auth_enabled

    @is_auth_enabled.setter
    def is_auth_enabled(self, is_set: bool) -> None:
        """Set AUTH on/off."""
        self.__is_auth_enabled = is_set

    @property
    def server_url(self) -> str:
        """Get the Bamboo server url."""
        return self.__server_url

    @server_url.setter
    def server_url(self, server_url_value: str) -> None:
        """Sets Bamboo server url. There might be cases when we need to work with multiple servers."""
        self.__server_url = server_url_value

    @property
    def plan_key(self) -> str:
        """Get the Bamboo plan key."""
        return self.__plan_key

    @plan_key.setter
    def plan_key(self, plan_key_value: str) -> None:
        """Sets the plan key to use while performing queries."""
        self.__plan_key = plan_key_value

    @property
    def artifact_url_mask(self) -> str:
        """Get the artifact url mask."""
        return self.__artifact_url_mask

    @property
    def latest_queue_url_mask(self) -> str:
        """Get the latest queue url mask."""
        return self.__latest_queue_url_mask

    @property
    def plan_results_url_mask(self) -> str:
        """Get the plan results url mask."""
        return self.__plan_results_url_mask

    @property
    def query_plan_url_mask(self) -> str:
        """Get the query url mask."""
        return self.__query_plan_url_mask

    @property
    def stop_plan_url_mask(self) -> str:
        """Get the url mask to stop a running plan."""
        return self.__stop_plan_url_mask

    @property
    def trigger_plan_url_mask(self) -> str:
        """Get the url mask to trigger builds."""
        return self.__trigger_plan_url_mask

    @property
    def http_header(self) -> dict:
        """Get the headers for HTTP request."""
        return self.__http_header

    @http_header.setter
    def http_header(self, http_header: dict) -> None:
        """Sets the corresponding HTTP header key-pair values."""
        self.__http_header = http_header

    @property
    def verbose(self) -> bool:
        """Get verbose."""
        return self.__verbose

    @verbose.setter
    def verbose(self, value: bool) -> None:
        """Sets the verbose option."""
        self.__verbose = value

    @staticmethod
    def pack_response_to_client(**values_to_pack) -> dict:
        """Pack the response to the user.

        :param values_to_pack: Values to pack in the response dictionary
        :return: A dict
        """
        response = dict()
        for key, value in values_to_pack.items():
            response[key] = value

        return response

    def get_request(self, **values_to_unpack) -> requests:
        """Performs a HTTP GET request to the Bamboo server.

        :param values_to_unpack: Values to un-pack in order to construct the HTTP Get request
        :return: A requests response object
        """
        url = values_to_unpack.get('url', "")
        headers = values_to_unpack.get('header', "") or self.http_header
        timeout = values_to_unpack.get('timeout', 60)
        allow_redirects = values_to_unpack.get('allow_redirects', False)

        try:
            response = http.get(url=url,
                                auth=self.auth,
                                headers=headers,
                                timeout=timeout,
                                allow_redirects=allow_redirects)
        except (
            requests.ConnectionError, requests.ConnectTimeout, requests.HTTPError,
            requests.RequestException, requests.Timeout
        ) as exc_value:
            raise ValueError(f"Error when requesting URL: '{url}'{LINE_SEP}{exc_value}")
        except Exception as exc_value:
            raise Exception(f"Unknown error when requesting URL: '{url}'{LINE_SEP}{exc_value}")

        return response

    def post_request(self, **values_to_unpack) -> requests:
        """Performs a HTTP POST request to the Bamboo server.

        :param values_to_unpack: Values to un-pack in order to construct the HTTP POST request
        :return: A requests response object
        """
        url = values_to_unpack.get('url', "")
        headers = values_to_unpack.get('header', "") or self.http_header
        data = values_to_unpack.get('data', {})
        timeout = values_to_unpack.get('timeout', 30)
        allow_redirects = values_to_unpack.get('allow_redirects', False)

        try:
            response = http.post(url=url,
                                 auth=self.auth,
                                 headers=headers,
                                 data=data,
                                 timeout=timeout,
                                 allow_redirects=allow_redirects)
        except (
            requests.ConnectionError, requests.ConnectTimeout, requests.HTTPError,
            requests.RequestException, requests.Timeout
        ) as exc_value:
            raise ValueError(f"Error when requesting URL: '{url}'{LINE_SEP}{exc_value}")
        except Exception as exc_value:
            raise Exception(f"Unknown error when requesting URL: '{url}'{LINE_SEP}{exc_value}")

        return response

    @Validation.check_input
    def trigger_plan_build(self, server_url: str = None, plan_key: str = None, req_values: tuple = None) -> dict:
        """Trigger a plan build using Bamboo API.
        TODO: deal with errors from plan restriction, like strict no of plans to build

        :param server_url: Bamboo server URL used in API call [str]
        Optional. Use this if you have a cluster of Bamboo servers and need to swap between servers.
        :param plan_key: Bamboo plan key [str]
        :param req_values: Values to insert into request (tuple)
        :return: A dictionary containing HTTP status_code and request content
        :raise: Exception, ValueError on Errors
        """

        server_url = server_url or self.server_url
        plan_key = plan_key or self.plan_key

        # Execute all stages by default if no options received
        request_payload = {'stage&executeAllStages': [True]}
        if req_values:
            # req_values[0] = True/False
            request_payload['stage&executeAllStages'] = [req_values[0]]

            # Example
            #     req_value[1] = {'bamboo.driver': "xyz", 'bamboo.test': "xyz_1"}
            #     API supports a list as values
            for key, value in req_values[1].items():
                # Use custom revision when triggering build
                if key.lower() == 'custom.revision':
                    request_payload["bamboo.customRevision"] = [value]
                    continue

                request_payload["bamboo.{key}".format(key=key)] = [value]

        url = self.trigger_plan_url_mask.format(server_url=server_url)
        url = f"{url}{plan_key}.json"
        if self.verbose:
            print(f"URL used to trigger build: '{url}'")

        # Trigger the build by performing a HTTP POST request and check HTTP response code
        http_post_response = self.post_request(url=url, data=json.dumps(request_payload))
        if http_post_response.status_code != 200:
            return self.pack_response_to_client(
                response=False, status_code=http_post_response.status_code, content=http_post_response.text, url=url
            )

        try:
            # Get the JSON reply from the web page
            http_post_response.encoding = "utf-8"
            response_json = http_post_response.json()
        except ValueError as exc_value:
            raise ValueError(f"Error decoding JSON: {exc_value}")
        except Exception as exc_value:
            raise Exception(f"Unknown error: {exc_value}")

        # Send response to client
        return self.pack_response_to_client(
            response=True, status_code=http_post_response.status_code, content=response_json, url=url
        )

    @Validation.check_input
    def stop_build(self, server_url: str = None, plan_build_key: str = None) -> dict:
        """Stop a running plan build from Bamboo using Bamboo API.
        This method is not officially supported, as so please be aware there might be conflicts when upgrading to a new
        Bamboo version. What I have observed between Bamboo official release, is that the return code for the POST URL
        returns different HTTP codes (like 200, 302). It all depends on the implementation in the Bamboo server.

        :param server_url: Bamboo server URL used in API call [str]
        Optional. Use this if you have a cluster of Bamboo servers and need to swap between servers.
        :param plan_build_key: Bamboo plan build key [str]
        :return: A dictionary containing HTTP status_code and request content
        :raise: Exception, ValueError on errors
        """

        server_url = server_url or self.server_url

        url = self.stop_plan_url_mask.format(server_url=server_url)
        url = f"{url}?planResultKey={plan_build_key}"

        if self.verbose:
            print(f"URL used to stop plan: '{url}'")

        # Stop a build by performing a HTTP POST request and check HTTP response code
        http_post_response = self.post_request(url=url)
        print(http_post_response.status_code)
        if http_post_response.status_code not in [200, 302]:
            return self.pack_response_to_client(
                response=False, status_code=http_post_response.status_code, content=http_post_response.text, url=url
            )

        # Send response to client
        return self.pack_response_to_client(
            response=True, status_code=http_post_response.status_code, content=http_post_response, url=url
        )

    @Validation.check_input
    def query_plan(self, server_url: str = None, plan_key: str = None) -> dict:
        """Query a plan build using Bamboo API.

        :param server_url: Bamboo server URL used in API call [str]
        Optional. Use this if you have a cluster of Bamboo servers and need to swap between servers.
        :param plan_key: Bamboo plan key [str]
        :return: A dictionary containing HTTP status_code and request content
        :raise: Exception, ValueError on errors
        """

        server_url = server_url or self.server_url
        plan_key = plan_key or self.plan_key

        url = self.plan_results_url_mask.format(server_url=server_url)
        url = f"{url}{plan_key}.json?max-results=10000"

        if self.verbose:
            print(f"URL used in query: '{url}'")

        # Query a build by performing a HTTP GET request and check HTTP response code
        http_get_response = self.get_request(url=url)
        if http_get_response.status_code != 200:
            return self.pack_response_to_client(
                response=False, status_code=http_get_response.status_code, content=http_get_response.text, url=url
            )

        try:
            # Get the JSON reply from the web page
            http_get_response.encoding = "utf-8"
            response_json = http_get_response.json()
        except ValueError as exc_value:
            raise ValueError(f"Error decoding JSON: {exc_value}")
        except Exception as exc_value:
            raise Exception(f"Unknown error: {exc_value}")

        # Send response to client
        return self.pack_response_to_client(
            response=True, status_code=http_get_response.status_code, content=response_json, url=url
        )

    @Validation.check_input
    def query_job_for_artifacts(
            self,
            server_url: str = None,
            plan_build_key: str = None,
            job_name: str = None,
            artifact_names: tuple = None
    ) -> dict:
        """Query Bamboo plan run build for stage artifacts.
        TODO: add support to get artifacts from sub-dirs as well

        :param server_url: Bamboo server URL used in API call [str]
        Optional. Use this if you have a cluster of Bamboo servers and need to swap between servers.
        :param plan_build_key: Bamboo plan build key [str]
        :param job_name: Bamboo plan job name [str]
        :param artifact_names: Names of the artifacts as in Bamboo plan stage job [tuple]
        :return: A dictionary containing HTTP status_code, request content and list of artifacts
        :raise: Exception, ValueError on Errors
        """

        server_url = server_url or self.server_url

        # Artifacts to return
        artifacts = dict()

        http_failed_conn_counter = 0
        for artifact_name in artifact_names:
            url = self.artifact_url_mask.format(
                server_url=server_url,
                plan_build_key=plan_build_key,
                job_name=job_name,
                artifact_name=artifact_name
            )

            if self.verbose:
                print(f"URL used to query for artifacts: '{url}'")

            # Query a build by performing a HTTP GET request and check HTTP response code
            http_get_response = self.get_request(url=url)
            if http_get_response.status_code != 200:
                http_failed_conn_counter += 1
                continue

            try:
                # page = requests.get(url).text  <-- Works if Bamboo plan does not require AUTH
                soup = BeautifulSoup(http_get_response.text, 'html.parser')
                # All "<a href></a>" elements
                a_href_elements = (soup.find_all('a', href=True))

                for a_href_element in a_href_elements:
                    file_path = a_href_element['href']
                    file_name = a_href_element.extract().get_text()

                    # Do not add HREF value in case PAGE NOT FOUND error
                    if file_name != "Site homepage":
                        artifacts[file_name] = f"{server_url}{file_path}"
            except ValueError as exc_value:
                raise ValueError(f"Error when downloading artifact: {exc_value}")
            except Exception as exc_value:
                raise Exception(f"Unknown error when downloading artifact: {exc_value}")

        http_return_code = 200
        if http_failed_conn_counter == len(artifact_names):
            http_return_code = 444

        response_to_client = self.pack_response_to_client(
            response=True, status_code=http_return_code, content=None, url=None
        )
        response_to_client['artifacts'] = artifacts

        # Send response to client
        return response_to_client

    def get_artifact(self, url: str = None, destination_file: str = None) -> dict:
        """Download artifacts from Bamboo plan build run.

        :param url: URL used in to download the artifact [str]
        :param destination_file: Full path to destination file [str]
        :return: A dictionary containing HTTP status_code and request content
        :raise: Exception, ValueError on Errors
        """

        if not url or not destination_file:
            return {'content': "Incorrect input provided!"}

        if self.verbose:
            print(f"URL used to download artifact: '{url}'")

        # Query a build by performing a HTTP GET request and check HTTP response code
        http_get_response = self.get_request(url=url)
        if http_get_response.status_code != 200:
            return self.pack_response_to_client(
                response=False, status_code=http_get_response.status_code, content=http_get_response.text, url=url
            )

        try:
            get_file = requests.get(url)

            with open(destination_file, 'wb') as f:
                f.write(get_file.content)
        except ValueError as exc_value:
            raise ValueError(f"Error when downloading artifact: {exc_value}")
        except Exception as exc_value:
            raise Exception(f"Unknown error when downloading artifact: {exc_value}")

        # Send response to client
        return self.pack_response_to_client(
            response=True, status_code=http_get_response.status_code, content=None, url=url
        )
