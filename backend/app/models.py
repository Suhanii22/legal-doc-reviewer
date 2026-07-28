from sqlalchemy import Column, Integer, String , DateTime , ForeignKey ,Text ,Float
from app.db.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import func
from pgvector.sqlalchemy import Vector
from enum import Enum
from sqlalchemy import Enum as SQLEnum

class UserRole(Enum):
    Uploader="uploader"
    Reviewer="reviewer"

class ContractStatus(Enum):
    Processing="processing"
    Completed="completed"
    Failed="failed"   

class Risk_type(Enum):
    Risky="risky"
    Safe="safe"
    Non_Standard="non_standard"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole) , nullable=False )
    created_at = Column(DateTime(timezone=True),server_default=func.now())


class Contract(Base):
    __tablename__= "contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id=Column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=False)
    filename=Column(String,nullable=False)
    idempotent_key=Column(String,nullable=False)
    status=Column(SQLEnum(ContractStatus))
    uploaded_at=Column(DateTime(timezone=True),server_default=func.now()) 




class Clause(Base):
    __tablename__= "clauses"

    id = Column(UUID(as_uuid=True), primary_key=True , default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True),ForeignKey("contracts.id",ondelete="CASCADE"),nullable=False)
    text=Column(Text, nullable=False)
    category=Column(String)
    position_in_doc=Column(Integer)
    embedding=Column(Vector(1536))    


class Ref_Clause(Base):
    __tablename__= "ref_clauses"

    id = Column(String,primary_key=True)
    text=Column(Text,nullable=False)
    category=Column(String, nullable=False)
    risk_label=Column(SQLEnum(Risk_type),nullable=False)
    reason=Column(Text,nullable=False)
    embedding=Column(Vector(1536))


class Flag(Base):
    __tablename__="flags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clause_id=Column(UUID(as_uuid=True), ForeignKey("clauses.id",ondelete="CASCADE"),nullable=False)
    risk_label = Column( String,nullable=False )
    confidence_score = Column(Float,nullable=False )
    ai_reasoning = Column(Text)
    status = Column(String,nullable=False,default="pending" )
    claimed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True )
    claimed_at = Column(DateTime)
    version = Column(Integer,default=1)
    created_at = Column(DateTime(timezone=True),server_default=func.now())


class Review(Base):
    __tablename__="reviews"

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    flag_id = Column( UUID(as_uuid=True), ForeignKey("flags.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=False )
    final_label = Column( String,nullable=False)
    review_notes = Column(Text)
    reviewed_at = Column( DateTime(timezone=True), server_default=func.now())






