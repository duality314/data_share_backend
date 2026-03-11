from apiflask import Schema
from apiflask.fields import Integer, String, Nested


class AuthRegisterInSchema(Schema):
    username = String(required=True)
    password = String(required=True)


class UserOutSchema(Schema):
    id = Integer(required=True)
    username = String(required=True)


class AuthLoginInSchema(Schema):
    username = String(required=True)
    password = String(required=True)


class AuthLoginOutSchema(Schema):
    token = String(required=True)
    user = Nested(UserOutSchema, required=True)


class StatusSchema(Schema):
    status = String(required=True)
