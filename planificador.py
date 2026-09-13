"""Lectura y evaluacion para el problema de flow shop permutacional."""

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Sequence


@dataclass(frozen=True)
class Instancia:
    """Instancia Taillard: tiempos_procesamiento[maquina][trabajo]."""

    trabajos: int
    maquinas: int
    tiempos_procesamiento: tuple[tuple[int, ...], ...]
    semilla: int | None = None
    limite_superior: float | None = None
    limite_inferior: float | None = None


def leer_instancia(ruta: str | Path) -> Instancia:
    """Lee una instancia Taillard y devuelve sus dimensiones y tiempos."""
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
    if (
        inicio_matriz < len(lineas)
        and len(lineas[inicio_matriz].split()) == 2
    ):
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

    tiempos = [int(valor) for valor in valores_matriz]
    tiempos_procesamiento = tuple(
        tuple(tiempos[fila * trabajos : (fila + 1) * trabajos])
        for fila in range(maquinas)
    )
    return Instancia(
        trabajos=trabajos,
        maquinas=maquinas,
        tiempos_procesamiento=tiempos_procesamiento,
        semilla=int(metadatos[2]),
        limite_superior=float(metadatos[3]),
        limite_inferior=float(metadatos[4]),
    )


def _validar_permutacion(permutacion: Sequence[int], trabajos: int) -> None:
    """Comprueba que cada trabajo aparezca exactamente una vez."""
    if len(permutacion) != trabajos or set(permutacion) != set(range(trabajos)):
        raise ValueError(
            f"La permutación debe contener exactamente los trabajos 0 a {trabajos - 1}"
        )


def tiempos_finalizacion(
    tiempos_procesamiento: Sequence[Sequence[int]],
    permutacion: Sequence[int],
) -> tuple[tuple[int, ...], ...]:
    """Calcula los tiempos de finalización por máquina y trabajo programado."""
    maquinas = len(tiempos_procesamiento)
    if maquinas == 0:
        raise ValueError("Debe existir al menos una máquina")
    trabajos = len(tiempos_procesamiento[0])
    if trabajos == 0 or any(
        len(fila) != trabajos for fila in tiempos_procesamiento
    ):
        raise ValueError("La matriz de tiempos debe ser rectangular y no vacía")
    _validar_permutacion(permutacion, trabajos)

    # Cada operación espera al trabajo anterior y a la máquina anterior.
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


def calcular_fitness(
    tiempos_procesamiento: Sequence[Sequence[int]],
    permutacion: Sequence[int],
) -> int:
    """Devuelve el makespan de una permutación; menor valor es mejor."""
    # El makespan es la finalización del último trabajo en la última máquina.
    return tiempos_finalizacion(tiempos_procesamiento, permutacion)[-1][-1]
