"""Wind HTTP 网关请求头测试。"""

import os
import sys
import unittest

_SRC = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, os.path.abspath(_SRC))

from wind_http_client import (  # noqa: E402
    MCP_CLIENT_NAME,
    MCP_CLIENT_VERSION,
    WindHttpClient,
    build_gateway_request_headers,
)


class TestGatewayHeaders(unittest.TestCase):
    def test_default_headers(self):
        headers = build_gateway_request_headers()
        self.assertEqual(headers["X-Wind-MCP-Client"], MCP_CLIENT_NAME)
        self.assertEqual(headers["X-Wind-MCP-Version"], MCP_CLIENT_VERSION)
        self.assertEqual(
            headers["User-Agent"],
            f"{MCP_CLIENT_NAME}/{MCP_CLIENT_VERSION}",
        )
        self.assertNotIn("Authorization", headers)

    def test_bearer_token_from_env(self):
        os.environ["WIND_GATEWAY_TOKEN"] = "secret-token"
        try:
            headers = build_gateway_request_headers()
            self.assertEqual(headers["Authorization"], "Bearer secret-token")
        finally:
            os.environ.pop("WIND_GATEWAY_TOKEN", None)

    def test_client_uses_shared_headers(self):
        custom = {"X-Wind-MCP-Client": "test"}
        client = WindHttpClient(request_headers=custom)
        self.assertIs(client.request_headers, custom)


if __name__ == "__main__":
    unittest.main()
