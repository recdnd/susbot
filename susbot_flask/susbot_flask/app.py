# flask_susbot/app.py
from flask import Flask
from flask_cors import CORS
from flask_susbot.routes.dispatcher import dispatcher_bp

app = Flask(__name__)
CORS(app)

# ✅ 註冊 dispatcher 為主入口
app.register_blueprint(dispatcher_bp)

# ✅ 可視需要保留原來的其他 route，例如 goodmorning
# from routes.goodmorning_handler import goodmorning_bp
# app.register_blueprint(goodmorning_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
