#---------------------------------------------------
# Limpieza de datos
# Proyecto: Análisis de Brechas en deserción escolar en Colombia (2011-2024)
# Autores: Katerin Lopez Moros y Bayron Meza Guzman
#---------------------------------------------------

# En este script realizamos la limpieza y preparación de los datos del dataset original
# Para que esté listo para el análisis exploratorio y modelado posterior


# Importar librerías necesarias 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker as mtick
import warnings 
warnings.filterwarnings("ignore")

# Esta es la ruta del archivo CSV
RUTA_CSV = "data/MEN_ESTADISTICAS_EN_EDUCACION_EN_PREESCOLAR,_BÁSICA_Y_MEDIA_POR_DEPARTAMENTO_20260424.csv"

separador = "-" * 70

# ===================================== 
# 1. Cargamos el dataset para inspeccionarlo
# =====================================
print(separador)
print("CARGA DEL DATASET ORIGINAL")
print(separador)

df= pd.read_csv(RUTA_CSV, encoding="utf-8-sig")

# Mostramos las dimensiones originales del dataset
print(f"Dimensiones del dataset original: {df.shape[0]} filas × {df.shape[1]} columnas")
print(f"Período cubierto: {df['AÑO'].min()} – {df['AÑO'].max()}")
print(f"Columnas: {list(df.columns)}")


# =====================================
# 2. Inspeccionamos los duplicados para verificar que no hay 
# =====================================

print(separador)
print("1. Eliminación de DUPLICADOS")
print(separador)

# Duplicados exactos por columnas completas
duplicados_exactos = df.duplicated().sum()
print(f"Filas duplicadas exactas: {duplicados_exactos}")

# Duplicados por combinación de AÑO y DEPARTAMENTO
duplicados_clave = df.duplicated(subset=["AÑO", "DEPARTAMENTO"]).sum()
print(f"Filas duplicadas por (AÑO y DEPARTAMENTO): {duplicados_clave}") 

# Eliminación (por precaución, aunque no se encontraron duplicados)
df = df.drop_duplicates()
df = df.reset_index(drop=True)  # Reiniciamos el índice después de eliminar duplicados  

# Imprimimos el mensaje de confirmación
print(f"Filas tras eliminación de duplicados: {df.shape[0]}")
print("SIN DUPLICADOS - DATASET ÍNTEGRO. \n")


# =====================================
# 3. Ajustamos los tipos de datos 
# NOTA: Se hace antes del tratamiento de nulos para evitar problemas de conversión 
# y poder manejar los nulos númericamente (con NaN)
# =====================================

print(separador)
print("2. Ajuste de TIPOS DE DATOS")
print(separador)

# 3.1. CÓDIGO-DEPARTAMENTO → string de 2 dígitos para preservar los ceros del DANE (que mencionamos en el documento)
df["CODIGO_DEPARTAMENTO"] = (
    df["CÓDIGO_DEPARTAMENTO"]
    .astype(str)
    .str.strip() 
    .str.zfill(2)
)

# Mensaje de confirmación
print(" CÓDIGO_DEPARTAMENTO convertido a str con zfill(2) CON ÉXITO!.")

# 3.2. DEPARTAMENTO → mayúsculas sin espacios extras
df["DEPARTAMENTO"] = (
    df["DEPARTAMENTO"]
    .str.strip() 
    .str.upper() 
)

# Mensaje de confirmación
print(" DEPARTAMENTO convertido a str + upper CON ÉXITO!.")    

# 3.3. AÑO → entero (int) para validar el rango 
df["AÑO"] = pd.to_numeric(df["AÑO"], errors="coerce").astype("int64")
fuera_de_rango = df[~df["AÑO"].between(2011, 2024)]
print(f" AÑO convertido a int CON ÉXITO! Valores fuera de rango (2011-2024): {len(fuera_de_rango)}")

# 3.4. Columnas de porcentajes: strip('%'), coma a punto, y convertir a float64

# Aquí creamos una función reutilizable 
def limpiar_porcentaje(serie: pd.Series) -> pd.Series:
    """Convierte columna de valores tipo '3,5%' a float64"""
    return (
        serie.astype(str)
            .str.strip() 
            .str.replace("%", "", regex=False) 
            .str.replace(",", ".", regex=False) 
            .str.replace("nan", "", regex=False) 
            .pipe(pd.to_numeric, errors="coerce")
    )

