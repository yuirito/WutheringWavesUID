from typing import Any

import requests


def get_bbs_headers(ck: str) -> dict[str, str]:
    """
    生成库街区请求头
    :return: 请求头字典
    日志记录：无
    """
    return {
        "Host": "api.kurobbs.com",
        "source": "ios",
        "lang": "zh-Hans",
        "User-Agent": "KuroGameBox/48 CFNetwork/1492.0.1 Darwin/23.3.0",
        "Cookie": f"user_token={ck}",
        "channelId": "1",
        "channel": "appstore",
        "version": "2.2.0",
        "token": ck,
        "Connection": "keep-alive",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "model": "iPhone15,2",
        "osVersion": "17.3",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Accept-Encoding": "gzip, deflate, br",
    }


def bbssignin(ck: str) -> str:
    """
    执行库街区签到
    :return: 签到结果或错误信息
    日志记录：
    - debug: 库街区签到响应
    - info: 成功完成签到
    - error: 签到失败
    """
    try:
        url = "https://api.kurobbs.com/user/signIn"
        data = {"gameId": "2"}
        response = requests.post(url, headers=get_bbs_headers(ck), data=data)
        response.raise_for_status()
        resp_data: dict[str, Any] = response.json()
        if resp_data["code"] == 200:
            return "签到成功"
        else:
            msg: str = str(resp_data.get("msg", "未知错误"))
            return f"签到失败: {msg}"
    except Exception as e:
        error_message = f"签到失败: {e}"
        return "ERROR:" + error_message
