# Proyecto1-Meta

Implementación de un problema **Permutation Flow Shop Scheduling (PFSP)** con
instancias Taillard. Se minimiza el *makespan*: todos los trabajos pasan por las
máquinas en el mismo orden y cada trabajo mantiene la misma permutación en todas
ellas.

## Estructura

- `planificador.py`: parser Taillard, tiempos de finalización y fitness.
- `algoritmo_genetico.py`: población, torneo, OX, mutación, elitismo y búsqueda local.
- `ag.py`: punto de entrada de una corrida y escritura de resultados CSV.
- `ejecutar_30_corridas.py`: automatiza corridas sobre una instancia y método.
- `graficar_resultados.py`: grafica el makespan de uno o varios CSV.
- `comparar_metodos.py`: calcula RPD y prueba de Wilcoxon para AG y memético.
- `pruebas.py`: pruebas unitarias del parser, fitness y operadores.

## Instalación

Se recomienda usar un entorno virtual:

```powershell
py -3 -m venv .venv
\.venv\Scripts\Activate.ps1
py -3 -m pip install -r requirements.txt
```

## Pruebas

```powershell
py -3 -m unittest pruebas.py
```

## Una corrida

Los caminos de entrada son relativos a la raíz del proyecto y los CSV relativos
se guardan en `result/`:

```powershell
py -3 ag.py 1 100 0.8 0.2 100 taillard\ta001.txt resultados.csv
```

Los parámetros son, en orden: semilla, tamaño de población, probabilidad de
cruce, probabilidad de mutación, generaciones, instancia y CSV de salida.
Para ejecutar el memético, añade `--metodo memetico` y opcionalmente
`--frecuencia-busqueda 2`. Los errores de entrada se muestran como mensajes
breves y el proceso termina con código 2.

Cada fila del CSV contiene `metodo`, `instancia`, los límites de Taillard,
`rpd` y `mejor_solucion`, la permutación de trabajos que produjo el mejor
makespan de esa corrida.

## Experimento y gráfica

```powershell
py -3 ejecutar_30_corridas.py --entrada taillard\ta001.txt --salida resultados.csv
py -3 ejecutar_30_corridas.py --metodo memetico --frecuencia-busqueda 2 --salida memetico_ta001.csv
py -3 graficar_resultados.py resultados.csv memetico_ta001.csv --salida graficos\comparacion.png
py -3 comparar_metodos.py resultados.csv memetico_ta001.csv
```

Por defecto el experimento escribe `result/r_ins_20_10_01_c4.csv` y usa
`taillard/ta001.txt`. Los parámetros se pueden cambiar con argumentos de CLI.
El RPD se calcula como `100 * (makespan - limite_superior) / limite_superior`.

