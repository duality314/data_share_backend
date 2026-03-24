from sqlalchemy import BigInteger, String, Text, Boolean, Integer, Column, ForeignKey
from db import database

class Dataset(database.Model):
    __tablename__ = 'datasets'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=False, default="")
    domain = Column(String(80), nullable=False, default="general")    # 专业领域
    data_type = Column(String(40), nullable=False, default="file")    # 数据类型（csv/sql/json等）
    storage_type = Column(String(20), nullable=False, default="local")  # 存储类型：local/s3
    file_path = Column(String(255), nullable=True)                    # 本地文件存储路径（兼容旧数据）
    s3_url = Column(Text, nullable=True)                              # S3对象预签名下载URL
    file_size = Column(BigInteger, nullable=False, default=0)
    is_listed = Column(Boolean, nullable=False, default=False)        # 是否上架公开
    downloads = Column(Integer, nullable=False, default=0)            # 下载次数  
    owner_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)

#todo: 实现s3url和file二选一的校验逻辑，确保用户只能提供其中一个字段

