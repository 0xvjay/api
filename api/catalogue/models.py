from slugify import slugify
from sqlalchemy import UUID, Boolean, Column, Float, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import relationship

from api.models import BaseTimeStamp, BaseUUID


class SubCategoryProduct(BaseUUID):
    __tablename__ = "catalogue_subcategory_product"

    sub_category_id = Column(
        UUID, ForeignKey("catalogue_subcategory.id", ondelete="CASCADE")
    )
    product_id = Column(UUID, ForeignKey("catalogue_product.id", ondelete="CASCADE"))


class Category(BaseUUID):
    __tablename__ = "catalogue_category"

    name = Column(String(255), index=True)
    is_active = Column(Boolean, default=True)

    sub_categories = relationship("SubCategory", backref="category")


class SubCategory(BaseUUID):
    __tablename__ = "catalogue_subcategory"

    name = Column(String(255), index=True)
    is_active = Column(Boolean, default=True, index=True)
    slug = Column(String(255))

    category_id = Column(UUID, ForeignKey("catalogue_category.id", ondelete="CASCADE"))
    products = relationship(
        "Product",
        secondary="catalogue_subcategory_product",
        back_populates="sub_categories",
    )

    def __init__(self, *args, **kwargs):
        if "slug" not in kwargs:
            kwargs["slug"] = slugify(kwargs.get("name", ""))
        super().__init__(*args, **kwargs)


class Product(BaseTimeStamp):
    __tablename__ = "catalogue_product"

    name = Column(String(255), index=True)
    slug = Column(String(255))
    description = Column(Text)
    short_description = Column(Text)
    rating = Column(Float, default=0)
    price = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)
    is_discountable = Column(Boolean, default=True)

    sub_categories = relationship(
        "SubCategory",
        secondary="catalogue_subcategory_product",
        back_populates="products",
    )
    reviews = relationship("ProductReview", back_populates="product")

    def __init__(self, *args, **kwargs):
        if "slug" not in kwargs:
            kwargs["slug"] = slugify(kwargs.get("name", ""))
        super().__init__(*args, **kwargs)
