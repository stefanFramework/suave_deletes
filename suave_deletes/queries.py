from sqlalchemy import and_
from sqlalchemy.orm import Query, class_mapper
from sqlalchemy.sql.elements import Null

from suave_deletes.mixins import is_soft_delete_supported


class SuaveDeleteQuery(Query):
    def join(self, *entities, **kwargs) -> "SuaveDeleteQuery":
        query = super().join(*entities, **kwargs)

        for instance in entities:
            if is_soft_delete_supported(instance):
                mapper = class_mapper(instance)
                query = query.filter(and_(mapper.c.deleted_at == None))  # noqa: E711

        return query

    def with_deleted_at(self) -> "SuaveDeleteQuery":
        if not self._where_criteria:
            return self

        self._where_criteria = tuple(
            c for c in self._where_criteria if not self._has_deleted_at_filter(c)
        )

        return self

    def _has_deleted_at_filter(self, clause) -> bool:
        return (
            clause.left.name == "deleted_at"
            and clause.operator.__name__ == "is_"
            and isinstance(clause.right, Null)
        )
