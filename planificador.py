"""Lectura y evaluacion para el problema de flow shop permutacional."""

from dataclasses import dataclass
from pathlib import Path
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
    valores_encabezado = archivo.read_text(encoding="utf-8").split()
    if len(valores_encabezado) < 5:
        raise ValueError(f"{archivo} no contiene un encabezado Taillard completo")

    trabajos, maquinas = int(valores_encabezado[0]), int(valores_encabezado[1])
    if trabajos <= 0 or maquinas <= 0:
        raise ValueError("El número de trabajos y máquinas debe ser positivo")

    valores_esperados = 5 + trabajos * maquinas
    if len(valores_encabezado) != valores_esperados:
        raise ValueError(
            f"{archivo} debe contener {valores_esperados} valores y contiene "
            f"{len(valores_encabezado)}"
        )

    # Los cinco primeros valores son metadatos; el resto es la matriz.
    tiempos = [int(valor) for valor in valores_encabezado[5:]]
    tiempos_procesamiento = tuple(
        tuple(tiempos[fila * trabajos : (fila + 1) * trabajos])
        for fila in range(maquinas)
    )
    return Instancia(
        trabajos=trabajos,
        maquinas=maquinas,
        tiempos_procesamiento=tiempos_procesamiento,
        semilla=int(valores_encabezado[2]),
        limite_superior=float(valores_encabezado[3]),
        limite_inferior=float(valores_encabezado[4]),
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
