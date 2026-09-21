"""Compara resultados del AG y del algoritmo memetico."""

import argparse
from pathlib import Path
import warnings

import pandas as pd
from scipy.stats import wilcoxon


def cargar_resultados(
    ruta: Path,
    metodo: str | None,
    instancia: str | None,
    limite_superior: float | None,
) -> pd.DataFrame:
    datos = pd.read_csv(ruta)
    requeridas = {"semilla", "mejor_makespan"}
    faltantes = requeridas - set(datos.columns)
    if faltantes:
        raise ValueError(f"{ruta} no contiene las columnas: {', '.join(sorted(faltantes))}")
    if "limite_superior" not in datos:
        if limite_superior is None:
            raise ValueError(f"{ruta} es un CSV antiguo; usa --limite-superior")
        datos["limite_superior"] = limite_superior
    if "metodo" not in datos:
        if metodo is None:
            raise ValueError(f"{ruta} es un CSV antiguo; usa --metodo para identificarlo")
        datos["metodo"] = metodo
    if "instancia" not in datos:
        if instancia is None:
            raise ValueError(f"{ruta} es un CSV antiguo; usa --instancia para identificarlo")
        datos["instancia"] = instancia
    datos["mejor_makespan"] = pd.to_numeric(datos["mejor_makespan"], errors="raise")
    datos["limite_superior"] = pd.to_numeric(datos["limite_superior"], errors="raise")
    datos["rpd"] = (
        100 * (datos["mejor_makespan"] - datos["limite_superior"])
        .where(datos["limite_superior"] != 0)
        / datos["limite_superior"].where(datos["limite_superior"] != 0)
    )
    return datos


def comparar(ag: pd.DataFrame, memetico: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    ag = ag.copy()
    memetico = memetico.copy()
    for nombre, datos, metodo in (
        ("AG", ag, "genetico"),
        ("memetico", memetico, "memetico"),
    ):
        instancias = datos["instancia"].dropna().unique()
        if len(instancias) != 1:
            raise ValueError(f"El archivo de {nombre} debe contener una sola instancia")
        if datos["semilla"].duplicated().any():
            raise ValueError(f"El archivo de {nombre} contiene semillas repetidas")
        metodos = set(datos["metodo"])
        if metodos != {metodo}:
            raise ValueError(f"El archivo de {nombre} contiene metodos inesperados: {metodos}")
    if ag["instancia"].iloc[0] != memetico["instancia"].iloc[0]:
        raise ValueError("AG y memetico deben corresponder a la misma instancia")
    for datos in (ag, memetico):
        if "rpd" not in datos:
            datos["rpd"] = (
                100 * (datos["mejor_makespan"] - datos["limite_superior"])
                .where(datos["limite_superior"] != 0)
                / datos["limite_superior"].where(datos["limite_superior"] != 0)
            )
    ag = ag[ag["metodo"] == "genetico"].set_index("semilla")
    memetico = memetico[memetico["metodo"] == "memetico"].set_index("semilla")
    semillas = ag.index.intersection(memetico.index)
    if len(semillas) != len(ag.index) or len(semillas) != len(memetico.index):
        raise ValueError("AG y memetico deben compartir exactamente las mismas semillas")
    if len(semillas) < 2:
        raise ValueError("Se necesitan al menos dos semillas compartidas para Wilcoxon")
    ag = ag.loc[semillas]
    memetico = memetico.loc[semillas]
    diferencias = ag["mejor_makespan"].to_numpy() - memetico["mejor_makespan"].to_numpy()
    if (diferencias == 0).all():
        raise ValueError("AG y memetico empatan en todas las semillas; Wilcoxon no es informativo")
    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
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
    parser.add_argument("--limite-superior", type=float)
    parser.add_argument("--instancia-ag")
    parser.add_argument("--instancia-memetico")
    parser.add_argument("--metodo-ag", choices=("genetico", "memetico"))
    parser.add_argument("--metodo-memetico", choices=("genetico", "memetico"))
    parser.add_argument("--salida", type=Path, default=Path("result/comparacion_metodos.csv"))
    args = parser.parse_args()
    resumen, pvalor = comparar(
        cargar_resultados(args.ag, args.metodo_ag, args.instancia_ag, args.limite_superior),
        cargar_resultados(
            args.memetico,
            args.metodo_memetico,
            args.instancia_memetico,
            args.limite_superior,
        ),
    )
    raiz = Path(__file__).resolve().parent
    salida = args.salida if args.salida.is_absolute() else raiz / args.salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    resumen.to_csv(salida, index=False)
    print(f"Wilcoxon: estadistico={resumen.attrs['estadistico_wilcoxon']}, pvalor={pvalor}")
    print(f"Comparacion guardada en {salida}")


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError, OSError, RuntimeWarning) as error:
        print(f"Error: {error}")
        raise SystemExit(2)
