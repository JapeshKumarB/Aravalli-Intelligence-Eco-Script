# Aravalli Intelligence – Ecological Anomaly Detection

## Overview

Aravalli Intelligence is a proof-of-concept system that detects ecological degradation using a dual-signal approach:

* **NDVI (Vegetation Index)** – to monitor vegetation trends
* **VIIRS Nightlight Data** – to monitor human activity

The system identifies statistical anomalies using **Z-score filtering** and groups high-risk regions using **DBSCAN spatial clustering**.
Results are visualized through an interactive **Streamlit dashboard**.

## Project Structure

```
GEE_pixel_process.py      → Extract pixel data of NDVI & NightLight
GEE_data_process.py       → Extract raw data values of NDVI & NightLight 
combined.csv              → Processed dataset
combined_top_pixels.csv   → Filtered anomaly dataset
app.py                    → Streamlit dashboard
anomaly_map_integration.py → Spatial clustering & map visualization
```

Preprocessed CSV files are used in the deployed dashboard for smooth execution.

---

## Setup Instructions (Local Run)

### 1️. Clone the Repository

```bash
git clone https://github.com/JapeshKumarB/Aravalli-Intelligence-Eco-Script.git
cd Aravalli-Intelligence-Eco-Script
```

### 2️. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️. Run the Application

```bash
streamlit run app.py
```

The dashboard will open in your browser.

---

## Notes

* Google Earth Engine scripts are included for data extraction.
* The deployed version uses preprocessed datasets for stability and ease of testing.
* To run the data extraction scripts (GEE_pixel_process.py, GEE_data_process.py), create a Google Earth Engine account, enable the Earth Engine API, install the required package using:

```bash
pip install earthengine-api
earthengine authenticate
```

After authentication, the extraction scripts can be executed locally.

---

