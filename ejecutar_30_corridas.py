from pathlib import Path
import subprocess
import sys
import argparse

PROYECTO = Path(__file__).resolve().parent
SCRIPT_PRINCIPAL = PROYECTO / "ag.py"


def main():
    parser = argparse.ArgumentParser(description="Ejecuta varias corridas PFSP")
    parser.add_argument("--corridas", type=int, default=30)
    parser.add_argument("--poblacion", type=int, default=100)
    parser.add_argument("--cruce", type=float, default=0.8)
    parser.add_argument("--mutacion", type=float, default=0.2)
    parser.add_argument("--iteraciones", type=int, default=100)
    parser.add_argument("--entrada", type=Path, default=Path("taillard/ta001.txt"))
    parser.add_argument("--salida", type=Path, default=Path("r_ins_20_10_01_c4.csv"))
    parser.add_argument("--metodo", choices=("genetico", "memetico"), default="genetico")
    parser.add_argument("--frecuencia-busqueda", type=int, default=1)
    argumentos = parser.parse_args()
    resultado = PROYECTO / "result"
    resultado.mkdir(exist_ok=True)
    ruta_salida = resultado / argumentos.salida
    if ruta_salida.exists():
        ruta_salida.unlink()

    for semilla in range(1, argumentos.corridas + 1):
        comando = [
            sys.executable,
            str(SCRIPT_PRINCIPAL),
            str(semilla),
            str(argumentos.poblacion), str(argumentos.cruce),
            str(argumentos.mutacion), str(argumentos.iteraciones),
            str(argumentos.entrada), str(argumentos.salida),
        ]
        if argumentos.metodo == "memetico":
            comando.extend([
                "--metodo", argumentos.metodo,
                "--frecuencia-busqueda", str(argumentos.frecuencia_busqueda),
            ])
        subprocess.run(comando, cwd=str(PROYECTO), check=True)


if __name__ == "__main__":
    try:
        main()
    except (subprocess.CalledProcessError, OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(2)