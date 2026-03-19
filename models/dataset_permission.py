from sqlalchemy import BigInteger, Column, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy import func
from db import database


class DatasetPermission(database.Model):
    __tablename__ = 'dataset_permissions'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    dataset_id = Column(BigInteger, ForeignKey('datasets.id'), nullable=False)
    grantee_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    granted_by = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source_share_id = Column(BigInteger, ForeignKey('share_datasets.id'), nullable=True)

    __table_args__ = (
        UniqueConstraint('dataset_id', 'grantee_id', name='uq_dataset_grantee'),
        Index('ix_dataset_grantee', 'dataset_id', 'grantee_id'),
    )
