"""
En este script se hacen transformaciones adicionales para el dashboard

Y se ejecuta despúes de el script de limpieza de datos
leyendo el csv limpio y guardando un nuevo csv con las transformaciones hechas
y actualiza en CSV limpio
"""

# Importaciones de librerías necesarias
import pandas as pd
import numpy as np
import os 
import warnings

from validacion import RUTA_LIMPIO 
warnings.filterwarnings('ignore')

# Creamos variables para las rutas de los archivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_LIMPIO_CSV = os.path.join(BASE_DIR, "data", "processed", "MEN_EDUCACION_LIMPIO.csv")

# Añadimos un separador para delimitar en la terminal
separador = "-" * 70

# _______________________________
# Hacemos la carga del csv limpio
# _______________________________
print(separador)
print("Transformaciones adicionales para el dashboard")
print(separador)

df= pd.read_csv(RUTA_LIMPIO_CSV, encoding="utf-8-sig")
print(f"Dataset ya cargado, con {df.shape[0]} filas y {df.shape[1]} columnas")

# Detectamos las columnas de deserción 
# Para ello creamos una función para detectar las columnas
def detectar_columnas(candidatos, df):
    for c in candidatos:
        if c in df.columns:
            return c
    return None

# Nombres de las columnas del dataset 
COL_ANIO = "AÑO"
COL_DEPTO = "DEPARTAMENTO"
COL_DESERCION = detectar_columnas(["DESERCIÓN", "DESERCIÓN"], df)
COL_DESER_SEC = detectar_columnas(["DESERCIÓN SECUNDARIA", "DESERCIÓN_SECUNDARIA"], df)

# _______________________________
# Añadimos la variable PERIODO
# _______________________________
print(f"\n{separador}")
print("1. Variable PERIODO")
print(separador)

df["PERIODO"] = df[COL_ANIO].apply(
    lambda x: "1. Pre - pandemia" if x < 2020
    else "2. Pandemia" if x <= 2021
    else "3. Recuperación"
)

print(f"Distribución de PERIODO: ")
print(df["PERIODO"].value_counts().sort_index().to_string())

# _______________________________
# Añadimos la variable DELTA_PANDEMIA
# Que hace referencia a la diferencia de deserción entre 
# 2019 y 2021 por departamento
# _______________________________
print(f"\n{separador}")
print("2. Variable DELTA_PANDEMIA")
print(separador)

desercion_2019 =(
    df[df[COL_ANIO] == 2019]
    .set_index(COL_DEPTO)[COL_DESERCION]
)

desercion_2021 = (
    df[df[COL_ANIO] == 2021]
    .set_index(COL_DEPTO)[COL_DESERCION]
)

delta = (desercion_2021 - desercion_2019).reset_index()
delta.columns = [COL_DEPTO, "DELTA_PANDEMIA"]

# Merge al dataset completo limpio 
if "DELTA_PANDEMIA" in df.columns:
    df = df.drop(columns=["DELTA_PANDEMIA"])
df = df.merge(delta, on=COL_DEPTO, how="left")

print(f" Top de los 5 departamentos más afectados: ")
top_5 = delta.sort_values("DELTA_PANDEMIA", ascending=False).head(5)
print(top_5.to_string(index=False))


# _______________________________
# Variable DELTA_RECUPERACION 
# Que hace referencia entre la diferencia de deserción 
# entre 2021 y 2024 por departamento
# _______________________________
print(f"\n{separador}")
print("3. Variable DELTA_RECUPERACION")
print(separador)

anio_maximo = df[COL_ANIO].max()

desercion_recuperacion = (
    df[df[COL_ANIO] == anio_maximo]
    .set_index(COL_DEPTO)[COL_DESERCION]
)

delta_rec = (desercion_recuperacion - desercion_2021).reset_index()
delta_rec.columns = [COL_DEPTO, "DELTA_RECUPERACION"]

# Merge al dataset completo limpio
if "DELTA_RECUPERACION" in df.columns:
    df = df.drop(columns=["DELTA_RECUPERACION"])
df = df.merge(delta_rec, on=COL_DEPTO, how="left")

print(f" Top de los 5 departamentos con mejor recuperación: ")
top_5_rec = delta_rec.sort_values("DELTA_RECUPERACION", ascending=True).head(5)
print(top_5_rec.to_string(index=False))

# _______________________________
# Variable CUARTIL_CONECTIVIDAD 
# El cual segmenta a los departamentos por nivel de conectividad
# _______________________________
print(f"\n{separador}")
print("4. Variable CUARTIL_CONECTIVIDAD")
print(separador)

COL_SEDES = detectar_columnas(["SEDES CONECTADAS A INTERNET", "SEDES_CONECTADAS_A_INTERNET"], df)

if COL_SEDES:
    df_con_sedes = df[df[COL_SEDES].notna()].copy()
    df_con_sedes["CUARTIL_CONECTIVIDAD"] = pd.qcut(
        df_con_sedes[COL_SEDES],
        q=4,
        labels=["Bajo", "Medio-Bajo", "Medio-Alto", "Alto"]
    )

    if "CUARTIL_CONECTIVIDAD" in df.columns:
        df = df.drop(columns=["CUARTIL_CONECTIVIDAD"])
    df = df.merge(
        df_con_sedes[["CLAVE_DPT_AÑO", "CUARTIL_CONECTIVIDAD"]],
        on="CLAVE_DPT_AÑO", how="left"
    )
    print(f" Distribución de cuartil: ")
    print(df["CUARTIL_CONECTIVIDAD"].value_counts().sort_index().to_string())
else: 
    print(" SEDES CONECTADAS A INTERNET no encontrada, por eso se omite el cuartil")


# _______________________________
# Variable TASA_RECUPERACION 
# Que hace referencia a que tan rápido baja la desercion post pandemia
# _______________________________
print(f"\n{separador}")
print("5. Variable TASA_RECUPERACION")
print(separador)

df = df.sort_values([COL_DEPTO, COL_ANIO]).reset_index(drop=True)
df["VARIACION_ANUAL"] = (
    df.groupby(COL_DEPTO, observed=True)[COL_DESERCION].diff()
)

print(f" Variación promedio por periodo: ")
print(
    df.groupby("PERIODO", observed = True)["VARIACION_ANUAL"]
    .mean()
    .round(3)
    .to_string()
)

# _______________________________
# Mensaje de ya guardado y que se añadio 
# _______________________________

print(f"\n{separador}")
print("GUARDADO")
print(separador)

df.to_csv(RUTA_LIMPIO_CSV, index=False, encoding="utf-8-sig")

print(f"""
Archivo actualizado : {RUTA_LIMPIO_CSV}
Dimensiones finales : {df.shape[0]} filas x {df.shape[1]} columnas
Variables nuevas añadidas:
    · PERIODO              — Pre-pandemia / Pandemia / Recuperación
    · DELTA_PANDEMIA       — diferencia deserción 2021 vs 2019
    · DELTA_RECUPERACION   — diferencia deserción {anio_maximo} vs 2021
    · CUARTIL_CONECTIVIDAD — nivel de conectividad (Bajo a Alto)
    · VARIACION_ANUAL      — cambio de deserción respecto al año anterior
""")

print(f"{separador}")
print( "Transformaciones completas")
print(f"{separador}")