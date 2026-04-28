# Importaciones 
import os
import pandas as pd
import numpy as np

# Configuración 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "MEN_ESTADISTICAS_EN_EDUCACION_EN_PREESCOLAR,_BÁSICA_Y_MEDIA_POR_DEPARTAMENTO_20260424.csv",
)

COLS_ID   = ["AÑO", "CÓDIGO_DEPARTAMENTO", "DEPARTAMENTO", "POBLACIÓN_5_16"]
COLS_KEY  = [
    "DESERCIÓN", "DESERCIÓN_TRANSICIÓN", "DESERCIÓN_PRIMARIA",
    "DESERCIÓN_SECUNDARIA", "DESERCIÓN_MEDIA",
    "COBERTURA_NETA", "COBERTURA_BRUTA",
    "REPITENCIA", "APROBACIÓN", "REPROBACIÓN",
    "SEDES_CONECTADAS_A_INTERNET",
]
 
SEP       = "-" * 70


# =====================================
# Carga del dataset
# =====================================

df = pd.read_csv(FILE_PATH, dtype=str)

print(SEP)
print("DATASET CARGADO CORRECTAMENTE (sin conversión de tipos)")
print(SEP)
print(f"Forma del dataset : {df.shape[0]} filas × {df.shape[1]} columnas")
print(f"Período           : {df['AÑO'].min()} – {df['AÑO'].max()}")
print(f"Departamentos     : {df['DEPARTAMENTO'].nunique()}")
print()
print("Tipos de datos originales:")
print(df.dtypes.value_counts().to_string())


# =====================================
# 1. DUPLICADOS
# =====================================

print()
print(SEP)
print("1. DUPLICADOS")
print(SEP)
total_duplicados = df.duplicated().sum()
key_duplicados = df.duplicated(subset=["AÑO", "DEPARTAMENTO"]).sum()
print(f"Las filas duplicadas exactas son: {total_duplicados}")
print(f"Duplicados por (AÑO Y DEPARTAMENTO): {key_duplicados}")


# =====================================
# 2. VALORES NULOS
# =====================================

print()
print(SEP)
print("2. VALORES NULOS")
print(SEP)
nulos = df.isnull().sum()
nulos_pct = (nulos/ len(df) * 100).round(1)
ndf = pd.DataFrame({"nulos": nulos, "porcentaje %": nulos_pct})
cola_nulos = ndf[ndf["nulos"]> 0]
if cola_nulos.empty:
    print("No hay valores nulos.")
else:
    print(cola_nulos.to_string())

print(f"\nColumnas sin nulos: {(ndf['nulos'] == 0).sum()} de {len(ndf)}")


# =====================================
# 3. TIPOS DE DATOS
# =====================================

print()
print(SEP)
print("3. TIPOS DE DATOS (detalle por columna)")
print(SEP)
print(df.dtypes.to_string())


# =====================================
# 4. DISTRIBUCIONES
# =====================================

print()
print(SEP)
print("4. DISTRIBUCIONES")
print(SEP)
print(f"{'Variable': <35} {'Skewness': >9} Interpretación")
print("=" *50)
num_cola = df.select_dtypes(include="number").columns.drop([
    "AÑO", 
    "CÓDIGO_DEPARTAMENTO"
], errors="ignore")

for c in num_cola:
    sk = df[c].skew()
    if sk > 1:
        label = "Asimétrica derecha (cola alta)"
    elif sk < -1:
        label = "Asimétrica izquierda (cola baja)"
    else:
        label = "Aproximadamente simétrica"
    print(f"{c:<33} {sk:>9.2f} {label}")


# =====================================
# 5. CORRELACIONES
# =====================================

print()
print(SEP)
print("5. CORRELACIONES — Top 20 pares (|r| descendente)")
print(SEP)
correlacion = df[num_cola].corr()
pairs = [
    (correlacion.columns[i], correlacion.columns[j], correlacion.iloc[i, j])
    for i in range(len(correlacion.columns))
    for j in range(i + 1, len(correlacion.columns))
]
pairs_df = (
    pd.DataFrame(pairs, columns=["var1", "var2", "r"])
    .sort_values("r", key=abs, ascending=False)
    .reset_index(drop=True)
)
print(f"{'#':>3}  {'Variable 1':<35} {'Variable 2':<35} {'r':>7}")
print("-" * 85)
for i, row in pairs_df.head(20).iterrows():
    print(f"  {i+1:>2}  {row['var1']:<35} {row['var2']:<35} {row['r']:>7.3f}")


# =====================================
# 6. RESUMENN ESTADISTICO
# =====================================

print()
print(SEP)
print("4. RESUMEN ESTADÍSTICO (variables de interés)")
print(SEP)
cols_stat = [c for c in COLS_KEY if c in df.columns]
print(df[cols_stat].describe().round(2).to_string()) 


# =====================================
# 8. OBSERVACIONES
# =====================================

print()
print(SEP)
print("8. OBSERVACIONES AUTOMÁTICAS")
print(SEP)
 
obs = []
 
if total_duplicados == 0:
    obs.append(("OK",   "Sin duplicados exactos ni por clave (AÑO, DEPARTAMENTO)."))
else:
    obs.append(("ADVERTENCIA", f"{total_duplicados} filas duplicadas detectadas. Revisa antes de continuar."))
 
for c, pct in nulos_pct[nulos_pct > 0].items():
    nivel = "CRIT" if pct >= 30 else "ADVERTENCIA"
    obs.append((nivel, f"{c} tiene {pct}% de nulos — considera imputación o filtrar periodo."))
 
for c in num_cola:
    sk = df[c].skew()
    if abs(sk) > 3:
        obs.append(("INFO", f"{c}: skewness extremo ({sk:.2f}). Evalua transformación log."))
 
for _, row in pairs_df[pairs_df["r"].abs() == 1.0].iterrows():
    obs.append(("ADVERTENCIA", f"Correlación perfecta (r=1): {row['var1']} ↔ {row['var2']}. "
                        "Posible dependencia aritmética; evita usar ambas en modelos."))
 
for label, msg in obs:
    tag = {"OK": "[✓]", "ADVERTENCIA": "[!]", "CRIT": "[✗]", "INFO": "[i]"}.get(label, "[ ]")
    print(f"  {tag}  {msg}")
 
print()
print(SEP)
print("FIN DEL REPORTE")
print(SEP)