import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sklearn.cluster import DBSCAN
import folium
import matplotlib.cm as cm
import matplotlib.colors as colors

def generate_anomaly_map(year, month, eps=0.008, min_samples=8):
  

    # Load pixel data

    df = pd.read_csv("combined_top_pixels.csv")
    df_filtered = df[(df["year"] == year) & (df["month"] == month)]

    if df_filtered.empty:
        return None

    # Take top anomalies

    df_filtered = df_filtered.sort_values("AnomalyScore", ascending=False)
   
    # Convert to GeoDataFrame

    geometry = [Point(xy) for xy in zip(df_filtered["longitude"], df_filtered["latitude"])]
    gdf = gpd.GeoDataFrame(df_filtered, geometry=geometry, crs="EPSG:4326")

    # DBSCAN clustering for hotspot cores

    coords = df_filtered[["longitude", "latitude"]].values
    if len(coords) > 5:
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
        gdf["cluster"] = clustering.labels_
    else:
        gdf["cluster"] = -1

    # Create Folium Map centered on mean location

    center_lat = df_filtered["latitude"].mean()
    center_lon = df_filtered["longitude"].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="OpenStreetMap")

    # Generate color map for clusters

    unique_clusters = gdf["cluster"].unique()
    colormap = cm.get_cmap("Reds", len(unique_clusters))
    norm = colors.Normalize(vmin=0, vmax=len(unique_clusters)-1)
    cluster_color_map = {cl: colors.rgb2hex(colormap(norm(i))) for i, cl in enumerate(unique_clusters)}

    # Add points to Folium map

    for _, row in gdf.iterrows():
        cluster = row["cluster"]
        color = cluster_color_map[cluster] if cluster != -1 else "#808080"  # gray for noise
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=3,
            color=color,
            fill=True,
            fill_opacity=0.7
        ).add_to(m)

    return m