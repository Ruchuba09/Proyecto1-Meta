# Proyecto 1 · Metaheurísticas — PFSP con Algoritmo Genético y Memético

Resolución del **Permutation Flow Shop Scheduling Problem (PFSP)** sobre las
instancias estándar de Taillard, comparando un **Algoritmo Genético (AG)** con un
**Algoritmo Memético** (AG + búsqueda local por inserción). El objetivo es
minimizar el *makespan* (`Cmax`): el instante en que termina el último trabajo en
la última máquina. La comparación entre métodos se hace con el **RPD** y el test
de **Wilcoxon**.

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
8. [Resultados y comparación estadística](#8-resultados-y-comparación-estadística)
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
mejoran con **búsqueda local por inserción** cada `frecuencia_busqueda`
generaciones. La búsqueda local prueba mover cada trabajo a cualquier otra
posición de la secuencia, acepta la primera mejora que encuentra y reinicia el
recorrido, hasta alcanzar un óptimo local.

> El vecindario de inserción tiene `n·(n-1)` vecinos y cada uno se evalúa en
> `O(n·m)`, por lo que el memético es mucho más costoso por generación que el AG.
> `--frecuencia-busqueda` permite controlar ese costo (1 = en todas las
> generaciones; 2 = una de cada dos; …).

Con la misma semilla y el mismo tamaño de población, el AG y el memético parten
de la **misma población inicial**, lo que permite compararlos por pares de
semillas.

## 3. Estructura del repositorio

```
Proyecto1-Meta/
├── planificador.py            # Parser de instancias Taillard, tiempos de finalización y fitness
├── algoritmo_genetico.py      # Población, torneo, OX, mutación, búsqueda local, AG y memético
├── ag.py                      # CLI: una corrida (AG o memético) y escritura del CSV
├── ejecutar_30_corridas.py    # Experimento: varias semillas sobre una instancia
├── comparar_metodos.py        # Comparación AG vs memético: RPD y test de Wilcoxon
├── pruebas.py                 # Pruebas unitarias (unittest)
├── requirements.txt           # Dependencias (solo para comparar y graficar)
├── taillard/                  # Instancias ta001 … ta120 (Taillard, 1993)
├── result/                    # CSV de resultados de las corridas
├── graficos/                  # Scripts de gráficas y sus imágenes (.png)
│   ├── graficar_resultados.py
│   └── graficar_pequenas.py
├── paper_instances/           # Dataset original del artículo (no lo usa el código)
├── Proyecto_PFSP_Enunciado.pdf
└── .gitignore
```

## 4. Instalación

Requiere **Python 3.10 o superior**. Para ejecutar el AG, el memético y las
pruebas **no hace falta instalar nada**. Las dependencias de `requirements.txt`
(`matplotlib`, `pandas`, `scipy`, `seaborn`) solo se necesitan para la
comparación estadística y las gráficas.

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
makespan encontrado. Si el archivo ya existe con un formato distinto al actual
(por ejemplo, un CSV antiguo sin la columna `metodo`), `ag.py` se niega a
añadirle filas: usa otro nombre de archivo. Los errores (instancia inexistente,
probabilidades fuera de rango, etc.) se informan con un mensaje breve.

El elitismo (1) y el tamaño del torneo (3) no se exponen por línea de comandos;
pueden cambiarse desde Python (ver 5.2).

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
`busqueda_local_insercion`. En `planificador.py`: `leer_instancia`,
`tiempos_finalizacion` y `calcular_fitness`.

### 5.3 Experimento de varias corridas

```bash
python ejecutar_30_corridas.py [opciones]
```

Ejecuta las semillas `1 … --corridas` y guarda todas las filas en un mismo CSV
dentro de `result/`. **Si el archivo de salida ya existía, se sobrescribe.**

| Opción | Por defecto | Descripción |
|---|---|---|
| `--corridas` | `30` | Número de semillas (1 a N) |
| `--poblacion` | `100` | Tamaño de la población |
| `--cruce` | `0.8` | Probabilidad de cruce |
| `--mutacion` | `0.2` | Probabilidad de mutación |
| `--iteraciones` | `100` | Generaciones |
| `--entrada` | `taillard/ta001.txt` | Instancia |
| `--salida` | `r_ins_20_10_01_c4.csv` | Nombre del CSV en `result/` |
| `--metodo` | `genetico` | `genetico` o `memetico` |
| `--frecuencia-busqueda` | `1` | Solo memético |

### 5.4 Comparación estadística AG vs. memético

```bash
python comparar_metodos.py result/<csv_ag>.csv result/<csv_memetico>.csv [--salida result/comparacion_metodos.csv]
```

Empareja las corridas de ambos métodos **por semilla**, calcula el RPD de cada
una y aplica el **test de rangos con signo de Wilcoxon** sobre el makespan. Imprime
el estadístico y el p-valor, y guarda la tabla por semilla en el CSV de salida
(`semilla`, `makespan_genetico`, `makespan_memetico`, `rpd_genetico`,
`rpd_memetico`).

Requisitos: ambos CSV deben tener el formato actual (con las columnas `metodo`,
`instancia` y `limite_superior`), corresponder a la **misma instancia y los mismos
parámetros**, y compartir al menos dos semillas.

### 5.5 Gráficas

Los scripts de `graficos/` se ejecutan desde cualquier carpeta y guardan su
imagen en `graficos/`:

```bash
python graficos/graficar_resultados.py   # makespan por corrida -> mejor_makespan_por_corrida.png
python graficos/graficar_pequenas.py     # RPD por corrida       -> grafico_escala_pequena.png
```

Los CSV de entrada se definen como constantes al inicio de cada script.

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
| `metodo` | `genetico` o `memetico` |
| `instancia` | Nombre de la instancia (p. ej. `ta001`) |
| `tamano_poblacion` | Tamaño de la población |
| `probabilidad_cruce` | `Pc` |
| `probabilidad_mutacion` | `Pm` |
| `numero_iteraciones` | Generaciones |
| `frecuencia_busqueda` | Frecuencia de la búsqueda local (vacío en el AG) |
| `tiempo_ejecucion` | Tiempo de la corrida (segundos) |
| `mejor_generacion` | Generación en que se alcanzó el mejor makespan por primera vez |
| `mejor_makespan` | Mejor makespan obtenido |
| `limite_superior` | Cota superior (UB) de la instancia |
| `limite_inferior` | Cota inferior (LB) de la instancia |
| `rpd` | Desviación porcentual relativa respecto a la cota superior |
| `mejor_solucion` | Permutación de trabajos que produjo el mejor makespan |

## 7. Pruebas

```bash
python -m unittest pruebas -v
```

Las 9 pruebas cubren: lectura del parser, cálculo de tiempos de finalización y
fitness con un ejemplo pequeño, rechazo de permutaciones inválidas, validez de
población y operadores, selección por torneo, reproducibilidad del AG y del
memético, y que la búsqueda local no empeora la solución y conserva la
permutación.

## 8. Resultados y comparación estadística

La métrica de comparación es el **RPD** (*Relative Percentage Deviation*)
respecto a la cota superior (`UB`) publicada en el encabezado de cada instancia:

```
RPD(%) = (Cmax_obtenido − Cmax_UB) / Cmax_UB × 100
```

Las cotas `UB` son las que traen los archivos de Taillard y pueden no coincidir
con los mejores valores conocidos más recientes de la literatura.

Flujo completo para comparar ambos métodos en una instancia (mismas semillas,
población y probabilidades):

```bash
python ejecutar_30_corridas.py --entrada taillard/ta001.txt --salida ta001_ag.csv
python ejecutar_30_corridas.py --entrada taillard/ta001.txt --salida ta001_mem.csv --metodo memetico
python comparar_metodos.py result/ta001_ag.csv result/ta001_mem.csv --salida result/comparacion_ta001.csv
```

> El memético puede tardar de varios minutos a horas por corrida según el tamaño
> de la instancia; ajusta `--frecuencia-busqueda`, la población y las
> generaciones para acotar el tiempo.

<!-- TODO: pegar aquí la tabla de resultados (mejor, media, RPD y p-valor por
     instancia y método) cuando se regeneren los CSV con el formato actual. -->

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
