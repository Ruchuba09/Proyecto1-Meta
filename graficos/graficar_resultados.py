<<<<<<< Updated upstream:graficar_resultados.py
"""Grafica el mejor makespan de un archivo de resultados."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROYECTO = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Grafica resultados PFSP")
    parser.add_argument("archivos", nargs="*", type=Path, help="CSV relativos a result/")
    parser.add_argument("--salida", type=Path, default=Path("graficos/mejor_makespan_por_corrida.png"))
    parser.add_argument("--mostrar", action="store_true")
    args = parser.parse_args()
    archivos = args.archivos or [Path("r_ins_20_10_01_c4.csv")]

    plt.figure(figsize=(10, 5))
    for archivo in archivos:
        ruta = archivo if archivo.is_absolute() else PROYECTO / "result" / archivo
        if not ruta.exists():
            raise FileNotFoundError(f"No encontre el CSV en {ruta}")
        datos = pd.read_csv(ruta)
        if "mejor_makespan" not in datos or "semilla" not in datos:
            raise ValueError(f"{ruta} no contiene semilla y mejor_makespan")
        etiqueta = datos["metodo"].iloc[0] if "metodo" in datos else ruta.stem
        instancia = datos["instancia"].iloc[0] if "instancia" in datos else ""
        plt.plot(
            datos["semilla"], datos["mejor_makespan"], marker="o",
            label=f"{etiqueta} {instancia}".strip(),
        )

    plt.title("Mejor makespan por corrida")
    plt.xlabel("Semilla")
    plt.ylabel("Makespan")
    plt.grid(axis="y", alpha=0.3)
    if len(archivos) > 1:
        plt.legend()
    salida = args.salida if args.salida.is_absolute() else PROYECTO / args.salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(salida, dpi=300)
    if args.mostrar:
        plt.show()


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"Error: {error}")
        raise SystemExit(2)
=======
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PROYECTO = Path(__file__).resolve().parent
ARCHIVO_RESULTADOS = PROYECTO / "result" / "r_ins_20_10_01_c4.csv"
CARPETA_GRAFICOS = PROYECTO / "graficos"
CARPETA_GRAFICOS.mkdir(exist_ok=True)

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
plt.savefig(CARPETA_GRAFICOS / "mejor_makespan_por_corrida.png", dpi=300)
plt.show()
>>>>>>> Stashed changes:graficos/graficar_resultados.py
