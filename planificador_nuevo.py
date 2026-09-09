"""Planificador para el problema de flow shop permutacional (PFSP).

Fusiona el parser de instancias Taillard (más robusto, tolera encabezados
con comentarios y formatos ligeramente distintos) con las funciones de
aleatoriedad, población y fitness vectorizado con numpy.
"""

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class Instancia:
    """Instancia Taillard: tiempos_procesamiento[maquina][trabajo]."""

    trabajos: int
    maquinas: int
    tiempos_procesamiento: np.ndarray  # forma (maquinas, trabajos)
    semilla: int | None = None
    limite_superior: float | None = None
    limite_inferior: float | None = None


def leer_instancia(ruta: str | Path) -> Instancia:
    """Lee una instancia Taillard y devuelve dimensiones, tiempos y bounds.

    Usa el parser basado en regex (más tolerante a comentarios, líneas en
    blanco y encabezados de dos números antes de la matriz) en vez de un
    simple split() de todo el archivo, porque no todos los .txt de los
    repositorios de Taillard vienen exactamente en el mismo formato.
    """
    archivo = Path(ruta)
    lineas = archivo.read_text(encoding="utf-8").splitlines()
    candidatos = [
        (indice, re.findall(r"-?\d+(?:\.\d+)?", linea))
        for indice, linea in enumerate(lineas)
        if linea.strip()
    ]
    indice_metadatos, metadatos = next(
        ((indice, valores) for indice, valores in candidatos if len(valores) >= 5),
        (None, []),
    )
    if indice_metadatos is None:
        raise ValueError(f"{archivo} no contiene un encabezado Taillard completo")

    metadatos = metadatos[:5]
    trabajos, maquinas = int(metadatos[0]), int(metadatos[1])
    if trabajos <= 0 or maquinas <= 0:
        raise ValueError("El número de trabajos y máquinas debe ser positivo")

    inicio_matriz = indice_metadatos + 1
    while inicio_matriz < len(lineas) and (
        not lineas[inicio_matriz].strip()
        or lineas[inicio_matriz].lstrip().startswith("#")
    ):
        inicio_matriz += 1
    if inicio_matriz < len(lineas) and len(lineas[inicio_matriz].split()) == 2:
        inicio_matriz += 1
    valores_matriz = [
        valor
        for linea in lineas[inicio_matriz:]
        if linea.strip() and not linea.lstrip().startswith("#")
        for valor in linea.split()
    ]
    valores_esperados = trabajos * maquinas
    if len(valores_matriz) != valores_esperados:
        raise ValueError(
            f"{archivo} debe contener {valores_esperados} tiempos y contiene "
            f"{len(valores_matriz)}"
        )

    tiempos = np.array(valores_matriz, dtype=np.int64).reshape(maquinas, trabajos)
    return Instancia(
        trabajos=trabajos,
        maquinas=maquinas,
        tiempos_procesamiento=tiempos,
        semilla=int(metadatos[2]),
        limite_superior=float(metadatos[3]),
        limite_inferior=float(metadatos[4]),
    )


# ---------------------------------------------------------------------------
# Aleatoriedad (funciones genéricas y reutilizables, tal como pide el enunciado)
# ---------------------------------------------------------------------------

def aleatorio() -> float:
    """Número real aleatorio en [0, 1)."""
    return float(np.random.random())


def aleatorio_rango(a: float, b: float) -> float:
    """Número real aleatorio en [a, b)."""
    return a + (b - a) * aleatorio()


def aleatorio_entero(a: int, b: int) -> int:
    """Entero aleatorio en [a, b] (ambos extremos incluidos)."""
    return int(a + aleatorio() * (b - a + 1))


# ---------------------------------------------------------------------------
# Fitness
# ---------------------------------------------------------------------------

def _validar_permutacion(permutacion: Sequence[int], trabajos: int) -> None:
    """Comprueba que cada trabajo aparezca exactamente una vez."""
    if len(permutacion) != trabajos or set(permutacion) != set(range(trabajos)):
        raise ValueError(
            f"La permutación debe contener exactamente los trabajos 0 a {trabajos - 1}"
        )


