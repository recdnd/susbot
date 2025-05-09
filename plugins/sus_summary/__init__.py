from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, Event
from plugins.sus_broken import make_broken_summary
from plugins.sus_switch import is_disabled
import datetime, asyncio
import random

user_messages = {}
daily_trigger = {}

SUMMARY_TEMPLATES = [
    "sus言：{summary}",
    "sus語: {summary}",
    "sus總結：{summary}",
    "「{summary}」ーーsus",
]

sus_summary = on_message(priority=20, block=False)

@sus_summary.handle()
async def handle_summary(bot: Bot, event: Event):
    uid = event.user_id
    gid = event.group_id
    if is_disabled(gid):
        return
    gid = event.group_id
    key = f"{gid}_{uid}"
    text = event.get_plaintext().strip()

    user_messages.setdefault(key, []).append(text)
    if len(user_messages[key]) > 50:
        user_messages[key] = user_messages[key][-50:]

    if gid not in daily_trigger or daily_trigger[gid] != datetime.date.today():
        if len(user_messages[key][-5:]) >= 5 and len(user_messages[key]) >= 10:
            daily_trigger[gid] = datetime.date.today()
            await asyncio.sleep(3)
            await bot.send(event, "....sus在觀察..")
            await asyncio.sleep(5)
            summary = make_broken_summary(user_messages[key][-10:])
            template = random.choice(SUMMARY_TEMPLATES)
            await bot.send(event, template.format(summary=summary))
