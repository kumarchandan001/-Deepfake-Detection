import contextvars
from typing import Optional

# Thread/async-safe request scope variables
_tenant_id_context = contextvars.ContextVar("tenant_id", default=None)
_plan_key_context = contextvars.ContextVar("plan_key", default="free")

def set_tenant_id(tenant_id: Optional[str]) -> contextvars.Token:
    """
    Sets the verified active tenant ID in the request scope.
    """
    return _tenant_id_context.set(tenant_id)

def get_tenant_id() -> Optional[str]:
    """
    Retrieves the verified active tenant ID in the current request context.
    """
    return _tenant_id_context.get()

def set_plan_key(plan_key: str) -> contextvars.Token:
    """
    Sets the active subscription plan tier key.
    """
    return _plan_key_context.set(plan_key)

def get_plan_key() -> str:
    """
    Retrieves the subscription plan key active in the current request context.
    """
    return _plan_key_context.get()

def clear_saas_context():
    """
    Resets the context values.
    """
    _tenant_id_context.set(None)
    _plan_key_context.set("free")
