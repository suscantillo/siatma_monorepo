import json
import pandas as pd
import requests
from datetime import timedelta
import numpy as np
import rasterio
import uuid
from pyproj import Transformer

import requests
import pandas as pd
from datetime import timedelta
import uuid

def obtener_clima_30d(lon, lat, fecha_evento):
    """Devuelve un DataFrame limpio con datos climáticos de los 30 días previos"""

    hoy = pd.Timestamp.now().date()
    if (hoy - fecha_evento).days <= 1:
        fecha_evento = hoy - timedelta(days=3)

    start_date = fecha_evento - timedelta(days=30)
    end_date = fecha_evento - timedelta(days=1)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "daily": [
            "temperature_2m_mean",
            "precipitation_sum",
            "relative_humidity_2m_mean",
            "et0_fao_evapotranspiration"
        ],
        "timezone": "America/Bogota"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Debug: ver la estructura completa de la respuesta
        #import json
        #print("Respuesta completa de la API:")
        #print(json.dumps(data, indent=2, default=str))
        
        if "daily" not in data or "time" not in data["daily"]:
            print("API devolvió datos vacíos o incompletos")
            return None

        # Crear DataFrame
        df = pd.DataFrame(data["daily"])
        
        # Renombrar columna de tiempo
        df.rename(columns={"time": "fecha_clima"}, inplace=True)
        
        # Convertir fecha_clima a datetime si es string
        if df["fecha_clima"].dtype == 'object':
            df["fecha_clima"] = pd.to_datetime(df["fecha_clima"])
        
        # Agregar metadatos
        df["fecha_evento"] = fecha_evento
        df["id"] = str(uuid.uuid4())[:8]
        
        return df

    except Exception as e:
        print(f"Error obteniendo clima: {e}")
        import traceback
        traceback.print_exc()
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

