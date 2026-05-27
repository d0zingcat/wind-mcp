"""
Wind HTTP 代理客户端。

通过 REST 接口调用部署在 Wind 终端机器上的 HTTP 网关，模拟 WindPy 的 `w` 对象。
网关需实现 POST /wind 与 GET /health（见 README 代理模式说明）。
"""

import os

import pandas as pd
import requests

DEFAULT_BASE_URL = "http://127.0.0.1:6668"
BASE_URL = os.environ.get("WIND_API_URL", DEFAULT_BASE_URL)


class WindData:
    def __init__(self, raw_data=None, err_code=0, req_args=None):
        self.ErrorCode = err_code
        self.Codes = []
        self.Fields = []
        self.Times = []
        self.Data = []

        if isinstance(raw_data, dict) and "Data" in raw_data:
            self.Data = raw_data.get("Data", [])
            self.Codes = raw_data.get("Codes", [])
            self.Fields = raw_data.get("Fields", [])
            self.Times = raw_data.get("Times", [])
        elif (
            isinstance(raw_data, list)
            and len(raw_data) > 0
            and isinstance(raw_data[0], dict)
        ):
            keys = list(raw_data[0].keys())
            time_key = "index" if "index" in keys else None
            data_keys = [k for k in keys if k != time_key]

            if time_key:
                for row in raw_data:
                    t_val = row.get(time_key)
                    try:
                        self.Times.append(int(pd.to_datetime(t_val)))
                    except Exception:
                        self.Times.append(t_val)

            if req_args and len(req_args) > 0 and isinstance(req_args[0], str):
                self.Codes = [
                    c.strip() for c in req_args[0].split(",") if c.strip()
                ]

            self.Fields = data_keys
            for key in data_keys:
                self.Data.append([row.get(key) for row in raw_data])

            if not self.Data and self.Times:
                self.Data = [list(self.Times)]
        else:
            self.Data = raw_data if raw_data is not None else []


class WindHttpClient:
    def __init__(self, base_url=None):
        self.base_url = (base_url or BASE_URL).rstrip("/")

    def start(self):
        pass

    def stop(self):
        pass

    def isconnected(self):
        try:
            res = requests.get(f"{self.base_url}/health", timeout=5)
            if res.status_code != 200:
                return False
            payload = res.json()
            return payload.get("wind") == "connected"
        except Exception:
            return False

    def _call_wind_api(self, func_name, *args, **kwargs):
        usedf = kwargs.get("usedf", False)
        payload = {"type": func_name, "args": list(args)}

        try:
            res = requests.post(
                f"{self.base_url}/wind", json=payload, timeout=30
            )
            if res.status_code != 200:
                return -1, None

            body = res.json()
            error_code = body.get("errorCode", -1)
            raw_data = body.get("data", {})

            if error_code != 0:
                if usedf:
                    return error_code, raw_data
                return WindData(raw_data, error_code, list(args))

            if usedf:
                if isinstance(raw_data, list):
                    df = pd.DataFrame(raw_data)
                    for col in df.columns:
                        if df[col].dtype == "object":
                            try:
                                df[col] = pd.to_datetime(df[col], format="ISO8601")
                            except Exception:
                                pass
                    if "index" in df.columns:
                        df.set_index("index", inplace=True)
                    return error_code, df
                return error_code, pd.DataFrame()

            return WindData(raw_data, error_code, list(args))
        except Exception:
            return -1, None

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            return self._call_wind_api(name, *args, **kwargs)

        return wrapper


w = WindHttpClient(BASE_URL)
