from gsuid_core.aps import scheduler
from gsuid_core.gss import gss
from gsuid_core.sv import SV
from .deal import get_cookie
from .signin import game_signin
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from ..utils.database.models import  WavesUser
sv_kuro_sign_in = SV("库街区签到")

@scheduler.scheduled_job("cron", hour=2, minute=25)
async def auto_signin():
    wavesTokenUsers = await WavesUser.get_waves_all_user()
    msg: list[str] = []
    for w in wavesTokenUsers:
        ck= w.cookie
        uid = w.uid
        did = w.did
        msg.append(f"uid:{uid}签到结果："+game_signin(uid = uid, ck = ck, did = did))
    result_msg = "自动签到结果：\n" + "\n".join(msg)

    notify_groups = ["718927461","594918736"]
    for gp in notify_groups:
        for bot_id in gss.active_bot:
            await gss.active_bot[bot_id].target_send(
                result_msg,
                "group",
                gp,
                "onebot",
                "3248755428",
                "",
            )

@sv_kuro_sign_in.on_command(("签到", "signin", "checkin", "千岛"))
async def send_waves_get_ck_msg(bot: Bot, ev: Event):
    uid_ck_dict = await get_cookie(bot, ev)
    if not uid_ck_dict:
        await bot.send("您当前未绑定token或者token已全部失效\n")
        return
    for uid, ck_did in uid_ck_dict.items():
        ck = ck_did["ck"]
        did = ck_did["did"]
        msg = game_signin(uid=uid, ck=ck, did =did)
        await bot.send(f"uid:{uid}签到结果："+msg)

