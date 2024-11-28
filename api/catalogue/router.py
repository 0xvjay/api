import logging
from typing import List

from fastapi import APIRouter, status
from pydantic import UUID4

from api.catalogue.service.category import (
    create as create_category,
)
from api.catalogue.service.category import (
    delete as delete_category,
)
from api.catalogue.service.category import (
    get as get_categories,
)
from api.catalogue.service.category import (
    get_by_name as get_category_by_name,
)
from api.catalogue.service.category import (
    retrieve as retrieve_category,
)
from api.catalogue.service.category import (
    update as update_category,
)
from api.catalogue.service.product import (
    create as create_product,
)
from api.catalogue.service.product import (
    delete as delete_product,
)
from api.catalogue.service.product import (
    get as get_products,
)
from api.catalogue.service.product import (
    get_by_name as get_product_by_name,
)
from api.catalogue.service.product import (
    retrieve as retrieve_product,
)
from api.catalogue.service.product import (
    update as update_product,
)
from api.catalogue.service.sub_category import (
    create as create_sub_category,
)
from api.catalogue.service.sub_category import (
    delete as delete_sub_category,
)
from api.catalogue.service.sub_category import (
    get as get_sub_categories,
)
from api.catalogue.service.sub_category import (
    get_by_name as get_sub_category_by_name,
)
from api.catalogue.service.sub_category import (
    retrieve as retrieve_sub_category,
)
from api.catalogue.service.sub_category import (
    update as update_sub_category,
)
from api.database import DBSession
from api.exceptions import DetailedHTTPException

from .exceptions import (
    CategoryNameExists,
    CategoryNotFound,
    ProductNameExists,
    ProductNotFound,
    SubCategoryNameExists,
    SubCategoryNotFound,
)
from .schemas import (
    CategoryCreateSchema,
    CategoryOutSchema,
    CategoryUpdateSchema,
    ProductCreateSchema,
    ProductOutMinimalSchema,
    ProductOutSchema,
    ProductUpdateSchema,
    SubCategoryCreateSchema,
    SubCategoryOutMinimalSchema,
    SubCategoryOutSchema,
    SubCategoryUpdateSchema,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["catalogue"])


@router.get("/categories/", response_model=List[CategoryOutSchema])
async def read_categories(db_session: DBSession):
    try:
        result = await get_categories(db_session=db_session)
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch categories: {str(e)}")
        raise DetailedHTTPException()


@router.get("/categories/{category_id}", response_model=CategoryOutSchema)
async def read_category(db_session: DBSession, category_id: UUID4):
    try:
        result = await retrieve_category(db_session=db_session, id=category_id)
        if result is None:
            raise CategoryNotFound()
        return result
    except CategoryNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to fetch category {category_id}: {str(e)}")
        raise DetailedHTTPException()


