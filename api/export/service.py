import logging
import os
from datetime import datetime
from typing import Any, Callable, List, Type

import pandas as pd
from fastapi import BackgroundTasks, Request
from sqlalchemy import Select, asc, desc, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from api.catalogue.models import Product
from api.config import settings
from api.core.crud import CRUDBase
from api.order.models import Order
from api.user.models import User

from .constant import Status
from .exceptions import UnSupportedFileFormat, UnSupportedModelName, UnSupportedOperator
from .models import Export
from .schemas import ExportCreateSchema, ExportFilter

logger = logging.getLogger(__name__)


class CRUDExport(CRUDBase[Export, ExportCreateSchema, Any]):
    """Enhanced export handler with background processing and flexible query building"""

    def _apply_filter(self, query: Select, filter_: ExportFilter, model: Any) -> Select:
        """Apply filter to query with proper typing"""
        field = getattr(model, filter_.field)

        if filter_.operator == "eq":
            return query.where(field == filter_.value)
        elif filter_.operator == "in_":
            return query.where(field.in_(filter_.value))
        elif filter_.operator == "between":
            start, end = filter_.value
            return query.where(field.between(start, end))
        elif filter_.operator == "gt":
            return query.where(field > filter_.value)
        elif filter_.operator == "lt":
            return query.where(field < filter_.value)
        elif filter_.operator == "contains":
            return query.where(field.contains(filter_.value))
        else:
            raise UnSupportedOperator()

    def _apply_sorting(self, query: Select, sort_by: List[str], model: Any) -> Select:
        for sort_expr in sort_by:
            if sort_expr.startswith("-"):
                field = getattr(model, sort_expr[1:])
                query = query.order_by(desc(field))
            else:
                field = getattr(model, sort_expr)
                query = query.order_by(asc(field))
        return query

    def build_query(
        self,
        model: Type[DeclarativeMeta],
        filters: List[ExportFilter],
        sort_by: List[str],
        query_builder: Callable | None = None,
    ) -> Select:
        """Builds the query using either custom or default builder"""
        if query_builder:
            return query_builder()

        query = select(model)
        for filter_ in filters:
            query = self._apply_filter(query, filter_, model)
        query = self._apply_sorting(query, sort_by, model)
        return query

    async def process_export(
        self,
        db_session: AsyncSession,
        export_obj: Export,
        schema: ExportCreateSchema,
        query_builder: Callable | None = None,
    ):
        """Background task to process the export"""
        try:
            export_obj = await db_session.get(Export, export_obj.id)

            model = self._get_model_class(schema.model_name)
            query = self.build_query(
                model=model,
                filters=schema.filters,
                sort_by=schema.sort_by,
                query_builder=query_builder,
            )

            export_obj.status = Status.IN_PROGRESS
            await db_session.commit()

            try:
                if schema.file_format == "xlsx":
                    filename = await self._to_excel(db_session, export_obj, query)
                else:
                    raise UnSupportedFileFormat()

                export_obj.file = filename
                export_obj.status = Status.COMPLETED
                export_obj.finished_at = datetime.now()

            except Exception as e:
                export_obj.status = Status.FAILED
                export_obj.finished_at = datetime.now()
                raise e

            await db_session.commit()

        except Exception as e:
            await db_session.rollback()
            logger.exception(f"Export processing failed: {str(e)}")

    async def _to_excel(
        self, db_session: AsyncSession, export_obj: Export, query: Select
    ) -> str:
        """Generate Excel file from query results with improved formatting"""
        result = await db_session.execute(query)
        data = result.unique().scalars().all()

        rows = []
        for item in data:
            row = {}
            for column in inspect(self.model).columns:
                row[column.name] = getattr(item, column.name)
            rows.append(row)

        df = pd.DataFrame(rows)

        exports_dir = os.path.join(settings.STATIC_DIR, "exports")
        os.makedirs(exports_dir, exist_ok=True)

        filename = f"{export_obj.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        full_path = os.path.join(exports_dir, filename)

        with pd.ExcelWriter(full_path, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Data")

            workbook = writer.book
            worksheet = writer.sheets["Data"]

            header_format = workbook.add_format(
                {"bold": True, "bg_color": "#D3D3D3", "border": 1}
            )

            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                column_len = max(df[value].astype(str).apply(len).max(), len(value)) + 2
                worksheet.set_column(col_num, col_num, column_len)

        return os.path.join("exports", filename)

    async def create(
        self,
        request: Request,
        db_session: AsyncSession,
        schema: ExportCreateSchema,
        background_tasks: BackgroundTasks,
        query_builder: Callable | None = None,
    ) -> Export:
        """Create export record and schedule background processing"""
        await self._create_add_log(request=request, db_session=db_session)

        db_export = Export(
            status=Status.CREATED,
            user_id=schema.created_by,
            started_at=datetime.now(),
        )
        db_session.add(db_export)
        await db_session.commit()
        await db_session.refresh(db_export)

        background_tasks.add_task(
            self.process_export, db_session, db_export, schema, query_builder
        )

        return db_export

    def _get_model_class(self, model_name: str) -> Type[DeclarativeMeta]:
        # This method should be implemented to return the appropriate model class
        # based on the model name
        models = {
            "User": User,
            "Order": Order,
            "Product": Product,
        }

        if model_name not in models:
            raise UnSupportedModelName()

        return models[model_name]


export_crud = CRUDExport(Export, "Export")
