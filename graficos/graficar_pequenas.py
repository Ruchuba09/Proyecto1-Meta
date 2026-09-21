from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

# 1. Definir rutas relativas
CARPETA_GRAFICOS = Path(__file__).resolve().parent
PROYECTO = CARPETA_GRAFICOS.parent
CARPETA_RESULT = PROYECTO / "result"

# Archivos de entrada (CSV en carpeta result)
ARCHIVO_TA001 = CARPETA_RESULT / "resultado_memetico_ta001.csv"
ARCHIVO_TA002 = CARPETA_RESULT / "busqueda_estrategica_ta002.csv"

# Archivo de salida (PNG dentro de la misma carpeta graficos)
RUTA_SALIDA = CARPETA_GRAFICOS / "grafico_escala_pequena.png"

# 2. Comprobar que los CSV existan
if not ARCHIVO_TA001.exists() or not ARCHIVO_TA002.exists():
    raise FileNotFoundError(
        f"No se encontraron los CSV en {CARPETA_RESULT}. "
        "Verifica que estén dentro de la carpeta 'result'."
    )

# 3. Cargar datos
df_ta001 = pd.read_csv(ARCHIVO_TA001)
df_ta002 = pd.read_csv(ARCHIVO_TA002)

# Cotas de Taillard
cref_ta001 = 1278
cref_ta002 = 1359

# 4. Calcular RPD (%)
df_ta001['rpd'] = ((df_ta001['mejor_makespan'] - cref_ta001) / cref_ta001) * 100
df_ta002['rpd'] = ((df_ta002['mejor_makespan'] - cref_ta002) / cref_ta002) * 100

n_corridas = min(len(df_ta001), len(df_ta002))
corridas = range(1, n_corridas + 1)

# 5. Generar y guardar gráfico
plt.figure(figsize=(7, 4), dpi=300)

plt.plot(
    corridas,
    df_ta001['rpd'][:n_corridas],
    marker='o',
    color='#1f77b4',
    linewidth=1.8,
    label='AM en ta001 (100 iteraciones)',
)
plt.plot(
    corridas,
    df_ta002['rpd'][:n_corridas],
    marker='s',
    color='#ff7f0e',
    linewidth=1.8,
    label='AG en ta002 (700 iteraciones)',
)

plt.title(
    'Comparación de RPD (%) por corrida en escala pequeña (20x5)',
    fontsize=11,
    fontweight='bold',
)
plt.xlabel('Número de corrida', fontsize=10)
plt.ylabel('RPD (%) respecto a cota de Taillard', fontsize=10)
plt.xticks(range(1, n_corridas + 1))
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper right', frameon=True, fontsize=9)
plt.tight_layout()

plt.savefig(RUTA_SALIDA)
print(f"Gráfico generado exitosamente en: {RUTA_SALIDA}")