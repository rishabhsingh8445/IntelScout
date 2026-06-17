from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import enum

class SourceType(str, enum.Enum):
    careers = "careers"
    press_releases = "press_releases"
    social_media = "social_media"
    news = "news"

class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    timeframe = Column(String, nullable=False, default="Since Launch")
    report_markdown = Column(Text, nullable=True)
    raw_context = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    is_watched = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    items = relationship("ScrapedItem", back_populates="competitor", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="competitor", cascade="all, delete-orphan")
    snapshots = relationship("CompetitorSnapshot", back_populates="competitor", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="competitor", cascade="all, delete-orphan")

class ScrapedItem(Base):
    __tablename__ = "scraped_items"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False)
    source_type = Column(Enum(SourceType), nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default={})
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    competitor = relationship("Competitor", back_populates="items")

class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    confidence_score = Column(Integer, default=0)
    category = Column(String, nullable=True) # e.g., "Hiring", "Product Launch"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    competitor = relationship("Competitor", back_populates="insights")

class CompetitorSnapshot(Base):
    __tablename__ = "competitor_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False)
    snapshot_date = Column(DateTime(timezone=True), server_default=func.now())
    pricing_data = Column(Text, nullable=True)
    feature_list = Column(Text, nullable=True)
    messaging = Column(Text, nullable=True)
    raw_context = Column(Text, nullable=True)

    competitor = relationship("Competitor", back_populates="snapshots")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False)
    detected_changes = Column(Text, nullable=False)
    possible_goal = Column(Text, nullable=True)
    threat_level = Column(String, nullable=False) # e.g., "Low", "Medium", "High"
    recommended_action = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    competitor = relationship("Competitor", back_populates="alerts")
