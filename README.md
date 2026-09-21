# Proyecto 1 · Metaheurísticas — PFSP con Algoritmo Genético y Memético

Resolución del **Permutation Flow Shop Scheduling Problem (PFSP)** sobre las
instancias estándar de Taillard, comparando un **Algoritmo Genético (AG)** con un
**Algoritmo Memético** (AG + búsqueda local). El objetivo es minimizar el
*makespan* (`Cmax`): el instante en que termina el último trabajo en la última
máquina.

- Python 3.10+ · el núcleo del algoritmo usa **solo la biblioteca estándar**.
- Ejecuciones reproducibles mediante semilla.
- Operadores implementados como funciones independientes y reutilizables.

---

## Contenido

1. [El problema](#1-el-problema)
2. [Qué implementa el proyecto](#2-qué-implementa-el-proyecto)
3. [Estructura del repositorio](#3-estructura-del-repositorio)
4. [Instalación](#4-instalación)
5. [Uso](#5-uso)
6. [Formatos de entrada y salida](#6-formatos-de-entrada-y-salida)
7. [Pruebas](#7-pruebas)
8. [Resultados registrados](#8-resultados-registrados)
9. [Equipo](#9-equipo)
10. [Referencias](#10-referencias)

---

## 1. El problema

Se tienen `n` trabajos que deben pasar por `m` máquinas, siempre en el mismo
orden (M1 → M2 → … → Mm). Cada trabajo tiene un tiempo de procesamiento distinto
en cada máquina. La restricción *permutacional* obliga a que **todas las máquinas
procesen los trabajos en la misma secuencia**. Se busca la permutación
`π = (π1, …, πn)` que minimiza el makespan.

El tiempo de finalización de la posición `i` de la secuencia en la máquina `j` es:

```
C(i, j) = max( C(i-1, j), C(i, j-1) ) + p(π_i, j)

Cmax = C(n, m)
```

Es decir, una operación empieza cuando (a) la máquina quedó libre del trabajo
anterior y (b) el propio trabajo terminó en la máquina previa. Como el espacio de
búsqueda crece como `n!`, el problema se aborda con metaheurísticas.

## 2. Qué implementa el proyecto

**Representación.** Cada individuo es una permutación de `0 … n-1` (tupla de
enteros). **Fitness** = makespan (menor es mejor).

| Componente | Implementación |
|---|---|
| Población inicial | Permutaciones aleatorias uniformes |
| Selección | Torneo (tamaño 3 por defecto) |
| Cruce | *Order Crossover* (OX), aplicado a cada pareja con probabilidad `Pc` |
| Mutación | Intercambio de dos posiciones al azar, aplicado a cada individuo con probabilidad `Pm` |
| Reemplazo | Generacional con elitismo (1 individuo por defecto) |
| Criterio de término | Número fijo de generaciones |

**Variante memética.** Es el mismo AG, pero los hijos (ya cruzados y mutados) se
mejoran con **búsqueda local** cada `frecuencia_busqueda` generaciones. La búsqueda
local explora el vecindario de intercambios de pares de posiciones con estrategia
de *primera mejora* y se repite hasta alcanzar un óptimo local.

> La búsqueda local evalúa O(n²) vecinos por hijo, por lo que el memético es
> mucho más costoso por generación que el AG. `--frecuencia-busqueda` permite
> controlar ese costo (1 = en todas las generaciones; 2 = una de cada dos; …).

## 3. Estructura del repositorio

```
Proyecto1-Meta-Ricardo/
├── planificador.py            # Parser de instancias Taillard, tiempos de finalización y fitness
├── algoritmo_genetico.py      # Población, torneo, OX, mutación, búsqueda local, AG y memético
├── ag.py                      # CLI: una corrida (AG o memético) y escritura del CSV
├── ejecutar_30_corridas.py    # Experimento: 30 semillas sobre una instancia
├── graficar_resultados.py     # Gráfica del makespan por corrida
├── pruebas.py                 # Pruebas unitarias (unittest)
├── requirements.txt           # Dependencias (solo para graficar)
├── taillard/                  # Instancias ta001 … ta120 (Taillard, 1993)
├── result/                    # CSV de resultados de las corridas
├── graficos/                  # Gráficas generadas (.png)
├── paper_instances/           # Dataset original del artículo (no lo usa el código)
├── Proyecto_PFSP_Enunciado.pdf
└── distribucion               # Reparto de tareas del equipo
```

## 4. Instalación

Requiere **Python 3.10 o superior**. Para ejecutar el AG, el memético y las
pruebas **no hace falta instalar nada**; las dependencias de `requirements.txt`
(`numpy`, `matplotlib`, `pandas`) solo se necesitan para graficar.

Se recomienda un entorno virtual.

**Windows (PowerShell)**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

> En los ejemplos siguientes se usa `python`. En Windows también puedes usar
> `py -3`. Las rutas con `/` funcionan en todos los sistemas.

## 5. Uso

### 5.1 Una corrida desde la línea de comandos

```bash
python ag.py <semilla> <población> <Pc> <Pm> <generaciones> <instancia> <salida.csv> [opciones]
```

| Argumento | Descripción |
|---|---|
| `semilla` | Semilla aleatoria (entero) |
| `población` | Tamaño de la población |
| `Pc` | Probabilidad de cruce, en `[0, 1]` |
| `Pm` | Probabilidad de mutación, en `[0, 1]` |
| `generaciones` | Número de generaciones |
| `instancia` | Ruta a la instancia, relativa a la raíz del proyecto (o absoluta) |
| `salida.csv` | **Nombre** del CSV; se guarda en `result/` (una ruta absoluta se respeta tal cual) |

| Opción | Descripción |
|---|---|
| `--metodo {genetico,memetico}` | Algoritmo a ejecutar (por defecto `genetico`) |
| `--frecuencia-busqueda N` | Solo memético: aplica búsqueda local cada `N` generaciones (por defecto `1`) |

Ejemplos:

```bash
# Algoritmo genético
python ag.py 1 100 0.8 0.2 100 taillard/ta001.txt resultados.csv

# Algoritmo memético, búsqueda local cada 2 generaciones
python ag.py 1 100 0.8 0.2 100 taillard/ta001.txt resultados.csv --metodo memetico --frecuencia-busqueda 2
```

Cada ejecución **añade una fila** al CSV (no lo sobrescribe) e imprime el mejor
makespan encontrado. El elitismo (1) y el tamaño del torneo (3) no se exponen por
línea de comandos; pueden cambiarse desde Python (ver 5.2).

### 5.2 Como biblioteca de Python

```python
from planificador import leer_instancia, calcular_fitness
from algoritmo_genetico import algoritmo_genetico, algoritmo_memetico

instancia = leer_instancia("taillard/ta001.txt")

resultado = algoritmo_genetico(
    instancia.tiempos_procesamiento,
    tamaño_poblacion=100,
    generaciones=100,
    probabilidad_cruce=0.8,
    probabilidad_mutacion=0.2,
    elitismo=1,
    tamaño_torneo=3,
    semilla=1,
)
print(resultado.mejor_fitness)        # mejor makespan
print(resultado.mejor_permutacion)    # secuencia de trabajos
print(resultado.historial)            # mejor fitness en cada generación

# Variante memética: mismos parámetros + frecuencia_busqueda
memetico = algoritmo_memetico(
    instancia.tiempos_procesamiento,
    tamaño_poblacion=30,
    generaciones=20,
    semilla=1,
    frecuencia_busqueda=2,
)

# RPD (%) respecto a la cota superior publicada en la instancia
rpd = (memetico.mejor_fitness - instancia.limite_superior) / instancia.limite_superior * 100
```

Funciones reutilizables de `algoritmo_genetico.py`: `generar_poblacion_inicial`,
`seleccion_torneo`, `cruce_ox`, `mutacion_intercambio` y
`busqueda_local_intercambio`. En `planificador.py`: `leer_instancia`,
`tiempos_finalizacion` y `calcular_fitness`.

### 5.3 Experimento de 30 corridas

```bash
python ejecutar_30_corridas.py
```

Ejecuta las semillas 1 a 30 con el **algoritmo genético** y los parámetros
definidos como constantes al inicio del script (por defecto: `taillard/ta001.txt`,
población 100, `Pc` 0.8, `Pm` 0.2, 100 generaciones). El resultado se guarda en
`result/r_ins_20_10_01_c4.csv`, y **se sobrescribe** si ya existía. Para cambiar
la instancia o los parámetros, edita esas constantes.

### 5.4 Gráfica

```bash
python graficar_resultados.py
```

Grafica el mejor makespan por semilla del CSV indicado en la constante
`ARCHIVO_RESULTADOS` (al inicio del script) y guarda la imagen en
`graficos/mejor_makespan_por_corrida.png`.

## 6. Formatos de entrada y salida

### Instancia (formato Taillard)

```
#number of jobs, number of machines, initial seed, upper bound and lower bound :
#          20           5   873654221        1278        1232
# NbJobs NbMachines
20 5
#processing times :
 54 83 15 71 ...        <- fila 1: máquina 1, un valor por trabajo
 ...                    <- una fila por máquina
```

La matriz se lee como **filas = máquinas, columnas = trabajos**. El parser toma
además la semilla y las cotas superior/inferior (`limite_superior`,
`limite_inferior`) del encabezado.

### CSV de resultados

| Columna | Contenido |
|---|---|
| `semilla` | Semilla de la corrida |
| `tamano_poblacion` | Tamaño de la población |
| `probabilidad_cruce` | `Pc` |
| `probabilidad_mutacion` | `Pm` |
| `numero_iteraciones` | Generaciones |
| `tiempo_ejecucion` | Tiempo de la corrida (segundos) |
| `mejor_generacion` | Generación en que se alcanzó el mejor makespan por primera vez |
| `mejor_makespan` | Mejor makespan obtenido |
| `mejor_solucion` | Permutación de trabajos que lo produjo |

## 7. Pruebas

```bash
python -m unittest pruebas -v
```

Las 8 pruebas cubren: lectura del parser, cálculo de tiempos de finalización y
fitness con un ejemplo pequeño, rechazo de permutaciones inválidas, validez de
población y operadores, selección por torneo, reproducibilidad del AG y del
memético, y que la búsqueda local nunca empeora la solución.

## 8. Resultados registrados

Resumen de los CSV incluidos en `result/`. `RPD` es la desviación porcentual
relativa respecto a la cota superior (`UB`) publicada en el encabezado de cada
instancia:

```
RPD(%) = (Cmax_obtenido − Cmax_UB) / Cmax_UB × 100
```

| Instancia | Tamaño | UB | Pob. | Gen. | Pc / Pm | Corridas | Mejor | Media | RPD mejor | RPD media | Tiempo medio (s) |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| ta001 | 20×5 | 1278 | 100 | 100 | 0.8 / 0.2 | 30 | 1297 | 1304.6 | 1.49 | 2.08 | 0.3 |
| ta001 | 20×5 | 1278 | 200 | 500 | 0.9 / 0.15 | 5 | 1278 | 1278.0 | 0.00 | 0.00 | 719.6 |
| ta002 | 20×5 | 1359 | 150 | 700 | 0.9 / 0.1–0.2 | 20 | 1359 | 1359.8 | 0.00 | 0.06 | 352.1 |
| ta002 | 20×5 | 1359 | 200 | 500 | 0.9 / 0.15 | 5 | 1359 | 1359.8 | 0.00 | 0.06 | 356.8 |
| ta003 | 20×5 | 1081 | 150 | 700 | 0.9 / 0.1–0.2 | 19 | 1081 | 1086.9 | 0.00 | 0.55 | 654.2 |
| ta041 | 50×10 | 3025 | 80 | 200 | 0.9 / 0.15 | 10 | 3299 | 3343.7 | 9.06 | 10.54 | 7.1 |
| ta041 | 50×10 | 3025 | 120 | 800 | 0.9 / 0.15 | 11 | 3218 | 3288.3 | 6.38 | 8.70 | 29.0 |
| ta041 | 50×10 | 3025 | 300 | 2500 | 0.9 / 0.2 | 1 | 3272 | 3272.0 | 8.17 | 8.17 | 204.5 |
| ta051 | 50×20 | 3875 | 80 | 200 | 0.9 / 0.15 | 10 | 4257 | 4333.7 | 9.86 | 11.84 | 12.6 |
| ta051 | 50×20 | 3875 | 120 | 400 | 0.9 / 0.15 | 10 | 4255 | 4316.3 | 9.81 | 11.39 | 32.9 |
| ta051 | 50×20 | 3875 | 80 | 300 | 0.9 / 0.15 | 2 | 3950 | 3952.0 | 1.94 | 1.99 | 8114.4 |
| ta051 | 50×20 | 3875 | 120 | 800 | 0.9 / 0.15 | 1 | 3963 | 3963.0 | 2.27 | 2.27 | 9292.8 |

**Nota:** los CSV no registran qué método (`genetico` o `memetico`) generó cada
fila; el tiempo medio de corrida permite distinguirlas de forma orientativa. Las
cotas `UB` son las que traen los archivos de Taillard y pueden no coincidir con
los mejores valores conocidos más recientes de la literatura.

## 9. Equipo

| Integrante | Responsabilidad |
|---|---|
| **Ricardo** | Módulo de datos: parser de instancias, función de fitness y validación con casos pequeños. Informe: introducción, definición formal y modelo matemático. |
| **Jennifer** | Operadores metaheurísticos: población inicial, selección, cruce, mutación y bucle principal del AG (elitismo y parámetros). Control de versiones y pruebas. Informe: marco teórico y diseño del AG. |
| **Integrante 3** *(completar nombre)* | Búsqueda local y algoritmo memético; diseño experimental, cálculo de RPD y análisis estadístico. Informe: resultados, discusión y conclusiones. |

## 10. Referencias

- E. Taillard, "Benchmarks for basic scheduling problems," *European Journal of
  Operational Research*, 1993. Instancias:
  <http://mistic.heig-vd.ch/taillard/problemes.dir/ordonnancement.dir/ordonnancement.html>
- C. R. Reeves, "A genetic algorithm for flowshop sequencing," *Computers &
  Operations Research*, 1995.
- Enunciado del proyecto: [`Proyecto_PFSP_Enunciado.pdf`](Proyecto_PFSP_Enunciado.pdf)
