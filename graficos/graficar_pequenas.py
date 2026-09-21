"""Compara AG y memetico sobre la misma instancia pequena."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

CARPETA_GRAFICOS = Path(__file__).resolve().parent
PROYECTO = CARPETA_GRAFICOS.parent


def cargar(
    ruta: Path,
    metodo: str,
    limite_superior: float | None,
    instancia: str,
) -> pd.DataFrame:
    datos = pd.read_csv(ruta)
    requeridas = {"semilla", "mejor_makespan"}
    faltantes = requeridas - set(datos.columns)
    if faltantes:
        raise ValueError(f"{ruta} no contiene las columnas: {sorted(faltantes)}")
    if "limite_superior" not in datos:
        if limite_superior is None:
            raise ValueError(
                f"{ruta} es un CSV antiguo; usa --limite-superior"
            )
        datos["limite_superior"] = limite_superior
    if "metodo" not in datos:
        datos["metodo"] = metodo
    if "instancia" not in datos:
        datos["instancia"] = instancia
    datos["limite_superior"] = pd.to_numeric(datos["limite_superior"], errors="raise")
    datos = datos[datos["metodo"] == metodo].copy()
    if datos.empty or datos["instancia"].nunique() != 1:
        raise ValueError(f"{ruta} no contiene resultados validos de {metodo}")
    return datos


def main() -> None:
    parser = argparse.ArgumentParser(description="Grafica AG y memetico en una instancia")
    parser.add_argument("ag", type=Path)
    parser.add_argument("memetico", type=Path)
    parser.add_argument("--limite-superior", type=float)
    parser.add_argument("--instancia", default="historica")
    parser.add_argument("--salida", type=Path, default=Path("graficos/grafico_escala_pequena.png"))
    args = parser.parse_args()
    ag = cargar(args.ag, "genetico", args.limite_superior, args.instancia)
    memetico = cargar(args.memetico, "memetico", args.limite_superior, args.instancia)
    if ag["instancia"].iloc[0] != memetico["instancia"].iloc[0]:
        raise ValueError("Los dos CSV deben corresponder a la misma instancia")
    for datos in (ag, memetico):
        if (datos["limite_superior"] == 0).any():
            raise ValueError("No se puede calcular RPD con cota superior cero")
        datos["rpd"] = 100 * (datos["mejor_makespan"] - datos["limite_superior"]) / datos["limite_superior"]
    cantidad = min(len(ag), len(memetico))
    ag = ag.sort_values("semilla").head(cantidad)
    memetico = memetico.sort_values("semilla").head(cantidad)
    plt.figure(figsize=(7, 4), dpi=300)
    plt.plot(range(1, cantidad + 1), ag["rpd"], marker="o", label="AG")
    plt.plot(range(1, cantidad + 1), memetico["rpd"], marker="s", label="Memetico")
    plt.title(f"Comparacion de RPD en {ag['instancia'].iloc[0]}")
    plt.xlabel("Numero de corrida")
    plt.ylabel("RPD (%)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    salida = args.salida if args.salida.is_absolute() else PROYECTO / args.salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(salida)
    print(f"Grafico generado en: {salida}")


if __name__ == "__main__":
    main()
