import streamlit as st
import json as json
import plotly.express as px
import pandas as pd
import unicodedata
from pathlib import Path
import matplotlib.pyplot as plt

CARPETA_DATOS = Path(__file__).parent.parent.parent / "Data/Processed"

cambios = {"BOGOTA, D.C.": "BOGOTA", "ARCHIPIELAGO DE SAN ANDRES, PROVIDENCIA Y SANTA CATALINA": "SAN ANDRES", "LA GUAJIRA": "GUAJIRA"}

def limpiar(texto):
    texto = texto.upper()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = cambios.get(texto, texto)
    return texto

@st.cache_data
def cargar_mapa():
    archivo = open(CARPETA_DATOS / "co_2018_MGN_DPTO_POLITICO.geojson", encoding="utf-8")
    with archivo:
        mapa = json.load(archivo)
    for zona in mapa["features"]:
        nombre = zona["properties"]["DPTO_CNMBR"]
        zona["properties"]["nombre_limpio"] = limpiar(nombre)
    return mapa

@st.cache_data
def cargar_datos(año):
    año_str = str(año)
    tabla = pd.read_csv(CARPETA_DATOS / f"Metricas delitos segun departamento - Filtrado {año_str}.csv")
    tabla["depto_limpio"] = tabla["DEPARTAMENTO"].apply(limpiar)
    return tabla

@st.cache_data
def cargar_todos():
    tabla = pd.read_csv(CARPETA_DATOS / "Metricas delitos segun departamento - 2023-2025.csv")
    tabla["depto_limpio"] = tabla["DEPARTAMENTO"].apply(limpiar)
    return tabla

def calcular(tabla, fila, sufijo):
    nacional = tabla[f"CANTIDAD_{sufijo}"].sum() / tabla["Población"].sum() * 100000
    tasa = fila[f"TASA_{sufijo}"]
    if nacional > 0:
        diferencia = (tasa - nacional) / nacional * 100
    else:
        diferencia = 0
    return tasa, diferencia
    
