from flask import abort
from werkzeug.security import generate_password_hash, check_password_hash

from config import database
from models.user import User

def register_user(username: str, password: str):
    """注册新用户：创建用户记录并返回用户信息"""
    # 用户名是否已存在
    existing = User.query.filter_by(username=username).first()
    if existing:
        abort(409, description="username already exists")
    # 哈希密码并保存用户
    password_hash = generate_password_hash(password)  # 生成密码哈希
    new_user = User(username=username, password_hash=password_hash)
    try:
        database.session.add(new_user)
        database.session.commit()
    except Exception:
        database.session.rollback() # 确保 session 干净，不影响后续请求
        abort(500, description="Database error")
    return {"status": "success"}

def authenticate_user(username: str, password: str):
    """验证用户登录，返回用户对象（用于生成JWT）"""
    if not username or not password:
        abort(400, description="username/password required")
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        abort(401, description="invalid credentials")
    return user
