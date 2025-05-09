from nonebot import on_message
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.rule import to_me

test = on_message(rule=to_me(), priority=10, block=True)

@test.handle()
async def _(event: MessageEvent):
    await test.finish("susbot 接收到消息，運作正常！")