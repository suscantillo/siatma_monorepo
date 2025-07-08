import os
import pandas as pd
from datetime import datetime
import rasterio
from rasterio.transform import rowcol
from pyproj import Transformer
from utils import obtener_clima_30d
from features import calcular_features

# Rutas
DEM_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cafe", "9.tif")
SLOPE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cafe", "slope_zona_cafetera.tif")
SALIDA_DIR = os.path.join(os.path.dirname(__file__), "..", "consultas")
os.makedirs(SALIDA_DIR, exist_ok=True)

# Transformador: de WGS84 (EPSG:4326) → CRS de los TIFs (EPSG:9377)
transformer = Transformer.from_crs("EPSG:4326", "EPSG:9377", always_xy=True)

def reproyectar(x, y):
    lon, lat = transformer.transform(x, y)
    return lon, lat  # para usar en los raster

def extraer_valor_raster(ruta_tif, lon_proj, lat_proj):
    with rasterio.open(ruta_tif) as src:
        transform = src.transform
        row, col = rowcol(transform, lon_proj, lat_proj)
        valor = src.read(1)[row, col]
        return float(valor)

def generar_features_para_prediccion(x, y):
    print(f"🔍 Coordenadas recibidas para predicción: X={x}, Y={y}")

    # 1. Fecha actual
    fecha_evento = datetime.now().date()

    # 2. Clima de los 30 días previos (usa X/Y en 4326)
    df_clima = obtener_clima_30d(x, y, fecha_evento)

    if df_clima is None or df_clima.empty:
        raise ValueError("No se pudo obtener datos climáticos para la ubicación dada.")


    # 3. Reproyectar coordenadas a EPSG:9377 para extracción raster
    lon_proj, lat_proj = reproyectar(x, y)

    # 4. Altura y pendiente desde raster
    altura = extraer_valor_raster(DEM_PATH, lon_proj, lat_proj)
    pendiente = extraer_valor_raster(SLOPE_PATH, lon_proj, lat_proj)

    # 5. Añadir a dataframe
    df_clima["slope"] = pendiente
    df_clima["altura"] = altura
    df_clima["X"] = x
    df_clima["Y"] = y
    df_clima["Mes"] = fecha_evento.month
    df_clima["lat"] = lat_proj
    df_clima["lon"] = lon_proj

    # 6. Guardar CSV mientras no hay backend
    ruta_salida = os.path.join(SALIDA_DIR, "consulta.csv")

    # 7. Calcular features
    df_features = calcular_features(df_clima, ruta_salida)

    return df_features
