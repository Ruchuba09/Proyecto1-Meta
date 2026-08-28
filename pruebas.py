import tempfile
import unittest
from pathlib import Path

from planificador import calcular_fitness, leer_instancia, tiempos_finalizacion


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


if __name__ == "__main__":
    unittest.main()