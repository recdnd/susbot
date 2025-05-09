
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, Event
from plugins.sus_broken import make_broken_comment

fallback_handler = on_message(priority=100, block=False)

@fallback_handler.handle()
async def fallback_sus(bot: Bot, event: Event):
    msg = event.get_plaintext().strip()
    if "@sus" not in msg:
        return

    trigger_keywords = {"總結", "总结", "評", "评价", "怎麼看", "呢", "吗", "？", "?"}
    if any(word in msg for word in trigger_keywords):
        return

    raw = msg.replace("@sus", "").strip()
    if not raw:
        return
    broken = make_broken_comment([raw])
    await bot.send(event, f"sus+「{broken}」")
