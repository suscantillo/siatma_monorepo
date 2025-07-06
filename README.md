
# SIATMA - Módulo de Predicción de Deslizamientos

Este módulo es la implementación del **modelo predictivo de deslizamientos** para el sistema SIATMA (Sistema Integral de Alerta Temprana Multi-Amenaza).  
Expone una **API REST en Flask** que permite consultar el nivel de riesgo de deslizamiento en puntos geográficos específicos, a partir de variables climáticas y topográficas ya procesadas.

---
##  Datos y modelos

Este repositorio **no incluye archivos de datos ni modelos entrenados** (`.csv`, `.tif`, `.pkl`, `.h5`, etc.) para mantener el peso del repositorio bajo y evitar archivos binarios en control de versiones.

###  ¿Dónde conseguirlos?

descarga los archivos desde aquí:
https://uninorte-my.sharepoint.com/:f:/g/personal/sdariana_uninorte_edu_co/EuBPtf7JFKpJk5fz0dNtih8BvJLX138gff86LBj41G53Eg?e=c07hP7

Una vez descargados:

- Descomprime los archivos del modelo y colócalos en la carpeta `models/`
- Coloca tus archivos de datos dentro de `data/`

##  ¿Qué hace este modelo?

- Carga un modelo **ensemble** entrenado con Random Forest, XGBoost y una red neuronal.
- Predice la **probabilidad de ocurrencia de un deslizamiento**.
- Clasifica el riesgo en niveles: `MÍNIMO`, `BAJO`, `MODERADO`, `ALTO`, `CRÍTICO`.
- Devuelve recomendaciones automáticas según el nivel de riesgo.
- Expone endpoints para:
  - Predicción individual (`/predict`)
  - Predicción por lote (`/batch_predict`)
  - Verificación del estado del modelo (`/health`)
  - Consulta de variables necesarias (`/features`)

---

##  ¿Cómo funciona?

1. Al iniciar, la API carga modelos previamente entrenados desde archivos `.pkl` y `.h5`.
2. Los datos enviados al endpoint deben contener **27 variables ya calculadas** (features).
3. La API transforma los datos, aplica el ensemble y responde con:
   - Probabilidad
   - Nivel de riesgo
   - Recomendaciones
   - Metadatos

---

##  Variables requeridas

El modelo necesita **27 variables** como entrada. Estas incluyen:

- Variables climáticas agregadas: `rain_3d`, `rain_7d`, `rain_15d`, etc.
- Interacciones: `slope_x_rain3d`, `precip_temp_ratio`, etc.
- Datos geográficos: `X`, `Y`, `lat`, `lon`, `slope`, `altura`
- Índices derivados: `humidity_index`, `water_balance`, etc.

Puedes consultarlas vía `/features`.

---

## Qué falta: pipeline automático de features

Actualmente, el modelo **no está conectado directamente a datos crudos**. Se espera que el input ya venga con los 27 features. Sin embargo, en el sistema completo la idea es automatizar todo el flujo.

El pipeline que hace falta debe:

- Recibir una ubicación (`lat`, `lon`) y una fecha de análisis.
- Descargar datos climáticos recientes (últimos 30 días) para ese punto.
- Calcular las variables derivadas necesarias.
- Extraer pendiente y altura desde el DEM existente.
- Generar automáticamente el DataFrame listo para el modelo.
- Integrarse directamente a la API para que el usuario **solo deba ingresar ubicación y fecha**, sin preocuparse por cálculos.

Este pipeline es fundamental para conectar el modelo con la app final o el dashboard interactivo.

---

## Cómo probar el modelo:

0. agreguen los archivos del modelo en la carpeta `models`
1. Crea un entorno virtual y actívalo.
2. Instala dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecuta la API:

```bash
python app/api.py
```

4. Asegúrate de que esté corriendo
5. Abre el archivo `test_predict.html` en tu navegador y haz clic en el botón **"Enviar predicción"**.
6. Verás la respuesta del modelo en pantalla.


## Notas finales:

- El modelo fue entrenado sobre eventos reales de deslizamiento con datos climáticos históricos.
- Este módulo es **solo la parte del modelo y predicción**, no incluye interfaz de usuario ni mapa.
- Está listo para integrarse con otros componentes del sistema SIATMA, como la capa de visualización o automatización de consulta climática.
- El notebook de la prueba final que hice se llama: `zona_cafetera.ipynb`, en los notebooks se entiende mejorcito (creo), como hice las cosas
- en la carpeta scripts hay un .py que con el que calculé los features, lit se llama: `features.py` y en `utils.py` está la función que usé para extraer los datos climáticos de los 30 días antes de cada evento
- Hay muchas cosas que hice desde Qgis como sacar los puntos negativos al azar en la zona cafetera, recortar los shapefiles, sacar el slope, altura y eso
- Diviertanse con las cosas que están en la carpeta data, ahí hay dem, información de los deslizameintos, shapefiles de las zonas de estudio, un archivo si quieren visualizar en qgis y otras cosas más, Bendiciones en el cielo.
