# 📚 Análisis de Brechas en Deserción Escolar en Colombia (2011–2024)

> Proyecto de Análisis de Datos — Datos Abiertos Colombia · Ministerio de Educación Nacional

---

## 📋 Descripción del problema

Colombia presenta brechas educativas profundas entre sus territorios. Aunque existen políticas nacionales de universalización de la educación básica y media, los indicadores de permanencia y rendimiento escolar varían significativamente entre departamentos. La deserción escolar en secundaria y media representa una pérdida de capital humano que impacta negativamente, a largo plazo, la movilidad social y el desarrollo regional.

---

## ❓ Pregunta de investigación

> **¿Cómo ha evolucionado la brecha en tasas de deserción escolar entre departamentos colombianos durante 2011–2024, y cuáles niveles educativos (transición, primaria, secundaria, media) concentran el mayor y más persistente rezago?**

---

## 💡 Hipótesis

> *"La pandemia de COVID-19 (2020–2021) provocó un aumento significativo en la deserción escolar, siendo el nivel de secundaria el más afectado, y los departamentos con menor conectividad a internet mostraron una recuperación más lenta en los años posteriores (2022–2024)."*

---

## 🗂️ Fuente de datos

| Atributo | Detalle |
|---|---|
| **Nombre** | Estadísticas en Educación Preescolar, Básica y Media por Departamento |
| **Entidad** | Ministerio de Educación Nacional de Colombia (MEN) |
| **Portal** | [datos.gov.co](https://www.datos.gov.co) |
| **Formato** | CSV (UTF-8, coma decimal, porcentajes con símbolo `%`) |
| **Registros** | 462 filas × 37 columnas |
| **Período** | 2011 – 2024 (14 años) |
| **Cobertura** | 34 departamentos + Bogotá D.C. |
| **Licencia** | Datos abiertos del Estado colombiano — uso libre con atribución |

### Variables principales

| Categoría | Variables |
|---|---|
| Identificación | `AÑO`, `CÓDIGO_DEPARTAMENTO`, `DEPARTAMENTO` |
| Población | `POBLACIÓN_5_16`, `TASA_MATRICULACIÓN_5_16` |
| Cobertura neta | General, transición, primaria, secundaria, media |
| Cobertura bruta | General, transición, primaria, secundaria, media |
| Deserción | General, transición, primaria, secundaria, media |
| Aprobación | General, transición, primaria, secundaria, media |
| Reprobación | General, transición, primaria, secundaria, media |
| Repitencia | General, transición, primaria, secundaria, media |
| Infraestructura | `TAMAÑO_PROMEDIO_DE_GRUPO`, `SEDES_CONECTADAS_A_INTERNET` |

---

## 📐 Métricas de éxito

| Métrica | Descripción |
|---|---|
| **Brecha interdepartamental** | Diferencia entre el percentil 90 y 10 de deserción por nivel y año |
| **Tendencia temporal** | Pendiente de regresión lineal de la deserción por departamento |
| **Índice de persistencia** | N.º de años consecutivos en que un depto. supera la media nacional |
| **Nivel crítico** | Nivel educativo con mayor varianza interdepartamental por año |
| **Efecto pandemia** | Cambio porcentual en deserción pre/post COVID por depto. y nivel |
| **Correlación cobertura–deserción** | ¿Mayor cobertura bruta se asocia con mayor deserción? |

### Criterios de éxito del análisis

- Identificar **al menos 5 departamentos** con rezago persistente (>5 años por encima de la media nacional).
- Determinar el **nivel educativo de mayor riesgo** con evidencia estadística.
- Cuantificar si las brechas se **redujeron o ampliaron** en el período post-pandemia (2022–2024).

---

## 🗄️ Estructura del proyecto

```
Proyecto_Analisis_de_Datos/
│
├── data/
│   └── MEN_ESTADISTICAS_EN_EDUCACION_EN_PREESCOLAR__BÁSICA_Y_MEDIA_POR_DEPARTAMENTO_20260424.csv
│
├── index.py               # Script principal de análisis
├── requirements.txt       # Dependencias del proyecto
└── README.md              # Este archivo
```

---

## ⚙️ Instalación y uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/<tu-usuario>/Proyecto_Analisis_de_Datos.git
cd Proyecto_Analisis_de_Datos
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Agregar el dataset

Coloca el archivo CSV en la carpeta `data/` del proyecto.

### 4. Ejecutar el análisis principal

```bash
python index.py
```

---

## 📦 Dependencias

```
pandas
numpy
```

> Archivo `requirements.txt` incluido en el repositorio.

---

## 👩‍💻 Autores
  
Bayron Meza Guzman  
Katerin Vanesa Lopez Moros

---

## 📄 Licencia

Los datos utilizados son de acceso público y provienen del portal de Datos Abiertos del Estado colombiano. El código de este repositorio es de uso libre con fines académicos.
