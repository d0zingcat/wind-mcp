"""wind_edb 工具单元测试（mock Wind 后端）。"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

_SRC = os.path.join(os.path.dirname(__file__), "..", "src")
if _SRC not in sys.path:
    sys.path.insert(0, os.path.abspath(_SRC))


class WindEdbToolTest(unittest.TestCase):
    @patch("wind_mcp_direct_server.w")
    def test_wind_edb_calls_backend_and_normalizes_codes(self, mock_w):
        import wind_mcp_direct_server as srv

        mock_result = MagicMock()
        mock_result.ErrorCode = 0
        mock_result.Data = [[1.0, 2.0]]
        mock_result.Codes = ["M0000612"]
        mock_result.Fields = ["CLOSE"]
        mock_result.Times = [20240131]
        mock_w.edb.return_value = mock_result

        out = srv.wind_edb(
            ["M0000612", "M0000705"],
            "2024-01-01",
            "2025-03-14",
            "Fill=Previous",
        )

        mock_w.edb.assert_called_once_with(
            "M0000612,M0000705",
            "2024-01-01",
            "2025-03-14",
            "Fill=Previous",
        )
        self.assertEqual(out["ErrorCode"], 0)
        self.assertEqual(out["Codes"], ["M0000612"])

    @patch("wind_mcp_direct_server.w")
    def test_wind_edb_returns_error_on_exception(self, mock_w):
        import wind_mcp_direct_server as srv

        mock_w.edb.side_effect = RuntimeError("wind down")

        out = srv.wind_edb("M0000612", "2024-01-01", "2025-03-14")

        self.assertEqual(out["ErrorCode"], -1)
        self.assertIn("wind down", out["error"])


if __name__ == "__main__":
    unittest.main()
