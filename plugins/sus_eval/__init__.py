
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, Event
from plugins.sus_broken import make_broken_comment
import asyncio

sus_eval = on_message(priority=30, block=False)
user_messages = {}

@sus_eval.handle()
async def eval_request(bot: Bot, event: Event):
    msg = event.get_plaintext()
    if "@sus" not in msg:
        return

    trigger_words = {"總結", "总结", "評", "评价", "怎麼看", "呢", "吗", "？", "?"}
    if not any(word in msg for word in trigger_words):
        return

    gid = event.group_id
    all_recent = []
    for k, v in user_messages.items():
        if str(gid) in k:
            all_recent.extend(v[-10:])

    if not all_recent:
        return

    await asyncio.sleep(1)
    await bot.send(event, "可..可以說嗎..")
    await asyncio.sleep(1)
    com = make_broken_comment(all_recent)
    await bot.send(event, f"sus認為：{com}")
