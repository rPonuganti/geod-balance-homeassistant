# GEOD Balance for Home Assistant

This custom integration for Home Assistant allows you to monitor the GEOD token balance of a Polygon wallet address using the Polygonscan API.

## About this fork
This is a fork of the original project to fix an issue that wasn't addressed due to inactivity. 
I’ve made the necessary changes for my use case and will try to maintain this fork as needed. Thanks to the original author for their great work!

## Features

- Fetches GEOD token balance for a specified Polygon wallet address
- Updates balance every hour
- Configurable through the Home Assistant UI

## Installation

### HACS (Recommended)

1. Ensure that [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. In the HACS panel, go to "Integrations" and click the "+" button.
3. Search for "GEOD Balance" and install it.
4. Restart Home Assistant.

### Manual Installation

1. Download the `geod_balance` folder from this repository.
2. Copy the folder to your `custom_components` directory in your Home Assistant configuration directory.
3. Restart Home Assistant.

## Configuration

1. In the Home Assistant UI, go to "Configuration" > "Integrations".
2. Click the "+" button to add a new integration.
3. Search for "GEOD Balance" and select it.
4. Enter the required information:
   - Wallet Address: Your Polygon wallet address
   - Nickname: A name for this wallet (used in the sensor name)
   - API Key: Your Polygonscan API key

## Usage

After configuration, a new sensor will be created with the following attributes:

- State: Current GEOD token balance
- Unit of Measurement: GEOD

The sensor name will be in the format: `{nickname}_geod_balance`

## Troubleshooting

- Ensure your Polygon wallet address is correct and contains GEOD tokens.
- Verify that your Polygonscan API key is valid and has the necessary permissions.
- Check the Home Assistant logs for any error messages related to the integration.

## Support

If you encounter any issues or have feature requests, please open an issue on the GitHub repository.

## License

This project is licensed under the MIT License.