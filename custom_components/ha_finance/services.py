"""Service handlers for Ha Finance Record integration."""
from __future__ import annotations

import logging
import uuid

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    FREQUENCY_OPTIONS,
    SERVICE_ADD_TRANSACTION,
    SERVICE_ADJUST_BALANCE,
    SERVICE_ADD_PLAN,
    SERVICE_UPDATE_PLAN,
    SERVICE_DELETE_PLAN,
    SERVICE_SET_PLAN_ACTIVE,
)
from .coordinator import get_coordinator_for_account

_LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Service schemas
# ---------------------------------------------------------------------------

SERVICE_ADD_TRANSACTION_SCHEMA = vol.Schema(
    {
        vol.Required("account_id"): cv.string,
        vol.Required("amount"): vol.Coerce(float),
        vol.Optional("note", default=""): cv.string,
    }
)

SERVICE_ADJUST_BALANCE_SCHEMA = vol.Schema(
    {
        vol.Required("account_id"): cv.string,
        vol.Required("new_balance"): vol.Coerce(float),
    }
)

SERVICE_ADD_PLAN_SCHEMA = vol.Schema(
    {
        vol.Required("account_id"): cv.string,
        vol.Required("title"): cv.string,
        vol.Required("amount"): vol.Coerce(float),
        vol.Required("frequency"): vol.In(FREQUENCY_OPTIONS),
        vol.Required("day"): vol.All(vol.Coerce(int), vol.Range(min=1, max=28)),
        vol.Optional("month", default=1): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=12)
        ),
        vol.Optional("active", default=True): cv.boolean,
    }
)

SERVICE_UPDATE_PLAN_SCHEMA = vol.Schema(
    {
        vol.Required("account_id"): cv.string,
        vol.Required("plan_id"): cv.string,
        vol.Optional("title"): cv.string,
        vol.Optional("amount"): vol.Coerce(float),
        vol.Optional("frequency"): vol.In(FREQUENCY_OPTIONS),
        vol.Optional("day"): vol.All(vol.Coerce(int), vol.Range(min=1, max=28)),
        vol.Optional("month"): vol.All(vol.Coerce(int), vol.Range(min=1, max=12)),
        vol.Optional("active"): cv.boolean,
    }
)

SERVICE_DELETE_PLAN_SCHEMA = vol.Schema(
    {
        vol.Required("account_id"): cv.string,
        vol.Required("plan_id"): cv.string,
    }
)

