import logging
import time
import requests
import json
import os
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK

class TeslaStockPrice(plugins.Plugin):
    __author__ = 'https://github.com/ATOMNFT'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'Displays the current Tesla stock price in USD using AlphaVantage API (Refreshes every 2hrs)'

    PRICE_FILE = 'tesla_price.json'  # Path to save the price
    API_URL = "https://www.alphavantage.co/query"
    SYMBOL = "TSLA"  # Tesla stock symbol
    API_KEY = "YOUR_API_KEY"  # Replace with your actual API key

    def on_loaded(self):
        logging.info("TeslaStockPrice plugin loaded.")
        self.last_update = 0  # Track the last update time
        self.price = self.load_price()  # Load price from file

    def load_price(self):
        """Load the Tesla stock price from a file."""
        if os.path.exists(self.PRICE_FILE):
            with open(self.PRICE_FILE, 'r') as f:
                try:
                    data = json.load(f)
                    return data.get('price', 'Loading...')
                except json.JSONDecodeError:
                    logging.error("Failed to decode JSON from price file.")
        return 'Loading...'

    def save_price(self, price):
        """Save the Tesla stock price to a file."""
        with open(self.PRICE_FILE, 'w') as f:
            json.dump({'price': price}, f)

    def on_ui_setup(self, ui):
        # Position the text based on your screen type or set custom position
        position = (10, 100)  # Adjust x, y for your screen layout
        ui.add_element(
            'tesla_price',
            LabeledValue(
                color=BLACK,
                label='TSLA: $',
                value=self.price,  # Use loaded price here
                position=position,
                label_font=fonts.Small,
                text_font=fonts.Small,
            )
        )

    def on_ui_update(self, ui):
        current_time = time.time()
        # Check if 2hrs have passed since the last update
        if current_time - self.last_update >= 7200:  # 2 hours in seconds
            try:
                # Fetch current Tesla stock price from Alpha Vantage API
                response = requests.get(
                    self.API_URL,
                    params={
                        "function": "TIME_SERIES_DAILY",
                        "symbol": self.SYMBOL,
                        "apikey": self.API_KEY,
                    }
                )
                data = response.json()
                time_series = data.get("Time Series (Daily)")
                if time_series:
                    # Get the latest trading day data
                    latest_date = max(time_series.keys())
                    latest_data = time_series[latest_date]
                    price = latest_data["4. close"]  # Closing price for the latest day
                    price = f"{float(price):.2f}"  # Format price to two decimal places
                else:
                    price = "N/A"  # Handle missing data
                ui.set('tesla_price', price)
                logging.info(f"Updated Tesla stock price: {price}")
                self.save_price(price)  # Save the price to file
                self.last_update = current_time  # Update the last fetch time
            except Exception as e:
                logging.error(f"Failed to fetch Tesla stock price: {e}")
