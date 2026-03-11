from flask import abort
from sqlalchemy import BigInteger

from db import database
from models.share import Share
from models.dataset import Dataset

def create_share(consumer_id: BigInteger, dataset_id: BigInteger, description: str):
    """注册新共享"""
    # 检查必填参数
    if not dataset_id:
        abort(400, description="datasetId required")

    dataset = Dataset.query.filter_by(id=dataset_id).first()
    if not dataset:
        abort(404, description="dataset not found")
    if dataset.owner_id == consumer_id:
        abort(400, description="cannot request your own dataset")

    # 用户名是否已存在
    existing = Share.query.filter_by(consumer_id=consumer_id, dataset_id=dataset_id).first()
    if existing:
        abort(409, description="share already exists")
    else:
        # 创建新的共享记录
        new_share = Share(
            provider_id=dataset.owner_id,
            consumer_id=consumer_id,
            dataset_id=dataset_id,
            request_description=description or "",
        )
        database.session.add(new_share)
    database.session.commit()
    return {"status": "success"}

def update_share(share_id: int, provider_id: int, is_shared: bool):
    """更新共享状态"""
    share = Share.query.get(share_id)
    if not share:
        abort(404, description="share not found")
    if share.provider_id != provider_id:
        abort(403, description="not allowed")
    share.is_shared = is_shared
    database.session.commit()
    return {"status": "success"}

def list_my_sharing(provider_id: int):
    """列出当前用户的所有共享（我的共享）"""
    shares = Share.query.filter_by(provider_id=provider_id).order_by(Share.id.desc()).all()
    return shares

def list_shared_with_me(consumer_id: int):
    """列出当前用户的所有共享（我被共享的数据集），过滤条件是is_shared=True，即只显示被批准的共享"""
    shares = Share.query.filter_by(consumer_id=consumer_id, is_shared=True).order_by(Share.id.desc()).all()
    return shares