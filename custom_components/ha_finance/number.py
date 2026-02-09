"""Number entities for Ha Finance Record integration."""
from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ACCOUNT_ID, DEFAULT_QUICK_AMOUNT, DOMAIN
from .coordinator import FinanceCoordinator

if TYPE_CHECKING:
    from .models import Account


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""
    coordinator: FinanceCoordinator = hass.data[DOMAIN][entry.entry_id]
    account_id = entry.data[CONF_ACCOUNT_ID]

    entities: list[NumberEntity] = [
        BalanceNumber(coordinator, account_id),
        QuickAmountNumber(coordinator, account_id),
    ]

    # Add recurring plan amount numbers
    if coordinator.account:
        for plan_id in coordinator.account.recurring_plans:
            entities.append(PlanAmountNumber(coordinator, account_id, plan_id))
            entities.append(PlanDayNumber(coordinator, account_id, plan_id))

    async_add_entities(entities)

    # Register listener for new plans
    @callback
    def async_add_plan_entities() -> None:
        """Add entities for new recurring plans."""
        if not coordinator.account:
            return
        existing_plan_ids = {
            e.plan_id
            for e in entities
            if isinstance(e, (PlanAmountNumber, PlanDayNumber))
        }
        new_entities: list[NumberEntity] = []
        for plan_id in coordinator.account.recurring_plans:
            if plan_id not in existing_plan_ids:
                new_entities.append(PlanAmountNumber(coordinator, account_id, plan_id))
                new_entities.append(PlanDayNumber(coordinator, account_id, plan_id))
        if new_entities:
            async_add_entities(new_entities)
            entities.extend(new_entities)

    entry.async_on_unload(coordinator.async_add_listener(async_add_plan_entities))


class FinanceNumberBase(CoordinatorEntity[FinanceCoordinator], NumberEntity):
    """Base class for finance number entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FinanceCoordinator,
        account_id: str,
    ) -> None:
        """Initialize the number entity."""
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


class BalanceNumber(FinanceNumberBase):
    """Number entity for account balance."""

    _attr_native_min_value = -9999999999
    _attr_native_max_value = 9999999999
    _attr_native_step = 0.01
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:cash-multiple"
    _attr_translation_key = "balance"

    def __init__(self, coordinator: FinanceCoordinator, account_id: str) -> None:
        """Initialize balance number."""
        super().__init__(coordinator, account_id)
        self._attr_unique_id = f"{account_id}_balance"

    @property
    def native_value(self) -> float | None:
        """Return the current balance."""
        account = self.account
        if account is None:
            return None
        return account.balance

    async def async_set_native_value(self, value: float) -> None:
        """Set the balance."""
        await self.coordinator.async_adjust_balance(value)


class QuickAmountNumber(FinanceNumberBase):
    """Number entity for quick record amount."""

    _attr_native_min_value = -9999999999
    _attr_native_max_value = 9999999999
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:calculator"
    _attr_translation_key = "quick_amount"

    def __init__(self, coordinator: FinanceCoordinator, account_id: str) -> None:
        """Initialize quick amount number."""
        super().__init__(coordinator, account_id)
        self._attr_unique_id = f"{account_id}_quick_amount"
        self._value: float = DEFAULT_QUICK_AMOUNT

    @property
    def native_value(self) -> float:
        """Return the current quick amount."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Set the quick amount."""
        self._value = value
        self.async_write_ha_state()

    def reset(self) -> None:
        """Reset the quick amount to zero."""
        self._value = DEFAULT_QUICK_AMOUNT
        self.async_write_ha_state()


class PlanAmountNumber(FinanceNumberBase):
    """Number entity for recurring plan amount."""

    _attr_native_min_value = -9999999999
    _attr_native_max_value = 9999999999
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:calendar-clock"
    _attr_translation_key = "plan_amount"

    def __init__(
        self, coordinator: FinanceCoordinator, account_id: str, plan_id: str
    ) -> None:
        """Initialize plan amount number."""
        super().__init__(coordinator, account_id)
        self.plan_id = plan_id
        self._attr_unique_id = f"{account_id}_{plan_id}_amount"

    @property
    def name(self) -> str:
        """Return the name."""
        account = self.account
        if account and self.plan_id in account.recurring_plans:
            plan = account.recurring_plans[self.plan_id]
            return f"{plan.title} 金額"
        return f"{self.plan_id} 金額"

    @property
    def native_value(self) -> float | None:
        """Return the plan amount."""
        account = self.account
        if account is None:
            return None
        plan = account.recurring_plans.get(self.plan_id)
        if plan is None:
            return None
        return plan.amount

    async def async_set_native_value(self, value: float) -> None:
        """Set the plan amount."""
        await self.coordinator.async_update_recurring_plan(self.plan_id, amount=value)


class PlanDayNumber(FinanceNumberBase):
    """Number entity for recurring plan execution day."""

    _attr_native_min_value = 1
    _attr_native_max_value = 31
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:calendar-today"
    _attr_translation_key = "plan_day"

    def __init__(
        self, coordinator: FinanceCoordinator, account_id: str, plan_id: str
    ) -> None:
        """Initialize plan day number."""
        super().__init__(coordinator, account_id)
        self.plan_id = plan_id
        self._attr_unique_id = f"{account_id}_{plan_id}_day"

    @property
    def name(self) -> str:
        """Return the name."""
        account = self.account
        if account and self.plan_id in account.recurring_plans:
            plan = account.recurring_plans[self.plan_id]
            return f"{plan.title} 執行日"
        return f"{self.plan_id} 執行日"

    @property
    def native_value(self) -> int | None:
        """Return the plan day."""
        account = self.account
        if account is None:
            return None
        plan = account.recurring_plans.get(self.plan_id)
        if plan is None:
            return None
        return plan.day

    async def async_set_native_value(self, value: float) -> None:
        """Set the plan day."""
        await self.coordinator.async_update_recurring_plan(self.plan_id, day=int(value))
