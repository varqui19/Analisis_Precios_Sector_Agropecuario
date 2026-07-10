import pandas as pd
import numpy as np
import glob
import os

# 1. Configuración de la ruta de los archivos
carpeta_datos = #ruta de la carpeta
archivos_excel = glob.glob(os.path.join(carpeta_datos, "*.xlsx"))

print(f"Archivos encontrados para consolidar: {[os.path.basename(f) for f in archivos_excel]}")

# Listas globales para acumular los datos de todos los meses
todos_los_hechos = []
todos_los_productos = []

ciudades_lista = ['Barranquilla', 'Bogotá', 'Bucaramanga', 'Cartagena', 'Cali', 'Cúcuta', 'Medellín', 'Pereira']

# Columnas mapeadas para el formato DANE
columnas_manuales = ['producto']
for ciudad in ciudades_lista:
    columnas_manuales.append(f"{ciudad}_precio")
    columnas_manuales.append(f"{ciudad}_var_porcentaje")

# Diccionario de traducción para convertir el nombre del archivo en FECHAS 
mapeo_fechas = {
    "enero": "2026-01-01",
    "febrero": "2026-02-01",
    "marzo": "2026-03-01",
    "abril": "2026-04-01",
    "mayo": "2026-05-01"
}

# 2. BUCLE PRINCIPAL: Procesar cada mes automáticamente
for ruta_archivo in archivos_excel:
    nombre_archivo = os.path.basename(ruta_archivo)
    
    # Omitir archivos temporales ocultos de Excel
    if nombre_archivo.startswith("~$"):
        continue
        
    print(f"Procesando: {nombre_archivo}...")
    
    # Obtenemos el nombre base en minúsculas (ej: 'enero')
    nombre_base = os.path.splitext(nombre_archivo)[0].lower().strip()
    
    # Asignamos la fecha real estándar YYYY-MM-DD. Si no coincide, por defecto usa la fecha de Enero
    fecha_periodo = mapeo_fechas.get(nombre_base, "2026-01-01")
    
    # Leemos la pestaña '1' de este archivo en específico
    df_raw = pd.read_excel(ruta_archivo, sheet_name='1', header=None)
    
    # Tomamos las filas de datos e inyectamos las columnas manuales
    df_datos = df_raw.iloc[10:, :17].copy()
    df_datos.columns = columnas_manuales
    df_datos['producto'] = df_datos['producto'].astype(str).str.strip()
    
    # Separar productos y capturar su Categoría de los subtítulos
    categoria_actual = "Otros"
    filas_limpias = []
    
    for idx, row in df_datos.iterrows():
        prod = str(row['producto']).strip()
        valores_ciudades = row.iloc[1:].replace(['-', 'n.d.', 'n.d', '', ' '], np.nan).dropna()
        
        if len(valores_ciudades) == 0:
            if prod != 'nan' and prod != '' and not prod.startswith('Fuente') and not prod.startswith('Total'):
                categoria_actual = prod
        else:
            if prod not in ['nan', '', 'Producto', 'Precio $/Kg'] and not prod.startswith('Fuente') and not prod.startswith('Total'):
                nueva_fila = row.to_dict()
                nueva_fila['producto'] = prod
                nueva_fila['categoria'] = categoria_actual
                filas_limpias.append(nueva_fila)
                
    if len(filas_limpias) == 0:
        continue
        
    df_limpio_mes = pd.DataFrame(filas_limpias)
    
    # Guardamos los productos y categorías de este mes para la dimensión maestra
    todos_los_productos.append(df_limpio_mes[['producto', 'categoria']])
    
    # DESPIVOTAR (Melt) para este mes
    df_precios = pd.melt(
        df_limpio_mes, id_vars=['producto', 'categoria'], value_vars=[f"{c}_precio" for c in ciudades_lista],
        var_name='ciudad', value_name='precio_kg'
    )
    df_precios['ciudad'] = df_precios['ciudad'].str.replace('_precio', '')
    
    df_variaciones = pd.melt(
        df_limpio_mes, id_vars=['producto', 'categoria'], value_vars=[f"{c}_var_porcentaje" for c in ciudades_lista],
        var_name='ciudad', value_name='var_mensual_porcentaje'
    )
    df_variaciones['ciudad'] = df_variaciones['ciudad'].str.replace('_var_porcentaje', '')
    
    df_fact_mes = pd.merge(df_precios, df_variaciones, on=['producto', 'categoria', 'ciudad'])
    
    # Agregar la columna identificadora como FECHA REAL
    df_fact_mes['periodo'] = fecha_periodo
    
    # Guardar en el acumulador global de hechos
    todos_los_hechos.append(df_fact_mes)

# 3. CONSOLIDACIÓN Y EXPORTACIÓN FINAL (Fuera del bucle)
print("\n Consolidando todos los meses en archivos maestros únicos...")

# Unificar todas las tablas de hechos de los 5 meses
df_fact_total = pd.concat(todos_los_hechos, ignore_index=True)

# LIMPIEZA NUMÉRICA RADICAL: Aseguramos transformación estricta a números limpios
for col in ['precio_kg', 'var_mensual_porcentaje']:
    # Quitamos caracteres raros y espacios remanentes
    df_fact_total[col] = df_fact_total[col].astype(str).str.replace(' ', '', regex=False)
    df_fact_total[col] = df_fact_total[col].replace(['-', 'n.d.', 'n.d', '', 'nan'], np.nan)
    # Convertimos a formato numérico (float/int). Los errores se vuelven nulos limpios en vez de texto
    df_fact_total[col] = pd.to_numeric(df_fact_total[col], errors='coerce')

# Eliminamos filas completamente vacías en métricas
df_fact_total.dropna(subset=['precio_kg', 'var_mensual_porcentaje'], how='all', inplace=True)

# Unificar y remover duplicados de productos para la dimensión
df_productos_total = pd.concat(todos_los_productos, ignore_index=True).drop_duplicates()
df_productos_total['producto'] = df_productos_total['producto'].astype(str).str.strip()

# 4. EXPORTACIÓN DE LOS 3 ARCHIVOS MÁSTERS PARA POWER BI
df_fact_total[['producto', 'ciudad', 'precio_kg', 'var_mensual_porcentaje', 'periodo']].to_csv("Fact_Precios_Sipsa.csv", index=False, encoding='utf-8-sig')
df_productos_total.to_csv("Dim_Productos_Sipsa.csv", index=False, encoding='utf-8-sig')
pd.DataFrame({'ciudad': ciudades_lista}).to_csv("Dim_Ciudades_Sipsa.csv", index=False, encoding='utf-8-sig')

print("\n ¡PROCESO COMPLETADO CON ÉXITO DESDE LA RAÍZ!")
print(f"Filas totales unificadas en la tabla de hechos: {len(df_fact_total)}")
