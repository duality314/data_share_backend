from apiflask import Schema
from apiflask.fields import Integer, String, Nested

class AuthBaseSchema(Schema):
    username = String(required=True)
    password = String(required=True,load_only=True)

class AuthRegisterInSchema(AuthBaseSchema):
    pass


class UserOutSchema(Schema):
    id = Integer(required=True,dump_only=True)
    username = String(required=True)


class AuthLoginInSchema(AuthBaseSchema):
    pass


class AuthLoginOutSchema(Schema):
    token = String(required=True,dump_only=True)
    user = Nested(UserOutSchema, required=True)


class StatusSchema(Schema):
    status = String(required=True,dump_only=True)
