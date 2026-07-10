# 📊 Análisis de Precios del Sector Agropecuario (SIPSA - DANE)

Este proyecto automatiza la extracción, limpieza, consolidación y modelado de los datos del **Sistema de Información de Precios y Abastecimiento del Sector Agropecuario (SIPSA)** publicados mensualmente por el DANE en Colombia. 

A través de un script en **Python**, se procesan los reportes mensuales en formato Excel para generar un **Modelo Estrella** optimizado para su visualización interactiva en **Power BI**, permitiendo auditorías comerciales, operativas y financieras detalladas.

---

## Estructura del Modelo de Datos (Modelo Estrella)

Para garantizar un rendimiento óptimo de las consultas DAX en Power BI y evitar redundancia de información, los datos planos de los archivos del DANE se normalizaron en las siguientes entidades:

* **`Fact_Precios_Sipsa.csv` (Tabla de Hechos):** Contiene las métricas clave indexadas por tiempo y región.
    * `precio_kg` (Valor numérico limpio, sin textos informativos).
    * `var_mensual_porcentaje` (Inflación o variación del precio).
    * `periodo` (Formato de fecha real `AAAA-MM-DD` para ordenar cronológicamente de manera automática).
* **`Dim_Productos_Sipsa.csv` (Dimensión):** Catálogo maestro único de alimentos emparejado con su respectiva categoría agrícola (Frutas, Hortalizas, Tubérculos, etc.) extraída de los subtítulos del reporte original.
* **`Dim_Ciudades_Sipsa.csv` (Dimensión):** Listado fijo de las 8 ciudades principales bajo monitoreo logístico.

---

## Tecnologías Utilizadas

* **Python 3.11**
    * `pandas` (Manipulación de datos y proceso de despivote/melt).
    * `numpy` (Tratamiento de valores nulos y limpieza radical de strings).
    * `glob` & `os` (Lectura dinámica del directorio de archivos).
* **Power BI Desktop** (Modelado dimensional, relaciones $1 \rightarrow *$ y analítica visual).

---

## Arquitectura del Script de Limpieza 

El script implementa una ingeniería de datos en 4 capas para asegurar la calidad de la información:

1.  **Lectura por Lotes:** Identifica dinámicamente todos los archivos `.xlsx` de la carpeta local, ignorando archivos temporales o bloqueados por Windows (`~$`).
2.  **Inteligencia de Categorías:** Recorre las celdas de productos fila por fila. Si detecta una fila sin valores numéricos, asume que es un encabezado de categoría agrícola y lo propaga hacia abajo a los productos correspondientes.
3.  **Normalización Lineal (Melt):** Transforma la estructura ancha original de las columnas por ciudades en una estructura angosta o vertical, ideal para motores tabulares.
4.  **Tipado Estricto de Datos:** Convierte las marcas de texto vacías (`'-'`, `'n.d.'`) en nulos reales (`NaN`) y transforma los periodos de texto ("enero", "febrero") en variables de tipo fecha real (`2026-01-01`).

---

## Arquitectura de los Reportes en Power BI

El informe final está estructurado estratégicamente en 3 pantallas para toma de decisiones ejecutivas:

### 1. Informe Comercial (Análisis de Mercado y Canastas)
* **Foco:** Comportamiento de precios por alimento.
* **Visuales:** Matriz expansiva de Categorías  Productos con su `precio_kg` promedio, acompañado de gráficos Top 5 y Bottom 5 de alimentos con mayor volatilidad comercial.

### 2. Informe Operativo (Logística y Geografía Regional)
* **Foco:** Dispersión territorial del costo de los alimentos.
* **Visuales:** Mapa de calor de Colombia donde el tamaño de la burbuja representa el costo por kilo y el color (Verde a Rojo) alerta sobre la inflación de la ciudad, interactuando con gráficos de líneas de tendencias históricas.

### 3. Informe Financiero (Riesgo y Presupuesto)
* **Foco:** Monitoreo y control de sobrecostos.
* **Visuales:** Gráfico combinado de columnas agrupadas y de líneas. Las columnas representan el costo base (`precio_kg`) y la línea cruzada evalúa el porcentaje de inflación (`var_mensual_porcentaje`), permitiendo identificar instantáneamente qué alimentos representan un peligro financiero para la cadena de abastecimiento.

---

## Cómo Ejecutar el Proyecto

1. Clona este repositorio en tu máquina local.
2. Coloca los archivos mensuales descargados del DANE (ej. `enero.xlsx`, `febrero.xlsx`) en la raíz del proyecto.
3. Ejecuta el script de consolidación:
   ```bash
   
## Demo Interactivo

Puedes explorar el tablero final publicado en tiempo real y navegar por las tres pantallas operativas, comerciales y financieras aquí:

**[Abrir Dashboard Interactivo en Power BI Web](https://app.powerbi.com/view?r=eyJrIjoiZDZkNDZhYjItOGMwZi00MzI3LTgzZDEtZTIzZGY1M2YxNWNjIiwidCI6IjgwMDc3YmJjLWJjNWEtNDc3NS04NzA4LTIwODkyNjVjMDAzMyIsImMiOjR9)**