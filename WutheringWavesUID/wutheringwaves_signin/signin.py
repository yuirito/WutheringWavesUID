from typing import Any
import datetime
import requests


def get_game_headers(ck: str, did: str) -> dict[str, str]:
    """
    生成游戏签到请求头
    :return: 请求头字典
    日志记录：无
    """
    headers = {
        "Host": "api.kurobbs.com",
        "Accept": "application/json, text/plain, */*",
        "Sec-Fetch-Site": "same-site",
        "source": "ios",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Fetch-Mode": "cors",
        "token": ck,
        "devCode": did,
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) KuroGameBox/2.2.0",
        "Connection": "keep-alive",
        "content-type": "application/x-www-form-urlencoded; charset=utf-8"
    }
    return headers


def bbssignin(ck: str, did: str) -> str:
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
        response = requests.post(url, headers=get_game_headers(ck,did), data=data)
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

def get_user_info_by_token(ck: str, did: str) -> str:
    """
    根据 token 和用户 ID 获取用户信息
    :param token: 用户的 token
    :param devcode: 设备代码
    :param distinct_id: 唯一标识符
    :return: 用户 ID 或错误信息
    """

    url = "https://api.kurobbs.com/user/mineV2"
    
    try:
        response = requests.post(url, headers=get_game_headers(ck = ck, did=did))
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 200:
            user_id = result.get("data", {}).get("mine", {}).get("userId", "")
            #print(f"用户ID: {user_id}")
            return user_id
        else:
            return ""
    except requests.RequestException as e:
        return ""

def get_sign_prize(role_id, user_id, ck, did):
    """
    获取签到奖励
    :param role_id: 角色 ID
    :param user_id: 用户 ID
    :return: 奖励名称或错误信息
    日志记录：
        - debug: 签到奖励响应
        - debug: 成功获取签到奖励
        - error: 获取签到奖励失败
    """
    try:
        url = "https://api.kurobbs.com/encourage/signIn/queryRecordV2"
        data = {
            "gameId": 3,
            "serverId": '76402e5b20be2c39f095a152090afddc',
            "roleId": role_id,
            "userId": user_id
        }
        response = requests.post(url, headers=get_game_headers(ck=ck, did=did), data=data)
        response.raise_for_status()
        response_data = response.json()
        if response_data.get("code") != 200:
            error_message = f"获取签到奖励失败，响应代码: {response_data.get('code')}, 消息: {response_data.get('msg')}"
            return "ERROR:"+error_message
        data = response_data["data"]
        if isinstance(data, list) and len(data) > 0:
            first_goods_name = data[0]["goodsName"]
            return (f"成功获取签到奖励: {first_goods_name}")
        error_message = "ERROR:签到奖励数据格式不正确或数据为空"
        return error_message
    except Exception as e:
        error_message = f"ERROR:获取签到奖励失败: {e}"
        return error_message

def sign_in(role_id, user_id, ck, did):
        """
        执行游戏签到
        :param game_id: 游戏 ID
        :param role_id: 角色 ID
        :param user_id: 用户 ID
        :param month: 当前月份
        :param auto_reple_sign: 是否自动补签
        :return: 签到结果或错误信息
        日志记录：
            - debug: 游戏签到响应
            - info: 签到成功或已签到
            - error: 签到失败
        """
        try:
            url = "https://api.kurobbs.com/encourage/signIn/v2"
            game_name = "鸣潮"
            data = {
                "gameId": 3,
                "serverId": "76402e5b20be2c39f095a152090afddc",
                "roleId": role_id,
                "userId": user_id,
                "reqMonth": datetime.datetime.now().strftime("%m")
            }
    
            response = requests.post(url, headers=get_game_headers(ck, did), data=data)
            response.raise_for_status()
            response_data = response.json()
            code = response_data.get("code")
            result = ""
            
            if code == 200:
                # 如果成功，调用 get_sign_prize 获取奖励列表
                goods_names = get_sign_prize(role_id, user_id, ck, did)
                
                result = f"签到成功，签到奖励: {goods_names}"
            elif code == 1511:
                goods_names = get_sign_prize(role_id, user_id, ck, did)
                result = f"{game_name}今天已签到，签到奖励: {goods_names}"
            elif code == 1513:
                return f"ERROR:{game_name}签到报错：用户信息异常"
            elif code == 220:
                return f"ERROR:{game_name}签到报错：登录已过期，请重新登录"
            else:
                error_message = f"{game_name}签到失败，响应代码: {code}, 消息: {response_data.get('msg')}"
                return "ERROR:"+error_message
        
            
            return result
        except Exception as e:
            error_message = f"签到失败: {e}"
            return "ERROR:"+error_message

def game_signin(uid:str, ck:str, did:str) -> str:
    user_id = get_user_info_by_token(ck, did)
    if user_id == "":
        return "获取用户UserId失败"
    return sign_in(role_id=uid, user_id=user_id, ck = ck, did = did)
