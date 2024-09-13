from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.sql.selectable import Select, Alias
from sqlalchemy.orm.util import _ORMJoin


class SuaveDeleteMixin:
    __use_soft_deletes__ = True


def is_soft_delete_supported(instance):
    return getattr(instance, "__use_soft_deletes__", False) and hasattr(instance, "deleted_at")


@event.listens_for(Engine, "before_execute", retval=True)
def before_execute_listener(conn, clause, multi_params, params):
    if (not isinstance(clause, Select) or
            not hasattr(clause, "froms") or
            not isinstance(clause.froms, list)):
        return clause, multi_params, params

    for from_clause in clause.froms:

        if isinstance(from_clause, Alias):
            continue

        if isinstance(from_clause, _ORMJoin):
            continue

        table_name = from_clause.name
        filter_condition = text(f"{table_name}.deleted_at IS NULL")
        clause = clause.where(filter_condition)

    return clause, multi_params, params


