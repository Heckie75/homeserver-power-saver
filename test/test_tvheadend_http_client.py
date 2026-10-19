import unittest
from unittest.mock import patch

import requests

from checkers.tvheadendinterruptionchecker import TvHeadendHttpClient


class TestTvHeadendHttpClient(unittest.TestCase):

    @patch("checkers.tvheadendinterruptionchecker.requests.request")
    def test_request_failure_includes_endpoint_and_resource(self, request):

        request.side_effect = requests.exceptions.ConnectionError(
            "Connection refused")
        client = TvHeadendHttpClient("192.168.178.20", 9981, None, None)

        with self.assertRaisesRegex(
                RuntimeError,
                r"192\.168\.178\.20:9981.*status/subscriptions.*Connection refused"):
            client.get_subscriptions()

    @patch("checkers.tvheadendinterruptionchecker.requests.request")
    def test_request_uses_timeout(self, request):

        request.return_value.ok = True
        request.return_value.text = '{"totalCount": 0}'
        client = TvHeadendHttpClient("192.168.178.20", 9981, None, None)

        self.assertEqual(client.get_subscriptions(), {"totalCount": 0})
        self.assertEqual(request.call_args.kwargs["timeout"], 5)
