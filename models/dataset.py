from sqlalchemy import BigInteger, String, Text, Boolean, Integer, Column, ForeignKey
from config import database

class Dataset(database.Model):
    __tablename__ = 'datasets'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=False, default="")
    domain = Column(String(80), nullable=False, default="general")    # 专业领域
    data_type = Column(String(40), nullable=False, default="file")    # 数据类型（csv/sql/json等）
    object_key = Column(String(255), nullable=False)                 # S3对象键
    file_size = Column(BigInteger, nullable=False, default=0)
    is_listed = Column(Boolean, nullable=False, default=False)        # 是否上架公开
    downloads = Column(Integer, nullable=False, default=0)            # 下载次数  
    owner_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)

#todo: 实现s3url和file二选一的校验逻辑，确保用户只能提供其中一个字段

