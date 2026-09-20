from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROYECTO = Path(__file__).resolve().parent
ARCHIVO_RESULTADOS = PROYECTO / "result" / "busqueda_estrategica_ta002.csv"
CARPETA_GRAFICOS = PROYECTO / "graficos"
CARPETA_GRAFICOS.mkdir(exist_ok=True)
=======
CARPETA_GRAFICOS = PROYECTO / "graficos"
CARPETA_GRAFICOS.mkdir(exist_ok=True)
>>>>>>> 0a972d89d2716ef0938a426442d1e6d59346d388

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
plt.plot(df["semilla"], df["mejor_makespan"], marker="o")
plt.title("Mejor makespan por corrida")
plt.xlabel("Semilla")
plt.ylabel("Makespan")
plt.tight_layout()
plt.savefig(CARPETA_GRAFICOS / "mejor_makespan_por_corrida.png", dpi=300)
plt.show()
