import pandas as pd
import numpy as np

def calcular_features(df,ruta):
    """
    Extrae features climáticos de un DataFrame con datos de 30 días antes de cada evento.
    
    Args:
        df: DataFrame con columnas:
            - fecha_clima, temperature_2m_mean, precipitation_sum, relative_humidity_2m_mean,
            - et0_fao_evapotranspiration, id, fecha_evento, X, Y, Mes
    
    Returns:
        DataFrame con una fila por id y los features calculados
    """
    
    # Asegurar que las fechas estén en formato datetime
    df['fecha_clima'] = pd.to_datetime(df['fecha_clima'])
    df['fecha_evento'] = pd.to_datetime(df['fecha_evento'])
    
    # Ordenar por id y fecha_clima
    df = df.sort_values(['id', 'fecha_clima'])
    
    features_list = []
    
    # Procesar cada ID (cada evento)
    for event_id in df['id'].unique():
        event_data = df[df['id'] == event_id].copy()
        
        # Verificar que tenemos exactamente 30 días
        if len(event_data) != 30:
            print(f"Advertencia: ID {event_id} tiene {len(event_data)} días en lugar de 30")
        
        # Obtener información básica del evento
        event_info = event_data.iloc[0]
        
        # Calcular features de precipitación
        precip = event_data['precipitation_sum'].values
        
        # Acumulados de precipitación
        rain_3d = np.sum(precip[-3:])  # Últimos 3 días
        rain_7d = np.sum(precip[-7:])  # Últimos 7 días
        rain_15d = np.sum(precip[-15:])  # Últimos 15 días
        rain_30d = np.sum(precip)  # Todos los 30 días
        
        # Días con lluvia fuerte (> 30mm)
        heavy_rain_days = np.sum(precip > 30)
        
        # Proxy de humedad del suelo usando balance hídrico simplificado
        # Humedad del suelo = Precipitación acumulada - Evapotranspiración acumulada
        total_precip = np.sum(event_data['precipitation_sum'])
        total_et0 = np.sum(event_data['et0_fao_evapotranspiration'])
        soil_moisture_proxy = total_precip - total_et0
        
        # Feature de relación precipitación-temperatura
        # Según el artículo: alta precipitación + baja temperatura = mayor humedad del suelo
        mean_precip = np.mean(event_data['precipitation_sum'])
        mean_temp = np.mean(event_data['temperature_2m_mean'])
        
        # Ratio precipitación/temperatura (valores altos = más riesgo según el artículo)
        if mean_temp > 0:
            precip_temp_ratio = mean_precip / mean_temp
        else:
            precip_temp_ratio = mean_precip / 0.1  # Evitar división por cero
        
        # Feature adicional: índice de humedad (precipitación alta + temperatura baja)
        # Normalizar temperatura inversamente (temp baja = valor alto)
        temp_inverse = 1 / (mean_temp + 1)  # +1 para evitar problemas con temperaturas muy bajas
        humidity_index = mean_precip * temp_inverse
        
        # Precipitación máxima diaria
        max_daily_rain = np.max(event_data['precipitation_sum'])
        
        # Feature combinado: humedad antecedente × lluvia máxima
        # Según el artículo, esta combinación incrementa la probabilidad de movimientos en masa
        antecedent_moisture_x_maxrain = soil_moisture_proxy * max_daily_rain
        
        # Feature pendiente × lluvia 3 días (slope_x_rain3d)
        # Nota: No veo columna de pendiente en los datos, asumo que X,Y se pueden usar
        # para calcular algún proxy de pendiente o se debe agregar después
        slope_x_rain3d = 0  # Se calculará después cuando agregue datos de pendiente
        
        # Otros features útiles
        mean_humidity = np.mean(event_data['relative_humidity_2m_mean'])
        std_precip = np.std(event_data['precipitation_sum'])
        
        # Feature de variabilidad climática
        temp_range = np.max(event_data['temperature_2m_mean']) - np.min(event_data['temperature_2m_mean'])
        
        # Días consecutivos sin lluvia antes del evento
        precip_binary = (precip > 0).astype(int)
        dry_days_before = 0
        for i in range(len(precip_binary) - 1, -1, -1):
            if precip_binary[i] == 0:
                dry_days_before += 1
            else:
                break
        
        # Crear el diccionario de features
        features = {
            'id': event_id,
            'fecha_evento': event_info['fecha_evento'],
            'X': event_info['X'],
            'Y': event_info['Y'],
            'Mes': event_info['Mes'],
            
            # Features de precipitación
            'rain_3d': rain_3d,
            'rain_7d': rain_7d,
            'rain_15d': rain_15d,
            'rain_30d': rain_30d,
            'heavy_rain_days': heavy_rain_days,
            'max_daily_rain': max_daily_rain,
            
            # Features de humedad del suelo
            'soil_moisture_proxy': soil_moisture_proxy,
            'antecedent_moisture_x_maxrain': antecedent_moisture_x_maxrain,
            
            # Features de relación precipitación-temperatura
            'precip_temp_ratio': precip_temp_ratio,
            'humidity_index': humidity_index,
            'mean_precip': mean_precip,
            'mean_temp': mean_temp,
            'mean_humidity': mean_humidity,
            
            # Features adicionales
            'temp_range': temp_range,
            'precip_variability': std_precip,
            'dry_days_before': dry_days_before,
            
            # Feature combinado (se calculará después con datos de pendiente)
            'slope_x_rain3d': slope_x_rain3d,
            
            # Features de evapotranspiración
            'mean_et0': np.mean(event_data['et0_fao_evapotranspiration']),
            'total_et0': total_et0,
            'water_balance': total_precip - total_et0  # Balance hídrico
        }
        
        features_list.append(features)
    
    # Convertir a DataFrame
    result_df = pd.DataFrame(features_list)

    # cuando agregue datos de pendiente, su calcula slope_x_rain3d aquí
    # result_df['slope_x_rain3d'] = result_df['slope'] * result_df['rain_3d']
    
    # Guardar el resultado
    result_df.to_csv(ruta, index=False)
    
    print(f"Features extraídos para {len(result_df)} eventos")
    print(f"Columnas generadas: {list(result_df.columns)}")
    
    return result_df

# Ejemplo de uso:
# df = pd.read_csv("tu_archivo.csv")
# df = calcular_features(df,"la ruta de tu archivo")