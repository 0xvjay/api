from sqlalchemy import UUID, Column, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import relationship

from api.models import BaseTimeStamp


class ProductReview(BaseTimeStamp):
    __tablename__ = "review_product_review"

    rating = Column(SmallInteger)
    title = Column(String(255), nullable=False)
    body = Column(Text)

    product_id = Column(UUID, ForeignKey("catalogue_product.id", ondelete="CASCADE"))
    user_id = Column(UUID, ForeignKey("user_user.id", ondelete="CASCADE"))

    total_votes = Column(Integer, default=0)

    product = relationship("Product", back_populates="reviews")
    votes = relationship("Vote", back_populates="review")


class Vote(BaseTimeStamp):
    __tablename__ = "review_vote"

    vote = Column(SmallInteger)

    review_id = Column(UUID, ForeignKey("review_product_review.id", ondelete="CASCADE"))
    user_id = Column(UUID, ForeignKey("user_user.id", ondelete="CASCADE"))

    review = relationship("ProductReview", back_populates="votes")
