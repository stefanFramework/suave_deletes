class SuaveDeleteMixin:
    __use_soft_deletes__ = True


def is_soft_delete_supported(instance):
    return getattr(instance, "__use_soft_deletes__", False) and hasattr(instance, "deleted_at")