# Identificamos las columnas de porcentajes (que terminan con '%') y aplicamos la función
cola_porcentajes = [
    col for col in df.columns 
    if df[col].astype(str).str.contains("%").any()
]

print(f"\n Columnas identificadas con símbolo '%' detectadas ({len(cola_porcentajes)}):")
for col in cola_porcentajes:
    df[col] = limpiar_porcentaje(df[col])
    # Mensaje de confirmación para cada columna
    print(f"   → Columna '{col}' limpiada y convertida a float64 CON ÉXITO!")

# Mensaje de confirmación final
print(f"\nTotal de columnas convertidas a float64: {len(cola_porcentajes)}")

# 3.5. Columnas numéricas restantes: convertimos a float64 (si no lo son ya) para facilitar el análisis posterior
cola_num_extra =["POBLACIÓN_5_16", "SEDES_CONECTADAS_A_INTERNET", "TAMAÑO_PROMEDIO_DE_GRUPO"]

for col in cola_num_extra:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col].astype(str)
            .str.replace(",", ".", regex=False), 
            errors="coerce"
        )
        print(f"   → Columna '{col}' convertida a float64 CON ÉXITO!")

# Mensaje de confirmación final
print(f"\nTotal de columnas numéricas convertidas a float64: {len(cola_num_extra)}")

# 3.6. DEPARTEMENTO Y CODIGO_DEPARTAMENTO: convertimos a categoría (category) para optimizar memoria y análisis posterior
df["DEPARTAMENTO"] = df["DEPARTAMENTO"].astype("category")
df["CODIGO_DEPARTAMENTO"] = df["CODIGO_DEPARTAMENTO"].astype("category")
print("\n DEPARTAMENTO y CODIGO_DEPARTAMENTO convertidos a category CON ÉXITO!")

# Resumen de tipos de datos tras ajustes
print("\nTipos de datos tras ajustes:")
resumen_tipos = df.dtypes.astype(str).value_counts().rename_axis("Tipo").reset_index(name="Cantidad")
print(resumen_tipos.to_string(index=False))



# =====================================
# 4.Tratamiento de valores nulos 
# Se hace después de ajustar los tipos de datos para evitar problemas de conversión 
# y poder manejar los nulos numéricamente (con NaN)
# ===================================== 

print(f"\n{separador}")
print("3. Tratamiento de VALORES NULOS")
print(separador)

nulos_post_conversion = df.isnull().sum()
cola_con_nulos = nulos_post_conversion[nulos_post_conversion > 0]

print("\n Columnas con nulos tras ajustes de tipos de datos:")
print(cola_con_nulos.to_string())

# 4.1. TAMAÑO_PROMEDIO_DE_GRUPO (231 nulos, 50%)
# NO SE IMPUTA 
# Se registra la máscara para filtrar en análisis posteriores
MASCARA_TAMAÑO = df["TAMAÑO_PROMEDIO_DE_GRUPO"].isna()
print(f"\n TAMAÑO_PROMEDIO_DE_GRUPO")
print(f"Nulos: {MASCARA_TAMAÑO.sum()}")
print(f"Años sin dato: {sorted(df.loc[MASCARA_TAMAÑO, 'AÑO'].unique().tolist())}")
print("Estrategia: Exclusión - NO SE IMPUTA (patrón estructural).")
print(f"Variable creada: df['TAMANO_DISPONIBLE']= True/False")
df["TAMANO_DISPONIBLE"] = ~MASCARA_TAMAÑO  # True si el dato está disponible, False si es nulo


# 4.2. SEDES_CONECTADAS_A_INTERNET (231 nulos, 50%)
# NO SE IMPUTA Mismo patrón estructural que TAMAÑO_PROMEDIO_DE_GRUPO
# Se crea mascara de disponibilidad 

MASCARA_INTERNET = df["SEDES_CONECTADAS_A_INTERNET"].isna()
print(f"\n SEDES_CONECTADAS_A_INTERNET")
print(f"Nulos: {MASCARA_INTERNET.sum()}")
print(f"Años sin dato: {sorted(df.loc[MASCARA_INTERNET, 'AÑO'].unique().tolist())}")
print("Estrategia: Exclusión - NO SE IMPUTA (patrón estructural).")
print(f"Variable creada: df['INTERNET_DISPONIBLE']= True/False")
df["INTERNET_DISPONIBLE"] = ~MASCARA_INTERNET  # True si el dato está disponible, False si es nulo  


# 4.3. DESERCIÓN_TRANSICIÓN (1 nulo, 0.2%)
# Un único registro puntual por lo que lo convertimos a 
# interpolacion lineal por departamento (método recomendado para series temporales con pocos nulos)

