from typing import Callable, List
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot import on
from nonebot.matcher import Matcher

_subscribed_callbacks: List[Callable[[GroupMessageEvent], None]] = []

def subscribe_group_message(callback: Callable[[GroupMessageEvent], None]):
    _subscribed_callbacks.append(callback)

    # ✅ 只註冊一次 matcher
    if not hasattr(subscribe_group_message, "_matcher"):
        matcher = on(GroupMessageEvent, block=False, priority=98)

        @matcher.handle()
        async def _(event: GroupMessageEvent):
            for cb in _subscribed_callbacks:
                try:
                    cb(event)
                except Exception as e:
                    print(f"[subscribe_group_message] callback error: {e}")

        subscribe_group_message._matcher = matcher  # 防重複註冊

    def unsubscribe():
        if callback in _subscribed_callbacks:
            _subscribed_callbacks.remove(callback)

    return unsubscribe
