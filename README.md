# Proyecto1-Meta
Imagina una fábrica textil donde cada pedido (trabajo) debe pasar, en el mismo orden, por una serie de estaciones: corte → costura → planchado → empaquetado. Cada estación es una máquina, y cada trabajo tarda un tiempo distinto en cada una de ellas.

# Este es el manual

## Descripción
Imagina una fábrica textil donde cada pedido (trabajo) debe pasar, en el mismo orden, por una serie de estaciones: corte → costura → planchado → empaquetado.

**Setup**
- **Objetivo**: crear y activar un entorno Python local e instalar dependencias.
- **Contexto**: el repositorio tiene un `requirements.txt` en esta misma carpeta. El entorno virtual `.venv` se crea en la raíz del repositorio (una carpeta por encima de esta).

Desde la raíz del repositorio (la carpeta que contiene `.venv`), ejecutar:

```powershell
python --version
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r .\Proyecto1-Meta-Elias\requirements.txt
```

Si prefieres usar `cmd`:

```cmd
\.\venv\Scripts\activate.bat
pip install -r .\Proyecto1-Meta-Elias\requirements.txt
```

Si ya estás dentro de la carpeta donde está este `README.md` y el `requirements.txt`, activa el venv desde la carpeta padre:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Ejecutar pruebas / ejemplo**
- Ejecutar el script de pruebas con `pytest` o directamente con Python:

```powershell
py -3 -m pytest .\Proyecto1-Meta-Elias\pruebas.py
# o
python .\Proyecto1-Meta-Elias\pruebas.py
```

**Notas**
- Si `requirements.txt` está vacío o contiene marcadores de posición, actualízalo con las librerías reales.
- Para reproducibilidad, indicar si quieres que fije versiones en `requirements.txt`.

---

#### Parámetros de entrada
- nombre_parametro1: descripción
-
-

#### Ejemplo de ejecución

#### Recordar crear archivo de salida `.csv`

-crear archivo graficar_resultados.py y ejecutar_30_corridas.py
