from apiflask import Schema
from apiflask.fields import Boolean, Integer, List, Nested, String


class ShareCreateInSchema(Schema):
    datasetId = Integer(required=True)
    message = String(load_default="")


class SharePatchInSchema(Schema):
    isApproved = Boolean(required=True)

class ShareCreateOutSchema(Schema):
    status = String(required=True)


class ShareItemSchema(Schema):
    id = Integer(required=True)
    consumerName = String(load_default="")
    providerName = String(load_default="")
    datasetName = String(required=True)
    request_description = String(load_default="")
    status = String(required=True)
    datasetId = Integer(load_default=None, allow_none=True)
    storage_type = String(load_default="unknown")


class ShareListOutSchema(Schema):
    sharing = List(Nested(ShareItemSchema), load_default=[])
    shared = List(Nested(ShareItemSchema), load_default=[])
    requests = List(Nested(ShareItemSchema), load_default=[])
