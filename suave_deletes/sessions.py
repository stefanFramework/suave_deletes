from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, class_mapper, sessionmaker

from suave_deletes.mixins import is_soft_delete_supported
from suave_deletes.queries import SuaveDeleteQuery


class SuaveDeleteSession(Session):
    def query(self, *entities, **kwargs):
        query = super().query(*entities, **kwargs)

        for instance in entities:
            if is_soft_delete_supported(instance):
                mapper = class_mapper(instance)
                query = query.filter(and_(mapper.c.deleted_at == None))  # noqa: E711

        return query

    def delete(self, instance):
        if is_soft_delete_supported(instance):
            instance.deleted_at = datetime.utcnow()
        else:
            super().delete(instance)

        self._cascade_delete(instance)

    def _cascade_delete(self, instance):
        mapper = class_mapper(instance.__class__)
        relationships = mapper.relationships

        for relationship in relationships:
            cascade = relationship.cascade

            if "delete" not in cascade:
                continue

            related_instances = getattr(instance, relationship.key)

            if related_instances is None:
                continue

            if isinstance(related_instances, list):
                for related_instance in related_instances:
                    self.delete(related_instance)
            else:
                self.delete(related_instances)


def create_suave_delete_session(engine: Engine) -> sessionmaker[SuaveDeleteSession]:
    return sessionmaker(bind=engine, class_=SuaveDeleteSession, query_cls=SuaveDeleteQuery)
