from apiflask import APIBlueprint
from flask_jwt_extended import create_access_token

from controllers.auth_controller import register_user, authenticate_user
from schemas import AuthLoginInSchema, AuthLoginOutSchema, AuthRegisterInSchema, StatusSchema

auth_bp = APIBlueprint("auth", __name__)

@auth_bp.post("/register")
@auth_bp.input(AuthRegisterInSchema , arg_name = "data")
@auth_bp.output(StatusSchema, 200)
def register(data):
    username = data["username"]
    password = data["password"]
    # 调用控制器执行注册逻辑
    user_info = register_user(username, password)
    return user_info

@auth_bp.post("/login")
@auth_bp.input(AuthLoginInSchema, arg_name = "data")
@auth_bp.output(AuthLoginOutSchema, 200)
def login(data):
    username = data["username"]
    password = data["password"]
    # 验证用户名密码
    user = authenticate_user(username, password)
    # 生成JWT令牌，有效期7天，载荷包含用户id（作为身份）和用户名
    access_token = create_access_token(identity=str(user.id), additional_claims={"username": user.username}, expires_delta=False)
    # 返回令牌和用户信息
    return {
        "token": access_token,
        "user": { "id": user.id, "username": user.username }
    }
