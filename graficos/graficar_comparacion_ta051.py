"""Grafica las tres configuraciones historicas ejecutadas sobre ta051."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

CARPETA_GRAFICOS = Path(__file__).resolve().parent
PROYECTO = CARPETA_GRAFICOS.parent
CARPETA_RESULTADOS = PROYECTO / "result"
ARCHIVO_SALIDA = CARPETA_GRAFICOS / "comparacion_ta051.png"

CORRIDAS = {
    "Busqueda estrategica (200 iteraciones)": ("busqueda_estrategica_ta051.csv", 200),
    "Busqueda media (400 iteraciones)": ("busqueda_media_ta051.csv", 400),
    "Busqueda larga (800 iteraciones)": ("busqueda_larga_ta051_v2.csv", 800),
}


def cargar_corrida(etiqueta: str, nombre_archivo: str, iteraciones_esperadas: int) -> pd.DataFrame:
    ruta = CARPETA_RESULTADOS / nombre_archivo
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontro el archivo {ruta}")

    datos = pd.read_csv(ruta)
    columnas_requeridas = {"semilla", "numero_iteraciones", "mejor_makespan"}
    faltantes = columnas_requeridas - set(datos.columns)
    if faltantes:
        raise ValueError(f"{ruta} no contiene las columnas: {sorted(faltantes)}")

    datos["semilla"] = pd.to_numeric(datos["semilla"], errors="raise")
    datos["numero_iteraciones"] = pd.to_numeric(datos["numero_iteraciones"], errors="raise")
    datos["mejor_makespan"] = pd.to_numeric(datos["mejor_makespan"], errors="raise")
    if datos.empty:
        raise ValueError(f"{ruta} no contiene corridas")
    datos = datos[datos["numero_iteraciones"] == iteraciones_esperadas].copy()
    if datos.empty:
        raise ValueError(f"{ruta} no contiene corridas de {iteraciones_esperadas} iteraciones")
    if datos["numero_iteraciones"].nunique() != 1:
        raise ValueError(
            f"{ruta} mezcla configuraciones; no se puede dibujar como una sola serie"
        )
    if datos["semilla"].duplicated().any():
        raise ValueError(f"{ruta} contiene semillas repetidas")
    return datos.sort_values("semilla").reset_index(drop=True)


def main() -> None:
    plt.figure(figsize=(10, 5), dpi=300)
    for etiqueta, (nombre_archivo, iteraciones_esperadas) in CORRIDAS.items():
        datos = cargar_corrida(etiqueta, nombre_archivo, iteraciones_esperadas)
        corridas = range(1, len(datos) + 1)
        plt.plot(
            corridas,
            datos["mejor_makespan"],
            marker="o",
            linewidth=1.8,
            label=etiqueta,
        )

    plt.title("Comparacion de corridas en ta051")
    plt.xlabel("Numero de corrida")
    plt.ylabel("Mejor makespan")
    plt.grid(axis="y", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(ARCHIVO_SALIDA)
    print(f"Grafico guardado en: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"Error: {error}")
        raise SystemExit(2)
