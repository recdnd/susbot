from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

sus = on_command("sus", aliases={"/sus"}, priority=1)

@sus.handle()
async def handle_sus(event: GroupMessageEvent):
    await sus.finish(Message("sus知道了……你就是那個sus！"))
