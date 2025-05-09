from nonebot import on_message
from nonebot.adapters.onebot.v11 import MessageEvent
import re

DISABLED_GROUPS = set()

def is_disabled(group_id: int) -> bool:
    return group_id in DISABLED_GROUPS

# 偵測封禁關鍵詞
pattern_disable = re.compile(r"(停|滾|垃圾|廢物|閉嘴|闭嘴|關|关|不别|shut)", re.IGNORECASE)
# 偵測解禁關鍵詞
pattern_enable = re.compile(r"(對.*?不起|原諒|原谅|不起|對.*?唔該)", re.IGNORECASE)

switch_handler = on_message(priority=1, block=False)

@switch_handler.handle()
async def _(event: MessageEvent):
    if not hasattr(event, "group_id"):
        return  # 忽略非群聊事件

    gid = event.group_id
    text = str(event.message).lower()

    if pattern_disable.search(text) and event.is_tome():
        DISABLED_GROUPS.add(gid)
        await switch_handler.send("對...對不起....sus不發了...")
    elif pattern_enable.search(text) and event.is_tome():
        if gid in DISABLED_GROUPS:
            DISABLED_GROUPS.remove(gid)
        await switch_handler.send("...sus...sus原諒...拜託不要嚇sus...")
