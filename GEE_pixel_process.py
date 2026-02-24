import ee
import pandas as pd

# Initialize Earth Engine
ee.Initialize(project='eco-script')

# ROI
roi_coords = [76.2, 27.0, 76.5, 27.3]
roi = ee.Geometry.Rectangle(roi_coords)

# SETTINGS
years = [2023, 2024, 2025, 2026]
SCALE = 100
TOP_PIXELS = 3000

# Sentinel-2 Collection
s2 = (
    ee.ImageCollection("COPERNICUS/S2_SR")
    .filterBounds(roi)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
)

def add_ndvi(image):
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return image.addBands(ndvi)

ndvi_collection = s2.map(add_ndvi).select('NDVI')

# VIIRS Collection
viirs = (
    ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG")
    .filterBounds(roi)
)

# MASTER LIST (for combined file)
all_records = []


# MAIN LOOP


for year in years:
    print(f"\nProcessing Year: {year}")
    yearly_records = []

    for month in range(1, 13):
        try:
            print(f"  Month: {month:02d}")

            start = ee.Date.fromYMD(year, month, 1)
            end = start.advance(1, 'month')

            ndvi_img = ndvi_collection.filterDate(start, end).mean()
            light_img = (
                viirs
                .filterDate(start, end)
                .mean()
                .select('avg_rad')
                .rename('Light')
            )

            combined = ndvi_img.addBands(light_img)

            # Create anomaly score
            anomaly = combined.expression(
                "(light - ndvi)",
                {
                    "ndvi": combined.select("NDVI"),
                    "light": combined.select("Light")
                }
            ).rename("AnomalyScore")

            combined = combined.addBands(anomaly)

            # Sample + sort + limit
            samples = combined.sample(
                region=roi,
                scale=SCALE,
                geometries=True
            )

            top_pixels = samples.sort("AnomalyScore", False).limit(TOP_PIXELS)

            result = top_pixels.getInfo()

            for feat in result['features']:
                props = feat['properties']
                coords = feat['geometry']['coordinates']

                record = {
                    "date": f"{year}-{month:02d}-01",
                    "year": year,
                    "month": month,
                    "longitude": coords[0],
                    "latitude": coords[1],
                    "NDVI": props.get("NDVI"),
                    "Light": props.get("Light"),
                    "AnomalyScore": props.get("AnomalyScore")
                }

                yearly_records.append(record)
                all_records.append(record)

        except Exception as e:
            print(f"  Skipping {year}-{month:02d} due to error:", e)
            continue

    # Save yearly file
    if yearly_records:
        df_year = pd.DataFrame(yearly_records)
        df_year.to_csv(f"{year}_top{TOP_PIXELS}_pixels.csv", index=False)
        print(f"  Saved {year} file successfully.")
    else:
        print(f"  No valid data for {year}.")

# Save combined file
if all_records:
    df_all = pd.DataFrame(all_records)
    df_all.to_csv("combined_top_pixels.csv", index=False)
    print("\nCombined file saved successfully.")

print("\nAll years processed successfully.")