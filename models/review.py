from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database.database import Base
from sqlalchemy.orm import relationship


class Review(Base):
    __tablename__ = "reviews"

    id = Column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    booking_id = Column(
        UUID(as_uuid=False), ForeignKey("bookings.id"), nullable=False, unique=True
    )  # One review per booking
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Add constraint to ensure rating is between 1 and 5
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    # Relationships
    booking = relationship("Booking", back_populates="reviews")

    # Convenience relationship to get user through booking
    @property
    def user(self):
        return self.booking.user if self.booking else None
