import logging
from typing import List

from fastapi import APIRouter, Depends, Request, status
from pydantic import UUID4

from api.auth.permissions import (
    CategoryPermissions,
    ProductPermissions,
    SubCategoryPermissions,
)
from api.catalogue.service import category_crud, product_crud, sub_category_crud
from api.core.cache import cache_response
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


@router.get(
    "/categories/",
    response_model=List[CategoryOutSchema],
    dependencies=[Depends(CategoryPermissions.read)],
)
@cache_response(expire=1800, prefix="categories")
async def read_categories(request: Request, db_session: DBSession):
    try:
        result = await category_crud.list(request=request, db_session=db_session)
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch categories: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/categories/{category_id}",
    response_model=CategoryOutSchema,
    dependencies=[Depends(CategoryPermissions.read)],
)
async def read_category(request: Request, db_session: DBSession, category_id: UUID4):
    try:
        result = await category_crud.get(
            request=request, db_session=db_session, id=category_id
        )
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
    dependencies=[Depends(CategoryPermissions.create)],
)
async def add_category(
    request: Request, db_session: DBSession, category: CategoryCreateSchema
):
    try:
        db_obj = await category_crud.get_by_name(
            db_session=db_session, name=category.name
        )
        if db_obj is not None:
            raise CategoryNameExists()
        result = await category_crud.create(
            request=request, db_session=db_session, category=category
        )
        return result
    except CategoryNameExists:
        raise
    except Exception as e:
        logger.exception(f"Failed to create category: {str(e)}")
        raise DetailedHTTPException()


@router.put(
    "/categories/{category_id}",
    response_model=CategoryOutSchema,
    dependencies=[Depends(CategoryPermissions.update)],
)
async def edit_category(
    request: Request,
    db_session: DBSession,
    category: CategoryUpdateSchema,
    category_id: UUID4,
):
    try:
        db_category = await category_crud.get(
            request=request, db_session=db_session, id=category_id
        )
        if db_category is None:
            raise CategoryNotFound()
        if db_category.name != category.name:
            existing_category = await category_crud.get_by_name(
                db_session=db_session, name=category.name
            )
            if existing_category is not None and existing_category.id != category_id:
                raise CategoryNameExists()
        updated_category = await category_crud.update(
            request=request,
            db_session=db_session,
            category=category,
            db_category=db_category,
        )
        return updated_category
    except (CategoryNameExists, CategoryNotFound):
        raise
    except Exception as e:
        logger.exception(f"Failed to update category: {str(e)}")
        raise DetailedHTTPException()


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(CategoryPermissions.delete)],
)
async def remove_category(request: Request, db_session: DBSession, category_id: UUID4):
    try:
        db_category = await category_crud.get(
            request=request, db_session=db_session, id=category_id
        )
        if db_category is None:
            raise CategoryNotFound()
        await category_crud.delete(
            request=request, db_session=db_session, db_obj=db_category
        )
        return
    except CategoryNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete category {category_id}: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/products/",
    response_model=List[ProductOutMinimalSchema],
    dependencies=[Depends(ProductPermissions.read)],
)
@cache_response(expire=1800, prefix="products")
async def read_products(request: Request, db_session: DBSession):
    try:
        result = await product_crud.list(request=request, db_session=db_session)
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch products: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/products/{product_id}",
    response_model=ProductOutSchema,
    dependencies=[Depends(ProductPermissions.read)],
)
async def read_product(request: Request, db_session: DBSession, product_id: UUID4):
    try:
        result = await product_crud.get(
            request=request, db_session=db_session, id=product_id
        )
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
    dependencies=[Depends(ProductPermissions.create)],
)
async def add_product(
    request: Request, db_session: DBSession, product: ProductCreateSchema
):
    try:
        db_obj = await product_crud.get_by_name(
            db_session=db_session, name=product.name
        )
        if db_obj is not None:
            raise ProductNameExists()
        result = await product_crud.create(
            request=request, db_session=db_session, product=product
        )
        return result
    except ProductNameExists:
        raise
    except Exception as e:
        logger.exception(f"Failed to create product: {str(e)}")
        raise DetailedHTTPException()


