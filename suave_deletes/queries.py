import logging
from sqlalchemy import and_, inspect
from sqlalchemy.orm import Query, class_mapper, aliased
from sqlalchemy.sql.elements import Null

from suave_deletes.mixins import is_soft_delete_supported

logger = logging.getLogger(__name__)

class SuaveDeleteQuery(Query):
    def join(self, *entities, **kwargs) -> "SuaveDeleteQuery":
        query = super().join(*entities, **kwargs)

        for instance in entities:
            try:
                if is_soft_delete_supported(instance):
                    mapper = class_mapper(instance)
                    query = query.filter(and_(mapper.c.deleted_at == None))  # noqa: E711
            except Exception as ex:
                logger.error(f"Instance not supported: {type(instance)}")
                continue

        return query

    def with_deleted_at(self) -> "SuaveDeleteQuery":
        try:
            if not self._where_criteria:
                return self

            self._where_criteria = tuple(
                c for c in self._where_criteria if not self._has_deleted_at_filter(c)
            )

            return self
        except Exception as ex:
            return self


    def _has_deleted_at_filter(self, clause) -> bool:
        try:
            return (
                    clause.left.name == "deleted_at"
                    and clause.operator.__name__ == "is_"
                    and isinstance(clause.right, Null)
            )
        except Exception as ex:
            return False

