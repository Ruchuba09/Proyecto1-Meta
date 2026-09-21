# Proyecto1-Meta

Implementación de un problema **Permutation Flow Shop Scheduling (PFSP)** con
instancias Taillard. Se minimiza el *makespan*: todos los trabajos pasan por las
máquinas en el mismo orden y cada trabajo mantiene la misma permutación en todas
ellas.

## Estructura

- `planificador.py`: parser Taillard, tiempos de finalización y fitness.
- `algoritmo_genetico.py`: población, torneo, OX, mutación, elitismo y búsqueda local.
- `ag.py`: punto de entrada de una corrida y escritura de resultados CSV.
- `ejecutar_30_corridas.py`: automatiza 30 semillas sobre una instancia.
- `graficar_resultados.py`: grafica el makespan de las corridas.
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
`--frecuencia-busqueda 2`.

Cada fila del CSV contiene también `mejor_generacion`, `mejor_solucion`, la
permutación de trabajos que produjo el mejor makespan de esa corrida.

## Experimento y gráfica

```powershell
py -3 ejecutar_30_corridas.py
py -3 graficar_resultados.py
```

El experimento escribe `result/r_ins_20_10_01_c4.csv`. Para usar otra instancia
o parámetros, edita las constantes de `ejecutar_30_corridas.py`.
### Graficar instancias pequeñas y comparar métodos

Los CSV nuevos incluyen método, instancia y cota superior. Para reutilizar los
CSV históricos del repositorio, pasa la cota con `--limite-superior`:

```powershell
py -3 graficos/graficar_pequenas.py result/ag.csv result/memetico.csv --limite-superior 1278 --instancia-ag ta001 --instancia-memetico ta001 --metodo-ag genetico --metodo-memetico memetico
```

Las rutas de entrada se pasan como argumentos al script; ya no se definen como
constantes en cada script de gráficos. Para comparar CSV históricos, identifica
explícitamente cada archivo:

```powershell
py -3 comparar_metodos.py result/ag.csv result/memetico.csv --limite-superior 1278 --instancia-ag ta001 --instancia-memetico ta001 --metodo-ag genetico --metodo-memetico memetico
```

Los flags de instancia y método solo son necesarios cuando esas columnas no
existen en el CSV.