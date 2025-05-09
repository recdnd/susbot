import sys
sys.path.append("./")

import nonebot
from nonebot.adapters.onebot.v11 import Adapter

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(Adapter)

# ✅ 配置 token 和允許來源
driver.config.onebot_access_token = ""
driver.config.websocket_reverse_allowed_origins = ["*"]

# ✅ 載入 plugins 資料夾
nonebot.load_plugins("plugins")

if __name__ == "__main__":
    nonebot.run(host="127.0.0.1", port=8081)
