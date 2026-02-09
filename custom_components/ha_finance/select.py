"""Select entities for Ha Finance Record integration."""
from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_ACCOUNT_ID,
    DOMAIN,
    FREQUENCY_DAILY,
    FREQUENCY_MONTHLY,
    FREQUENCY_WEEKLY,
    FREQUENCY_YEARLY,
)
from .coordinator import FinanceCoordinator

if TYPE_CHECKING:
    from .models import Account

FREQUENCY_LABELS = {
    FREQUENCY_DAILY: "每日",
    FREQUENCY_WEEKLY: "每週",
    FREQUENCY_MONTHLY: "每月",
    FREQUENCY_YEARLY: "每年",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities."""
    coordinator: FinanceCoordinator = hass.data[DOMAIN][entry.entry_id]
    account_id = entry.data[CONF_ACCOUNT_ID]

    entities: list[SelectEntity] = []

    # Add recurring plan frequency selects
    if coordinator.account:
        for plan_id in coordinator.account.recurring_plans:
            entities.append(PlanFrequencySelect(coordinator, account_id, plan_id))

    async_add_entities(entities)

    # Register listener for new plans
    @callback
    def async_add_plan_entities() -> None:
        """Add entities for new recurring plans."""
        if not coordinator.account:
            return
        existing_plan_ids = {
            e.plan_id for e in entities if isinstance(e, PlanFrequencySelect)
        }
        new_entities: list[SelectEntity] = []
        for plan_id in coordinator.account.recurring_plans:
            if plan_id not in existing_plan_ids:
                new_entities.append(PlanFrequencySelect(coordinator, account_id, plan_id))
        if new_entities:
            async_add_entities(new_entities)
            entities.extend(new_entities)

    entry.async_on_unload(coordinator.async_add_listener(async_add_plan_entities))


class PlanFrequencySelect(CoordinatorEntity[FinanceCoordinator], SelectEntity):
    """Select entity for recurring plan frequency."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:calendar-sync"
    _attr_translation_key = "plan_frequency"
    _attr_options = list(FREQUENCY_LABELS.values())

    def __init__(
        self, coordinator: FinanceCoordinator, account_id: str, plan_id: str
    ) -> None:
        """Initialize plan frequency select."""
        super().__init__(coordinator)
        self._account_id = account_id
        self.plan_id = plan_id
        self._attr_unique_id = f"{account_id}_{plan_id}_frequency"

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

    @property
    def name(self) -> str:
        """Return the name."""
        account = self.account
        if account and self.plan_id in account.recurring_plans:
            plan = account.recurring_plans[self.plan_id]
            return f"{plan.title} 頻率"
        return f"{self.plan_id} 頻率"

    @property
    def current_option(self) -> str | None:
        """Return the current frequency."""
        account = self.account
        if account is None:
            return None
        plan = account.recurring_plans.get(self.plan_id)
        if plan is None:
            return None
        return FREQUENCY_LABELS.get(plan.frequency, plan.frequency)

    async def async_select_option(self, option: str) -> None:
        """Set the frequency."""
        # Reverse lookup: label to value
        frequency_value = None
        for value, label in FREQUENCY_LABELS.items():
            if label == option:
                frequency_value = value
                break

        if frequency_value:
            await self.coordinator.async_update_recurring_plan(
                self.plan_id, frequency=frequency_value
            )
