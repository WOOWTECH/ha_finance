"""Storage management for Ha Finance Record integration."""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION
from .models import FinanceData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class FinanceStore:
    """Class to manage finance data storage.

    This is a singleton per HomeAssistant instance to prevent data races
    when multiple accounts are configured.
    """

    _instances: dict[str, "FinanceStore"] = {}
    _instance_lock = asyncio.Lock()
    _data_lock: asyncio.Lock

    def __new__(cls, hass: HomeAssistant) -> "FinanceStore":
        """Ensure only one instance per hass instance."""
        hass_id = id(hass)
        key = str(hass_id)
        # Note: This is synchronous, but race conditions are mitigated by
        # ensuring get_or_create pattern is called from async context
        if key not in cls._instances:
            instance = super().__new__(cls)
            instance._initialized = False
            instance._data_lock = asyncio.Lock()
            cls._instances[key] = instance
        return cls._instances[key]

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the store."""
        if getattr(self, "_initialized", False):
            return
        self._hass = hass
        self._store: Store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: FinanceData | None = None
        self._initialized = True

    @property
    def data(self) -> FinanceData:
        """Get the current data."""
        if self._data is None:
            self._data = FinanceData()
        return self._data

    async def async_load(self) -> FinanceData:
        """Load data from storage."""
        async with self._data_lock:
            if self._data is not None:
                return self._data
            stored_data = await self._store.async_load()
            if stored_data is None:
                self._data = FinanceData()
            else:
                self._data = FinanceData.from_dict(stored_data)
            _LOGGER.debug("Loaded finance data: %s accounts", len(self._data.accounts))
            return self._data

    async def async_save(self) -> None:
        """Save data to storage."""
        async with self._data_lock:
            if self._data is not None:
                await self._store.async_save(self._data.to_dict())
                _LOGGER.debug("Saved finance data")

    async def async_remove(self) -> None:
        """Remove all stored data."""
        async with self._data_lock:
            await self._store.async_remove()
            self._data = FinanceData()
            _LOGGER.debug("Removed all finance data")

    @classmethod
    def clear_instance(cls, hass: HomeAssistant) -> None:
        """Clear the instance for a specific hass (for testing)."""
        hass_id = id(hass)
        key = str(hass_id)
        if key in cls._instances:
            del cls._instances[key]
