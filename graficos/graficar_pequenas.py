import os
import matplotlib.pyplot as plt
import pandas as pd

# Detecta automáticamente la carpeta donde está este archivo (carpeta 'result')
directorio = os.path.dirname(os.path.abspath(__file__))

ruta_ta001 = os.path.join(directorio, 'resultado_memetico_ta001.csv')
ruta_ta002 = os.path.join(directorio, 'busqueda_estrategica_ta002.csv')
ruta_salida = os.path.join(directorio, 'grafico_escala_pequena.png')

# 1. Cargar datos
df_ta001 = pd.read_csv(ruta_ta001)
df_ta002 = pd.read_csv(ruta_ta002)

# 2. Cotas óptimas de Taillard
cref_ta001 = 1278
cref_ta002 = 1359

# 3. Calcular RPD (%)
df_ta001['rpd'] = (
    (df_ta001['mejor_makespan'] - cref_ta001) / cref_ta001
) * 100
df_ta002['rpd'] = (
    (df_ta002['mejor_makespan'] - cref_ta002) / cref_ta002
) * 100

n_corridas = min(len(df_ta001), len(df_ta002))
corridas = range(1, n_corridas + 1)

# 4. Generar gráfico
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
plt.savefig(ruta_salida)
print("Gráfico generado exitosamente en:", ruta_salida)