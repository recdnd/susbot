import re
import random
from collections import defaultdict

from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg

# 群組 → 用戶 → 發言記錄
message_cache = defaultdict(lambda: defaultdict(list))
MAX_LOG = 30

# ✅ 用新的方式定義 Message 捕獲器（避免錯誤）
mimic_logger = on_message(priority=10, block=False)

@mimic_logger.handle()
async def cache_message(event: GroupMessageEvent):
    gid = event.group_id
    uid = event.user_id
    text = str(event.message).strip()
    if text and not text.startswith("/") and len(text) <= 100:
        message_cache[gid][uid].append(text)
        if len(message_cache[gid][uid]) > MAX_LOG:
            message_cache[gid][uid] = message_cache[gid][uid][-MAX_LOG:]

# ✅ 模擬語言輸出命令
mimic_cmd = on_command("模擬", aliases={"模仿", "模拟"}, priority=2)

@mimic_cmd.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    gid = event.group_id
    target = None

    for seg in args:
        if seg.type == "at":
            target = seg.data.get("qq")
            break
    if not target:
        target = str(event.user_id)

    logs = message_cache[gid].get(int(target), [])
    if not logs:
        await mimic_cmd.finish("（無法模仿——記憶缺失）")

    tokens = []
    for line in logs:
        parts = re.split(r"[，。、！？.\s]+", line)
        tokens.extend([p for p in parts if 1 < len(p) <= 8])

    if len(tokens) < 6:
        await mimic_cmd.finish("（語素不足，模仿失效）")

    selected = random.sample(tokens, k=random.randint(6, 12))
    out = "..." + "..".join(selected) + "...."
    await mimic_cmd.finish(out)