print(f"\n DESERCIÓN_TRANSICIÓN")
nulos_dp =df[df["DESERCIÓN_TRANSICIÓN"].isna()]
[["AÑO", "DEPARTAMENTO", "DESERCIÓN_TRANSICIÓN"]]
print(f"Registro faltante: \n {nulos_dp.to_string(index=True)}")

# Interpolación lineal por departamento ordenada por año
df = df.sort_values(["DEPARTAMENTO", "AÑO"]).reset_index(drop=True)  # Ordenamos por departamento y año para la interpolación
df["DESERCIÓN_TRANSICIÓN"] = (
    df.groupby("DEPARTAMENTO", observed=True)["DESERCIÓN_TRANSICIÓN"]
    .transform(lambda s: s.interpolate(method="linear", limit_direction="both"))
)

nulos_restantes_dt = df["DESERCIÓN_TRANSICIÓN"].isna().sum()
print(f"Nulos tras interpolación: {nulos_restantes_dt}")
print("Estrategia: Interpolación lineal por departamento CON ÉXITO!.")


# Hacemos una verificación final de los nulos tras el tratamiento
print(f"\n Nulos restantes por columna tras tratamiento (excluidas columnas de disponibilidad):")
cola_analisis = [
    col for col in df.columns 
    if col not in ["TAMANO_DISPONIBLE", "INTERNET_DISPONIBLE"]
]

resumen_nulos_final = df[cola_analisis].isnull().sum()
resumen_nulos_final = resumen_nulos_final[resumen_nulos_final > 0]

if resumen_nulos_final.empty:
    print("¡No quedan nulos en las columnas de análisis!")
else:
    print(resumen_nulos_final.to_string())



# =====================================
# 5. Correcciones de valores con replace, map y zip
# =====================================

print(f"\n{separador}")
print("4. Correcciones de VALORES con replace, map y zip")
print(separador)

# 5.1. replace() para estandarizar nombres de departamentos (si se detectan inconsistencias)
# El MEN a publicado historicamente algunos nombres de departamentos con variaciones (ej: "BOGOTÁ D.C." vs "BOGOTA D.C."), 
# por lo que hacemos una revisión y corrección manual si es necesario.

correciones_departamentos = {
    "BOGOTÁ D.C.": "BOGOTÁ D.C.",
    "BOGOTA"       : "BOGOTÁ D.C.",
    "NARINO"       : "NARIÑO",
    "VAUPES"       : "VAUPÉS",
    "CORDOBA"      : "CÓRDOBA",
    "GUAINIA"      : "GUAINÍA",
    "CHOCO"        : "CHOCÓ"
}

# Convertimos a str para aplicar el replace, luego volver a category
df["DEPARTAMENTO"] = (
    df["DEPARTAMENTO"]
    .astype(str)
    .replace(correciones_departamentos, regex=False)
    .astype("category")
)
print("replace()- correcciones tipográficas en DEPARTAMENTO CON ÉXITO!")
for original, corregido in correciones_departamentos.items():
    print(f"   → '{original}' corregido a '{corregido}'")


# 5.2. map() para agregar columna REGION geográfica
region_map = {
    "AMAZONAS"         : "Amazonia",
    "CAQUETÁ"          : "Amazonia",
    "GUAINÍA"          : "Amazonia",
    "GUAVIARE"         : "Amazonia",
    "PUTUMAYO"         : "Amazonia",
    "VAUPÉS"           : "Amazonia",
    "ANTIOQUIA"        : "Andina",
    "BOYACÁ"           : "Andina",
    "CALDAS"           : "Andina",
    "CUNDINAMARCA"     : "Andina",
    "HUILA"            : "Andina",
    "NARIÑO"           : "Andina",
    "NORTE DE SANTANDER": "Andina",
    "QUINDÍO"          : "Andina",
    "RISARALDA"        : "Andina",
    "SANTANDER"        : "Andina",
    "TOLIMA"           : "Andina",
    "BOGOTÁ D.C."      : "Andina",
    "ATLÁNTICO"        : "Caribe",
    "BOLÍVAR"          : "Caribe",
    "CESAR"            : "Caribe",
    "CÓRDOBA"          : "Caribe",
    "LA GUAJIRA"       : "Caribe",
    "MAGDALENA"        : "Caribe",
    "SAN ANDRÉS"       : "Caribe",
    "SUCRE"            : "Caribe",
    "CHOCÓ"            : "Pacífica",
    "CAUCA"            : "Pacífica",
    "VALLE DEL CAUCA"  : "Pacífica",
    "ARAUCA"           : "Orinoquía",
    "CASANARE"         : "Orinoquía",
    "META"             : "Orinoquía",
    "VICHADA"          : "Orinoquía",
}

