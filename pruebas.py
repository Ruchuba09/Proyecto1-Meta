import tempfile
import unittest
import random
from pathlib import Path

import pandas as pd

from algoritmo_genetico import (
    algoritmo_genetico,
    algoritmo_memetico,
    busqueda_local_insercion,
    cruce_ox,
    generar_poblacion_inicial,
    mutacion_intercambio,
    seleccion_torneo,
)
from planificador import calcular_fitness, leer_instancia, tiempos_finalizacion
from comparar_metodos import comparar


class PruebasPfsp(unittest.TestCase):
    def test_lector_lee_encabezado_y_matriz_taillard(self):
        content = "3 2 123 99 0\n2 5 1\n4 2 3\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "small.txt"
            path.write_text(content, encoding="utf-8")
            instancia = leer_instancia(path)

        self.assertEqual((instancia.trabajos, instancia.maquinas), (3, 2))
        self.assertEqual(instancia.tiempos_procesamiento, ((2, 5, 1), (4, 2, 3)))
        self.assertEqual(instancia.semilla, 123)

    def test_fitness_usa_finalizacion_dinamica(self):
        tiempos_procesamiento = ((2, 5, 1), (4, 2, 3))
        self.assertEqual(
            tiempos_finalizacion(tiempos_procesamiento, (0, 1, 2)),
            ((2, 7, 8), (6, 9, 12)),
        )
        self.assertEqual(calcular_fitness(tiempos_procesamiento, (0, 1, 2)), 12)
        self.assertEqual(calcular_fitness(tiempos_procesamiento, (2, 0, 1)), 10)

    def test_permutacion_invalida_es_rechazada(self):
        with self.assertRaises(ValueError):
            calcular_fitness(((2, 5, 1), (4, 2, 3)), (0, 0, 1))

    def test_poblacion_y_operadores_conservan_permutaciones(self):
        rng = random.Random(4)
        poblacion = generar_poblacion_inicial(5, 8, rng)
        self.assertEqual(len(poblacion), 8)
        self.assertTrue(all(set(individuo) == set(range(5)) for individuo in poblacion))

        hijo1, hijo2 = cruce_ox(poblacion[0], poblacion[1], rng, 1.0)
        mutado = mutacion_intercambio(hijo1, rng, 1.0)
        self.assertEqual(set(hijo1), set(range(5)))
        self.assertEqual(set(hijo2), set(range(5)))
        self.assertEqual(set(mutado), set(range(5)))

    def test_cruce_rechaza_padres_con_repeticiones(self):
        with self.assertRaises(ValueError):
            cruce_ox((0, 0, 1), (0, 1, 1), random.Random(1), 1.0)

    def test_seleccion_torneo_prefiere_el_mejor_fitness(self):
        class RngDeterminista:
            def __init__(self):
                self.indices = iter((0, 1))

            def randrange(self, limite):
                return next(self.indices)

        poblacion = [(0, 1), (1, 0)]
        self.assertEqual(
            seleccion_torneo(poblacion, (20, 5), RngDeterminista(), 2),
            (1, 0),
        )

    def test_algoritmo_genetico_es_reproducible_y_conserva_elitismo(self):
        tiempos = ((2, 5, 1), (4, 2, 3))
        parametros = dict(
            tamaño_poblacion=10,
            generaciones=15,
            probabilidad_cruce=0.9,
            probabilidad_mutacion=0.2,
            elitismo=1,
            semilla=12,
        )
        resultado1 = algoritmo_genetico(tiempos, **parametros)
        resultado2 = algoritmo_genetico(tiempos, **parametros)
        self.assertEqual(resultado1, resultado2)
        self.assertLessEqual(resultado1.historial[-1], resultado1.historial[0])
        self.assertEqual(resultado1.mejor_fitness, 10)

    def test_algoritmo_genetico_conserva_mejor_global_sin_elitismo(self):
        tiempos = ((2, 5, 1), (4, 2, 3))
        resultado = algoritmo_genetico(
            tiempos, tamaño_poblacion=6, generaciones=8,
            probabilidad_cruce=0.9, probabilidad_mutacion=0.8,
            elitismo=0, semilla=1,
        )
        self.assertEqual(resultado.mejor_fitness, min(resultado.historial))
        self.assertEqual(resultado.mejor_generacion, resultado.historial.index(min(resultado.historial)))
        self.assertEqual(calcular_fitness(tiempos, resultado.mejor_permutacion), resultado.mejor_fitness)

    def test_algoritmo_memetico_conserva_mejor_global_sin_elitismo(self):
        tiempos = ((2, 5, 1), (4, 2, 3))
        resultado = algoritmo_memetico(
            tiempos, tamaño_poblacion=6, generaciones=8,
            probabilidad_cruce=0.9, probabilidad_mutacion=0.8,
            elitismo=0, semilla=1, frecuencia_busqueda=2,
        )
        self.assertEqual(resultado.mejor_fitness, min(resultado.historial))
        self.assertEqual(calcular_fitness(tiempos, resultado.mejor_permutacion), resultado.mejor_fitness)

    def test_fitness_rapido_coincide_con_tiempos_finalizacion(self):
        tiempos = ((2, 5, 1), (4, 2, 3), (3, 1, 2))
        for permutacion in ((0, 1, 2), (2, 0, 1), (1, 2, 0)):
            self.assertEqual(
                calcular_fitness(tiempos, permutacion),
                tiempos_finalizacion(tiempos, permutacion)[-1][-1],
            )

    def test_busqueda_local_no_empeora_la_solucion(self):
        tiempos = ((2, 5, 1), (4, 2, 3))
        inicial = (0, 1, 2)
        mejorada = busqueda_local_insercion(tiempos, inicial)
        self.assertLessEqual(calcular_fitness(tiempos, mejorada), calcular_fitness(tiempos, inicial))

    def test_busqueda_local_por_insercion_conserva_la_permutacion(self):
        tiempos = ((2, 5, 1), (4, 2, 3))
        resultado = busqueda_local_insercion(tiempos, (0, 1, 2))
        self.assertEqual(set(resultado), {0, 1, 2})
        self.assertLessEqual(calcular_fitness(tiempos, resultado), 12)

    def test_algoritmo_memetico_es_reproducible(self):
        tiempos = ((2, 5, 1), (4, 2, 3))
        resultado = algoritmo_memetico(tiempos, tamaño_poblacion=8, generaciones=5, semilla=7)
        self.assertEqual(resultado.mejor_fitness, 10)
        self.assertEqual(resultado, algoritmo_memetico(tiempos, tamaño_poblacion=8, generaciones=5, semilla=7))

    def test_comparacion_rechaza_instancias_mezcladas(self):
        base = {"semilla": [1, 2], "limite_superior": [100, 100], "mejor_makespan": [110, 111]}
        ag = pd.DataFrame({**base, "metodo": "genetico", "instancia": ["ta001", "ta002"]})
        memetico = pd.DataFrame({**base, "metodo": "memetico", "instancia": ["ta001", "ta001"]})
        with self.assertRaises(ValueError):
            comparar(ag, memetico)

    def test_comparacion_rechaza_semillas_repetidas(self):
        base = {"semilla": [1, 1], "limite_superior": [100, 100], "mejor_makespan": [110, 111]}
        ag = pd.DataFrame({**base, "metodo": "genetico", "instancia": "ta001"})
        memetico = pd.DataFrame({**base, "metodo": "memetico", "instancia": "ta001"})
        with self.assertRaises(ValueError):
            comparar(ag, memetico)

    def test_comparacion_rechaza_empate_total(self):
        base = {"semilla": [1, 2], "limite_superior": [0, 0], "mejor_makespan": [110, 111]}
        ag = pd.DataFrame({**base, "metodo": "genetico", "instancia": "paper"})
        memetico = pd.DataFrame({**base, "metodo": "memetico", "instancia": "paper"})
        with self.assertRaises(ValueError):
            comparar(ag, memetico)


if __name__ == "__main__":
    unittest.main()