SERVICE_SET_PLAN_ACTIVE_SCHEMA = vol.Schema(
    {
        vol.Required("account_id"): cv.string,
        vol.Required("plan_id"): cv.string,
        vol.Required("active"): cv.boolean,
    }
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _get_coordinator(hass: HomeAssistant, account_id: str):
    """Look up coordinator or raise ServiceValidationError."""
    coordinator = get_coordinator_for_account(hass, account_id)
    if coordinator is None:
        raise ServiceValidationError(
            f"No account found with id '{account_id}'",
            translation_domain=DOMAIN,
            translation_key="account_not_found",
            translation_placeholders={"account_id": account_id},
        )
    return coordinator


# ---------------------------------------------------------------------------
# Handler functions
# ---------------------------------------------------------------------------


async def async_handle_add_transaction(call: ServiceCall) -> None:
    """Handle add_transaction service call."""
    hass = call.hass
    account_id: str = call.data["account_id"]
    amount: float = call.data["amount"]
    note: str = call.data.get("note", "")

    coordinator = _get_coordinator(hass, account_id)
    await coordinator.async_add_transaction(amount, note)


async def async_handle_adjust_balance(call: ServiceCall) -> None:
    """Handle adjust_balance service call."""
    hass = call.hass
    account_id: str = call.data["account_id"]
    new_balance: float = call.data["new_balance"]

    coordinator = _get_coordinator(hass, account_id)
    await coordinator.async_adjust_balance(new_balance)


async def async_handle_add_plan(call: ServiceCall) -> None:
    """Handle add_plan service call."""
    hass = call.hass
    account_id: str = call.data["account_id"]
    title: str = call.data["title"]
    amount: float = call.data["amount"]
    frequency: str = call.data["frequency"]
    day: int = call.data["day"]
    month: int = call.data.get("month", 1)
    active: bool = call.data.get("active", True)

    plan_id = uuid.uuid4().hex[:8]

    coordinator = _get_coordinator(hass, account_id)
    await coordinator.async_add_recurring_plan(
        plan_id=plan_id,
        title=title,
        amount=amount,
        frequency=frequency,
        day=day,
        month=month,
        active=active,
    )


async def async_handle_update_plan(call: ServiceCall) -> None:
    """Handle update_plan service call."""
    hass = call.hass
    account_id: str = call.data["account_id"]
    plan_id: str = call.data["plan_id"]

    coordinator = _get_coordinator(hass, account_id)

    # Verify plan exists
    account = coordinator.account
    if account is None or plan_id not in account.recurring_plans:
        raise ServiceValidationError(
            f"No plan found with id '{plan_id}' in account '{account_id}'",
            translation_domain=DOMAIN,
            translation_key="plan_not_found",
            translation_placeholders={
                "plan_id": plan_id,
                "account_id": account_id,
            },
        )

    # Collect optional fields that were explicitly provided
    optional_fields = ("title", "amount", "frequency", "day", "month", "active")
    kwargs: dict = {}
    for field in optional_fields:
        if field in call.data:
            kwargs[field] = call.data[field]

    if kwargs:
        await coordinator.async_update_recurring_plan(plan_id, **kwargs)


async def async_handle_delete_plan(call: ServiceCall) -> None:
    """Handle delete_plan service call."""
    hass = call.hass
    account_id: str = call.data["account_id"]
    plan_id: str = call.data["plan_id"]

    coordinator = _get_coordinator(hass, account_id)

    # Verify plan exists
    account = coordinator.account
    if account is None or plan_id not in account.recurring_plans:
        raise ServiceValidationError(
            f"No plan found with id '{plan_id}' in account '{account_id}'",
            translation_domain=DOMAIN,
            translation_key="plan_not_found",
            translation_placeholders={
                "plan_id": plan_id,
                "account_id": account_id,
            },
        )

    await coordinator.async_remove_recurring_plan(plan_id)


async def async_handle_set_plan_active(call: ServiceCall) -> None:
    """Handle set_plan_active service call."""
    hass = call.hass
    account_id: str = call.data["account_id"]
    plan_id: str = call.data["plan_id"]
    active: bool = call.data["active"]

    coordinator = _get_coordinator(hass, account_id)

    # Verify plan exists
    account = coordinator.account
    if account is None or plan_id not in account.recurring_plans:
        raise ServiceValidationError(
            f"No plan found with id '{plan_id}' in account '{account_id}'",
            translation_domain=DOMAIN,
            translation_key="plan_not_found",
            translation_placeholders={
                "plan_id": plan_id,
                "account_id": account_id,
            },
        )

    await coordinator.async_set_plan_active(plan_id, active)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up Ha Finance services."""
    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_TRANSACTION,
        async_handle_add_transaction,
        schema=SERVICE_ADD_TRANSACTION_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_ADJUST_BALANCE,
        async_handle_adjust_balance,
        schema=SERVICE_ADJUST_BALANCE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_PLAN,
        async_handle_add_plan,
        schema=SERVICE_ADD_PLAN_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_PLAN,
        async_handle_update_plan,
        schema=SERVICE_UPDATE_PLAN_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_PLAN,
        async_handle_delete_plan,
        schema=SERVICE_DELETE_PLAN_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_PLAN_ACTIVE,
        async_handle_set_plan_active,
        schema=SERVICE_SET_PLAN_ACTIVE_SCHEMA,
    )
