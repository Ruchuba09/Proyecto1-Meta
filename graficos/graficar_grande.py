from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. Definir rutas relativas
CARPETA_GRAFICOS = Path(__file__).resolve().parent
PROYECTO = CARPETA_GRAFICOS.parent
CARPETA_RESULT = PROYECTO / "result"

ARCHIVO_RESULTADOS = CARPETA_RESULT / "r_ins_20_10_01_c4.csv"
RUTA_SALIDA = CARPETA_GRAFICOS / "mejor_makespan_por_corrida.png"

# 2. Comprobar existencia del archivo
if not ARCHIVO_RESULTADOS.exists():
    raise FileNotFoundError(
        f"No encontré el CSV en {ARCHIVO_RESULTADOS}. "
        "Primero corre ejecutar_30_corridas.py"
    )

# 3. Procesar y graficar
df = pd.read_csv(ARCHIVO_RESULTADOS)

columnas_numericas = [
    "semilla",
    "tamano_poblacion",
    "probabilidad_cruce",
    "probabilidad_mutacion",
    "numero_iteraciones",
    "tiempo_ejecucion",
    "mejor_generacion",
    "mejor_makespan",
]
for columna in columnas_numericas:
    if columna in df.columns:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")

plt.figure(figsize=(10, 5), dpi=300)
sns.lineplot(data=df, x="semilla", y="mejor_makespan", marker="o")
plt.title("Mejor makespan por corrida")
plt.xlabel("Semilla")
plt.ylabel("Makespan")
plt.tight_layout()

plt.savefig(RUTA_SALIDA)
print(f"Gráfico guardado en: {RUTA_SALIDA}")