from flask import abort
from sqlalchemy import BigInteger
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from db import database
from models.share import Share
from models.dataset import Dataset
from models.dataset_permission import DatasetPermission

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

    # 防重：仅检查是否存在 pending 的请求
    existing_pending = Share.query.filter_by(consumer_id=consumer_id, dataset_id=dataset_id, status='pending').first()
    if existing_pending:
        abort(409, description="pending share already exists")

    # 创建新的共享记录（status 默认为 'pending'）
    new_share = Share(
        provider_id=dataset.owner_id,
        consumer_id=consumer_id,
        dataset_id=dataset_id,
        request_description=description or "",
    )
    database.session.add(new_share)
    try:
        database.session.commit()
    except IntegrityError:
        database.session.rollback()
        # 在高并发下可能被其他事务插入，统一返回冲突
        abort(409, description="could not create share (conflict)")
    return {"status": "success", "share_id": new_share.id}

def update_share(share_id: int, provider_id: int, isApproved: bool):
    """批准或拒绝共享请求：批准时写入 DatasetPermission，拒绝时仅更新状态并保留记录用于审计"""
    share = Share.query.get(share_id)
    if not share:
        abort(404, description="share not found")
    if share.provider_id != provider_id:
        abort(403, description="not allowed")

    if share.status != 'pending':
        abort(400, description="share request already processed")

    if isApproved:
        # 批准：更新状态并创建运行时权限
        share.status = 'approved'
        share.responded_at = func.now()
        # 在同一事务内插入 DatasetPermission，若已存在则忽略
        existing_perm = DatasetPermission.query.filter_by(dataset_id=share.dataset_id, grantee_id=share.consumer_id).first()
        if not existing_perm:
            new_perm = DatasetPermission(
                dataset_id=share.dataset_id,
                grantee_id=share.consumer_id,
                granted_by=provider_id,
                source_share_id=share.id,
            )
            database.session.add(new_perm)
    else:
        # 拒绝：更新状态并保留审计记录
        share.status = 'rejected'
        share.responded_at = func.now()

    try:
        database.session.commit()
    except IntegrityError:
        database.session.rollback()
        abort(500, description="failed to update share")

    return {"status": "success"}

def list_my_sharing(provider_id: int):
    """列出当前用户的所有共享（我的共享）"""
    shares = Share.query.filter_by(provider_id=provider_id).order_by(Share.id.desc()).all()
    return shares

def list_shared_with_me(consumer_id: int):
    """列出当前用户的所有已批准共享（status='approved'）"""
    shares = Share.query.filter_by(consumer_id=consumer_id, status='approved').order_by(Share.id.desc()).all()
    return shares

def list_my_requests(consumer_id: int):
    """列出当前用户发起的共享请求（status='pending'）"""
    shares = Share.query.filter_by(consumer_id=consumer_id, status='pending').order_by(Share.id.desc()).all()
    return shares