@router.put(
    "/products/{product_id}",
    response_model=ProductOutMinimalSchema,
    dependencies=[Depends(ProductPermissions.update)],
)
async def edit_product(
    request: Request,
    db_session: DBSession,
    product: ProductUpdateSchema,
    product_id: UUID4,
):
    try:
        db_product = await product_crud.get(
            request=request, db_session=db_session, id=product_id
        )
        if db_product is None:
            raise ProductNotFound()
        if db_product != product.name:
            existing_product = await product_crud.get_by_name(
                db_session=db_session, name=product.name
            )
            if existing_product is not None and existing_product.id != product_id:
                raise ProductNameExists()
        updated_product = await product_crud.update(
            request=request,
            db_session=db_session,
            product=product,
            db_product=db_product,
        )
        return updated_product
    except (ProductNotFound, ProductNameExists):
        raise
    except Exception as e:
        logger.exception(f"Failed to update product: {str(e)}")
        raise DetailedHTTPException()


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(ProductPermissions.delete)],
)
async def remove_product(request: Request, db_session: DBSession, product_id: UUID4):
    try:
        db_product = await product_crud.get(
            request=request, db_session=db_session, id=product_id
        )
        if db_product is None:
            raise ProductNotFound()
        await product_crud.delete(
            request=request, db_session=db_session, db_obj=db_product
        )
        return
    except ProductNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete product {product_id}: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/sub_categories/",
    response_model=List[SubCategoryOutMinimalSchema],
    dependencies=[Depends(SubCategoryPermissions.read)],
)
@cache_response(expire=1800, prefix="sub_categories")
async def read_sub_categories(request: Request, db_session: DBSession):
    try:
        result = await sub_category_crud.list(request=request, db_session=db_session)
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch sub_categories: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/sub_categories/{sub_category_id}",
    response_model=SubCategoryOutSchema,
    dependencies=[Depends(SubCategoryPermissions.read)],
)
async def read_sub_category(
    request: Request, db_session: DBSession, sub_category_id: UUID4
):
    try:
        result = await sub_category_crud.get(
            request=request, db_session=db_session, id=sub_category_id
        )
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
    dependencies=[Depends(SubCategoryPermissions.create)],
)
async def add_sub_category(
    request: Request, db_session: DBSession, sub_category: SubCategoryCreateSchema
):
    try:
        db_obj = await sub_category_crud.get_by_name(
            db_session=db_session, name=sub_category.name
        )
        if db_obj is not None:
            raise SubCategoryNameExists()
        result = await sub_category_crud.create(
            request=request, db_session=db_session, schema=sub_category
        )
        return result
    except SubCategoryNameExists:
        raise
    except Exception as e:
        logger.exception(f"Failed to create sub_category: {str(e)}")
        raise DetailedHTTPException()


@router.put(
    "/sub_categories/{sub_category_id}",
    response_model=SubCategoryOutMinimalSchema,
    dependencies=[Depends(SubCategoryPermissions.update)],
)
async def edit_sub_category(
    request: Request,
    db_session: DBSession,
    sub_category: SubCategoryUpdateSchema,
    sub_category_id: UUID4,
):
    try:
        db_sub_category = await sub_category_crud.get(
            request=request, db_session=db_session, id=sub_category_id
        )
        if db_sub_category is None:
            raise SubCategoryNotFound()
        if db_sub_category != sub_category.name:
            existing_sub_category = await sub_category_crud.get_by_name(
                db_session=db_session, name=sub_category.name
            )
            if (
                existing_sub_category is not None
                and existing_sub_category.id != sub_category_id
            ):
                raise SubCategoryNameExists()
        updated_sub_category = await sub_category_crud.update(
            request=request,
            db_session=db_session,
            schema=sub_category,
            db_obj=db_sub_category,
        )
        return updated_sub_category
    except (SubCategoryNotFound, SubCategoryNameExists):
        raise
    except Exception as e:
        logger.exception(f"Failed to update sub_category: {str(e)}")
        raise DetailedHTTPException()


@router.delete(
    "/sub_categories/{sub_category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(SubCategoryPermissions.delete)],
)
async def remove_sub_category(
    request: Request, db_session: DBSession, sub_category_id: UUID4
):
    try:
        db_sub_category = await sub_category_crud.get(
            request=request, db_session=db_session, id=sub_category_id
        )
        if db_sub_category is None:
            raise SubCategoryNotFound()
        await sub_category_crud.delete(
            request=request, db_session=db_session, db_obj=db_sub_category
        )
        return
    except SubCategoryNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete sub_category {sub_category_id}: {str(e)}")
        raise DetailedHTTPException()
