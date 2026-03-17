from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class DrawRecord(Base):
    """
    Universal table for all historical game draws.
    """
    __tablename__ = "historical_draws"

    id = Column(Integer, primary_key=True, index=True)
    game_name = Column(String, index=True, nullable=False) # e.g., 'Powerball', 'MegaMillions'
    draw_date = Column(Date, nullable=False)
    
    white_balls = Column(String, nullable=False) # e.g., '14,21,33,42,59'
    special_ball = Column(Integer, nullable=True) # e.g., 24
    multiplier = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint('game_name', 'draw_date', name='uq_game_date'),
    )

class User(Base):
    """
    MVP User table.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    tier = Column(String, default="free", nullable=False) # 'free' or 'pro'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket_batches = relationship("SavedTicketBatch", back_populates="owner", cascade="all, delete-orphan")

class SavedTicketBatch(Base):
    """
    JMc - Groups a set of generated tickets together by the transaction.
    """
    __tablename__ = "saved_ticket_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_name = Column(String, nullable=False)
    
    # Store the pool used so we know the context of the generation
    pool_white_balls = Column(String, nullable=False)
    pool_special_balls = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", back_populates="ticket_batches")
    tickets = relationship("SavedTicket", back_populates="batch", cascade="all, delete-orphan")

class SavedTicket(Base):
    """
    JMc - Individual tickets linked to a generation batch.
    """
    __tablename__ = "saved_tickets"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("saved_ticket_batches.id"), nullable=False)
    
    # The actual ticket generated
    ticket_white_balls = Column(String, nullable=False)
    ticket_special_ball = Column(Integer, nullable=True)

    batch = relationship("SavedTicketBatch", back_populates="tickets")

