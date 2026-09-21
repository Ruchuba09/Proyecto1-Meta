# Escala mediana (50x10: ta041)
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

# Rutas relativas
CARPETA_GRAFICOS = Path(__file__).resolve().parent
PROYECTO = CARPETA_GRAFICOS.parent
ARCHIVO_CSV = PROYECTO / "result" / "resultado_gemetico_50x10_ta041_4.csv"
RUTA_SALIDA = CARPETA_GRAFICOS / "grafico_ta041.png"

if not ARCHIVO_CSV.exists():
  raise FileNotFoundError(
      f"No se encontró el archivo {ARCHIVO_CSV}. "
      "Verifica que esté dentro de la carpeta 'result'."
  )

# Cargar y ordenar datos
df = pd.read_csv(ARCHIVO_CSV)
df["mejor_makespan"] = pd.to_numeric(df["mejor_makespan"], errors="coerce")
df = df.sort_values("semilla").reset_index(drop=True)

cref = 3025  # Cota de Taillard para ta041

# Graficar
plt.figure(figsize=(7, 4), dpi=300)
plt.plot(
    df["semilla"],
    df["mejor_makespan"],
    marker="o",
    color="#2ca02c",
    linewidth=1.8,
    label="AM en ta041 (50x10, 250 iteraciones)",
)
plt.axhline(
    cref,
    color="crimson",
    linestyle="--",
    linewidth=1.5,
    label=f"Cota Taillard ({cref})",
)

plt.title(
    "Desempeño del Algoritmo Memético en ta041 (50x10)",
    fontsize=11,
    fontweight="bold",
)
plt.xlabel("Número de corrida (Semilla)", fontsize=10)
plt.ylabel("Mejor Makespan", fontsize=10)
plt.xticks(df["semilla"])
plt.ylim(3015, 3075)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend(loc="upper right", frameon=True, fontsize=9)
plt.tight_layout()

plt.savefig(RUTA_SALIDA)
print(f"Gráfico de escala mediana guardado en: {RUTA_SALIDA}")