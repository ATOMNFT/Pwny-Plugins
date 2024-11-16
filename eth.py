import logging
import time
import requests
import json
import os
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK

class EthereumPrice(plugins.Plugin):
    __author__ = 'https://github.com/ATOMNFT'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Displays the current Ethereum price in USD'
    
    PRICE_FILE = 'ethereum_price.json'  # Path to save the price

    def on_loaded(self):
        logging.info("EthereumPrice plugin loaded.")
        self.last_update = 0  # Track the last update time
        self.price = self.load_price()  # Load price from file

    def load_price(self):
        """Load the Ethereum price from a file."""
        if os.path.exists(self.PRICE_FILE):
            with open(self.PRICE_FILE, 'r') as f:
                try:
                    data = json.load(f)
                    return data.get('price', 'Loading...')
                except json.JSONDecodeError:
                    logging.error("Failed to decode JSON from price file.")
        return 'Loading...'

    def save_price(self, price):
        """Save the Ethereum price to a file."""
        with open(self.PRICE_FILE, 'w') as f:
            json.dump({'price': price}, f)

    def on_ui_setup(self, ui):
        # Position the text based on your screen type or set custom position
        position = (10, 100)  # Adjust x, y for your screen layout
        ui.add_element(
            'ethereum_price',
            LabeledValue(
                color=BLACK,
                label='ETH: $',
                value=self.price,  # Use loaded price here
                position=position,
                label_font=fonts.Small,
                text_font=fonts.Small,
            )
        )

    def on_ui_update(self, ui):
        current_time = time.time()
        # Check if 30 seconds have passed since the last update
        if current_time - self.last_update >= 30:
            try:
                # Fetch current Ethereum price from CoinGecko API
                response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd")
                data = response.json()
                price = data['ethereum']['usd']
                formatted_price = f"{price:,.2f}"  # Format price to 2 decimal places
                ui.set('ethereum_price', formatted_price)
                logging.info(f"Updated Ethereum price: {formatted_price}")
                self.save_price(formatted_price)  # Save the price to file
                self.last_update = current_time  # Update the last fetch time
            except Exception as e:
                logging.error(f"Failed to fetch Ethereum price: {e}")
