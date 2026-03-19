from sqlalchemy import BigInteger, String, Text, Boolean, Integer, Column, ForeignKey, DateTime, Index, func
from db import database

# 共享模型
class Share(database.Model):
    __tablename__ = 'share_datasets'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    provider_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    consumer_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    dataset_id = Column(BigInteger, ForeignKey('datasets.id'), nullable=False)
    request_description = Column(Text, nullable=False, default="无")
    # is_shared = Column(Boolean, nullable=False, default=False)        # 是否上架公开
    # 状态：pending / approved / rejected
    status = Column(String(20), nullable=False, default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    responded_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_share_consumer_status', 'consumer_id', 'status'),
        Index('ix_share_provider_status', 'provider_id', 'status'),
    )