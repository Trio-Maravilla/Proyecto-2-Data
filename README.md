# Pobreza y Criminalidad en Colombia

Proyecto 2 de aplicaciones para la ciencia de datos
Sara Michelle Sánchez Botina - 20616172
Nelson David Donado Palacios - 20616172
Leonardo Gómez Cifuentes - 202611307
(Trio maravilla)

Análisis de datos que cruza los **delitos registrados** por el ministerio de defensa en Colombia con el **Índice de Pobreza Multidimensional (IPM)** del DANE para los años **2023 a 2025**.

**Pregunta Análitica:** ¿existe algún tipo de correlación entre la pobreza y la tipificación del crimen en los departamentos de Colombia?
---

## Contenido

- [Datos](#datos)
- [Metodología](#metodología)
- [Dashboard](#dashboard)
- [Limitaciones](#limitaciones)

---

### Datos originales (`Data/Raw`)

| Fuente | Archivos | Descripción |
|---|---|---|
| Registros de delitos (datos abiertos, corte 02/11/2026) | 12 CSV | Delitos contra el medio ambiente, informáticos, sexuales, extorsión, hurto a vehículos, hurto a personas, incautación de estupefacientes, masacres, piratería terrestre, secuestro, terrorismo y violencia intrafamiliar |
| DANE: IPM departamental | `IPM_Departamental_2023/2024/2025.xlsx` | Las 15 privaciones del IPM, el IPM total y la población por departamento |

Los CSV de delitos son pesados y se guardan con **Git LFS**. Instala Git LFS antes de clonar.

### Datos procesados (`Data/Processed`)

| Archivo | Contenido |
|---|---|
| `Metricas delitos segun departamento - 2023-2025.csv` | Tabla final: 33 departamentos (Bogotá cuenta como uno) × 3 años = 99 filas |
| `Metricas delitos segun departamento - Filtrado 2023/2024/2025.csv` | La misma tabla separada por año |
| `co_2018_MGN_DPTO_POLITICO.geojson` | Polígonos departamentales (Marco Geoestadístico Nacional 2018) para el mapa |

**Columnas principales de la tabla final:**
- `DEPARTAMENTO`, `ANO`
- `CANTIDAD_delito`: número de casos registrados
- `TASA_delito`: casos por cada 100.000 habitantes
- Las 15 dimensiones del IPM (analfabetismo, trabajo informal, hacinamiento crítico, etc.), `Total` (IPM) y `Población`

---

## Metodología

### 1. Limpieza (`Data_Cleaning.ipynb`)
1. **Carga** de los 12 datasets de delitos.
2. **Unificación de fechas:** algunos datasets traen otro formato (informáticos, masacres, extorsión).
3. **Normalización de departamentos:** se quitan las tildes y se homologan los nombres (por ejemplo, *San Andrés Islas → SAN ANDRES*).
4. **Filtro temporal:** se crea la columna `ANO` y se dejan solo los años 2023 a 2025.
5. **Nulos y duplicados:**
   - Se eliminan 353 registros sin `SEXO` en delitos sexuales (menos del 0,4 % del total).
   - Se elimina la columna `ZONA` de masacres, que estaba vacía por completo.
   - **Los duplicados se conservan:** no hay un identificador único, así que una fila repetida puede corresponder a varios casos reales ocurridos el mismo día y en el mismo lugar.
6. **Agregación** de los casos por departamento y año, y **merge** (outer) de los 12 delitos.
7. **Unión con el IPM** (2023, 2024 y 2025). Los delitos sin registro se llenan con 0.
8. **Cálculo de tasas** por cada 100.000 habitantes.

### 2. Análisis (`Data_Analysis.ipynb`)
- **Correlación de Spearman** entre cada tasa de delito y cada dimensión del IPM, para el promedio 2023-2025 y para cada año por separado. Se usa Spearman porque no supone que la relación sea lineal y porque es menos sensible a valores extremos, como Bogotá o Antioquia.
- **Frecuencia relativa:** qué porcentaje de cada delito a nivel nacional ocurre en cada departamento.

---

## Dashboard

El dashboard (`Src/app/app.py`)

1. **Pobreza** Mapa coroplético del IPM y de sus dimensiones por departamento y año.
2. **Diccionario del delito:** qué significa cada tipo de delito.
3. **Delitos** Las cifras de delitos de un departamento comparadas con el promedio nacional.
4. **Correlación** Gráfico de dispersión con su correlación de Spearman, con filtros de año, delito, indicador del IPM y un departamento para resaltar. Matriz de correlaciones entre los delitos y las dimensiones del IPM.
6. **Lo que los datos no dicen:** las advertencias para interpretar los resultados.


## Limitaciones

- **Correlación no es causalidad:** que dos indicadores suban juntos no significa que uno cause el otro.
- **Solo se ven los delitos denunciados:** donde se denuncia menos, el delito puede estar subrepresentado.
- **Cantidad, no gravedad:** todos los casos pesan lo mismo, sin importar qué tan grave sea el delito.