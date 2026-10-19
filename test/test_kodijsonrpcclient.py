import unittest
from unittest.mock import patch

import requests

from utils.kodijsonrpcclient import KodiJsonRpcClient


class TestKodiJsonRpcClient(unittest.TestCase):

    @patch("utils.kodijsonrpcclient.requests.request")
    def test_connection_error_includes_endpoint_and_hint(self, request):

        request.side_effect = requests.exceptions.ConnectionError(
            "Connection refused")
        client = KodiJsonRpcClient("192.168.178.20", 9080, None, None)

        with self.assertRaisesRegex(
                RuntimeError,
                r"192\.168\.178\.20:9080.*Connection refused.*Is Kodi running and reachable"):
            client.get_active_players()

    @patch("utils.kodijsonrpcclient.requests.request")
    def test_http_error_includes_endpoint(self, request):

        request.return_value.ok = False
        request.return_value.status_code = 503
        client = KodiJsonRpcClient("192.168.178.20", 9080, None, None)

        with self.assertRaisesRegex(RuntimeError, r"192\.168\.178\.20:9080.*503"):
            client.get_active_players()
