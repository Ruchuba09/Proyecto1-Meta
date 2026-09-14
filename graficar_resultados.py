from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PROYECTO = Path(__file__).resolve().parent
ARCHIVO_RESULTADOS = PROYECTO / "result" / "r_ins_20_10_01_c4.csv"

if not ARCHIVO_RESULTADOS.exists():
    raise FileNotFoundError(
        f"No encontré el CSV en {ARCHIVO_RESULTADOS}. "
        "Primero corre ejecutar_30_corridas.py"
    )

df = pd.read_csv(ARCHIVO_RESULTADOS)

for columna in [
    "semilla",
    "tamano_poblacion",
    "probabilidad_cruce",
    "probabilidad_mutacion",
    "numero_iteraciones",
    "tiempo_ejecucion",
    "mejor_generacion",
    "mejor_makespan",
]:
    df[columna] = pd.to_numeric(df[columna], errors="coerce")

plt.figure(figsize=(10, 5))
sns.lineplot(data=df, x="semilla", y="mejor_makespan", marker="o")
plt.title("Mejor makespan por corrida")
plt.xlabel("Semilla")
plt.ylabel("Makespan")
plt.tight_layout()
plt.show()