df["REGION"] = df["DEPARTAMENTO"].astype(str).map(region_map).astype("category")

sin_region = df["REGION"].isna().sum()
print(f"\n map() - Columna REGION creada a partir de diccionario de departamentos -> región.")
print(f"Departamentos sin mapeo: {sin_region} (si es >0, revisar claves del diccionario)")
print(f"Regiones identificadas: {df['REGION'].cat.categories.tolist()}")



# 5.3. zip() para crear columna clave combinada DEPARTAMENTO_AÑO
df["CLAVE_DPT_AÑO"] =[
    f"{dpt}_{año}" 
    for dpt, año in zip(df["DEPARTAMENTO"].astype(str), df["AÑO"].astype(str))
]

print(f"\n zip() - Columna CLAVE_DPT_AÑO creada combinando DEPARTAMENTO y AÑO (ejemplo: '{df['CLAVE_DPT_AÑO'].iloc[0]}') CON ÉXITO!")

# 5.4. map() variable binaria PANDEMIA
df["PANDEMIA"] = df["AÑO"].map(lambda x: 1 if x >= 2020 else 0)
print(f"\n map() - Variable PANDEMIA (0/1) | registros con 1: {df['PANDEMIA'].sum()} | registros con 0: {df['PANDEMIA'].count() - df['PANDEMIA'].sum()} CON ÉXITO!")




# =====================================
# Deteccion y tratamiento de valores atípicos
# =====================================

print(f"\n{separador}")
print("5. Detección y tratamiento de VALORES ATÍPICOS")
print(separador)

# Variables de deserción por nivel educación (foco del proyecto)
variables_desercion = [
    "DESERCIÓN",
    "DESERCIÓN_TRANSICIÓN",
    "DESERCIÓN_PRIMARIA",
    "DESERCIÓN_SECUNDARIA",
    "DESERCIÓN_MEDIA"
]

# Filtramos solo las existentes en el dataframe
variables_desercion = [var for var in variables_desercion if var in df.columns]

print(f"\n ____ Regla del IQR (1.5x) por variable de deserción ____")
resumen_outliers=[]

for var in variables_desercion:
    serie= df[var].dropna()  # Excluimos nulos para el cálculo de IQR
    Q1 = serie.quantile(0.25)
    Q3 = serie.quantile(0.75)
    IQR = Q3 - Q1
    lim_inf = Q1 - 1.5 * IQR
    lim_sup = Q3 + 1.5 * IQR
    n_out = ((serie < lim_inf) | (serie > lim_sup)).sum()
    resumen_outliers.append({
        "Variable": var,
        "Q1": Q1,
        "Q3": Q3,
        "IQR": IQR,
        "Límite Inferior": lim_inf,
        "Límite Superior": lim_sup,
        "N° Outliers": n_out
    })

df_outliers = pd.DataFrame(resumen_outliers)
print(df_outliers.to_string(index=False))


# 6.1. NO eliminamos outliers - son señal analítica
print("""
    Decidimos NO eliminar los outliers
    - Justificación: En el contexto de análisis de deserción escolar, los valores atípicos pueden representar casos extremos pero reales (ej: departamentos con crisis educativas severas o mejoras significativas).
     · Los departamentos amazónicos y de la Orinoquía presentan tasas de
      deserción estructuralmente superiores a la media nacional. Eliminarlos
      equivale a borrar la brecha que el proyecto busca medir.
    · Los años 2020–2021 (pandemia) son, por diseño, atípicos temporales.
      Su eliminación destruiría la hipótesis central del proyecto.
    · Se etiquetan con la variable PANDEMIA (ya creada) para su tratamiento
      diferenciado en los modelos estadísticos.
""")

# 6.2. Visualización de outliers por variable de deserción (boxplot)

print(f"\n ____ Visualización de outliers con boxplot por variable de deserción ____")
fig, axes = plt.subplots(1, len(variables_desercion), figsize=(5 * len(variables_desercion), 6))
fig.suptitle(
    "Distribución de Tasas de Deserción por Nivel Educativo\n(Colombia 2011–2024 · todos los departamentos)",
    fontsize=13, fontweight="bold", y=1.02
)
 
