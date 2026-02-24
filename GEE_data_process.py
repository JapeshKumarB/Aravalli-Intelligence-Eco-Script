import ee
import pandas as pd
from datetime import datetime

# Initialize Earth Engine
ee.Initialize(project='eco-script')

# Define ROI
roi_coords = [76.2, 27.0, 76.5, 27.3]
roi = ee.Geometry.Rectangle(roi_coords)

start_date = '2023-01-01'
end_date = datetime.today().strftime('%Y-%m-%d')


# NDVI COLLECTION

s2 = (
    ee.ImageCollection("COPERNICUS/S2_SR")
    .filterBounds(roi)
    .filterDate(start_date, end_date)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
)

def add_ndvi(image):
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return image.addBands(ndvi)

ndvi_collection = s2.map(add_ndvi).select('NDVI')

# Convert to monthly NDVI
def monthly_ndvi(year, month):
    start = ee.Date.fromYMD(year, month, 1)
    end = start.advance(1, 'month')
    
    monthly = ndvi_collection.filterDate(start, end).mean()
    
    mean_dict = monthly.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=roi,
        scale=30,
        bestEffort=True
    )
    
    return ee.Feature(None, {
        'year': year,
        'month': month,
        'NDVI': mean_dict.get('NDVI')
    })


# VIIRS COLLECTION

viirs = (
    ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG")
    .filterBounds(roi)
    .filterDate(start_date, end_date)
)

def monthly_light(year, month):
    start = ee.Date.fromYMD(year, month, 1)
    end = start.advance(1, 'month')
    
    monthly = viirs.filterDate(start, end).mean()
    
    mean_dict = monthly.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=roi,
        scale=500,
        bestEffort=True
    )
    
    return ee.Feature(None, {
        'year': year,
        'month': month,
        'Light': mean_dict.get('avg_rad')
    })


# BUILD DATAFRAME

years = [2023, 2024, 2025, 2026]

records = []

for year in years:
    for month in range(1, 13):
        try:
            ndvi_feat = monthly_ndvi(year, month).getInfo()
            light_feat = monthly_light(year, month).getInfo()

            ndvi_val = ndvi_feat['properties']['NDVI']
            light_val = light_feat['properties']['Light']

            records.append({
                "date": f"{year}-{month:02d}-01",
                "year": year,
                "month": month,
                "NDVI": ndvi_val,
                "Light": light_val,
                "coordinates": roi_coords
            })

        except:
            pass

df = pd.DataFrame(records)


# SAVE FILES


# Combined file
df.to_csv("combined.csv", index=False)

# Year-wise files
for year in years:
    yearly = df[df['year'] == year]
    if not yearly.empty:
        yearly.to_csv(f"{year}.csv", index=False)

print("All CSV files created successfully.")
