# app.py
from apiflask import APIFlask
from werkzeug.exceptions import HTTPException
from flask_cors import CORS

from config import Config
from db import database, jwt


def create_app():
    app = APIFlask(
        __name__,
        title="Data Share Backend API",
        version="1.0.0",
        docs_path="/docs",
        openapi_blueprint_url_prefix="/",
    )
    app.config.from_object(Config)
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["JSON_SORT_KEYS"] = False

    app.security_schemes = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }

    database.init_app(app)  # 初始化数据库
    jwt.init_app(app)       # 初始化 JWT 管理
    CORS(app, origins=[Config.CORS_ORIGIN], supports_credentials=True)  # 配置跨域

    # 注册蓝图
    from routes import auth_bp, dataset_bp, share_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(dataset_bp, url_prefix="/api/datasets")
    app.register_blueprint(share_bp, url_prefix="/api/shares")
    # 健康检查路由
    @app.route("/health", methods=["GET"])
    def health_check():
        return {"ok": True}

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        status = err.code or 500
        return {
            "code": status,
            "message": err.name,
            "details": err.description,
        }, status

    return app


if __name__ == "__main__":
    # 数据库连接测试和应用启动
    app = create_app()
    try:
        # 测试数据库连接
        with app.app_context():
            database.create_all()  # 自动建表（仅用于开发测试环境，生产应使用迁移）
        print("Database connected and tables ready.")
    except Exception as e:
        print(f"Database connection failed: {e}")
    # 启动 Flask 开发服务器
    app.run(host="127.0.0.1", port=54320, debug=True)
