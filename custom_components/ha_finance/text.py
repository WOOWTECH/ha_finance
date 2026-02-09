"""Text entities for Ha Finance Record integration."""
from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ACCOUNT_ID, DOMAIN
from .coordinator import FinanceCoordinator

if TYPE_CHECKING:
    from .models import Account


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up text entities."""
    coordinator: FinanceCoordinator = hass.data[DOMAIN][entry.entry_id]
    account_id = entry.data[CONF_ACCOUNT_ID]

    entities: list[TextEntity] = [
        QuickNoteText(coordinator, account_id),
    ]

    # Add recurring plan title texts
    if coordinator.account:
        for plan_id in coordinator.account.recurring_plans:
            entities.append(PlanTitleText(coordinator, account_id, plan_id))

    async_add_entities(entities)

    # Register listener for new plans
    @callback
    def async_add_plan_entities() -> None:
        """Add entities for new recurring plans."""
        if not coordinator.account:
            return
        existing_plan_ids = {
            e.plan_id for e in entities if isinstance(e, PlanTitleText)
        }
        new_entities: list[TextEntity] = []
        for plan_id in coordinator.account.recurring_plans:
            if plan_id not in existing_plan_ids:
                new_entities.append(PlanTitleText(coordinator, account_id, plan_id))
        if new_entities:
            async_add_entities(new_entities)
            entities.extend(new_entities)

    entry.async_on_unload(coordinator.async_add_listener(async_add_plan_entities))


class FinanceTextBase(CoordinatorEntity[FinanceCoordinator], TextEntity):
    """Base class for finance text entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FinanceCoordinator,
        account_id: str,
    ) -> None:
        """Initialize the text entity."""
        super().__init__(coordinator)
        self._account_id = account_id

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


class QuickNoteText(FinanceTextBase):
    """Text entity for quick record note."""

    _attr_icon = "mdi:note-text"
    _attr_translation_key = "quick_note"
    _attr_native_max = 255

    def __init__(self, coordinator: FinanceCoordinator, account_id: str) -> None:
        """Initialize quick note text."""
        super().__init__(coordinator, account_id)
        self._attr_unique_id = f"{account_id}_quick_note"
        self._value: str = ""

    @property
    def native_value(self) -> str:
        """Return the current quick note."""
        return self._value

    async def async_set_value(self, value: str) -> None:
        """Set the quick note."""
        self._value = value
        self.async_write_ha_state()

    def reset(self) -> None:
        """Reset the quick note to empty."""
        self._value = ""
        self.async_write_ha_state()


class PlanTitleText(FinanceTextBase):
    """Text entity for recurring plan title."""

    _attr_icon = "mdi:tag"
    _attr_translation_key = "plan_title"
    _attr_native_max = 100

    def __init__(
        self, coordinator: FinanceCoordinator, account_id: str, plan_id: str
    ) -> None:
        """Initialize plan title text."""
        super().__init__(coordinator, account_id)
        self.plan_id = plan_id
        self._attr_unique_id = f"{account_id}_{plan_id}_title"

    @property
    def name(self) -> str:
        """Return the name."""
        account = self.account
        if account and self.plan_id in account.recurring_plans:
            plan = account.recurring_plans[self.plan_id]
            return f"{plan.title} 名稱"
        return f"{self.plan_id} 名稱"

    @property
    def native_value(self) -> str | None:
        """Return the plan title."""
        account = self.account
        if account is None:
            return None
        plan = account.recurring_plans.get(self.plan_id)
        if plan is None:
            return None
        return plan.title

    async def async_set_value(self, value: str) -> None:
        """Set the plan title."""
        await self.coordinator.async_update_recurring_plan(self.plan_id, title=value)