@router.post(
    "/categories/",
    response_model=CategoryOutSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_category(db_session: DBSession, category: CategoryCreateSchema):
    try:
        db_obj = await get_category_by_name(db_session=db_session, name=category.name)
        if db_obj is not None:
            raise CategoryNameExists()
        result = await create_category(db_session=db_session, category=category)
        return result
    except CategoryNameExists:
        raise
    except Exception as e:
        logger.exception(f"Failed to create category: {str(e)}")
        raise DetailedHTTPException()


@router.put("/categories/{category_id}", response_model=CategoryOutSchema)
async def edit_category(
    db_session: DBSession, category: CategoryUpdateSchema, category_id: UUID4
):
    try:
        db_category = await retrieve_category(db_session=db_session, id=category_id)
        if db_category is None:
            raise CategoryNotFound()
        if db_category != category.name:
            existing_category = await get_category_by_name(
                db_session=db_session, name=category.name
            )
            if existing_category is not None and existing_category.id != category_id:
                raise CategoryNameExists()
        updated_category = await update_category(
            db_session=db_session, category=category, db_category=db_category
        )
        return updated_category
    except (CategoryNameExists, CategoryNotFound):
        raise
    except Exception as e:
        logger.exception(f"Failed to update category: {str(e)}")
        raise DetailedHTTPException()


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_category(db_session: DBSession, category_id: UUID4):
    try:
        db_category = await retrieve_category(db_session=db_session, id=category_id)
        if db_category is None:
            raise CategoryNotFound()
        await delete_category(db_session=db_session, db_category=db_category)
        return
    except CategoryNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete category {category_id}: {str(e)}")
        raise DetailedHTTPException()


@router.get("/products/", response_model=List[ProductOutMinimalSchema])
async def read_products(db_session: DBSession):
    try:
        result = await get_products(db_session=db_session)
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch products: {str(e)}")
        raise DetailedHTTPException()


@router.get("/products/{product_id}", response_model=ProductOutSchema)
async def read_product(db_session: DBSession, product_id: UUID4):
    try:
        result = await retrieve_product(db_session=db_session, id=product_id)
        if result is None:
            raise ProductNotFound()
        return result
    except ProductNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to fetch product {product_id}: {str(e)}")
        raise DetailedHTTPException()


@router.post(
    "/products/",
    response_model=ProductOutMinimalSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_product(db_session: DBSession, product: ProductCreateSchema):
    try:
        db_obj = await get_product_by_name(db_session=db_session, name=product.name)
        if db_obj is not None:
            raise ProductNameExists()
        result = await create_product(db_session=db_session, product=product)
        return result
    except ProductNameExists:
        raise
    except Exception as e:
        logger.exception(f"Failed to create product: {str(e)}")
        raise DetailedHTTPException()


@router.put("/products/{product_id}", response_model=ProductOutMinimalSchema)
async def edit_product(
    db_session: DBSession, product: ProductUpdateSchema, product_id: UUID4
):
    try:
        db_product = await retrieve_product(db_session=db_session, id=product_id)
        if db_product is None:
            raise ProductNotFound()
        if db_product != product.name:
            existing_product = await get_product_by_name(
                db_session=db_session, name=product.name
            )
            if existing_product is not None and existing_product.id != product_id:
                raise ProductNameExists()
        updated_product = await update_product(
            db_session=db_session, product=product, db_product=db_product
        )
        return updated_product
    except (ProductNotFound, ProductNameExists):
        raise
    except Exception as e:
        logger.exception(f"Failed to update product: {str(e)}")
        raise DetailedHTTPException()


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_product(db_session: DBSession, product_id: UUID4):
    try:
        db_product = await retrieve_product(db_session=db_session, id=product_id)
        if db_product is None:
            raise ProductNotFound()
        await delete_product(db_session=db_session, db_product=db_product)
        return
    except ProductNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete product {product_id}: {str(e)}")
        raise DetailedHTTPException()


@router.get("/sub_categories/", response_model=List[SubCategoryOutMinimalSchema])
async def read_sub_categories(db_session: DBSession):
    try:
        result = await get_sub_categories(db_session=db_session)
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch sub_categories: {str(e)}")
        raise DetailedHTTPException()


@router.get("/sub_categories/{sub_category_id}", response_model=SubCategoryOutSchema)
async def read_sub_category(db_session: DBSession, sub_category_id: UUID4):
    try:
        result = await retrieve_sub_category(db_session=db_session, id=sub_category_id)
        if result is None:
            raise SubCategoryNotFound()
        return result
    except SubCategoryNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to fetch sub_category {sub_category_id}: {str(e)}")
        raise DetailedHTTPException()


@router.post(
    "/sub_categories/",
    response_model=SubCategoryOutMinimalSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_sub_category(
    db_session: DBSession, sub_category: SubCategoryCreateSchema
):
    try:
        db_obj = await get_sub_category_by_name(
            db_session=db_session, name=sub_category.name
        )
        if db_obj is not None:
            raise SubCategoryNameExists()
        result = await create_sub_category(
            db_session=db_session, sub_category=sub_category
        )
        return result
    except SubCategoryNameExists:
        raise
    except Exception as e:
        logger.exception(f"Failed to create sub_category: {str(e)}")
        raise DetailedHTTPException()


@router.put(
    "/sub_categories/{sub_category_id}", response_model=SubCategoryOutMinimalSchema
)
async def edit_sub_category(
    db_session: DBSession, sub_category: SubCategoryUpdateSchema, sub_category_id: UUID4
):
    try:
        db_sub_category = await retrieve_sub_category(
            db_session=db_session, id=sub_category_id
        )
        if db_sub_category is None:
            raise SubCategoryNotFound()
        if db_sub_category != sub_category.name:
            existing_sub_category = await get_sub_category_by_name(
                db_session=db_session, name=sub_category.name
            )
            if (
                existing_sub_category is not None
                and existing_sub_category.id != sub_category_id
            ):
                raise SubCategoryNameExists()
        updated_sub_category = await update_sub_category(
            db_session=db_session,
            sub_category=sub_category,
            db_subcategory=db_sub_category,
        )
        return updated_sub_category
    except (SubCategoryNotFound, SubCategoryNameExists):
        raise
    except Exception as e:
        logger.exception(f"Failed to update sub_category: {str(e)}")
        raise DetailedHTTPException()


@router.delete(
    "/sub_categories/{sub_category_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_sub_category(db_session: DBSession, sub_category_id: UUID4):
    try:
        db_sub_category = await retrieve_sub_category(
            db_session=db_session, id=sub_category_id
        )
        if db_sub_category is None:
            raise SubCategoryNotFound()
        await delete_sub_category(db_session=db_session, db_subcategory=db_sub_category)
        return
    except SubCategoryNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete sub_category {sub_category_id}: {str(e)}")
        raise DetailedHTTPException()
