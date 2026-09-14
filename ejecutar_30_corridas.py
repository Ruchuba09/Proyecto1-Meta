from pathlib import Path
import subprocess
import sys

NUM_CORRIDAS = 30
TAM_POBLACION = 100
PROB_CRUCE = 0.8
PROB_MUTACION = 0.2
NUM_ITERACIONES = 100

PROYECTO = Path(__file__).resolve().parent
SCRIPT_PRINCIPAL = PROYECTO / "ag.py"
ARCHIVO_ENTRADA = "taillard/ta001.txt"
ARCHIVO_SALIDA = "r_ins_20_10_01_c4.csv"


def main():
    resultado = PROYECTO / "result"
    resultado.mkdir(exist_ok=True)
    ruta_salida = resultado / ARCHIVO_SALIDA
    if ruta_salida.exists():
        ruta_salida.unlink()

    for semilla in range(1, NUM_CORRIDAS + 1):
        comando = [
            sys.executable,
            str(SCRIPT_PRINCIPAL),
            str(semilla),
            str(TAM_POBLACION),
            str(PROB_CRUCE),
            str(PROB_MUTACION),
            str(NUM_ITERACIONES),
            ARCHIVO_ENTRADA,
            ARCHIVO_SALIDA,
        ]
        subprocess.run(comando, cwd=str(PROYECTO), check=True)


if __name__ == "__main__":
    main()