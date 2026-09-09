import sys
import os
import time
import numpy as np

tiempo_proceso_ini = time.process_time()
sep = os.path.sep

if len(sys.argv) == 8:
    semilla = int(sys.argv[1])
    tamaño_poblacion = int(sys.argv[2])
    probabilidad_cruce = float(sys.argv[3])
    probabilidad_mutacion = float(sys.argv[4])
    numero_iteradores = int(sys.argv[5])
    entrada = 'data' + sep + sys.argv[6]
    salida = 'result'+ sep + sys.argv[7]
    print('parametros ingresados: ', semilla, tamaño_poblacion, probabilidad_cruce, probabilidad_mutacion, numero_iteradores, entrada, salida)

else:
    print('Error: cantidad de parametros incorrecta')
    print('Los parámetros a ingresar son: semilla, tamaño_poblacion, probabilidad_cruce, probabilidad_mutacion, numero_iteradores, entrada, salida')
    print('donde:')
    print('semilla: valor entero positivo')
    semilla = input()
    print('tamaño_poblacion: valor entero positivo')
    tamaño_poblacion = input()
    print('probabilidad_cruce: valor real positivo')
    probabilidad_cruce = input()
    print('probabilidad_mutacion: valor real positivo')
    probabilidad_mutacion = input()
    print('numero_iteradores: valor entero positivo')
    numero_iteradores = input()
    print('entrada: nombre de archivo de entrada (ubicado en la carpeta entradas)')
    entrada = "entradas" +input()
    print('salida: nombre de archivo de salida (ubicado en la carpeta salidas)')
    salida = "salidas" + input()
    sys.exit(1)

with open(entrada, 'r') as f:

    primera_linea = f.readlines().strip().split()
    num_trabajos = int(primera_linea[0])
    num_maquinas = int(primera_linea[1])
    limite_inferior = int(primera_linea[3])
    limite_superior = int(primera_linea[4])
    matriz = np.loadtxt(f, dtype=int)
print(f'P1:[{num_trabajos}, {num_maquinas}, {limite_inferior}, {limite_superior}]')
print(matriz)

np.random.seed(semilla)

def inicializar_poblacion(filas, columnas):
    poblacion = np.tile(np.arange(columnas), (filas, 1))
    for i in range(filas):
        np.random.shuffle(poblacion[i])
    return np.array(poblacion)

poblacion = inicializar_poblacion(tamaño_poblacion, num_trabajos)
print('poblacion inicial:')
print(poblacion)

tiempo_proceso_fin = time.process_time()
print(f'Tiempo de proceso: %f{tiempo_proceso_fin - tiempo_proceso_ini} segundos')