colores = ["#2E75B6", "#548235", "#C00000", "#FF6B35", "#7030A0"]
 
for ax, var, color in zip(axes, variables_desercion, colores):
    datos = df[var].dropna()
    bp = ax.boxplot(datos, patch_artist=True, notch=False,
                    boxprops=dict(facecolor=color, alpha=0.6),
                    medianprops=dict(color="black", linewidth=2),
                    flierprops=dict(marker="o", markersize=3, alpha=0.4,
                                    markerfacecolor=color))
    ax.set_title(var.replace("DESERCIÓN_", "").replace("_", "\n").title(),
                 fontsize=10, fontweight="bold")
    ax.set_ylabel("Tasa (%)" if var == variables_desercion[0] else "")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:.1f}%"))
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.set_xticklabels([])
 
    # Anotar n y outliers
    n_out_var = df_outliers.loc[df_outliers["Variable"] == var, "N° Outliers"].values[0]
    ax.text(0.5, -0.08, f"n={len(datos)}  |  outliers={n_out_var}",
            ha="center", va="top", transform=ax.transAxes,
            fontsize=8, color="gray")
 
plt.tight_layout()
plt.savefig("data/boxplots_desercion.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Boxplots guardados en: data/boxplots_desercion.png  CON ÉXITO!")


# =====================================
# 7. Agregacion de datos
# =====================================

print(f"\n{separador}")
print("6. AGREGACIÓN DE DATOS")
print(separador)

# 7.1. Promedio nacional anual de deserción total (DESERCIÓN_INTRA_ANUAL_TOTAL) para visualizar tendencia temporal
print("\n ____ Promedio nacional por año_____")
agg_nacional = (
    df.groupby("AÑO", observed=True)[variables_desercion]
    .mean()
    .round(2)
    .reset_index()
)
print(agg_nacional.to_string(index=False))


# 7.2. Promedio por región geográfica para identificar brechas regionales
print("\n ____ Promedio por región geográfica_____")
agg_region = (
    df.groupby("REGION", observed=True)[variables_desercion]
    .mean()
    .round(2)
    .reset_index()
)

# 7.3. Promedio por departamento para todo el periodo
print("\n ____ Top 10 departamentos con mayor deserción total por promedio _____")
agg_departamento = (
    df.groupby("DEPARTAMENTO", observed=True)["DESERCIÓN"]
    .mean()
    .round(2)
    .sort_values(ascending=False)
    .reset_index()
    .rename(columns={"DESERCIÓN": "PROMEDIO_DESERCION_TOTAL"} )
)
print(agg_departamento.head(10).to_string(index=False))

# 7.4. Impacto de la pandemia: media pre (2018-2019) vs media post (2020-2021)
print("\n ____ Impacto de la pandemia: comparación pre vs durante (PANDEMIA)_____") 
agg_pandemia = (
    df[df["AÑO"] >= 2018]
        .groupby("PANDEMIA")[variables_desercion]
        .mean()
        .round(2)
)
agg_pandemia.index = agg_pandemia.index.map({0: "Pre-pandemia (2018-2019)", 1: "Durante pandemia (2020-2021)"})
print(agg_pandemia.to_string())


# =====================================
# 8. Guardamos el dataset limpio 
# =====================================

print(f"\n{separador}")
print("7. DATASET LIMPIO — RESUMEN FINAL")
print(separador)
 
RUTA_SALIDA = "data/MEN_EDUCACION_LIMPIO.csv"
df.to_csv(RUTA_SALIDA, index=False, encoding="utf-8-sig")
 
print(f"""
  Archivo guardado          : {RUTA_SALIDA}
  Dimensiones finales       : {df.shape[0]} filas × {df.shape[1]} columnas
  Columnas agregadas        :
    · TAMANO_DISPONIBLE     — máscara de disponibilidad (bool)
    · SEDES_DISPONIBLE      — máscara de disponibilidad (bool)
    · REGIÓN                — región geográfica de Colombia
    · CLAVE_DEPTO_AÑO       — clave combinada DEPARTAMENTO-AÑO
    · PANDEMIA              — flag 0/1 para años 2020-2021
  Nulos en columnas orig.   : 0  (DESERCIÓN_TRANSICIÓN interpolada)
  Outliers                  : DOCUMENTADOS, no eliminados
""")
 
print(f"\n{'=' * 70}")
print("  LIMPIEZA COMPLETADA EXITOSAMENTE")
print(f"{'=' * 70}\n")