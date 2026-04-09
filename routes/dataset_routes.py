from apiflask import APIBlueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from controllers.dataset_controller import (
    create_dataset, list_my_datasets, list_market_datasets,
    get_dataset_detail, toggle_listing, download_dataset_file, get_dataset_download_url
)
from models.user import User
from schemas.dataset_schema import (
    DatasetDetailOutSchema,
    DatasetListingPatchInSchema,
    DatasetListingPatchOutSchema,
    DatasetMarketOutSchema,
    DatasetMarketQueryInSchema,
    DatasetMineOutSchema,
    DatasetDownloadUrlOutSchema,
    DatasetOutSchema,
    DatasetUploadInSchema,
)

dataset_bp = APIBlueprint("datasets", __name__)

# 上传登记数据集 
@dataset_bp.post("")
@dataset_bp.post("/")
@jwt_required()  # JWT保护，必须登录
@dataset_bp.input(DatasetUploadInSchema, location="form_and_files",arg_name="data")  # 从表单和文件中解析输入数据
@dataset_bp.output(DatasetOutSchema, 200)
def upload_dataset(data):
    current_user_id = int( get_jwt_identity() )          # 获取当前JWT中保存的用户ID
    # 调用控制器处理上传逻辑
    dataset = create_dataset(
        current_user_id,
        data["name"],
        data.get("description"),
        data.get("domain"),
        data.get("dataType"),
        data.get("objectKey"),
        data.get("fileSize")
        
    )
    return {"dataset": dataset}

# 获取我的数据集列表
@dataset_bp.get("/mine")
@jwt_required()
@dataset_bp.output(DatasetMineOutSchema, 200)
def my_datasets():
    current_user_id = int(get_jwt_identity())
    datasets = list_my_datasets(current_user_id)
    return {"owned": datasets}

# 数据市场列表 (对应 Express GET /api/datasets/market)
@dataset_bp.get("/market")
@dataset_bp.input(DatasetMarketQueryInSchema, location="query", arg_name="query")
@dataset_bp.output(DatasetMarketOutSchema, 200)
def market_list(query):
    datasets = list_market_datasets(query.get("domain"), query.get("sort"))
    return {"list": datasets}

# 数据集详情 + 预览 (对应 Express GET /api/datasets/:id)
@dataset_bp.get("/<int:dataset_id>")
@dataset_bp.output(DatasetDetailOutSchema, 200)
def dataset_detail(dataset_id):
    dataset, preview_lines = get_dataset_detail(dataset_id)
    owner = User.query.get(dataset.owner_id)
    return {
        "dataset": {
            "id": dataset.id,
            "name": dataset.name,
            "description": dataset.description,
            "domain": dataset.domain,
            "dataType": dataset.data_type,
            "fileSize": dataset.file_size,
            "downloads": dataset.downloads,
            "isListed": dataset.is_listed,
            "ownerName": owner.username if owner else "unknown",
        },
        "previewLines": preview_lines
    }

# 切换上架状态 (对应 Express PATCH /api/datasets/:id/listing)
@dataset_bp.patch("/<int:dataset_id>/listing")
@jwt_required()
@dataset_bp.input(DatasetListingPatchInSchema, arg_name="data")
@dataset_bp.output(DatasetListingPatchOutSchema, 200)
def set_listing(data, dataset_id):
    current_user_id = int(get_jwt_identity())
    updated = toggle_listing(dataset_id, current_user_id, data["isListed"])
    return {"dataset": {
        "id": updated.id,
        "isListed": updated.is_listed
    }}

# 数据下载 (对应 Express GET /api/datasets/:id/download)
@dataset_bp.get("/<int:dataset_id>/download")
@jwt_required()
def download_file(dataset_id):
    current_user_id = int(get_jwt_identity())
    # 控制器直接返回 send_file 响应
    return download_dataset_file(dataset_id, current_user_id)


@dataset_bp.get("/<int:dataset_id>/download-url")
@jwt_required()
@dataset_bp.output(DatasetDownloadUrlOutSchema, 200)
def download_url(dataset_id):
    current_user_id = int(get_jwt_identity())
    return get_dataset_download_url(dataset_id, current_user_id)
