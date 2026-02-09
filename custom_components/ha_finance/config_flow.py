"""Config flow for Ha Finance Record integration."""
from __future__ import annotations

import re
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    ACTION_ADD_RECURRING,
    ACTION_DELETE_ACCOUNT,
    ACTION_DELETE_PLAN,
    ACTION_EDIT_PLAN,
    ACTION_MANAGE_RECURRING,
    CONF_ACCOUNT_ID,
    CONF_ACCOUNT_NAME,
    CONF_INITIAL_BALANCE,
    CONF_PLAN_ACTIVE,
    CONF_PLAN_AMOUNT,
    CONF_PLAN_DAY,
    CONF_PLAN_FREQUENCY,
    CONF_PLAN_MONTH,
    CONF_PLAN_TITLE,
    DOMAIN,
    FREQUENCY_DAILY,
    FREQUENCY_MONTHLY,
    FREQUENCY_WEEKLY,
    FREQUENCY_YEARLY,
)


def generate_account_id(name: str) -> str:
    """Generate a valid account ID from the name."""
    # Convert to lowercase and replace spaces/special chars with underscore
    account_id = re.sub(r"[^a-zA-Z0-9_]", "_", name.lower())
    account_id = re.sub(r"_+", "_", account_id).strip("_")
    return account_id or "account"


def generate_plan_id(title: str) -> str:
    """Generate a valid plan ID from the title."""
    plan_id = re.sub(r"[^a-zA-Z0-9_]", "_", title.lower())
    plan_id = re.sub(r"_+", "_", plan_id).strip("_")
    return plan_id or "plan"


class HaFinanceConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ha Finance."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            account_name = user_input[CONF_ACCOUNT_NAME]
            account_id = user_input.get(CONF_ACCOUNT_ID) or generate_account_id(
                account_name
            )
            initial_balance = user_input.get(CONF_INITIAL_BALANCE, 0.0)

            # Check for duplicate account ID
            await self.async_set_unique_id(account_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=account_name,
                data={
                    CONF_ACCOUNT_ID: account_id,
                    CONF_ACCOUNT_NAME: account_name,
                    CONF_INITIAL_BALANCE: initial_balance,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ACCOUNT_NAME): cv.string,
                    vol.Optional(CONF_ACCOUNT_ID): cv.string,
                    vol.Optional(CONF_INITIAL_BALANCE, default=0.0): vol.Coerce(float),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> HaFinanceOptionsFlow:
        """Get the options flow for this handler."""
        return HaFinanceOptionsFlow(config_entry)


class HaFinanceOptionsFlow(OptionsFlow):
    """Handle options flow for Ha Finance."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._selected_plan_id: str | None = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial options step."""
        if user_input is not None:
            action = user_input.get("action")
            if action == ACTION_ADD_RECURRING:
                return await self.async_step_add_recurring()
            if action == ACTION_MANAGE_RECURRING:
                return await self.async_step_manage_recurring()
            if action == ACTION_DELETE_ACCOUNT:
                return await self.async_step_delete_account()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("action"): vol.In(
                        {
                            ACTION_ADD_RECURRING: "新增定期項目",
                            ACTION_MANAGE_RECURRING: "管理定期項目",
                            ACTION_DELETE_ACCOUNT: "刪除帳戶",
                        }
                    ),
                }
            ),
        )

    async def async_step_add_recurring(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle adding a recurring plan."""
        errors: dict[str, str] = {}

        if user_input is not None:
            title = user_input[CONF_PLAN_TITLE]
            plan_id = generate_plan_id(title)
            amount = user_input[CONF_PLAN_AMOUNT]
            frequency = user_input[CONF_PLAN_FREQUENCY]
            day = user_input[CONF_PLAN_DAY]
            month = user_input.get(CONF_PLAN_MONTH, 1)
            active = user_input.get(CONF_PLAN_ACTIVE, True)

            # Validate day based on frequency
            if frequency == FREQUENCY_WEEKLY and not (1 <= day <= 7):
                errors["base"] = "invalid_day_weekly"
            elif frequency == FREQUENCY_MONTHLY and not (1 <= day <= 28):
                errors["base"] = "invalid_day_monthly"
            elif frequency == FREQUENCY_YEARLY and not (1 <= day <= 28):
                errors["base"] = "invalid_day_yearly"
            else:
                # Get coordinator and add plan
                coordinator = self.hass.data[DOMAIN].get(self.config_entry.entry_id)
                if coordinator:
                    # Check for duplicate plan ID
                    account = coordinator.account
                    if account and plan_id in account.recurring_plans:
                        # Add suffix to make unique
                        counter = 1
                        while f"{plan_id}_{counter}" in account.recurring_plans:
                            counter += 1
                        plan_id = f"{plan_id}_{counter}"

                    await coordinator.async_add_recurring_plan(
                        plan_id=plan_id,
                        title=title,
                        amount=amount,
                        frequency=frequency,
                        day=day,
                        month=month,
                        active=active,
                    )

                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="add_recurring",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PLAN_TITLE): cv.string,
                    vol.Required(CONF_PLAN_AMOUNT): vol.Coerce(float),
                    vol.Required(CONF_PLAN_FREQUENCY, default=FREQUENCY_MONTHLY): vol.In(
                        {
                            FREQUENCY_DAILY: "Daily",
                            FREQUENCY_WEEKLY: "Weekly",
                            FREQUENCY_MONTHLY: "Monthly",
                            FREQUENCY_YEARLY: "Yearly",
                        }
                    ),
                    vol.Required(CONF_PLAN_DAY, default=1): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=28)
                    ),
                    vol.Optional(CONF_PLAN_MONTH, default=1): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=12)
                    ),
                    vol.Optional(CONF_PLAN_ACTIVE, default=True): cv.boolean,
                }
            ),
            errors=errors,
        )

    async def async_step_manage_recurring(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle managing recurring plans."""
        coordinator = self.hass.data[DOMAIN].get(self.config_entry.entry_id)
        if not coordinator or not coordinator.account:
            return self.async_abort(reason="no_account")

        account = coordinator.account
        plans = account.recurring_plans

        if not plans:
            return self.async_abort(reason="no_plans")

        if user_input is not None:
            self._selected_plan_id = user_input.get("plan")
            return await self.async_step_plan_action()

        plan_options = {
            plan_id: f"{plan.title} (${plan.amount:+.0f}/{self._get_frequency_label(plan.frequency)})"
            for plan_id, plan in plans.items()
        }

        return self.async_show_form(
            step_id="manage_recurring",
            data_schema=vol.Schema(
                {
                    vol.Required("plan"): vol.In(plan_options),
                }
            ),
        )

    async def async_step_plan_action(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle plan action selection."""
        if user_input is not None:
            action = user_input.get("action")
            if action == ACTION_EDIT_PLAN:
                return await self.async_step_edit_plan()
            if action == ACTION_DELETE_PLAN:
                return await self.async_step_delete_plan()

        return self.async_show_form(
            step_id="plan_action",
            data_schema=vol.Schema(
                {
                    vol.Required("action"): vol.In(
                        {
                            ACTION_EDIT_PLAN: "編輯項目",
                            ACTION_DELETE_PLAN: "刪除項目",
                        }
                    ),
                }
            ),
        )

    async def async_step_edit_plan(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle editing a recurring plan."""
        errors: dict[str, str] = {}
        coordinator = self.hass.data[DOMAIN].get(self.config_entry.entry_id)
        if not coordinator or not coordinator.account:
            return self.async_abort(reason="no_account")

        plan = coordinator.account.recurring_plans.get(self._selected_plan_id)
        if not plan:
            return self.async_abort(reason="plan_not_found")

        if user_input is not None:
            frequency = user_input[CONF_PLAN_FREQUENCY]
            day = user_input[CONF_PLAN_DAY]
            month = user_input.get(CONF_PLAN_MONTH, getattr(plan, "month", 1))

            # Validate day based on frequency
            if frequency == FREQUENCY_WEEKLY and not (1 <= day <= 7):
                errors["base"] = "invalid_day_weekly"
            elif frequency == FREQUENCY_MONTHLY and not (1 <= day <= 28):
                errors["base"] = "invalid_day_monthly"
            elif frequency == FREQUENCY_YEARLY and not (1 <= day <= 28):
                errors["base"] = "invalid_day_yearly"
            else:
                await coordinator.async_update_recurring_plan(
                    self._selected_plan_id,
                    title=user_input[CONF_PLAN_TITLE],
                    amount=user_input[CONF_PLAN_AMOUNT],
                    frequency=frequency,
                    day=day,
                    month=month,
                )
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="edit_plan",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PLAN_TITLE, default=plan.title): cv.string,
                    vol.Required(CONF_PLAN_AMOUNT, default=plan.amount): vol.Coerce(
                        float
                    ),
                    vol.Required(
                        CONF_PLAN_FREQUENCY, default=plan.frequency
                    ): vol.In(
                        {
                            FREQUENCY_DAILY: "Daily",
                            FREQUENCY_WEEKLY: "Weekly",
                            FREQUENCY_MONTHLY: "Monthly",
                            FREQUENCY_YEARLY: "Yearly",
                        }
                    ),
                    vol.Required(CONF_PLAN_DAY, default=plan.day): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=28)
                    ),
                    vol.Optional(
                        CONF_PLAN_MONTH, default=getattr(plan, "month", 1)
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=12)),
                }
            ),
            errors=errors,
        )

    async def async_step_delete_plan(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle deleting a recurring plan."""
        coordinator = self.hass.data[DOMAIN].get(self.config_entry.entry_id)
        if not coordinator:
            return self.async_abort(reason="no_account")

        if user_input is not None:
            if user_input.get("confirm"):
                await coordinator.async_remove_recurring_plan(self._selected_plan_id)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="delete_plan",
            data_schema=vol.Schema(
                {
                    vol.Required("confirm", default=False): cv.boolean,
                }
            ),
            description_placeholders={"plan_id": self._selected_plan_id},
        )

    async def async_step_delete_account(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle account deletion confirmation."""
        if user_input is not None:
            if user_input.get("confirm"):
                await self.hass.config_entries.async_remove(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="delete_account",
            data_schema=vol.Schema(
                {
                    vol.Required("confirm", default=False): cv.boolean,
                }
            ),
        )

    def _get_frequency_label(self, frequency: str) -> str:
        """Get display label for frequency."""
        labels = {
            FREQUENCY_DAILY: "日",
            FREQUENCY_WEEKLY: "週",
            FREQUENCY_MONTHLY: "月",
            FREQUENCY_YEARLY: "年",
        }
        return labels.get(frequency, frequency)
