# sensor.py

import logging
from datetime import timedelta

from homeassistant.helpers.entity import Entity
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    POLYGONSCAN_API_URL,
    GEOD_CONTRACT_ADDRESS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up GEOD Balance sensor based on a config entry."""
    nickname = entry.data.get("nickname")
    wallet_address = entry.data.get("wallet_address")
    api_key = entry.data.get("api_key")

    # Create the coordinator
    coordinator = GeodBalanceDataUpdateCoordinator(hass, wallet_address, api_key)
    await coordinator.async_config_entry_first_refresh()

    # Define the sensor name using the nickname
    sensor_name = f"{nickname}_geod_balance"

    # Add the sensor entity
    async_add_entities([GeodBalanceSensor(coordinator, sensor_name)], True)

class GeodBalanceDataUpdateCoordinator(DataUpdateCoordinator):
    """DataUpdateCoordinator to manage fetching GEOD balance."""

    def __init__(self, hass, wallet_address, api_key):
        """Initialize the coordinator."""
        self.wallet_address = wallet_address
        self.api_key = api_key
        super().__init__(
            hass,
            _LOGGER,
            name="GEOD Balance Data",
            update_interval=timedelta(hours=1),  # Update every hour
        )

    async def _async_update_data(self):
        """Fetch data from Polygonscan API."""
        params = {
            "module": "account",
            "action": "tokenbalance",
            "contractaddress": GEOD_CONTRACT_ADDRESS,
            "address": self.wallet_address,
            "tag": "latest",
            "apikey": self.api_key,
        }

        try:
            session = async_get_clientsession(self.hass)
            async with session.get(POLYGONSCAN_API_URL, params=params, timeout=10) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching data: HTTP {response.status}")
                data = await response.json()

                if data.get("status") != "1":
                    raise UpdateFailed(f"Error fetching balance: {data.get('message')}")

                balance = int(data["result"]) / (10 ** 18)  # Assuming GEOD has 18 decimals
                return round(balance, 6)

        except Exception as e:
            _LOGGER.error("Error fetching GEOD balance: %s", e)
            raise UpdateFailed(f"Error fetching GEOD balance: {e}")

class GeodBalanceSensor(Entity):
    """Representation of a GEOD Balance Sensor."""

    def __init__(self, coordinator, name):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._name = name
        self._state = None
        self._unit_of_measurement = "GEOD"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data if self.coordinator.data is not None else STATE_UNKNOWN

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{DOMAIN}_{self.coordinator.wallet_address}"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.wallet_address)},
            "name": self._name,
            "manufacturer": "YourNameOrCompany",
        }

    async def async_added_to_hass(self):
        """Register update listener."""
        self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Unregister update listener."""
        self.coordinator.async_remove_listener(self.async_write_ha_state)
