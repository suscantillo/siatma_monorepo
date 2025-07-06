import pandas as pd
import requests
import time
from datetime import timedelta
import random
import numpy as np
import rasterio
from pyproj import Transformer
def obtener_clima_30d(lat, lon, fecha_evento):
    """Obtiene datos diarios para los 30 días antes de fecha_evento"""
    start_date = fecha_evento - timedelta(days=30)
    end_date = fecha_evento - timedelta(days=1)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "daily": [
            "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
            "precipitation_sum", "relative_humidity_2m_max", "relative_humidity_2m_min",
            "relative_humidity_2m_mean", "pressure_msl_mean", "wind_speed_10m_max",
            "et0_fao_evapotranspiration"
        ],
        "timezone": "America/Bogota"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("daily", {})
    except requests.exceptions.RequestException as e:
        print(f"Error para lat={lat}, lon={lon}, fecha_evento={fecha_evento}: {e}")
        return None

def ver_propiedades_tif(file_path):
    """Muestra las propiedades de un archivo TIFF"""

    with rasterio.open(file_path) as src:
        print("Información del DEM:")
        print(f"- CRS: {src.crs}")
        print(f"- Tamaño (píxeles): {src.width} x {src.height}")
        print(f"- Resolución (tamaño de píxel): {src.res}")
        print(f"- Número de bandas: {src.count}")
        print(f"- Tipo de datos: {src.dtypes[0]}")
        
        # Leer la banda 1 (elevación)
        band1 = src.read(1)
        
        # Calcular estadísticas básicas, ignorando nodata
        nodata = src.nodata
        if nodata is not None:
            band1 = np.where(band1 == nodata, np.nan, band1)
        
        print(f"- Valor mínimo: {np.nanmin(band1)}")
        print(f"- Valor máximo: {np.nanmax(band1)}")
        print(f"- Valor promedio: {np.nanmean(band1)}")
        
# Inicializar el transformador ( 4326 → 9377)
transformer = Transformer.from_crs("EPSG:4326", "EPSG:9377", always_xy=True)        
def reproyectar(x, y):
    lon, lat = transformer.transform(x, y)
    return pd.Series({'lon': lon, 'lat': lat})   
     
def pasar_a_9377(df, x_col='X', y_col='Y'):
    """Convierte coordenadas de EPSG:4326 a EPSG:9377"""

    # Crear nuevas columnas
    df[['lon', 'lat']] = df.apply(lambda row: reproyectar(row[x_col], row[y_col]), axis=1)

    # Mostrar ejemplo
    df.head()

