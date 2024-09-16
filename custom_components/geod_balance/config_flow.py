# config_flow.py

import logging
import requests
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_NAME
from homeassistant.core import callback

from .const import DOMAIN, CONF_WALLET_ADDRESS, CONF_NICKNAME, POLYGONSCAN_API_URL, GEOD_CONTRACT_ADDRESS

_LOGGER = logging.getLogger(__name__)

class GeodBalanceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GEOD Balance."""

    VERSION = 2
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step of the config flow."""
        errors = {}

        if user_input is not None:
            wallet_address = user_input.get(CONF_WALLET_ADDRESS)
            nickname = user_input.get(CONF_NICKNAME)
            api_key = user_input.get(CONF_API_KEY)

            # Validate the provided inputs
            if not self._is_valid_polygon_address(wallet_address):
                errors["base"] = "invalid_wallet_address"
            else:
                # Attempt to validate the API key by making a test API call
                if not await self._validate_api_key(api_key, wallet_address):
                    errors["base"] = "invalid_api_key"

            if not errors:
                return self.async_create_entry(
                    title=nickname,
                    data={
                        CONF_WALLET_ADDRESS: wallet_address,
                        CONF_NICKNAME: nickname,
                        CONF_API_KEY: api_key,
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_WALLET_ADDRESS): str,
                vol.Required(CONF_NICKNAME): str,
                vol.Required(CONF_API_KEY): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    def _is_valid_polygon_address(self, address):
        """Validate the Polygon wallet address format."""
        if address.startswith("0x") and len(address) == 42:
            return True
        return False

    async def _validate_api_key(self, api_key, wallet_address):
        """Validate the provided Polygonscan API key by making a test API call."""
        params = {
            "module": "account",
            "action": "balance",
            "address": wallet_address,
            "tag": "latest",
            "apikey": api_key,
        }

        try:
            session = self.hass.helpers.aiohttp_client.async_get_clientsession()
            async with session.get(POLYGONSCAN_API_URL, params=params, timeout=10) as response:
                data = await response.json()

                if data.get("status") == "1":
                    return True
                else:
                    _LOGGER.error("Polygonscan API Key validation failed: %s", data.get("message"))
                    return False

        except (requests.RequestException, asyncio.TimeoutError) as e:
            _LOGGER.error("Error validating Polygonscan API Key: %s", e)
            return False

    async def async_step_import(self, user_input):
        """Handle configuration by YAML import (if applicable)."""
        return await self.async_step_user(user_input)
