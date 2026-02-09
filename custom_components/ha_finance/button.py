"""Button entities for Ha Finance Record integration."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ACCOUNT_ID, DOMAIN, TRANSACTION_MANUAL
from .coordinator import FinanceCoordinator

if TYPE_CHECKING:
    from .models import Account

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities."""
    coordinator: FinanceCoordinator = hass.data[DOMAIN][entry.entry_id]
    account_id = entry.data[CONF_ACCOUNT_ID]

    async_add_entities([
        ConfirmRecordButton(coordinator, account_id),
    ])


class ConfirmRecordButton(CoordinatorEntity[FinanceCoordinator], ButtonEntity):
    """Button entity to confirm a quick record."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:check-circle"
    _attr_translation_key = "confirm_record"

    def __init__(self, coordinator: FinanceCoordinator, account_id: str) -> None:
        """Initialize the button entity."""
        super().__init__(coordinator)
        self._account_id = account_id
        self._attr_unique_id = f"{account_id}_confirm_record"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._account_id)},
        )

    @property
    def account(self) -> Account | None:
        """Get the account."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get_account(self._account_id)

    async def async_press(self) -> None:
        """Handle button press."""
        hass = self.hass

        # Use entity registry to find entities by unique_id (safer approach)
        entity_registry = async_get_entity_registry(hass)

        # Find quick amount entity by unique_id using efficient lookup
        quick_amount_unique_id = f"{self._account_id}_quick_amount"
        quick_note_unique_id = f"{self._account_id}_quick_note"

        quick_amount_entity_id = entity_registry.async_get_entity_id(
            "number", DOMAIN, quick_amount_unique_id
        )
        quick_note_entity_id = entity_registry.async_get_entity_id(
            "text", DOMAIN, quick_note_unique_id
        )

        if quick_amount_entity_id is None:
            _LOGGER.warning(
                "Could not find quick amount entity for account %s", self._account_id
            )
            return

        # Get states
        amount_state = hass.states.get(quick_amount_entity_id)
        note_state = hass.states.get(quick_note_entity_id) if quick_note_entity_id else None

        if amount_state is None:
            _LOGGER.warning("Quick amount entity state not found")
            return

        try:
            amount = float(amount_state.state)
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid quick amount value: %s", amount_state.state)
            return

        if amount == 0:
            _LOGGER.debug("Quick amount is zero, skipping transaction")
            return

        note = note_state.state if note_state and note_state.state != "unknown" else ""

        # Add transaction
        await self.coordinator.async_add_transaction(
            amount=amount,
            note=note,
            transaction_type=TRANSACTION_MANUAL,
        )

        # Reset quick amount via service call
        try:
            await hass.services.async_call(
                "number",
                "set_value",
                {"entity_id": quick_amount_entity_id, "value": 0},
                blocking=True,
            )
        except Exception as exc:
            _LOGGER.warning("Failed to reset quick amount: %s", exc)

        # Reset quick note via service call
        if quick_note_entity_id:
            try:
                await hass.services.async_call(
                    "text",
                    "set_value",
                    {"entity_id": quick_note_entity_id, "value": ""},
                    blocking=True,
                )
            except Exception as exc:
                # Text entity might not support empty string in some cases
                _LOGGER.warning("Failed to reset quick note: %s", exc)
