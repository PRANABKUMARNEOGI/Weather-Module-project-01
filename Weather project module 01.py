import datetime
import requests
import pandas as pd


def get_coordinates(city_name):
    """Fetch latitude and longitude for a given city name using Geocoding API."""
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"

    try:
        response = requests.get(geo_url)
        response.raise_for_status()
        data = response.json()

        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            return {
                "lat": result["latitude"],
                "lon": result["longitude"],
                "name": result["name"],
                "country": result["country"],
            }
        else:
            print(f"❌ City '{city_name}' not found.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to Geocoding API: {e}")
        return None


def get_weather_forecast(lat, lon):
    """Fetch 3-day weather forecast using latitude and longitude."""
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&"
        f"daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode&"
        f"timezone=auto&forecast_days=3"
    )

    try:
        response = requests.get(weather_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to Weather API: {e}")
        return None


def interpret_weather_code(code):
    """Translate WMO Weather Interpretation Codes into human-readable text."""
    # Source: WMO Code Table 4677
    codes = {
        0: "Clear sky ☀️",
        1: "Mainly clear 🌤️",
        2: "Partly cloudy ⛅",
        3: "Overcast ☁️",
        45: "Foggy 🌫️",
        48: "Depositing rime fog 🌫️",
        51: "Light drizzle 🌧️",
        53: "Moderate drizzle 🌧️",
        55: "Dense drizzle 🌧️",
        61: "Slight rain 🌧️",
        63: "Moderate rain 🌧️",
        65: "Heavy rain 🌧️",
        71: "Slight snow fall ❄️",
        73: "Moderate snow fall ❄️",
        75: "Heavy snow fall ❄️",
        95: "Thunderstorm ⛈️",
    }
    return codes.get(code, "Unknown Weather Condition 🤔")


def main():
    print("=" * 45)
    print("       🌦️  3-DAY WEATHER PREDICTOR  🌦️       ")
    print("=" * 45)

    city = input("Enter the city name (e.g., London, Tokyo, New York): ").strip()
    if not city:
        print("City name cannot be empty!")
        return

    print(f"\n🔍 Searching for {city}...")
    location_data = get_coordinates(city)

    if location_data:
        print(
            f"📍 Found: {location_data['name']}, {location_data['country']} ({location_data['lat']}, {location_data['lon']})"
        )
        print("⏳ Fetching live forecast data...")

        forecast = get_weather_forecast(location_data["lat"], location_data["lon"])

        if forecast and "daily" in forecast:
            daily_data = forecast["daily"]

            # Structure data for Pandas DataFrame
            forecast_list = []
            for i in range(len(daily_data["time"])):
                # Format raw date string to a nicer weekday string
                date_obj = datetime.datetime.strptime(
                    daily_data["time"][i], "%Y-%m-%d"
                )
                day_name = date_obj.strftime("%A (%b %d)")

                forecast_list.append(
                    {
                        "Day": day_name,
                        "Max Temp (°C)": daily_data["temperature_2m_max"][i],
                        "Min Temp (°C)": daily_data["temperature_2m_min"][i],
                        "Rain Prob. (%)": daily_data[
                            "precipitation_probability_max"
                        ][i],
                        "Condition": interpret_weather_code(
                            daily_data["weathercode"][i]
                        ),
                    }
                )

            # Display via Pandas Table
            df = pd.DataFrame(forecast_list)
            print("\n" + "=" * 65)
            print(f"🔮 WEATHER PREDICTION FOR: {location_data['name'].upper()}")
            print("=" * 65)
            print(df.to_string(index=False))
            print("=" * 65)
        else:
            print("❌ Failed to parse forecast data.")


if __name__ == "__main__":
    main()
