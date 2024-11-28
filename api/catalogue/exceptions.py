from api.exceptions import NotFound, BadRequest


class ProductNotFound(NotFound):
    detail = "Product not found"


class ProductNameExists(BadRequest):
    detail = "Product name already exists"


class CategoryNotFound(NotFound):
    detail = "Category not found"


class CategoryNameExists(BadRequest):
    detail = "Category name already exists"


class SubCategoryNotFound(NotFound):
    detail = "SubCategory not found"


class SubCategoryNameExists(BadRequest):
    detail = "SubCategory name already exists"
