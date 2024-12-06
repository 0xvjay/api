from api.exceptions import BadRequest


class UnSupportedOperator(BadRequest):
    detail = "Unsupported operator"


class UnSupportedFileFormat(BadRequest):
    detail = "Unsupported file format"


class UnSupportedModelName(BadRequest):
    detail = "Unsupported model name"
