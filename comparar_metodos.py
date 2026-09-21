"""Compara resultados del AG y del algoritmo memetico."""

import argparse
from pathlib import Path

import pandas as pd
from scipy.stats import wilcoxon


def cargar_resultados(ruta: Path) -> pd.DataFrame:
    datos = pd.read_csv(ruta)
    requeridas = {"semilla", "metodo", "instancia", "mejor_makespan", "limite_superior"}
    faltantes = requeridas - set(datos.columns)
    if faltantes:
        raise ValueError(f"{ruta} no contiene las columnas: {', '.join(sorted(faltantes))}")
    datos["mejor_makespan"] = pd.to_numeric(datos["mejor_makespan"], errors="raise")
    datos["limite_superior"] = pd.to_numeric(datos["limite_superior"], errors="raise")
    datos["rpd"] = 100 * (datos["mejor_makespan"] - datos["limite_superior"]) / datos["limite_superior"]
    return datos


def comparar(ag: pd.DataFrame, memetico: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    for datos in (ag, memetico):
        if "rpd" not in datos:
            datos["rpd"] = 100 * (
                datos["mejor_makespan"] - datos["limite_superior"]
            ) / datos["limite_superior"]
    ag = ag[ag["metodo"] == "genetico"].set_index("semilla")
    memetico = memetico[memetico["metodo"] == "memetico"].set_index("semilla")
    semillas = ag.index.intersection(memetico.index)
    if len(semillas) < 2:
        raise ValueError("Se necesitan al menos dos semillas compartidas para Wilcoxon")
    ag = ag.loc[semillas]
    memetico = memetico.loc[semillas]
    estadistico, pvalor = wilcoxon(ag["mejor_makespan"], memetico["mejor_makespan"])
    resumen = pd.DataFrame({
        "semilla": semillas,
        "makespan_genetico": ag["mejor_makespan"].to_numpy(),
        "makespan_memetico": memetico["mejor_makespan"].to_numpy(),
        "rpd_genetico": ag["rpd"].to_numpy(),
        "rpd_memetico": memetico["rpd"].to_numpy(),
    })
    resumen.attrs["estadistico_wilcoxon"] = estadistico
    resumen.attrs["pvalor_wilcoxon"] = pvalor
    return resumen, pvalor


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara AG y memetico con RPD y Wilcoxon")
    parser.add_argument("ag", type=Path)
    parser.add_argument("memetico", type=Path)
    parser.add_argument("--salida", type=Path, default=Path("result/comparacion_metodos.csv"))
    args = parser.parse_args()
    resumen, pvalor = comparar(cargar_resultados(args.ag), cargar_resultados(args.memetico))
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    resumen.to_csv(args.salida, index=False)
    print(f"Wilcoxon: estadistico={resumen.attrs['estadistico_wilcoxon']}, pvalor={pvalor}")
    print(f"Comparacion guardada en {args.salida}")


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"Error: {error}")
        raise SystemExit(2)
