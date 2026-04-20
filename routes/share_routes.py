from apiflask import APIBlueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from controllers.share_controller import create_share, list_my_sharing, list_shared_with_me, update_share, list_my_requests
from models.user import User
from models.dataset import  Dataset
from schemas.share_schema import ShareCreateInSchema, ShareCreateOutSchema, ShareListOutSchema, SharePatchInSchema

share_bp = APIBlueprint("shares", __name__)

# 创建共享
@share_bp.post("/requests")
@jwt_required()
@share_bp.input(ShareCreateInSchema, arg_name="data")
@share_bp.output(ShareCreateOutSchema, 200)
def create(data):
    consumer_id = int( get_jwt_identity() )          # 获取当前JWT中保存的用户ID
    # 调用控制器执行注册逻辑
    status = create_share(consumer_id, data["datasetId"], data.get("message"))
    return status

# 批准是否共享
@share_bp.patch('/<int:share_id>')
@jwt_required()
@share_bp.input(SharePatchInSchema, arg_name="data")
@share_bp.output(ShareCreateOutSchema, 200)
def update(data, share_id):
    provider_id = int(get_jwt_identity())
    # 调用控制器执行注册逻辑
    status = update_share(share_id, provider_id, data["isApproved"])
    return status

# 列出我共享给别人的数据集(别人对我的共享请求)
@share_bp.get('/sharing-with-others')
@jwt_required()
@share_bp.output(ShareListOutSchema, 200)
def list_my_sharing_route():
    provider_id = int(get_jwt_identity())# 获取当前JWT中保存的用户ID
    # 调用控制器执行注册逻辑
    sharing_dataset = list_my_sharing(provider_id)
    sharing_list = []
    for sd in sharing_dataset:
        dataset = Dataset.query.get(sd.dataset_id) if sd.dataset_id else None
        sharing_list.append({
            "id": sd.id,
            "consumerName": User.query.get(sd.consumer_id).username if sd.consumer_id else "unknown",
            "datasetName": dataset.name if dataset else "unknown",
            "request_description": sd.request_description,
            "objectKey": dataset.object_key if dataset else "unknown",
            "storageType": dataset.storage_type if dataset else "",
            "status": sd.status,
        })
    return {"sharing": sharing_list}

# 列出共享给我的数据集
@share_bp.get('/shared-with-me')
@jwt_required()
@share_bp.output(ShareListOutSchema, 200)
def list_shared_with_me_route():
    consumer_id = int(get_jwt_identity())# 获取当前JWT中保存的用户ID
    # 调用控制器执行注册逻辑
    shared_dataset = list_shared_with_me(consumer_id)
    shared_list = []
    for sd in shared_dataset:
        dataset = Dataset.query.get(sd.dataset_id) if sd.dataset_id else None
        shared_list.append({
            "id": sd.id,
            "providerName": User.query.get(sd.provider_id).username if sd.provider_id else "unknown",
            "datasetName": dataset.name if dataset else "unknown",
            "datasetId": sd.dataset_id,
            "storageType": dataset.storage_type if dataset else "",
        })
    return {"shared": shared_list}

# 列出我请求共享的数据集
@share_bp.get('/requests-by-me')
@jwt_required()
@share_bp.output(ShareListOutSchema, 200)
def list_my_requests_route():
    consumer_id = int(get_jwt_identity())
    requested = list_my_requests(consumer_id)
    requests_list = []
    for sd in requested:
        dataset = Dataset.query.get(sd.dataset_id) if sd.dataset_id else None
        requests_list.append({
            "id": sd.id,
            "providerName": User.query.get(sd.provider_id).username if sd.provider_id else "unknown",
            "datasetName": dataset.name if dataset else "unknown",
            "request_description": sd.request_description,
            "status": sd.status,
            "datasetId": sd.dataset_id,
            "storageType": dataset.storage_type if dataset else "",
        })
    return {"requests": requests_list}
