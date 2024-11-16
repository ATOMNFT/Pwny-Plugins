import logging
import time
import requests
import json
import os
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK

class DogecoinPrice(plugins.Plugin):
    __author__ = 'https://github.com/ATOMNFT'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Displays the current Dogecoin price in USD'
    
    PRICE_FILE = 'dogecoin_price.json'  # Path to save the price

    def on_loaded(self):
        logging.info("DogecoinPrice plugin loaded.")
        self.last_update = 0  # Track the last update time
        self.price = self.load_price()  # Load price from file

    def load_price(self):
        """Load the Dogecoin price from a file."""
        if os.path.exists(self.PRICE_FILE):
            with open(self.PRICE_FILE, 'r') as f:
                try:
                    data = json.load(f)
                    return data.get('price', 'Loading...')
                except json.JSONDecodeError:
                    logging.error("Failed to decode JSON from price file.")
        return 'Loading...'

    def save_price(self, price):
        """Save the Dogecoin price to a file."""
        with open(self.PRICE_FILE, 'w') as f:
            json.dump({'price': price}, f)

    def on_ui_setup(self, ui):
        # Position the text based on your screen type or set custom position
        position = (10, 100)  # Adjust x, y for your screen layout
        ui.add_element(
            'dogecoin_price',
            LabeledValue(
                color=BLACK,
                label='DOGE: $',
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
                # Fetch current Dogecoin price from CoinGecko API
                response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=dogecoin&vs_currencies=usd")
                data = response.json()
                price = data['dogecoin']['usd']
                formatted_price = f"{price:,.4f}"  # Format price to 4 decimal places for small values
                ui.set('dogecoin_price', formatted_price)
                logging.info(f"Updated Dogecoin price: {formatted_price}")
                self.save_price(formatted_price)  # Save the price to file
                self.last_update = current_time  # Update the last fetch time
            except Exception as e:
                logging.error(f"Failed to fetch Dogecoin price: {e}")
