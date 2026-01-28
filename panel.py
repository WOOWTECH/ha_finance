"""Panel and WebSocket API for Ha Finance Record."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol

from homeassistant.components import frontend, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant, callback

from .const import (
    DOMAIN,
    FREQUENCY_DAILY,
    FREQUENCY_MONTHLY,
    FREQUENCY_OPTIONS,
    FREQUENCY_WEEKLY,
    FREQUENCY_YEARLY,
    TRANSACTION_MANUAL,
)
from .models import RecurringPlan, Transaction

if TYPE_CHECKING:
    from .coordinator import FinanceCoordinator
    from .store import FinanceStore

_LOGGER = logging.getLogger(__name__)

PANEL_URL = "/ha_finance_panel"
PANEL_ICON = "mdi:finance"
PANEL_TITLE = "Finance Record"
PANEL_TITLE_ZH = "財務紀錄"
PANEL_VERSION = "3.1.0"  # Account management tab + date filters


def _get_panel_title(hass: HomeAssistant) -> str:
    """Get panel title based on HA language setting."""
    language = hass.config.language or "en"
    if language.startswith("zh"):
        return PANEL_TITLE_ZH
    return PANEL_TITLE


async def async_setup_panel(hass: HomeAssistant) -> None:
    """Set up the Ha Finance panel."""
    # Register static path for frontend files
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                PANEL_URL,
                hass.config.path(
                    "custom_components/ha_finance/frontend"
                ),
                cache_headers=False,
            )
        ]
    )

    # Register the panel using frontend.async_register_built_in_panel
    frontend.async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title=_get_panel_title(hass),
        sidebar_icon=PANEL_ICON,
        frontend_url_path="ha-finance",
        config={
            "_panel_custom": {
                "name": "ha-finance-panel",
                "module_url": f"{PANEL_URL}/ha-finance-panel.js?v={PANEL_VERSION}",
            }
        },
        require_admin=False,
    )

    # Register WebSocket commands
    websocket_api.async_register_command(hass, ws_get_accounts)
    websocket_api.async_register_command(hass, ws_get_account)
    websocket_api.async_register_command(hass, ws_add_transaction)
    websocket_api.async_register_command(hass, ws_update_transaction)
    websocket_api.async_register_command(hass, ws_delete_transaction)
    websocket_api.async_register_command(hass, ws_add_plan)
    websocket_api.async_register_command(hass, ws_update_plan)
    websocket_api.async_register_command(hass, ws_delete_plan)
    websocket_api.async_register_command(hass, ws_get_chart_data)
    websocket_api.async_register_command(hass, ws_add_account)
    websocket_api.async_register_command(hass, ws_update_account)
    websocket_api.async_register_command(hass, ws_delete_account)

    _LOGGER.info("Ha Finance panel registered")


async def async_remove_panel(hass: HomeAssistant) -> None:
    """Remove the Ha Finance panel."""
    frontend.async_remove_panel(hass, "ha-finance")


def _get_store(hass: HomeAssistant) -> FinanceStore:
    """Get the finance store."""
    from .store import FinanceStore
    return FinanceStore(hass)


async def _get_coordinator_for_account(
    hass: HomeAssistant, account_id: str
) -> FinanceCoordinator | None:
    """Get coordinator for a specific account."""
    if DOMAIN not in hass.data:
        return None
    for coordinator in hass.data[DOMAIN].values():
        if hasattr(coordinator, "account") and coordinator.account:
            if coordinator.account.id == account_id:
                return coordinator
    return None


# WebSocket Handlers

@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_finance/accounts",
    }
)
@websocket_api.async_response
async def ws_get_accounts(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Get all accounts."""
    store = _get_store(hass)
    await store.async_load()

    accounts = [
        {
            "id": account.id,
            "name": account.name,
            "balance": account.balance,
        }
        for account in store.data.accounts.values()
    ]

    connection.send_result(msg["id"], {"accounts": accounts})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_finance/account",
        vol.Required("account_id"): str,
    }
)
@websocket_api.async_response
async def ws_get_account(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Get account details including transactions and plans."""
    store = _get_store(hass)
    await store.async_load()

    account = store.data.get_account(msg["account_id"])
    if account is None:
        connection.send_error(msg["id"], "not_found", "Account not found")
        return

    result = {
        "account": {
            "id": account.id,
            "name": account.name,
            "balance": account.balance,
            "transactions": [tx.to_dict() for tx in account.transactions],
            "recurring_plans": {
                plan_id: plan.to_dict()
                for plan_id, plan in account.recurring_plans.items()
            },
        }
    }

    connection.send_result(msg["id"], result)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_finance/add_transaction",
        vol.Required("account_id"): str,
        vol.Required("amount"): vol.Coerce(float),
        vol.Optional("note", default=""): str,
    }
)
@websocket_api.async_response
async def ws_add_transaction(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Add a new transaction."""
    coordinator = await _get_coordinator_for_account(hass, msg["account_id"])
    transaction: Transaction | None = None

    if coordinator is None:
        # Fall back to direct store access
        store = _get_store(hass)
        await store.async_load()
        account = store.data.get_account(msg["account_id"])
        if account is None:
            connection.send_error(msg["id"], "not_found", "Account not found")
            return

        transaction = Transaction.create(
            amount=msg["amount"],
            note=msg["note"],
            transaction_type=TRANSACTION_MANUAL,
        )
        account.add_transaction(transaction)
        await store.async_save()
    else:
        transaction = await coordinator.async_add_transaction(
            amount=msg["amount"],
            note=msg["note"],
        )

    if transaction is None:
        connection.send_error(msg["id"], "error", "Failed to create transaction")
        return

    connection.send_result(
        msg["id"],
        {"success": True, "transaction": transaction.to_dict()},
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_finance/update_transaction",
        vol.Required("account_id"): str,
        vol.Required("transaction_id"): str,
        vol.Optional("amount"): vol.Coerce(float),
        vol.Optional("note"): str,
    }
)
@websocket_api.async_response
async def ws_update_transaction(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update an existing transaction."""
    store = _get_store(hass)
    await store.async_load()

    account = store.data.get_account(msg["account_id"])
    if account is None:
        connection.send_error(msg["id"], "not_found", "Account not found")
        return

    # Find and update transaction
    transaction = None
    for tx in account.transactions:
        if tx.id == msg["transaction_id"]:
            transaction = tx
            break

    if transaction is None:
        connection.send_error(msg["id"], "not_found", "Transaction not found")
        return

    # Update balance if amount changed
    if "amount" in msg:
        old_amount = transaction.amount
        new_amount = msg["amount"]
        account.balance += (new_amount - old_amount)
        transaction.amount = new_amount

    if "note" in msg:
        transaction.note = msg["note"]

    await store.async_save()

    # Refresh coordinator if available
    coordinator = await _get_coordinator_for_account(hass, msg["account_id"])
    if coordinator:
        await coordinator.async_refresh()

    connection.send_result(msg["id"], {"success": True})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_finance/delete_transaction",
        vol.Required("account_id"): str,
        vol.Required("transaction_id"): str,
    }
)
@websocket_api.async_response
async def ws_delete_transaction(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Delete a transaction."""
    store = _get_store(hass)
    await store.async_load()

    account = store.data.get_account(msg["account_id"])
    if account is None:
        connection.send_error(msg["id"], "not_found", "Account not found")
        return

    # Find and remove transaction
    transaction = None
    for i, tx in enumerate(account.transactions):
        if tx.id == msg["transaction_id"]:
            transaction = tx
            account.transactions.pop(i)
            break

    if transaction is None:
        connection.send_error(msg["id"], "not_found", "Transaction not found")
        return

    # Reverse the balance change
    account.balance -= transaction.amount
    await store.async_save()

    # Refresh coordinator if available
    coordinator = await _get_coordinator_for_account(hass, msg["account_id"])
    if coordinator:
        await coordinator.async_refresh()

    connection.send_result(msg["id"], {"success": True})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_finance/add_plan",
        vol.Required("account_id"): str,
        vol.Required("title"): str,
        vol.Required("amount"): vol.Coerce(float),
        vol.Required("frequency"): vol.In(FREQUENCY_OPTIONS),
        vol.Required("day"): vol.All(vol.Coerce(int), vol.Range(min=1, max=28)),
        vol.Optional("month", default=1): vol.All(vol.Coerce(int), vol.Range(min=1, max=12)),
        vol.Optional("active", default=True): bool,
    }
)
@websocket_api.async_response
async def ws_add_plan(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Add a new recurring plan."""
    import uuid

    coordinator = await _get_coordinator_for_account(hass, msg["account_id"])

    if coordinator:
        # Generate plan_id
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        await coordinator.async_add_recurring_plan(
            plan_id=plan_id,
            title=msg["title"],
            amount=msg["amount"],
            frequency=msg["frequency"],
            day=msg["day"],
            month=msg["month"],
            active=msg["active"],
        )
        connection.send_result(msg["id"], {"success": True, "plan_id": plan_id})
    else:
        connection.send_error(msg["id"], "not_found", "Account coordinator not found")


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_finance/update_plan",
        vol.Required("account_id"): str,
        vol.Required("plan_id"): str,
        vol.Optional("title"): str,
        vol.Optional("amount"): vol.Coerce(float),
        vol.Optional("frequency"): vol.In(FREQUENCY_OPTIONS),
        vol.Optional("day"): vol.All(vol.Coerce(int), vol.Range(min=1, max=28)),
        vol.Optional("month"): vol.All(vol.Coerce(int), vol.Range(min=1, max=12)),
        vol.Optional("active"): bool,
    }
)
@websocket_api.async_response
async def ws_update_plan(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update a recurring plan."""
    coordinator = await _get_coordinator_for_account(hass, msg["account_id"])

    if coordinator is None:
        connection.send_error(msg["id"], "not_found", "Account coordinator not found")
        return

    # Extract update fields
    update_fields = {}
    for field in ["title", "amount", "frequency", "day", "month", "active"]:
        if field in msg:
            update_fields[field] = msg[field]

    await coordinator.async_update_recurring_plan(msg["plan_id"], **update_fields)
    connection.send_result(msg["id"], {"success": True})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_finance/delete_plan",
        vol.Required("account_id"): str,
        vol.Required("plan_id"): str,
    }
)
@websocket_api.async_response
async def ws_delete_plan(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Delete a recurring plan."""
    coordinator = await _get_coordinator_for_account(hass, msg["account_id"])

    if coordinator is None:
        connection.send_error(msg["id"], "not_found", "Account coordinator not found")
        return

    await coordinator.async_remove_recurring_plan(msg["plan_id"])
    connection.send_result(msg["id"], {"success": True})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_finance/chart_data",
        vol.Required("account_id"): str,
        vol.Optional("months", default=6): vol.Coerce(int),
    }
)
@websocket_api.async_response
async def ws_get_chart_data(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Get chart data for income vs expenses by month."""
    from datetime import datetime
    from collections import defaultdict

    store = _get_store(hass)
    await store.async_load()

    account = store.data.get_account(msg["account_id"])
    if account is None:
        connection.send_error(msg["id"], "not_found", "Account not found")
        return

    # Group transactions by month
    months_data: dict[str, dict[str, float]] = defaultdict(
        lambda: {"income": 0.0, "expenses": 0.0}
    )

    for tx in account.transactions:
        try:
            tx_date = datetime.fromisoformat(tx.timestamp)
            month_key = tx_date.strftime("%Y-%m")

            if tx.amount >= 0:
                months_data[month_key]["income"] += tx.amount
            else:
                months_data[month_key]["expenses"] += abs(tx.amount)
        except (ValueError, TypeError):
            continue

    # Sort by month and limit to requested number
    sorted_months = sorted(months_data.keys(), reverse=True)[: msg["months"]]
    sorted_months.reverse()  # Oldest first for chart

    chart_data = [
        {
            "month": month,
            "income": round(months_data[month]["income"], 2),
            "expenses": round(months_data[month]["expenses"], 2),
        }
        for month in sorted_months
    ]

    connection.send_result(msg["id"], {"data": chart_data})


# Account Management WebSocket Handlers

@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_finance/add_account",
        vol.Required("name"): str,
        vol.Optional("initial_balance", default=0.0): vol.Coerce(float),
    }
)
@websocket_api.async_response
async def ws_add_account(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Add a new account."""
    import re
    import uuid

    name = msg["name"].strip()
    if not name:
        connection.send_error(msg["id"], "invalid_name", "Account name cannot be empty")
        return

    # Generate account ID from name
    account_id = re.sub(r"[^a-zA-Z0-9_]", "_", name.lower())
    account_id = f"{account_id}_{uuid.uuid4().hex[:6]}"

    store = _get_store(hass)
    await store.async_load()

    # Check for duplicate name
    for existing in store.data.accounts.values():
        if existing.name.lower() == name.lower():
            connection.send_error(msg["id"], "duplicate_name", "Account with this name already exists")
            return

    from .models import Account

    account = Account(
        id=account_id,
        name=name,
        balance=msg["initial_balance"],
    )
    store.data.add_account(account)
    await store.async_save()

    connection.send_result(
        msg["id"],
        {
            "success": True,
            "account": {
                "id": account.id,
                "name": account.name,
                "balance": account.balance,
            },
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_finance/update_account",
        vol.Required("account_id"): str,
        vol.Required("name"): str,
    }
)
@websocket_api.async_response
async def ws_update_account(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update an account (rename)."""
    name = msg["name"].strip()
    if not name:
        connection.send_error(msg["id"], "invalid_name", "Account name cannot be empty")
        return

    store = _get_store(hass)
    await store.async_load()

    account = store.data.get_account(msg["account_id"])
    if account is None:
        connection.send_error(msg["id"], "not_found", "Account not found")
        return

    # Check for duplicate name (excluding current account)
    for existing in store.data.accounts.values():
        if existing.id != msg["account_id"] and existing.name.lower() == name.lower():
            connection.send_error(msg["id"], "duplicate_name", "Account with this name already exists")
            return

    account.name = name
    await store.async_save()

    # Refresh coordinator if available
    coordinator = await _get_coordinator_for_account(hass, msg["account_id"])
    if coordinator:
        await coordinator.async_refresh()

    connection.send_result(msg["id"], {"success": True})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_finance/delete_account",
        vol.Required("account_id"): str,
    }
)
@websocket_api.async_response
async def ws_delete_account(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Delete an account."""
    store = _get_store(hass)
    await store.async_load()

    account = store.data.get_account(msg["account_id"])
    if account is None:
        connection.send_error(msg["id"], "not_found", "Account not found")
        return

    store.data.remove_account(msg["account_id"])
    await store.async_save()

    connection.send_result(msg["id"], {"success": True})