def calcular_fitness(tiempos_procesamiento: np.ndarray, permutacion: Sequence[int]) -> int:
    """Devuelve el makespan de una permutación (menor valor es mejor).

    Se queda con la versión O(m) en memoria (solo la fila de finalización
    de la máquina anterior) en vez de guardar la matriz completa, porque
    esta función se llama miles de veces dentro del AG/Memético y ahí sí
    importa el costo por evaluación. No valida la permutación en cada
    llamada por la misma razón de rendimiento; valida antes con
    `_validar_permutacion` si generas permutaciones "a mano".
    """
    m = tiempos_procesamiento.shape[0]
    c = np.zeros(m, dtype=np.int64)
    for j in permutacion:
        c[0] = c[0] + tiempos_procesamiento[0][j]
        for i in range(1, m):
            c[i] = max(c[i - 1], c[i]) + tiempos_procesamiento[i][j]
    return int(c[m - 1])


def tiempos_finalizacion(
    tiempos_procesamiento: np.ndarray, permutacion: Sequence[int]
) -> tuple[tuple[int, ...], ...]:
    """Matriz completa de tiempos de finalización (máquina x posición).

    Más costosa que `calcular_fitness` (guarda toda la tabla), pero útil
    para depurar contra el ejemplo del enunciado o graficar un diagrama de
    Gantt. No se usa dentro del bucle del AG.
    """
    maquinas, trabajos = tiempos_procesamiento.shape
    _validar_permutacion(permutacion, trabajos)
    finalizacion = [[0] * trabajos for _ in range(maquinas)]
    for posicion, trabajo in enumerate(permutacion):
        for maquina in range(maquinas):
            trabajo_anterior = finalizacion[maquina][posicion - 1] if posicion else 0
            maquina_anterior = finalizacion[maquina - 1][posicion] if maquina else 0
            finalizacion[maquina][posicion] = (
                max(trabajo_anterior, maquina_anterior)
                + tiempos_procesamiento[maquina][trabajo]
            )
    return tuple(tuple(fila) for fila in finalizacion)


def rpd(valor: float, mejor_conocido: float) -> float:
    """Relative Percentage Deviation (%) respecto al mejor valor conocido."""
    return (valor - mejor_conocido) / mejor_conocido * 100


# ---------------------------------------------------------------------------
# Población
# ---------------------------------------------------------------------------

def permutacion_aleatoria(n: int) -> list[int]:
    """Genera una permutación aleatoria de [0, n) mediante Fisher-Yates."""
    perm = list(range(n))
    for i in range(n - 1, 0, -1):
        j = aleatorio_entero(0, i)
        perm[i], perm[j] = perm[j], perm[i]
    return perm


def inicializar_poblacion(tam: int, n: int) -> list[list[int]]:
    """Crea `tam` permutaciones aleatorias de tamaño n."""
    return [permutacion_aleatoria(n) for _ in range(tam)]


def evaluar_poblacion(poblacion: Sequence[Sequence[int]], p: np.ndarray) -> list[int]:
    """Calcula el fitness (makespan) de cada individuo de la población."""
    return [calcular_fitness(p, ind) for ind in poblacion]


def mejor_individuo(
    poblacion: Sequence[Sequence[int]], fitness: Sequence[int]
) -> tuple[Sequence[int], int]:
    """Devuelve (individuo, fitness) del mejor (mínimo makespan) de la población."""
    i = min(range(len(fitness)), key=lambda k: fitness[k])
    return poblacion[i], fitness[i]


if __name__ == "__main__":
    instancia = leer_instancia("archivos/ins_20_5_00.txt")
    print("trabajos:", instancia.trabajos, "maquinas:", instancia.maquinas)
    print(
        "semilla :", instancia.semilla,
        "| UB:", instancia.limite_superior,
        "| LB:", instancia.limite_inferior,
    )
    identidad = list(range(instancia.trabajos))
    c = calcular_fitness(instancia.tiempos_procesamiento, identidad)
    print("makespan identidad:", c, "| RPD: %.2f%%" % rpd(c, instancia.limite_superior))
