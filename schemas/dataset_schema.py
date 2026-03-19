from apiflask import Schema
from apiflask.fields import Boolean, Integer, List, Nested, String, File, Function


class DatasetItemSchema(Schema):
    id = Integer(required=True, dump_only=True)
    name = String(required=True)
    description = String(required=True)
    domain = String(required=True)
    dataType = String(attribute="data_type", required=True)
    fileSize = Integer(attribute="file_size", required=True)
    isListed = Boolean(attribute="is_listed", required=True)
    downloads = Integer(required=True, dump_only=True)
    ownerId = Integer(attribute="owner_id", required=True)
    createdAt = Function(lambda obj: getattr(obj, "id", None), required=True)


class DatasetOutSchema(Schema):
    dataset = Nested(DatasetItemSchema, required=True)


class DatasetMineOutSchema(Schema):
    owned = List(Nested(DatasetItemSchema), required=True)


class DatasetMarketOutSchema(Schema):
    list = List(Nested(DatasetItemSchema), required=True)


class DatasetUploadFormInSchema(Schema):
    name = String(required=True)
    description = String(load_default="")
    domain = String(load_default="general")
    dataType = String(load_default="file")


class DatasetUploadFileInSchema(Schema):
    file = File(required=True)


class DatasetUploadInSchema(Schema):
    name = String(required=True)
    description = String(load_default="")
    domain = String(load_default="general")
    dataType = String(load_default="file")
    file = File(required=True)


class DatasetMarketQueryInSchema(Schema):
    domain = String(load_default=None, allow_none=True)
    sort = String(load_default=None, allow_none=True)


class DatasetDetailDatasetSchema(Schema):
    id = Integer(required=True)
    name = String(required=True)
    description = String(required=True)
    domain = String(required=True)
    dataType = String(required=True)
    fileSize = Integer(required=True)
    downloads = Integer(required=True)
    isListed = Boolean(required=True)
    ownerName = String(required=True)


class DatasetDetailOutSchema(Schema):
    dataset = Nested(DatasetDetailDatasetSchema, required=True)
    previewLines = List(String(), required=True)


class DatasetListingPatchInSchema(Schema):
    isListed = Boolean(required=True)


class DatasetListingPatchDatasetSchema(Schema):
    id = Integer(required=True)
    isListed = Boolean(required=True)


class DatasetListingPatchOutSchema(Schema):
    dataset = Nested(DatasetListingPatchDatasetSchema, required=True)
