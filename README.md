
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
2. Los datos enviados al endpoint deben contener **latitud y longitud en EPSG:4326** (features).
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
5. Abre el archivo `siatma_dashboard.html` en tu navegador ingresa una ubicación (dentro de caldas/antioquia/cauca la puedes buscar en google maps, en el resto del país no sirve poque el DEM es solo de la zona cafetera" y haz clic en el botón **"Enviar predicción"**.
6. Verás la respuesta del modelo en pantalla.


## Notas finales:

- El modelo fue entrenado sobre eventos reales de deslizamiento con datos climáticos históricos.
- Hay muchas cosas que hice desde Qgis como sacar los puntos negativos al azar en la zona cafetera, recortar los shapefiles, sacar el slope, altura y eso
- En data, hay dem, información de los deslizameintos, shapefiles de las zonas de estudio, un archivo si quieren visualizar en qgis y otras cosas más, Bendiciones en el cielo.
