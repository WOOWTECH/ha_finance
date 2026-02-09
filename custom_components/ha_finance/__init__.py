"""Ha Finance Record integration for Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import CONF_ACCOUNT_ID, CONF_ACCOUNT_NAME, CONF_INITIAL_BALANCE, DOMAIN
from .coordinator import FinanceCoordinator
from .models import Account
from .panel import async_setup_panel, async_remove_panel
from .store import FinanceStore

_LOGGER = logging.getLogger(__name__)

# Key for tracking panel registration state in hass.data
_PANEL_REGISTERED_KEY = "_panel_registered"

PLATFORMS_LIST: list[Platform] = [
    Platform.NUMBER,
    Platform.TEXT,
    Platform.BUTTON,
    Platform.SENSOR,
    Platform.SELECT,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ha Finance from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Register panel only once (first account setup)
    if not hass.data[DOMAIN].get(_PANEL_REGISTERED_KEY):
        await async_setup_panel(hass)
        hass.data[DOMAIN][_PANEL_REGISTERED_KEY] = True

    coordinator = FinanceCoordinator(hass, entry)
    await coordinator.async_setup()

    # Ensure account exists in storage
    account_id = entry.data[CONF_ACCOUNT_ID]
    account_name = entry.data[CONF_ACCOUNT_NAME]
    initial_balance = entry.data.get(CONF_INITIAL_BALANCE, 0.0)

    if coordinator.data.get_account(account_id) is None:
        account = Account(
            id=account_id,
            name=account_name,
            balance=initial_balance,
        )
        coordinator.data.add_account(account)
        await coordinator.store.async_save()
        await coordinator.async_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register device
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, account_id)},
        name=account_name,
        manufacturer="Ha Finance",
        model="Financial Account",
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS_LIST)

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator: FinanceCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_shutdown()

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS_LIST):
        hass.data[DOMAIN].pop(entry.entry_id)

    # Remove panel if no more config entries (only _PANEL_REGISTERED_KEY remains)
    remaining_entries = [k for k in hass.data.get(DOMAIN, {}).keys() if k != _PANEL_REGISTERED_KEY]
    if not remaining_entries and hass.data[DOMAIN].get(_PANEL_REGISTERED_KEY):
        await async_remove_panel(hass)
        hass.data[DOMAIN][_PANEL_REGISTERED_KEY] = False

    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options listener."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle removal of an entry."""
    account_id = entry.data[CONF_ACCOUNT_ID]

    # Try to get coordinator from hass.data first (if not yet unloaded)
    coordinator: FinanceCoordinator | None = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if coordinator:
        coordinator.data.remove_account(account_id)
        await coordinator.store.async_save()
    else:
        # Coordinator already unloaded, access store directly
        store = FinanceStore(hass)
        await store.async_load()
        store.data.remove_account(account_id)
        await store.async_save()
        # Clear the store instance since we're removing the account
        FinanceStore.clear_instance(hass)
