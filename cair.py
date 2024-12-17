import streamlit as st
import requests
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Streamlit App Title
st.title("🌆 City Air Quality Analysis Tool")

# Input city name
city = st.text_input("🏙️ Enter the name of an Indian city (e.g., Hyderabad):")

# Define the AQICN API Token
WAQI_API_TOKEN = "8cdb6ac240ad8b485494d18e6948ffdf4bc4294b"
WAQI_API_BASE_URL = "https://api.waqi.info/feed"

# Function to fetch air quality data
def fetch_air_quality(city_name):
    try:
        url = f"{WAQI_API_BASE_URL}/{city_name}/?token={WAQI_API_TOKEN}"
        response = requests.get(url)
        data = response.json()
        if data["status"] == "ok":
            return data["data"]
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Function to create a beautified heatmap with stronger colors
def plot_heatmap(pollutants):
    # Convert pollutants data to a format that seaborn can understand
    pollutant_names = {
        "co": "Carbon Monoxide (CO)",
        "h": "Humidity (H)",
        "no2": "Nitrogen Dioxide (NO₂)",
        "o3": "Ozone (O₃)",
        "p": "Pressure (P)",
        "pm10": "Particulate Matter <10µm (PM₁₀)",
        "pm25": "Particulate Matter <2.5µm (PM₂.₅)",
        "so2": "Sulfur Dioxide (SO₂)",
        "t": "Temperature (T)",
        "w": "Wind Speed (W)",
        "wg": "Wind Gust (WG)"
    }

    # Prepare the data for the heatmap
    heatmap_data = {}
    for pollutant, value in pollutants.items():
        pollutant_name = pollutant_names.get(pollutant, pollutant.upper())
        heatmap_data[pollutant_name] = value.get('v', 0)  # Default to 0 if data missing

    # Convert to a DataFrame for heatmap plotting
    df = pd.DataFrame(list(heatmap_data.items()), columns=['Pollutant', 'Value'])
    df.set_index('Pollutant', inplace=True)

    # Create the heatmap with a stronger red color palette
    plt.figure(figsize=(7, 7))
    sns.set(font_scale=1.2)  # Adjust font size globally for readability
    ax = sns.heatmap(df.T, annot=True, fmt="g", cmap='Reds', cbar=True, annot_kws={'size': 12}, linewidths=0.5)

    # Add title and adjust padding
    ax.set_title('Air Quality Heatmap', fontsize=16, weight='bold', pad=20)
    plt.yticks(rotation=0)
    plt.xticks(rotation=45, ha='right')

    # Adjust layout for better spacing
    plt.tight_layout()
    st.pyplot(plt)

# Function to suggest precautions based on AQI
def suggest_precautions(aqi):
    if aqi <= 50:
        precautions = "✔️ Air quality is good. You can go about your daily activities without any concerns."
    elif aqi <= 100:
        precautions = "⚠️ Air quality is moderate. Sensitive individuals may experience minor health effects. Consider limiting outdoor activities if you have respiratory issues."
    elif aqi <= 150:
        precautions = "⚠️ Air quality is unhealthy for sensitive groups. Children, elderly, and individuals with respiratory or heart conditions should limit prolonged outdoor activities."
    elif aqi <= 200:
        precautions = "🚨 Air quality is unhealthy. Everyone may begin to experience health effects. Limit outdoor activities, especially for sensitive individuals."
    elif aqi <= 300:
        precautions = "🚨 Air quality is very unhealthy. Health alerts are issued, and everyone may experience more serious health effects. Avoid outdoor activities."
    else:
        precautions = "☠️ Air quality is hazardous. Emergency health conditions are likely. Avoid all outdoor activities and take immediate action to reduce exposure."
    return precautions

# Display the results
if st.button("Get Air Quality Analysis"):
    if city:
        with st.spinner("Fetching air quality data..."):
            air_quality_data = fetch_air_quality(city)
            if air_quality_data:
                st.success(f"Air Quality Data for **{city.capitalize()}**:")

                # Display main AQI index
                aqi = air_quality_data.get("aqi", "N/A")
                st.markdown(f"### 🌍 **Air Quality Index (AQI): {aqi}**")

                # Suggest precautions based on AQI
                precautions = suggest_precautions(aqi)
                st.markdown(f"### 🚨 **Precautions**:\n{precautions}")

                # Show specific pollutant levels
                pollutants = air_quality_data.get("iaqi", {})
                pollutant_names = {
                    "co": "Carbon Monoxide (CO)",
                    "h": "Humidity (H)",
                    "no2": "Nitrogen Dioxide (NO₂)",
                    "o3": "Ozone (O₃)",
                    "p": "Pressure (P)",
                    "pm10": "Particulate Matter <10µm (PM₁₀)",
                    "pm25": "Particulate Matter <2.5µm (PM₂.₅)",
                    "so2": "Sulfur Dioxide (SO₂)",
                    "t": "Temperature (T)",
                    "w": "Wind Speed (W)",
                    "wg": "Wind Gust (WG)"
                }

                st.markdown("### 🔬 **Pollutant Levels**")
                for pollutant, value in pollutants.items():
                    pollutant_name = pollutant_names.get(pollutant, pollutant.upper())
                    st.markdown(f"- **{pollutant_name}:** {value.get('v', 'N/A')}")

                # Additional info (if available)
                city_info = air_quality_data.get("city", {}).get("name", "N/A")
                st.markdown(f"### 📍 **City Info:** {city_info}")

                if "time" in air_quality_data:
                    time_info = air_quality_data["time"].get("s", "N/A")
                    st.markdown(f"### 🕒 **Data Last Updated:** {time_info}")

                # Plot heatmap
                st.markdown("### 🔥 **Air Quality Heatmap**")
                plot_heatmap(pollutants)

            else:
                st.error("Could not fetch air quality data. Please try another city.")
    else:
        st.error("Please enter a valid city name.")
