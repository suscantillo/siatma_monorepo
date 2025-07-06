import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import xgboost as xgb
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class SIATMAEnsembleModel:
    """
    Sistema Integral de Alerta Temprana Multi-Amenaza
    Modelo de ensemble learning para predicción de deslizamientos
    """
    
    def __init__(self):
        self.rf_model = None
        self.xgb_model = None
        self.nn_model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.is_trained = False
        
    def prepare_features(self, df):
        """
        Prepara las características para el entrenamiento
        """
        # Definir columnas de características (excluir target, id, fecha)
        exclude_cols = ['target', 'id', 'fecha_evento']
        self.feature_columns = [col for col in df.columns if col not in exclude_cols]
        
        X = df[self.feature_columns].copy()
        y = df['target'].copy()
        
        # Verificar valores faltantes
        if X.isnull().sum().sum() > 0:
            print("Advertencia: Se encontraron valores faltantes. Rellenando con mediana...")
            X = X.fillna(X.median())
        
        return X, y
    
    def train_random_forest(self, X_train, y_train):
        """
        Entrena el modelo Random Forest optimizado para variables geológicas
        """
        print("Entrenando Random Forest...")
        
        # Parámetros optimizados para análisis geológico
        self.rf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features='sqrt',
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
        
        self.rf_model.fit(X_train, y_train)
        
        # Obtener importancia de características
        rf_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("Top 10 características más importantes (Random Forest):")
        print(rf_importance.head(10))
        
        return self.rf_model
    
    def train_xgboost(self, X_train, y_train, X_val, y_val):
        """
        Entrena el modelo XGBoost optimizado para patrones meteorológicos
        """
        print("Entrenando XGBoost...")
        
        # Parámetros optimizados para patrones meteorológicos complejos
        self.xgb_model = xgb.XGBClassifier(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            eval_metric='logloss',
            early_stopping_rounds=50
        )
        
        # Entrenar con validación temprana
        self.xgb_model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        
        # Obtener importancia de características
        xgb_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.xgb_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("Top 10 características más importantes (XGBoost):")
        print(xgb_importance.head(10))
        
        return self.xgb_model
    
    def train_neural_network(self, X_train, y_train, X_val, y_val):
        """
        Entrena la red neuronal para análisis de patrones complejos
        """
        print("Entrenando Red Neuronal...")
        
        # Arquitectura de la red neuronal
        self.nn_model = Sequential([
            Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(32, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            
            Dense(16, activation='relu'),
            Dropout(0.2),
            
            Dense(1, activation='sigmoid')
        ])
        
        # Compilar el modelo
        self.nn_model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # Callbacks para optimización
        callbacks = [
            EarlyStopping(patience=20, restore_best_weights=True),
            ReduceLROnPlateau(patience=10, factor=0.5, min_lr=1e-6)
        ]
        
        # Entrenar la red neuronal
        history = self.nn_model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=100,
            batch_size=64,
            callbacks=callbacks,
            verbose=0
        )
        
        return self.nn_model, history
    
    def train_ensemble(self, df, test_size=0.2, val_size=0.2):
        """
        Entrena el modelo de ensemble completo
        """
        print("=== INICIANDO ENTRENAMIENTO DEL ENSEMBLE SIATMA ===\n")
        
        # Preparar características
        X, y = self.prepare_features(df)
        
        # División de datos
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_size/(1-test_size), random_state=42, stratify=y_temp
        )
        
        print(f"Tamaño del conjunto de entrenamiento: {X_train.shape[0]}")
        print(f"Tamaño del conjunto de validación: {X_val.shape[0]}")
        print(f"Tamaño del conjunto de prueba: {X_test.shape[0]}\n")
        
        # Escalar características para la red neuronal
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Entrenar modelos individuales
        self.train_random_forest(X_train, y_train)
        self.train_xgboost(X_train, y_train, X_val, y_val)
        self.train_neural_network(X_train_scaled, y_train, X_val_scaled, y_val)
        
        # Marcar como entrenado ANTES de evaluar
        self.is_trained = True
        
        # Evaluar ensemble
        print("\n=== EVALUACIÓN DEL ENSEMBLE ===")
        self.evaluate_ensemble(X_test, X_test_scaled, y_test)
        
        print("\n¡Entrenamiento completado exitosamente!")
        
        return {
            'X_test': X_test,
            'X_test_scaled': X_test_scaled,
            'y_test': y_test
        }
    
    def predict_ensemble(self, X, X_scaled=None):
        """
        Realiza predicción con el ensemble
        """
        if not self.is_trained:
            raise ValueError("El modelo debe ser entrenado antes de hacer predicciones")
        
        if X_scaled is None:
            X_scaled = self.scaler.transform(X)
        
        # Predicciones de cada modelo
        rf_pred = self.rf_model.predict_proba(X)[:, 1]
        xgb_pred = self.xgb_model.predict_proba(X)[:, 1]
        nn_pred = self.nn_model.predict(X_scaled).flatten()
        
        # Ensemble con pesos optimizados
        # Random Forest: 0.4 (variables geológicas)
        # XGBoost: 0.4 (patrones meteorológicos)
        # Neural Network: 0.2 (patrones complejos)
        ensemble_prob = 0.4 * rf_pred + 0.4 * xgb_pred + 0.2 * nn_pred
        ensemble_pred = (ensemble_prob > 0.5).astype(int)
        
        return ensemble_pred, ensemble_prob
    
    def evaluate_ensemble(self, X_test, X_test_scaled, y_test):
        """
        Evalúa el rendimiento del ensemble
        """
        # Predicciones del ensemble
        ensemble_pred, ensemble_prob = self.predict_ensemble(X_test, X_test_scaled)
        
        # Métricas individuales
        rf_pred = self.rf_model.predict(X_test)
        xgb_pred = self.xgb_model.predict(X_test)
        nn_pred = (self.nn_model.predict(X_test_scaled) > 0.5).astype(int).flatten()
        
        # Calcular métricas
        models = {
            'Random Forest': rf_pred,
            'XGBoost': xgb_pred,
            'Neural Network': nn_pred,
            'Ensemble': ensemble_pred
        }
        
        print("Métricas por modelo:")
        print("=" * 50)
        
        for name, pred in models.items():
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            accuracy = accuracy_score(y_test, pred)
            precision = precision_score(y_test, pred)
            recall = recall_score(y_test, pred)
            f1 = f1_score(y_test, pred)
            
            print(f"\n{name}:")
            print(f"  Accuracy: {accuracy:.3f}")
            print(f"  Precision: {precision:.3f}")
            print(f"  Recall: {recall:.3f}")
            print(f"  F1-Score: {f1:.3f}")
            
            # Verificar objetivos SIATMA
            if name == 'Ensemble':
                print(f"\nOBJETIVOS SIATMA:")
                print(f"  ✓ Precision >80%: {'SÍ' if precision > 0.8 else 'NO'} ({precision:.1%})")
                print(f"  ✓ Recall >90%: {'SÍ' if recall > 0.9 else 'NO'} ({recall:.1%})")
                false_positive_rate = 1 - precision
                print(f"  ✓ False Positive Rate <15%: {'SÍ' if false_positive_rate < 0.15 else 'NO'} ({false_positive_rate:.1%})")
        
        # ROC AUC para el ensemble
        auc_score = roc_auc_score(y_test, ensemble_prob)
        print(f"\nROC AUC Score (Ensemble): {auc_score:.3f}")
        
        return ensemble_pred, ensemble_prob
    
    def save_model(self, filepath_prefix="siatma_model"):
        """
        Guarda el modelo entrenado
        """
        if not self.is_trained:
            raise ValueError("El modelo debe ser entrenado antes de guardarlo")
        
        # Guardar modelos
        joblib.dump(self.rf_model, f"{filepath_prefix}_rf.pkl")
        joblib.dump(self.xgb_model, f"{filepath_prefix}_xgb.pkl")
        self.nn_model.save(f"{filepath_prefix}_nn.h5")
        
        # Guardar scaler y metadatos
        joblib.dump(self.scaler, f"{filepath_prefix}_scaler.pkl")
        
        metadata = {
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained
        }
        joblib.dump(metadata, f"{filepath_prefix}_metadata.pkl")
        
        print(f"Modelo guardado con prefijo: {filepath_prefix}")
    
    def load_model(self, filepath_prefix="siatma_model"):
        """
        Carga un modelo previamente entrenado
        """
        try:
            # Cargar modelos
            self.rf_model = joblib.load(f"{filepath_prefix}_rf.pkl")
            self.xgb_model = joblib.load(f"{filepath_prefix}_xgb.pkl")
            
            from tensorflow.keras.models import load_model
            self.nn_model = load_model(f"{filepath_prefix}_nn.h5")
            
            # Cargar scaler y metadatos
            self.scaler = joblib.load(f"{filepath_prefix}_scaler.pkl")
            metadata = joblib.load(f"{filepath_prefix}_metadata.pkl")
            
            self.feature_columns = metadata['feature_columns']
            self.is_trained = metadata['is_trained']
            
            print(f"Modelo cargado exitosamente desde: {filepath_prefix}")
            
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            raise

# Función principal de entrenamiento
def train_siatma_model(df):
    """
    Función principal para entrenar el modelo SIATMA
    """
    print("Iniciando entrenamiento del Sistema SIATMA")
    print(f"Dataset: {df.shape[0]} registros, {df.shape[1]} columnas")
    print(f"Distribución target: {df['target'].value_counts().to_dict()}")
    
    # Crear instancia del modelo
    siatma = SIATMAEnsembleModel()
    
    # Entrenar ensemble
    test_data = siatma.train_ensemble(df)
    
    # Guardar modelo
    siatma.save_model("siatma_ensemble_v1")
    
    return siatma, test_data

# Ejemplo de uso
    # Cargar el DataFrame
    # df = pd.read_csv("dataset.csv")
    
    # Entrenar modelo
    # modelo, datos_test = train_siatma_model(df)