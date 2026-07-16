from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, Text, Enum, Index
from sqlalchemy.sql import func
from database import Base
import enum

class MessageStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"
    replied = "replied"

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100))  # saree, suit, dupatta, etc.
    color = Column(String(100))
    price = Column(Float)
    description = Column(Text)
    cloudinary_url = Column(String(500))
    cloudinary_public_id = Column(String(200))
    media_type = Column(String(10), default="image")  # image or video
    tags = Column(Text)  # comma-separated
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    phone = Column(String(20), nullable=False)
    direction = Column(String(10))  # inbound / outbound
    content = Column(Text)
    status = Column(String(20), default=MessageStatus.sent)
    msg_type = Column(String(30), default="text")  # text, image, broadcast, thankyou
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Speeds up "newest N messages for this phone" (chat history lookup)
    # regardless of how large the table grows.
    __table_args__ = (
        Index("ix_messages_phone_created", "phone", "created_at"),
    )

class BroadcastJob(Base):
    __tablename__ = "broadcast_jobs"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    message_text = Column(Text)
    media_url = Column(String(500))
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, running, done, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

class VideoJob(Base):
    __tablename__ = "video_jobs"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    prompt = Column(Text)
    status = Column(String(20), default="pending")  # pending, processing, done, failed
    kieai_job_id = Column(String(200))
    output_url = Column(String(500))
    cloudinary_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SocialPost(Base):
    __tablename__ = "social_posts"
    id = Column(Integer, primary_key=True)
    platform = Column(String(30))  # instagram, youtube, facebook, google_my_business
    caption = Column(Text)
    media_url = Column(String(500))
    postiz_post_id = Column(String(200))
    scheduled_at = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))
    status = Column(String(20), default="scheduled")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DailyStat(Base):
    __tablename__ = "daily_stats"
    id = Column(Integer, primary_key=True)
    stat_date = Column(String(10), unique=True)  # YYYY-MM-DD
    msgs_sent = Column(Integer, default=0)
    msgs_received = Column(Integer, default=0)
    posts_published = Column(Integer, default=0)
    videos_created = Column(Integer, default=0)
    thankyou_sent = Column(Integer, default=0)
