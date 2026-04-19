from sqlalchemy import BigInteger, Column, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy import func
from config import database

# 数据集权限模型：记录哪些用户对哪些数据集具有访问权限，来源于哪个共享请求
# 有记录说明用户具有访问权限，无记录说明没有访问权限（不区分未授权和拒绝，简化逻辑）
class DatasetPermission(database.Model):
    __tablename__ = 'dataset_permissions'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    dataset_id = Column(BigInteger, ForeignKey('datasets.id'), nullable=False)
    grantee_id = Column(BigInteger, ForeignKey('users.id'), nullable=False) # 被授权人
    granted_by = Column(BigInteger, ForeignKey('users.id'), nullable=False) # 授权人
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False) # 授权时间
    source_share_id = Column(BigInteger, ForeignKey('share_datasets.id'), nullable=True) # 来源共享ID

    __table_args__ = (
        UniqueConstraint('dataset_id', 'grantee_id', name='uq_dataset_grantee'),
        Index('ix_dataset_grantee', 'dataset_id', 'grantee_id'),
    )
