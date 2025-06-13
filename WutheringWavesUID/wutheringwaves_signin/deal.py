from typing import List, Optional, Union

from gsuid_core.bot import Bot
from gsuid_core.models import Event

from ..utils import hint
from ..utils.api.api import GAME_ID
from ..utils.api.model import KuroWavesUserInfo
from ..utils.database.models import WavesBind, WavesUser
from ..utils.error_reply import ERROR_CODE, WAVES_CODE_101, WAVES_CODE_103
from ..utils.waves_api import waves_api


async def get_cookie(bot: Bot, ev: Event) -> dict[str, dict[str,str]]:
    uid_list = await WavesBind.get_uid_list_by_game(ev.user_id, ev.bot_id)
    if uid_list is None:
        return {}

    uid_ck_dict: dict[str, dict[str,str]] = {}
    for uid in uid_list:
        waves_user: Optional[WavesUser] = await WavesUser.select_waves_user(
            uid, ev.user_id, ev.bot_id
        )
        if not waves_user:
            continue

        ck = await waves_api.get_self_waves_ck(uid, ev.user_id, ev.bot_id)
        if not ck:
            continue
        uid_ck_dict[uid]={}
        uid_ck_dict[uid]["ck"] = waves_user.cookie
        uid_ck_dict[uid]["did"] = waves_user.did
    return uid_ck_dict