def main():
    st.set_page_config(page_title="IPM-ROBOS", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")
    st.markdown("""
    <style>
    .stApp, [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
    }
    
    h1, h2, h3, p, span, label, [data-testid="stMetricValue"] {  
        color: #1E293B !important;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: #F1F5F9 !important; 
        border-color: #1E293B !important;    
        color: #000000 !important;            
    }
    /* Flechita de la caja */
    [data-testid="stSelectbox"] div[data-baseweb="select"] span,
    [data-testid="stSelectbox"] div[data-baseweb="select"] input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    [data-testid="stSelectbox"] svg {
        fill: #000000 !important;
        color: #000000 !important;
    }
    
    /* Lista desplegable de la caja */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[role="listbox"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
    }

    /* Opciones dentro del menu */
    li[role="option"],
    li[role="option"] span,
    li[role="option"] div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"],
    li[role="option"]:hover span,
    li[role="option"][aria-selected="true"] span {
        background-color: #E2E8F0 !important;
        color: #000000 !important;
        
    }
       
    [data-testid="stMetricLabel"] span[role="img"] {
        font-size: 2.2rem !important;
        vertical-align: middle !important;
        color: #8B008B !important;
    }
    [data-testid="stMainBlockContainer"] {
    max-width: 1700px;
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("Pobreza y Delito: ¿Qué tanto influye el IPM en los hurtos en Colombia?")
    st.caption("Análisis departamental de la relación entre pobreza multidimensional y modalidades de robo (2023–2025).")
    st.sidebar.header("Datos")
    st.header("IPM Por departamento")
    izq_ipm, der_ipm = st.columns([4.5, 3])

    with izq_ipm:
        año_ipm = st.selectbox("AÑO - IPM", [2023, 2024, 2025])
        mapa = cargar_mapa()
        tabla = cargar_datos(año_ipm)
        fig = px.choropleth(
            tabla,
            geojson=mapa,
            locations="depto_limpio",
            featureidkey="properties.nombre_limpio",
            color="Total",
            color_continuous_scale=["#FDF5E6","#8B008B"],
            labels={"Total": "% IPM "},
            range_color=[0, 100],
            
        )
        fig.update_layout(height= 820,margin=dict(l=0, r=0, t=0, b=0),coloraxis_colorbar=dict(lenmode="pixels",len=650,
                                                                                              thickness=20,x=0.88,outlinecolor="#000000",outlinewidth=1.5, #grosor, distancia del mapa, color, y ancho del color
                                                                                              tickfont=dict(color="#000000", size=13), # El color de los numeros y el tamaño
                                                                                              title=dict(font=dict(color="#000000", size=14))), # el titulo de la barra 
                                                                                              dragmode="pan", paper_bgcolor="rgba(0,0,0,0)",
                                                                                              clickmode = "event+select")
        
        fig.update_geos(visible=False, bgcolor="rgba(0,0,0,0)",projection_type="mercator",lataxis_range=[-4.5, 13.5],lonaxis_range=[-79.5, -66.5])  
        fig.update_traces(marker_line_color="#000000",  marker_line_width=1.2) 
        evento = st.plotly_chart(fig, use_container_width=True, on_select="rerun",
            selection_mode="points",key = "mapa_ipm", config={"scrollZoom": False, "displayModeBar": False})
    with der_ipm:
        st.markdown("<div style='margin-top: 85px;'></div>", unsafe_allow_html=True)
        if evento and evento.selection:
                puntos_seleccionados = evento.selection.points
        else:
            puntos_seleccionados = []
        if puntos_seleccionados:
            punto = puntos_seleccionados[0]
            if "point_index" in punto:
                datos_mostrar = tabla.iloc[punto["point_index"]]
            else:
                depto_elegido = punto["location"]
                datos_mostrar = tabla[tabla["depto_limpio"] == depto_elegido].iloc[0]
                
            st.subheader(f"📍 {datos_mostrar['DEPARTAMENTO']} ({año_ipm})")
        else:
            datos_mostrar = tabla.select_dtypes("number").mul(tabla["Población"], axis=0).sum() / tabla["Población"].sum()
            st.subheader(f"Promedio General ({año_ipm})")
            
        c1, c2 = st.columns(2)
        analfabetismo = float(datos_mostrar["Analfabetismo"])
        logro_educativo_bajo = float(datos_mostrar["Bajo logro educativo"])
        barreras_primera_infancia = float(datos_mostrar["Barreras a servicios para cuidado de la primera infancia"])
        barreras_servicio_salud = float(datos_mostrar["Barreras de acceso a servicios de salud"])
        desempleo_prolongado = float(datos_mostrar["Desempleo de larga duración"])
        hacinamiento_critico = float(datos_mostrar["Hacinamiento crítico"])
        eliminacion_excretas = float(datos_mostrar["Inadecuada eliminación de excretas"])
        inasistencia_escolar = float(datos_mostrar["Inasistencia escolar"])
        material_inadecuado_paredes = float(datos_mostrar["Material inadecuado de paredes exteriores"])
        material_inadecuado_pisos = float(datos_mostrar["Material inadecuado de pisos"])
        rezago_escolar = float(datos_mostrar["Rezago escolar"])
        sin_acceso_al_agua = float(datos_mostrar["Sin acceso a fuente de agua mejorada"])
        sin_aseguramiento_salud = float(datos_mostrar["Sin aseguramiento en salud"])
        trabajo_infantil = float(datos_mostrar["Trabajo infantil"])
        trabajo_informal = float(datos_mostrar["Trabajo informal"])
        with c1: 
            st.metric(":material/menu_book: Analfabetismo", f"{analfabetismo:.1f}%")
            st.metric(":material/school: Bajo logro educativo", f"{logro_educativo_bajo:.1f}%")
            st.metric(":material/child_care: Cuidado infancia", f"{barreras_primera_infancia:.1f}%")
            st.metric(":material/local_hospital: Acceso servicios de salud", f"{barreras_servicio_salud:.1f}%")
            st.metric(":material/hourglass_empty: Desempleo prolongado", f"{desempleo_prolongado:.1f}%")
            st.metric(":material/groups: Hacinamiento", f"{hacinamiento_critico:.1f}%")
            st.metric(":material/wc: Eliminacion excretas", f"{eliminacion_excretas:.1f}%")
            st.metric(":material/backpack: Inasistencia escolar", f"{inasistencia_escolar:.1f}%")
        with c2: 
            st.metric(":material/house: Material inadecuado de paredes", f"{material_inadecuado_paredes:.1f}%")
            st.metric(":material/layers: Material inadecuado de pisos", f"{material_inadecuado_pisos:.1f}%")
            st.metric(":material/trending_down: Rezago escolar", f"{rezago_escolar:.1f}%")
            st.metric(":material/water_drop: Sin acceso al agua", f"{sin_acceso_al_agua:.1f}%")
            st.metric(":material/health_and_safety: Sin aseguramiento en salud", f"{sin_aseguramiento_salud:.1f}%")
            st.metric(":material/child_friendly: Trabajo infantil", f"{trabajo_infantil:.1f}%")
            st.metric(":material/construction: Trabajo informal", f"{trabajo_informal:.1f}%")
            
    st.divider()
    
    # Segundo mapa - Sobre robos
    
    st.header("Tipos de robo")
    st.markdown("""
    * **Delitos contra el medio ambiente:** Dañar o explotar ilegalmente la naturaleza, como talar bosques, contaminar ríos, traficar animales o hacer minería ilegal. Se cuenta por casos.
    * **Delitos informáticos:** Crímenes cometidos por internet o dispositivos electrónicos. Incluye hackear sistemas, robar contraseñas o datos personales, crear páginas falsas para estafar (phishing), usar virus y robar dinero de cuentas bancarias.
    * **Delitos sexuales:** Cualquier agresión o abuso contra la libertad sexual de alguien, como violaciones, tocamientos abusivos o explotación sexual. Se cuenta por el número de víctimas.
    * **Extorsión:** Amenazar o presionar a alguien para obligarlo a hacer algo (generalmente pagar dinero) a cambio de no hacerle daño a él, a su familia o a su negocio. Se cuenta por víctimas.
    * **Hurto a vehículos:** El robo de carros, camionetas o motos. Se cuenta por la cantidad de vehículos robados (unidades), no por personas.
    * **Hurto a personas:** El robo directo de las cosas de valor que alguien lleva encima (celular, billetera, bolso, etc.). Se cuenta por víctimas.
    * **Incautación de estupefacientes:** No es un delito contra un ciudadano, sino el registro de las drogas ilegales que la Policía logra decomisar en sus operativos. Estos datos van de enero de 2010 a julio de 2026.
    * **Masacres:** El asesinato intencional y al mismo tiempo de 3 o más personas indefensas en un mismo lugar y por un mismo atacante (sin contar enfrentamientos entre bandas criminales). Se cuenta tanto por casos como por víctimas (medido así desde 2022).
    * **Piratería terrestre:** Asaltar camiones de carga o buses de pasajeros para robar la mercancía o los bienes que llevan, ya sea en plena carretera o cuando están estacionados. Se cuenta por las personas afectadas.
    * **Secuestro:** Retener a una persona contra su voluntad. Incluye tanto los casos donde no se pide nada a cambio como aquellos donde exigen dinero o condiciones para liberarla.
    * **Terrorismo:** Ataques graves (con explosivos o medios destructivos) diseñados para sembrar pánico en la población y poner en peligro vidas, edificios, transporte o comunicaciones. Se cuenta por casos.
    * **Violencia intrafamiliar:** Maltrato físico o psicológico dentro del hogar hacia cualquier miembro de la familia o hacia personas que estén bajo el cuidado de alguien en esa casa. Se cuenta por víctimas.""")
    
    st.header("Robos por departamento")
    
    delitos = {"Medio ambiente":"del_med_ambiente", 
                            "Informaticos":"del_informaticos",
                            "Sexuales":"del_sexuales",
                            " Extorción":"extorsion",
                            "Hurto vehiculos":"hurto_vehiculos",
                            "Hurto personas":"hurto_personas",
                            "Incautacion":"incautacion_estupefacientes",
                            "Masacres":"masacres",
                            "Pirateria Terrestre":"pirateria_terrestre",
                            "Secuestro":"secuestro",
                            "Terrorismo":"terrorismo",
                            "Violencia intrafamiliar":"violencia_intrafamiliar"}
    f1,f2,f3 = st.columns(3)
    with f1:
                año_robo = st.selectbox("AÑO - ROBO", [2023, 2024, 2025])
                tabla_robo = cargar_datos(año_robo)
                tabla_todos = cargar_todos()
                
    with f2:
                depto = st.selectbox("DEPARTAMENTO",["AMAZONAS","ANTIOQUIA","ARAUCA","ATLANTICO",
                                                    "BOGOTA","BOLIVAR","BOYACA","CALDAS","CAQUETA",
                                                    "CASANARE","CAUCA","CESAR","CHOCO","CORDOBA","CUNDINAMARCA",
                                                    "GUAINIA","GUAVIARE","HUILA","GUAJIRA","MAGDALENA","META","NARIÑO",
                                                    "NORTE DE SANTANDER","PUTUMAYO","QUINDIO","RISARALDA","SAN ANDRES",
                                                    "SANTANDER","SUCRE","TOLIMA","VALLE DEL CAUCA","VAUPES","VICHADA"])
    with f3:
        delito = st.selectbox("DELITOS ", list(delitos.keys()))
            
    fila_elegida = tabla_robo[tabla_robo["DEPARTAMENTO"] == depto].iloc[0]
    st.subheader(f"📍 {depto} ({año_robo})")
    
    izq_robo, der_robo = st.columns([1,1])
    
    with izq_robo:
        
        c1, c2 = st.columns(2)
        with c1:
            tasa, dif = calcular(tabla_robo, fila_elegida, "del_med_ambiente")
            st.metric(":material/eco: Medio ambiente", f"{tasa:,.1f}",
                       delta=f"{dif:+.0f}% vs. país", delta_color="inverse")

            tasa, dif = calcular(tabla_robo, fila_elegida, "del_informaticos")
            st.metric(":material/computer: Informáticos", f"{tasa:,.1f}",
                      delta=f"{dif:+.0f}% vs. país", delta_color="inverse")
            
            tasa, dif = calcular(tabla_robo, fila_elegida, "del_sexuales")
            st.metric(":material/gavel: Sexuales", f"{tasa:,.1f}",
                      delta=f"{dif:+.0f}% vs. país", delta_color="inverse")

            tasa, dif = calcular(tabla_robo, fila_elegida, "extorsion")
            st.metric(":material/money_off: Extorsion", f"{tasa:,.1f}",
                      delta=f"{dif:+.0f}% vs. país", delta_color="inverse")
            tasa, dif = calcular(tabla_robo, fila_elegida, "hurto_vehiculos")
            st.metric(":material/directions_car: Hurto vehiculos", f"{tasa:,.1f}",
                      delta=f"{dif:+.0f}% vs. país", delta_color="inverse")

            tasa, dif = calcular(tabla_robo, fila_elegida, "hurto_personas")
            st.metric(":material/account_balance_wallet: Huerto personas", f"{tasa:,.1f}",
                      delta=f"{dif:+.0f}% vs. país", delta_color="inverse")
            
        with c2:
            tasa, dif = calcular(tabla_robo, fila_elegida, "incautacion_estupefacientes")
            st.metric(":material/science: Incautacion estupefacientes", f"{tasa:,.1f}",
                      delta=f"{dif:+.0f}% vs. país", delta_color="inverse")

            tasa, dif = calcular(tabla_robo, fila_elegida, "masacres")
            st.metric(":material/crisis_alert: masacres", f"{tasa:,.1f}",
                      delta=f"{dif:+.0f}% vs. país", delta_color="inverse")
            
            tasa, dif = calcular(tabla_robo, fila_elegida, "pirateria_terrestre")
            st.metric(":material/local_shipping: Pirateria terrestre", f"{tasa:,.1f}",
                      delta=f"{dif:+.0f}% vs. país", delta_color="inverse")

            tasa, dif = calcular(tabla_robo, fila_elegida, "secuestro")
            st.metric(":material/lock_person: Secuestro", f"{tasa:,.1f}",
                      delta=f"{dif:+.0f}% vs. país", delta_color="inverse")
            tasa, dif = calcular(tabla_robo, fila_elegida, "terrorismo")
            st.metric(":material/explosion: Terrorismo", f"{tasa:,.1f}",
                      delta=f"{dif:+.0f}% vs. país", delta_color="inverse")

            tasa, dif = calcular(tabla_robo, fila_elegida, "violencia_intrafamiliar")
            st.metric(":material/family_restroom: Violencia intrafamiliar", f"{tasa:,.1f}",
                      delta=f"{dif:+.0f}% vs. país", delta_color="inverse")
        
        

       
    with der_robo:
        with st.container(border=True):
            columna_tasa = f"TASA_{delitos[delito]}"
            tabla_robo["Top"] = tabla_robo["DEPARTAMENTO"] == depto
            
            fig_rank = px.bar(tabla_robo,x=columna_tasa,y="DEPARTAMENTO",orientation="h",color="Top",
                color_discrete_map={True: "#8B008B", False: "#FDF5E6"},labels={columna_tasa: "Casos por 100.000 habitantes"},)
            
            fig_rank.update_layout(height=800, showlegend=False, title=f"Ranking de {delito} en ({año_robo})",
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#000000",margin=dict(r=70))
            fig_rank.update_yaxes(categoryorder="total ascending")
            fig_rank.update_traces(texttemplate="%{x:,.1f}",textposition="outside",cliponaxis=False)
            st.plotly_chart(fig_rank, width="stretch", config={"displayModeBar": False})
            
    nombre_delito = delitos[delito]
    nom_tasa= f"TASA_{nombre_delito}"
    nom_cantidad = f"CANTIDAD_{nombre_delito}"
    serie_depto = tabla_todos[tabla_todos["DEPARTAMENTO"] == depto][["ANO", nom_tasa]]
    serie_depto.columns = ["Año", "Tasa"]
    serie_depto["Serie"] = depto
    
    nacional = tabla_todos.groupby("ANO").agg( casos=(nom_cantidad, "sum"), poblacion=("Población", "sum")).reset_index()
    nacional["Tasa"] = nacional["casos"] / nacional["poblacion"] * 100000
    nacional["Año"] = nacional["ANO"]
    nacional["Serie"] = "Colombia"

    datos_linea = pd.concat([serie_depto, nacional[["Año", "Tasa", "Serie"]]],ignore_index=True)
    
    with st.container(border=True):
        fig_evolucion = px.line(datos_linea, x="Año", y="Tasa", color="Serie", markers=True,
        color_discrete_map={depto: "#8B008B", "Colombia": "#EBA31C"})
        fig_evolucion.update_layout(height=500, showlegend=True, title=f"Evolucion del delito de {delito} en {depto}",
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#000000",margin=dict(r=70))
        fig_evolucion.update_xaxes(dtick=1, title=None)
        st.plotly_chart(fig_evolucion,width="stretch", config={"displayModeBar": False})
        
    st.divider()
    st.header("ROBO - IMP")
    
    
    
    indicadores = {"Analfabetismo":"Analfabetismo",
                   "Bajo logro educatico":"Bajo logro educativo",
                   "Cuidado primera infancia":"Barreras a servicios para cuidado de la primera infancia",
                   "Acceso servicio de saluid":"Barreras de acceso a servicios de salud",
                    "Desempleo prolongado":"Desempleo de larga duración",
                    "Hacinamiento critico":"Hacinamiento crítico",
                    "Eliminacion de excretas":"Inadecuada eliminación de excretas",
                    "Inasistencia escolar":"Inasistencia escolar",
                    "Material inadecuado paredes":"Material inadecuado de paredes exteriores",
                    "Materias inadecuado pisos":"Material inadecuado de pisos",
                    "Regazo escolar":"Rezago escolar",
                    "Sin acceso al agua":"Sin acceso a fuente de agua mejorada",
                    "Sin aseguramiento en salud":"Sin aseguramiento en salud",
                    "Trabajo infantil":"Trabajo infantil",
                    "Trabajo informal":"Trabajo informal"}
    
    fi1,fi2,fi3,fi4 = st.columns(4)
    
    with fi1:
        años = st.selectbox("AÑOS", [2023, 2024, 2025])
        tabla_correlaciones = cargar_datos(años)

    with fi2: 
        depto_2 = st.selectbox("DEPARTAMENTOS",["Ninguno","AMAZONAS","ANTIOQUIA","ARAUCA","ATLANTICO",
                                                    "BOGOTA","BOLIVAR","BOYACA","CALDAS","CAQUETA",
                                                    "CASANARE","CAUCA","CESAR","CHOCO","CORDOBA","CUNDINAMARCA",
                                                    "GUAINIA","GUAVIARE","HUILA","GUAJIRA","MAGDALENA","META","NARIÑO",
                                                    "NORTE DE SANTANDER","PUTUMAYO","QUINDIO","RISARALDA","SAN ANDRES",
                                                    "SANTANDER","SUCRE","TOLIMA","VALLE DEL CAUCA","VAUPES","VICHADA"])
            
    with fi3:
        lista = []
        for i in delitos.keys():
            
            lista.append(i)
            
        delito_2 = st.selectbox("DELITOS",lista )
        
    with fi4:
        lista_indicadores = []
        for d in indicadores.keys():
            lista_indicadores.append(d)
        indices_ipm = st.selectbox("Dimension",lista_indicadores)
        
    indicador = indicadores[indices_ipm]
    crimen= f"TASA_{delitos[delito_2]}"
    tabla_correlaciones["Elegido"] = tabla_correlaciones["DEPARTAMENTO"] == depto_2
    
    col1,col2 = st.columns(2)
    with col1: 
        st.header("Grafico de dispersion")
        with st.container(border=True):
            
            fig_scatter = px.scatter(tabla_correlaciones, x=indicador,y=crimen,color="Elegido", color_discrete_map= { True: "#D53ED5", False:"#FDF5E6"},
                                    category_orders={"Elegido":[False,True]},hover_name="DEPARTAMENTO", labels={indicador:f"{indices_ipm} %", crimen:"Casos por 100.000 habitantes"})
            fig_scatter.update_traces(marker=dict(size=11, line=dict(width=1, color="#1E293B")))
            fig_scatter.update_layout(height=800, showlegend=False, title=f"{indices_ipm} vs. {delito_2} ({años})",paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",font_color="#000000",)
            fig_scatter.update_yaxes(rangemode="tozero")
            st.plotly_chart(fig_scatter,width="stretch", config={"displayModeBar": False})

    with col2:
        if depto_2 == "Ninguno":
            datos_mostrar = tabla_correlaciones.select_dtypes("number").mul(tabla_correlaciones["Población"], axis=0).sum() / tabla_correlaciones["Población"].sum()
            st.subheader("Promedio General")
        else:
            datos_mostrar = tabla_correlaciones[tabla_correlaciones["DEPARTAMENTO"] == depto_2].iloc[0]
            st.subheader(f"📍 {datos_mostrar['DEPARTAMENTO']} ({años})")
            
        c1, c2 = st.columns(2)
        analfabetismo = float(datos_mostrar["Analfabetismo"])
        logro_educativo_bajo = float(datos_mostrar["Bajo logro educativo"])
        barreras_primera_infancia = float(datos_mostrar["Barreras a servicios para cuidado de la primera infancia"])
        barreras_servicio_salud = float(datos_mostrar["Barreras de acceso a servicios de salud"])
        desempleo_prolongado = float(datos_mostrar["Desempleo de larga duración"])
        hacinamiento_critico = float(datos_mostrar["Hacinamiento crítico"])
        eliminacion_excretas = float(datos_mostrar["Inadecuada eliminación de excretas"])
        inasistencia_escolar = float(datos_mostrar["Inasistencia escolar"])
        material_inadecuado_paredes = float(datos_mostrar["Material inadecuado de paredes exteriores"])
        material_inadecuado_pisos = float(datos_mostrar["Material inadecuado de pisos"])
        rezago_escolar = float(datos_mostrar["Rezago escolar"])
        sin_acceso_al_agua = float(datos_mostrar["Sin acceso a fuente de agua mejorada"])
        sin_aseguramiento_salud = float(datos_mostrar["Sin aseguramiento en salud"])
        trabajo_infantil = float(datos_mostrar["Trabajo infantil"])
        trabajo_informal = float(datos_mostrar["Trabajo informal"])
        with c1: 
            st.metric(":material/menu_book: Analfabetismo", f"{analfabetismo:.1f}%")
            st.metric(":material/school: Bajo logro educativo", f"{logro_educativo_bajo:.1f}%")
            st.metric(":material/child_care: Cuidado infancia", f"{barreras_primera_infancia:.1f}%")
            st.metric(":material/local_hospital: Acceso servicios de salud", f"{barreras_servicio_salud:.1f}%")
            st.metric(":material/hourglass_empty: Desempleo prolongado", f"{desempleo_prolongado:.1f}%")
            st.metric(":material/groups: Hacinamiento", f"{hacinamiento_critico:.1f}%")
            st.metric(":material/wc: Eliminacion excretas", f"{eliminacion_excretas:.1f}%")
            st.metric(":material/backpack: Inasistencia escolar", f"{inasistencia_escolar:.1f}%")
        with c2: 
            st.metric(":material/house: Material inadecuado de paredes", f"{material_inadecuado_paredes:.1f}%")
            st.metric(":material/layers: Material inadecuado de pisos", f"{material_inadecuado_pisos:.1f}%")
            st.metric(":material/trending_down: Rezago escolar", f"{rezago_escolar:.1f}%")
            st.metric(":material/water_drop: Sin acceso al agua", f"{sin_acceso_al_agua:.1f}%")
            st.metric(":material/health_and_safety: Sin aseguramiento en salud", f"{sin_aseguramiento_salud:.1f}%")
            st.metric(":material/child_friendly: Trabajo infantil", f"{trabajo_infantil:.1f}%")
            st.metric(":material/construction: Trabajo informal", f"{trabajo_informal:.1f}%")
            
    lista_delitos = ["Todos"]
    for i in delitos.keys():
                
        lista_delitos.append(i)
                
                    
    delito_matriz = st.selectbox(" Delitos ", lista_delitos)
    
    
    
    numericas = tabla_todos.select_dtypes(include="number").columns
    excluir = ["ANO", "Población"]
    dimensiones_ipm = [c for c in numericas
                    if c not in excluir and not c.startswith(("CANTIDAD_", "TASA_"))]
    cols_tasas = [c for c in numericas if c.startswith("TASA_")]
    df_depto = (tabla_todos
                .groupby("DEPARTAMENTO")[cols_tasas + dimensiones_ipm]
                .mean())

    matriz_depto = (df_depto
                    .corr(method="spearman")
                    .loc[cols_tasas, dimensiones_ipm])
    matriz_depto = matriz_depto.round(2)
    
    if delito_matriz == "Todos":
            matriz_mostrar = matriz_depto
            alto = 450
    else:
        fila_delito = f"TASA_{delitos[delito_matriz]}"
        matriz_mostrar = matriz_depto.loc[[fila_delito]]
        alto = 220
    st.dataframe(matriz_mostrar)
    
    with st.expander("📌Notas de metodologia y advertencias",expanded=False):
        st.markdown("""
                    Para realizar el analisis se juntaron 12 archivos diferentes de delitos y 1 del DANE con la informacion del IPM
                    * **SESGOS**
                    * El analisis cuenta con la cantidad de robos registrados, esto no implica que sean los que mas ocurren sino los que mas estan registrados
                    * Tambien pueden haber manipulacion de datos para hacer que un pais no quede mal al momento del analisi""")
    
    
main()