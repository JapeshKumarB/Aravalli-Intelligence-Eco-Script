import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Aravalli AI Dashboard", layout="wide")
st.title("🌍 Aravalli AI: Threat Detection Dashboard")

# Sidebar

st.sidebar.header("⚙️ Detection Settings")

dataset_choice = st.sidebar.selectbox(
    "Select Dataset",
    ["All Years", "2023", "2024", "2025", "2026", "2027", "2028"]
)

WINDOW_SIZE = st.sidebar.slider("Trend Window Size", 3, 12, 6)

NDVI_THRESH = st.sidebar.slider(
    "NDVI Loss Threshold (Z-score)",
    -3.0, 0.0, -1.2, 0.1
)

LIGHT_THRESH = st.sidebar.slider(
    "Light Activity Threshold (Z-score)",
    0.0, 3.0, 1.2, 0.1
)

# Load correct dataset

if dataset_choice == "All Years":
    file_path = "combined.csv"
else:
    file_path = f"{dataset_choice}.csv"

if not os.path.exists(file_path):
    st.warning(f"No data available for {dataset_choice}.")
    st.stop()

df = pd.read_csv(file_path)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

# Brain logic

def calculate_slope(signal):
    if len(signal) < WINDOW_SIZE:
        return np.nan
    y = np.array(signal).reshape(-1, 1)
    x = np.arange(len(y)).reshape(-1, 1)
    model = LinearRegression().fit(x, y)
    return model.coef_[0][0]

df['ndvi_slope'] = df['NDVI'].rolling(window=WINDOW_SIZE).apply(calculate_slope)
df['light_volatility'] = df['Light'].rolling(window=WINDOW_SIZE).std()

valid = df.dropna().copy()

# Baseline statistics

mu_ndvi = valid['ndvi_slope'].mean()
sigma_ndvi = valid['ndvi_slope'].std()
mu_light = valid['light_volatility'].mean()
sigma_light = valid['light_volatility'].std()

valid['z_ndvi'] = (valid['ndvi_slope'] - mu_ndvi) / sigma_ndvi
valid['z_light'] = (valid['light_volatility'] - mu_light) / sigma_light

valid['is_anomaly'] = (
    (valid['z_ndvi'] < NDVI_THRESH) &
    (valid['z_light'] > LIGHT_THRESH)
)

anomalies = valid[valid['is_anomaly']]

# Plot (Professional style)

st.subheader("📈 Intelligence Graph")

fig, ax1 = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor("#f4f4f4")
ax1.set_facecolor("#f4f4f4")

# NDVI line

ax1.plot(
    valid['date'],
    valid['z_ndvi'],
    color="green",
    marker='o',
    linewidth=2,
    label="NDVI Trend (Z)"
)

ax1.axhline(
    NDVI_THRESH,
    color="green",
    linestyle='--',
    label=f"Loss Threshold ({NDVI_THRESH:.1f}σ)"
)

# Light line

ax2 = ax1.twinx()
ax2.plot(
    valid['date'],
    valid['z_light'],
    color="orange",
    marker='s',
    linestyle=':',
    linewidth=2,
    label="Light Activity (Z)"
)

ax2.axhline(
    LIGHT_THRESH,
    color="orange",
    linestyle='--',
    label=f"Activity Threshold (+{LIGHT_THRESH:.1f}σ)"
)

# Anomaly points

if not anomalies.empty:
    ax1.scatter(
        anomalies['date'],
        anomalies['z_ndvi'],
        color='red',
        s=200,
        label="CRITICAL ANOMALY",
        zorder=5
    )

# Labels

ax1.set_xlabel("Timeline")
ax1.set_ylabel("Vegetation Vitality Index (Z-score)", color="green")
ax2.set_ylabel("Human Activity Intensity (Z-score)", color="orange")

plt.title("Aravalli Intelligence: Unsupervised Threat Detection Dashboard")

# Combined legend

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

st.pyplot(fig)


# SYSTEM REPORT

st.subheader("🧠 System Intelligence Report")

st.text("""
[SYSTEM] Loading Sensor Data...
[SYSTEM] Calculating Signal Trends (dy/dx) and Volatility (sigma)...
[SYSTEM] Generating Visual Dashboard...
""")

st.markdown("### ARAVALLI AI: SENSOR CALIBRATION (NORMAL STATE)")

st.write(f"🌿 Baseline Vegetation Trend (Mean μ): {mu_ndvi:.6f}")
st.write(f"📏 Vegetation 'Wiggle' Room (Sigma σ): {sigma_ndvi:.6f}")
st.write(f"💡 Baseline Human Activity (Mean μ): {mu_light:.6f}")
st.write(f"📏 Human Activity 'Wiggle' (Sigma σ): {sigma_light:.6f}")

st.markdown("### ARAVALLI AI: THREAT DETECTION VERDICT")

if anomalies.empty:
    st.success("No critical anomalies detected.")
else:
    for _, row in anomalies.iterrows():
        ndvi_intensity = abs(row['z_ndvi'])
        light_intensity = abs(row['z_light'])

        st.error(f"🔴 ALERT TRIGGERED: {row['date'].date()}")

        st.write(
            f"▶ Vegetation Loss Speed: {abs(row['ndvi_slope']):.4f} NDVI units/month"
        )
        st.write(
            f"▶ Vegetation anomaly intensity: {ndvi_intensity:.2f}σ"
        )

        st.write(
            f"▶ Human activity volatility: {abs(row['light_volatility']):.4f} Light units/month"
        )
        st.write(
            f"▶ Human activity anomaly intensity: {light_intensity:.2f}σ"
        )

        st.markdown("---")

# Data table

st.subheader("📊 Processed Data")
st.dataframe(valid)

# Spatial Drill Down Map

import streamlit.components.v1 as components
import anomaly_map_integration as map_module  # combined GeoPandas+Folium module

if not anomalies.empty:
    latest_anomaly = anomalies.iloc[-1]
    year = latest_anomaly['year']
    month = latest_anomaly['month']

    st.subheader("🗺 Spatial Drill-Down Map")

    # Generate interactive map
    
    folium_map = map_module.generate_anomaly_map(year, month)

    if folium_map:
        # Embed Folium map as HTML
        components.html(folium_map._repr_html_(), height=600)
    else:
        st.warning("No pixel data available for this anomaly month.")
else:
    st.info("No anomalies found yet.")