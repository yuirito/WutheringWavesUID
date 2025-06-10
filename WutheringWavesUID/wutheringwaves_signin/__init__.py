from gsuid_core.aps import scheduler
from gsuid_core.gss import gss

@scheduler.scheduled_job("cron", hour=0, minute=1)
async def auto_signin():
    for bot_id in gss.active_bot:
        await gss.active_bot[bot_id].target_send(
            "定时任务测试",
            "group",
            "718927461",
            "onebot",
            "",
            "",
        )