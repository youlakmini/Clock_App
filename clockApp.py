import flet as ft
import requests
from datetime import datetime
import pytz
import asyncio

# Colours
COLOR_BG = "#1E1E1E"  # Dark background
COLOR_WHITE = "#E0E0E0"  # Light text
COLOR_PRIMARY = "#4CAF50"  # Green for accents
COLOR_SECONDARY = "#757575"  # Grey text

tz_global = None
city_global = None


async def update_clock(label_time, label_info, page):
    global tz_global, city_global

    while True:
        now = datetime.now(tz_global) if tz_global else datetime.now()
        label_time.value = now.strftime("%H:%M:%S")
        label_info.value = f"Time in {city_global}" if city_global else now.strftime("%A, %d %B %Y")

        page.update()  # ✅ Removed 'await'

        await asyncio.sleep(1)


def update_weather(e, city_input, weather_label, label_time, label_info, page):
    global tz_global, city_global
    city = city_input.value.strip()

    if not city:
        weather_label.value = "Enter a city name"
        tz_global, city_global = None, None
        page.update()
        return

    api_key = "eaf3be9013975089f1d247ce43a8176e"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            weather_label.value = f"{temp}°C {description.capitalize()}"

            # Set timezone
            offset = data["timezone"] / 3600
            tz_global = pytz.FixedOffset(offset * 60)
            city_global = city.capitalize()
        else:
            weather_label.value = "City not found"
            tz_global, city_global = None, None

    except requests.exceptions.RequestException:
        weather_label.value = "Network error!!!"
        tz_global, city_global = None, None

    page.update()


async def main(page: ft.Page):
    page.title = "Digital Clock"
    page.window_width = 400
    page.window_height = 520
    page.bgcolor = COLOR_BG
    page.window_resizable = False
    #page.window_maximized = False

    title_label = ft.Text("Digital Clock", size=26, weight="bold", color=COLOR_PRIMARY)
    label_time = ft.Text("00:00:00", size=50, weight="bold", color=COLOR_WHITE)
    label_info = ft.Text("", size=26, color=COLOR_WHITE)

    city_input = ft.TextField(
        label="Enter city name",
        text_align="center",
        bgcolor="#333333",
        color=COLOR_WHITE,
        border_radius=8,
    )
    weather_label = ft.Text("", size=16, color=COLOR_WHITE)

    update_button = ft.ElevatedButton(
        "Update Weather",
        icon=ft.Icons.SEARCH,
        bgcolor=COLOR_PRIMARY,
        color=COLOR_WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=lambda e: update_weather(e, city_input, weather_label, label_time, label_info, page),
    )

    container = ft.Container(
        ft.Column(
            [
                ft.Icon(name=ft.Icons.ACCESS_TIME, size=50, color=COLOR_PRIMARY),
                title_label,
                label_time,
                label_info,
                city_input,
                update_button,
                ft.Icon(name=ft.Icons.WB_SUNNY, size=40, color=COLOR_PRIMARY),
                weather_label,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        ),
        padding=120,
        border_radius=20,
        bgcolor="#2C2C2C",
    )

    page.add(container)
    asyncio.create_task(update_clock(label_time, label_info, page))  # ✅ Starts the clock updater


ft.app(target=main)
