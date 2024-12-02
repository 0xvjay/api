from typing import Any, Callable, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class Exporter:
    """A class to handle data export with dynamic filtering options"""

    def __init__(self, model: Any, query_builder: Callable | None = None, **filters):
        self.model = model
        self.filters = filters
        self.query = None
        self.query_builder = query_builder or self.default_query_builder

    def default_query_builder(self):
        """Default query building strategy"""
        query = select(self.model)

        for field, value in self.filters.items():
            if value is not None:
                if isinstance(value, list):
                    query = query.where(getattr(self.model, field).in_(value))
                elif isinstance(value, tuple) and len(value) == 2:
                    start, end = value
                    if start:
                        query = query.where(getattr(self.model, field) >= start)
                    if end:
                        query = query.where(getattr(self.model, field) <= end)
                else:
                    query = query.where(getattr(self.model, field) == value)

        return query

    def build_query(self):
        """Builds the query using the specified query builder"""
        self.query = self.query_builder()
        return self.query

    async def export(self, db_session: AsyncSession) -> List[Any]:
        """Execute the query and return results"""
        if not self.query:
            self.build_query()
        result = await db_session.execute(self.query)
        return result.unique().scalars().all()


# exporter = Exporter(
#     model=User,
#     user_ids=[1, 2, 3],                                       # List for IN query
#     query_builder=custom_query_builder,                       # function for query builder
#     created_at=(datetime(2024, 1, 1), datetime(2024, 2, 1)),  # Tuple for range
#     status='active'                                           # Simple equality
# )

# results = await exporter.export(db_session)
