import sys
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                            QPushButton, QVBoxLayout, QHBoxLayout, 
                            QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon
from dotenv import load_dotenv
import os

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("download.png"))
        self.input = QLineEdit(self)
        self.temperature = QLabel(self)
        self.button = QPushButton("Get Weather", self)
        self.emoji = QLabel(self)
        self.description = QLabel(self)
        self.feels_like = QLabel(self)
        self.humidity = QLabel(self)
        self.wind = QLabel(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Weather App")
        self.setMinimumSize(400, 600)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        header = QLabel("Weather Forecast")
        header_font = QFont("Arial", 24, QFont.Bold)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #2c3e50;")
        
        search_layout = QHBoxLayout()
        self.input.setPlaceholderText("Enter city name...")
        self.input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 16px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 20px;
                font-size: 16px;
                border-radius: 5px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1a5276;
            }
        """)
        
        search_layout.addWidget(self.input)
        search_layout.addWidget(self.button)
        
        weather_display = QFrame()
        weather_display.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        weather_layout = QVBoxLayout(weather_display)
        weather_layout.setAlignment(Qt.AlignCenter)
        weather_layout.setSpacing(15)

        self.temperature.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.temperature.setAlignment(Qt.AlignCenter)
        self.temperature.setStyleSheet("""
            QLabel {
                font-size: 72px;
                color: #2c3e50;
                font-weight: bold;
            }
        """)

        self.emoji.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.emoji.setAlignment(Qt.AlignCenter)
        self.emoji.setMinimumHeight(100)
        self.emoji.setStyleSheet("""
            QLabel {
                font-size: 100px;
            }
        """)

        self.description.setWordWrap(True)
        self.description.setAlignment(Qt.AlignCenter)
        self.description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.description.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #7f8c8d;
                font-weight: bold;
            }
        """)
        
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background-color: #e9ecef;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        details_layout = QVBoxLayout(details_frame)
        details_layout.setSpacing(10)

        for label in [self.feels_like, self.humidity, self.wind]:
            label.setWordWrap(True)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            label.setStyleSheet("font-size: 16px; color: #34495e;")
        
        details_layout.addWidget(self.feels_like)
        details_layout.addWidget(self.humidity)
        details_layout.addWidget(self.wind)
        
        weather_layout.addWidget(self.emoji, 0, Qt.AlignCenter)
        weather_layout.addWidget(self.temperature, 0, Qt.AlignCenter)
        weather_layout.addWidget(self.description, 0, Qt.AlignCenter)
        weather_layout.addWidget(details_frame)
        
        main_layout.addWidget(header)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(weather_display)
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.setLayout(main_layout)
        self.button.clicked.connect(self.get_data)
    
    def get_data(self):
        load_dotenv(".env")
        api_key = os.getenv("API_KEY")
        city = self.input.text()
        if not city:
            self.display_error("Please enter a city name")
            return
            
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data["cod"] == 200:
                self.display(data)
    
        except requests.exceptions.HTTPError as http_error:
            match response.status_code:
                case 400:
                    self.display_error("Bad Request\nPlease check your input")
                case 401:
                    self.display_error("Invalid API key")
                case 403:
                    self.display_error("Access denied")
                case 404:
                    self.display_error("City not found")
                case 500:
                    self.display_error("Server error")
                case 502:
                    self.display_error("Bad Gateway")
                case 503:
                    self.display_error("Service Unavailable")
                case 504:
                    self.display_error("Timeout")
                case _:
                    self.display_error(f"Error: {http_error}")
        
        except requests.exceptions.ConnectionError:
            self.display_error("No internet connection")

        except requests.exceptions.Timeout:
            self.display_error("Request timed out")

        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many redirects")

        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Error: {req_error}")

    def display_error(self, message):
        self.temperature.setStyleSheet("""
            font-size: 24px;
            color: #e74c3c;
            font-weight: bold;
        """)
        self.temperature.setText(message)
        self.temperature.adjustSize()
        self.emoji.clear()
        self.description.clear()
        self.feels_like.clear()
        self.humidity.clear()
        self.wind.clear()

    def display(self, data):
        desc = data['weather'][0]['description'].capitalize()
        temp_k = data['main']['temp']
        temp_c = temp_k - 273.15
        feels_like = data['main']['feels_like'] - 273.15
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        
        self.temperature.setStyleSheet("""
            font-size: 72px;
            color: #2c3e50;
            font-weight: bold;
        """)
        self.temperature.setText(f"{temp_c:.1f}°C")
        self.temperature.adjustSize()
        self.description.setText(desc)
        self.description.adjustSize()
        self.feels_like.setText(f"🌡 Feels like: {feels_like:.1f}°C")
        self.feels_like.adjustSize()
        self.humidity.setText(f"💦 Humidity: {humidity}%")
        self.humidity.adjustSize()
        self.wind.setText(f"🌬️ Wind: {wind_speed} m/s")
        self.wind.adjustSize()
        
        weather_id = data['weather'][0]['id']
        self.emoji.setText(self.get_emoji(weather_id))
        self.emoji.adjustSize()
    
    @staticmethod
    def get_emoji(weather_id):
        if 200 <= weather_id <= 232:
            return "🌩️"
        elif 300 <= weather_id <= 321:
            return "🌦️"
        elif 500 <= weather_id <= 531:
            return "🌧️"
        elif 600 <= weather_id <= 622:
            return "❄️"
        elif 701 <= weather_id <= 781:
            return "🌫️"
        elif weather_id == 800:
            return "☀️"
        elif 801 <= weather_id <= 804:
            return "☁️"
        else:
            return "🌈"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
