import os
from flask import abort, send_file, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from urllib.parse import urlparse

from db import database
from models.dataset import Dataset
from models.download_log import DownloadLog
from utils.preview import read_dataset_preview_lines


def _authorize_and_count_download(dataset_id: int, user_id: int):
    """统一下载授权、下载日志与计数逻辑"""
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        abort(404, description="not found")

    if not dataset.is_listed and dataset.owner_id != user_id:
        abort(403, description="not allowed")

    log = DownloadLog(user_id=user_id, dataset_id=dataset.id)
    database.session.add(log)
    dataset.downloads += 1
    database.session.commit()
    return dataset


def create_dataset(owner_id: int, name: str, description: str, domain: str, data_type: str, object_key: str = None, file_size: int = 0):
    """处理数据集登记：以 `object_key` 登记对象键（前端通常仅传 object_key）。
    保留 `s3_url` 参数以向后兼容，但仅做校验，不作为 object_key 的回退来源。
    """
    if not name:
        abort(400, description="name required")

    # 要求前端提供 object_key
    if not object_key:
        abort(400, description="objectKey required")

    # 创建数据集记录（仅保存 object_key），不再保存预签名 s3_url 或 storage_type
    dataset = Dataset(
        name=name,
        description=description or "",
        domain=domain or "general",
        data_type=data_type or "file",
        object_key=object_key,
        file_size=file_size,
        is_listed=False,
        downloads=0,
        owner_id=owner_id
    )
    database.session.add(dataset)
    database.session.commit()
    return dataset

def list_my_datasets(owner_id: int):
    """列出当前用户上传的所有数据集（我的数据）"""
    datasets = Dataset.query.filter_by(owner_id=owner_id).order_by(Dataset.id.desc()).all()
    return datasets

def list_market_datasets(domain: str = None, sort: str = None):
    """列出所有上架的数据集列表（数据市场）"""
    query = Dataset.query.filter_by(is_listed=True)
    if domain:
        query = query.filter_by(domain=domain)
    # 根据排序参数选择排序方式
    if sort == "downloads":
        query = query.order_by(Dataset.downloads.desc())
    elif sort == "size":
        query = query.order_by(Dataset.file_size.desc())
    else:
        query = query.order_by(Dataset.id.desc())
    # 最多返回200条
    datasets = query.limit(200).all()
    return datasets

def get_dataset_detail(dataset_id: int):
    """获取数据集详情和预览（仅限上架的数据）"""
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        abort(404, description="not found")
    # 若数据集未上架，则禁止访问（即使是拥有者也不提供详情，和原逻辑保持一致）
    if not dataset.is_listed:
        abort(403, description="not listed")
    # 仅读取文本/CSV预览，失败返回空数组
    preview_lines = read_dataset_preview_lines(dataset, max_lines=10)
    return dataset, preview_lines

def toggle_listing(dataset_id: int, owner_id: int, is_listed: bool):
    """切换数据集的上架/下架状态"""
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        abort(404, description="not found")
    if dataset.owner_id != owner_id:
        abort(403, description="not owner")
    dataset.is_listed = bool(is_listed)
    database.session.commit()
    return dataset

def download_dataset_file(dataset_id: int, user_id: int):
    """处理下载：local返回文件流，s3重定向到已登记URL"""
    dataset = _authorize_and_count_download(dataset_id, user_id)

    storage_type = (dataset.storage_type or "local").lower()
    if storage_type == "s3":
        if not dataset.s3_url:
            abort(404, description="download url missing")
        # return redirect(dataset.s3_url, code=302)
        #返回url的json
            return {"downloadUrl": dataset.s3_url}

    if not dataset.file_path:
        abort(404, description="file missing")
    if not os.path.exists(dataset.file_path):
        abort(404, description="file not found")

    filename = os.path.basename(dataset.file_path)
    return send_file(dataset.file_path, as_attachment=True, download_name=filename)


def get_dataset_download_url(dataset_id: int, user_id: int):
    """返回下载URL，复用下载授权与计数逻辑"""
    dataset = _authorize_and_count_download(dataset_id, user_id)
    storage_type = (dataset.storage_type or "local").lower()

    if storage_type == "s3":
        if not dataset.s3_url:
            abort(404, description="download url missing")
        return {"downloadUrl": dataset.s3_url, "source": "s3"}

    return {
        "downloadUrl": url_for("datasets.download_file", dataset_id=dataset.id, _external=False),
        "source": "local",
    }
