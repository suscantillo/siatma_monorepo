from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import os

# Importar clase del modelo
from model import SIATMAEnsembleModel 

modelo_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'siatma_ensemble_v1')


app = Flask(__name__)
CORS(app)  # Permite requests desde el frontend

# Cargar modelo al iniciar la API
print("Cargando modelo SIATMA...")
modelo = SIATMAEnsembleModel()

try:
    modelo.load_model(modelo_path)
    print("Modelo cargado exitosamente")
except Exception as e:
    print(f"Error cargando modelo: {e}")
    modelo = None

def get_risk_level(probability):
    """Convierte probabilidad a nivel de riesgo"""
    if probability >= 0.8:
        return "CRÍTICO"
    elif probability >= 0.6:
        return "ALTO"
    elif probability >= 0.4:
        return "MODERADO"
    elif probability >= 0.2:
        return "BAJO"
    else:
        return "MÍNIMO"

def get_recommendations(probability, risk_level):
    """Genera recomendaciones basadas en el riesgo"""
    if risk_level == "CRÍTICO":
        return [
            "EVACUACIÓN INMEDIATA del área",
            "Cerrar acceso a carreteras principales",
            "Activar sistema de alerta masiva",
            "Preparar centros de atención médica"
        ]
    elif risk_level == "ALTO":
        return [
            "Monitoreo constante del área",
            "Restringir acceso a zonas vulnerables",
            "Notificar a autoridades locales",
            "Preparar refugios temporales"
        ]
    elif risk_level == "MODERADO":
        return [
            "Incrementar vigilancia",
            "Monitorear precipitaciones",
            "Revisar planes de contingencia",
            "Informar a comunidades"
        ]
    else:
        return [
            "Mantener monitoreo rutinario",
            "Continuar recolección de datos",
            "Promover reforestación"
        ]

@app.route('/', methods=['GET'])
def home():
    """Endpoint de bienvenida"""
    return jsonify({
        'sistema': 'SIATMA - Sistema Integral de Alerta Temprana Multi-Amenaza',
        'version': '1.0',
        'estado': 'Activo' if modelo else 'Error - Modelo no disponible',
        'endpoints': {
            'predict': '/predict - Predicción de riesgo de deslizamiento',
            'batch_predict': '/batch_predict - Predicciones múltiples',
            'health': '/health - Estado del sistema'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Verifica el estado del sistema"""
    return jsonify({
        'estado': 'OK' if modelo else 'ERROR',
        'modelo_cargado': modelo is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict', methods=['POST'])
def predict_single():
    """
    Predicción individual de riesgo de deslizamiento
    
    Ejemplo de request:
    {
        "X": -75.123,
        "Y": 6.456,
        "Mes": 11,
        "rain_3d": 45.2,
        "rain_7d": 89.5,
        "slope": 25.3,
        "altura": 2150,
        ... (todas las características del modelo)
    }
    """
    try:
        if modelo is None:
            return jsonify({'error': 'Modelo no disponible'}), 500
        
        # Obtener datos del request
        data = request.json
        
        if not data:
            return jsonify({'error': 'No se enviaron datos'}), 400
        
        # Convertir a DataFrame
        df = pd.DataFrame([data])
        
        # Verificar que tenga todas las columnas necesarias
        missing_cols = set(modelo.feature_columns) - set(df.columns)
        if missing_cols:
            return jsonify({
                'error': f'Faltan columnas: {list(missing_cols)}',
                'columnas_requeridas': modelo.feature_columns
            }), 400
        
        # Reordenar columnas según el modelo
        df = df[modelo.feature_columns]
        
        # Hacer predicción
        prediction, probability = modelo.predict_ensemble(df)
        
        # Procesar resultados
        risk_level = get_risk_level(probability[0])
        recommendations = get_recommendations(probability[0], risk_level)
        
        # Respuesta
        resultado = {
            'prediccion': {
                'riesgo_deslizamiento': bool(prediction[0]),
                'probabilidad': float(probability[0]),
                'nivel_riesgo': risk_level,
                'confianza': float(probability[0]) * 100
            },
            'ubicacion': {
                'X': data.get('X'),
                'Y': data.get('Y'),
                'longitud': data.get('lon'),
                'latitud': data.get('lat')
            },
            'recomendaciones': recommendations,
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'modelo_version': 'SIATMA Ensemble v1.0',
                'tiempo_respuesta': '< 30 minutos'
            }
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/batch_predict', methods=['POST'])
def predict_batch():
    """
    Predicciones múltiples para análisis de áreas extensas
    
    Ejemplo de request:
    {
        "data": [
            {"X": -75.123, "Y": 6.456, "rain_3d": 45.2, ...},
            {"X": -75.124, "Y": 6.457, "rain_3d": 32.1, ...},
            ...
        ]
    }
    """
    try:
        if modelo is None:
            return jsonify({'error': 'Modelo no disponible'}), 500
        
        # Obtener datos del request
        request_data = request.json
        
        if not request_data or 'data' not in request_data:
            return jsonify({'error': 'Formato incorrecto. Usar: {"data": [...]'}), 400
        
        batch_data = request_data['data']
        
        # Convertir a DataFrame
        df = pd.DataFrame(batch_data)
        
        # Verificar columnas
        missing_cols = set(modelo.feature_columns) - set(df.columns)
        if missing_cols:
            return jsonify({
                'error': f'Faltan columnas: {list(missing_cols)}',
                'columnas_requeridas': modelo.feature_columns
            }), 400
        
        # Reordenar columnas
        df = df[modelo.feature_columns]
        
        # Hacer predicciones
        predictions, probabilities = modelo.predict_ensemble(df)
        
        # Procesar resultados
        resultados = []
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            risk_level = get_risk_level(prob)
            
            resultados.append({
                'index': i,
                'riesgo_deslizamiento': bool(pred),
                'probabilidad': float(prob),
                'nivel_riesgo': risk_level,
                'ubicacion': {
                    'X': batch_data[i].get('X'),
                    'Y': batch_data[i].get('Y')
                }
            })
        
        # Estadísticas del batch
        high_risk_count = sum(1 for r in resultados if r['nivel_riesgo'] in ['ALTO', 'CRÍTICO'])
        avg_probability = np.mean(probabilities)
        
        return jsonify({
            'predicciones': resultados,
            'resumen': {
                'total_puntos': len(resultados),
                'riesgo_alto_critico': high_risk_count,
                'probabilidad_promedio': float(avg_probability),
                'porcentaje_riesgo': (high_risk_count / len(resultados)) * 100
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/features', methods=['GET'])
def get_features():
    """Devuelve las características que necesita el modelo"""
    if modelo is None:
        return jsonify({'error': 'Modelo no disponible'}), 500
    
    return jsonify({
        'columnas_requeridas': modelo.feature_columns,
        'total_features': len(modelo.feature_columns),
        'ejemplo_datos': {
            'X': -75.123,
            'Y': 6.456,
            'Mes': 11,
            'rain_3d': 45.2,
            'rain_7d': 89.5,
            'rain_15d': 156.8,
            'slope': 25.3,
            'altura': 2150,
            'mean_temp': 18.5,
            'mean_humidity': 75.2
        }
    })

if __name__ == '__main__':
    print("Iniciando API SIATMA...")
    print("Endpoints disponibles:")
    print("   GET  /              - Información del sistema")
    print("   GET  /health        - Estado del sistema")
    print("   POST /predict       - Predicción individual")
    print("   POST /batch_predict - Predicciones múltiples")
    print("   GET  /features      - Características del modelo")
    
    app.run(debug=True, host='0.0.0.0', port=5000)