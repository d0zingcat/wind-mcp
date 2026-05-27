"""选择 Wind 后端：本机 WindPy 或 HTTP 代理。"""

import os
import sys


def _truthy(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")


def _should_use_proxy() -> bool:
    if _truthy(os.environ.get("WIND_USE_PROXY", "")):
        return True
    return bool(os.environ.get("WIND_API_URL", "").strip())


def _load_http_proxy_backend():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    from wind_http_client import w, BASE_URL

    if not os.environ.get("WIND_API_URL", "").strip():
        print(
            "[WARN] 未设置 WIND_API_URL，使用默认地址 "
            f"{BASE_URL}。请指向你的 Wind HTTP 网关。"
        )

    return w, True, f"http proxy ({BASE_URL})"


def load_wind_backend():
    """
    返回 (w, using_proxy, backend_label)。

    启用代理：WIND_USE_PROXY=1 或 WIND_API_URL，或命令行 --wind-proxy / --wind-api-url
    否则使用本机 WindPy。
    """
    if _should_use_proxy():
        return _load_http_proxy_backend()

    from WindPy import w

    return w, False, "local WindPy"
