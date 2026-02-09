"""Switch entities for Ha Finance Record integration."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up switch entities."""
    coordinator: FinanceCoordinator = hass.data[DOMAIN][entry.entry_id]
    account_id = entry.data[CONF_ACCOUNT_ID]

    entities: list[SwitchEntity] = []

    # Add recurring plan active switches
    if coordinator.account:
        for plan_id in coordinator.account.recurring_plans:
            entities.append(PlanActiveSwitch(coordinator, account_id, plan_id))

    async_add_entities(entities)

    # Register listener for new plans
    @callback
    def async_add_plan_entities() -> None:
        """Add entities for new recurring plans."""
        if not coordinator.account:
            return
        existing_plan_ids = {
            e.plan_id for e in entities if isinstance(e, PlanActiveSwitch)
        }
        new_entities: list[SwitchEntity] = []
        for plan_id in coordinator.account.recurring_plans:
            if plan_id not in existing_plan_ids:
                new_entities.append(PlanActiveSwitch(coordinator, account_id, plan_id))
        if new_entities:
            async_add_entities(new_entities)
            entities.extend(new_entities)

    entry.async_on_unload(coordinator.async_add_listener(async_add_plan_entities))


class PlanActiveSwitch(CoordinatorEntity[FinanceCoordinator], SwitchEntity):
    """Switch entity for recurring plan active state."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:power"
    _attr_translation_key = "plan_active"

    def __init__(
        self, coordinator: FinanceCoordinator, account_id: str, plan_id: str
    ) -> None:
        """Initialize plan active switch."""
        super().__init__(coordinator)
        self._account_id = account_id
        self.plan_id = plan_id
        self._attr_unique_id = f"{account_id}_{plan_id}_active"

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
            return f"{plan.title} 啟用"
        return f"{self.plan_id} 啟用"

    @property
    def is_on(self) -> bool | None:
        """Return the active state."""
        account = self.account
        if account is None:
            return None
        plan = account.recurring_plans.get(self.plan_id)
        if plan is None:
            return None
        return plan.active

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the plan."""
        await self.coordinator.async_set_plan_active(self.plan_id, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the plan."""
        await self.coordinator.async_set_plan_active(self.plan_id, False)
