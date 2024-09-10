import streamlit as st
import pandas as pd

# Cargar el archivo Excel
@st.cache_data
def load_data():
    return pd.read_excel("dataset_for_streamlit.xlsx")

# Cargar los datos
df = load_data()
posiciones_disponibles = df['POSICION_POWERBI'].dropna().unique()
posicion = st.selectbox('Selecciona la posición', posiciones_disponibles)

# Asegura que no haya valores nulos
ligas_disponibles = df['LIGA'].dropna().unique()
liga = st.selectbox('Selecciona la liga', ligas_disponibles)

# Filtrando jugadores por posición y liga seleccionadas
df_filtrado = df[(df['POSICION_POWERBI'] == posicion) & (df['LIGA'] == liga)]

# Si no hay jugadores después de filtrar, mostrar un mensaje
if df_filtrado.empty:
    st.warning('No se encontraron jugadores con los filtros seleccionados.')
else:
    # Definir las categorías de métricas
    metricas_fisicas = ['VELOCIDAD', 'COMPLEXIÓN', 'POTENCIA']
    metricas_defensivas = ['DUELOS DEFENSIVOS', 'TÁCTICA DEFENSIVA', '1x1', 'JUEGO AÉREO DEF.', 'MARCAJE EN ÁREA',
                           'CAPACIDAD DE JUEGO',
                           'MARCAJES EN ÁREA', 'COMUNICACIÓN', 'LECTURA DEFENSIVA']
    metricas_ofensivas = ['CAPACIDAD OFENSIVA', 'CALIDAD OFENSIVA', 'SAQUE DE BANDA', 'JUEGO AÉREO OF.',
                          'CALIDAD DE JUEGO CORTO',
                          'CALIDAD DE JUEGO LARGO', 'TOMA DE DECISIONES', 'RUPTURA', 'JUEGO DE ESPALDAS']
    metricas_generales = ['VALORACION AJUSTADA DEFENSIVA', 'VALORACION DEFENSIVA',
                          'VALORACION AJUSTADA OFENSIVA', 'VALORACION OFENSIVA', 'NOTA AJUSTADA', 'NOTA']

    # Crear sliders para las métricas Físicas
    st.subheader("Filtros Físicos")
    filtros_fisicos = {}
    for metrica in metricas_fisicas:
        if df_filtrado[metrica].notna().any():
            filtros_fisicos[metrica] = st.slider(
                f'Selecciona el rango para {metrica}', 0, 10, (0, 10))

    # Aplicar filtros físicos
    for metrica, (min_val, max_val) in filtros_fisicos.items():
        df_filtrado = df_filtrado[(df_filtrado[metrica] >= min_val) & (
            df_filtrado[metrica] <= max_val)]

    # Crear sliders para las métricas Defensivas
    st.subheader("Filtros Defensivos")
    filtros_defensivos = {}
    for metrica in metricas_defensivas:
        if df_filtrado[metrica].notna().any():
            filtros_defensivos[metrica] = st.slider(
                f'Selecciona el rango para {metrica}', 0, 10, (0, 10))

    # Aplicar filtros defensivos
    for metrica, (min_val, max_val) in filtros_defensivos.items():
        df_filtrado = df_filtrado[(df_filtrado[metrica] >= min_val) & (
            df_filtrado[metrica] <= max_val)]

    # Crear sliders para las métricas Ofensivas
    st.subheader("Filtros Ofensivos")
    filtros_ofensivos = {}
    for metrica in metricas_ofensivas:
        if df_filtrado[metrica].notna().any():
            filtros_ofensivos[metrica] = st.slider(
                f'Selecciona el rango para {metrica}', 0, 10, (0, 10))

    # Aplicar filtros ofensivos
    for metrica, (min_val, max_val) in filtros_ofensivos.items():
        df_filtrado = df_filtrado[(df_filtrado[metrica] >= min_val) & (
            df_filtrado[metrica] <= max_val)]

    # Crear sliders para las métricas Generales (NOTA y NOTA AJUSTADA)
    st.subheader("Filtros Generales")
    filtros_generales = {}
    for metrica in metricas_generales:
        if df_filtrado[metrica].notna().any():
            filtros_generales[metrica] = st.slider(
                f'Selecciona el rango para {metrica}', 0, 10, (0, 10))

    # Aplicar filtros generales
    for metrica, (min_val, max_val) in filtros_generales.items():
        df_filtrado = df_filtrado[(df_filtrado[metrica] >= min_val) & (
            df_filtrado[metrica] <= max_val)]

    # Mostrar jugadores filtrados
    st.subheader(f"Jugadores filtrados para la posición {posicion} en {liga}")
    st.dataframe(df_filtrado[['ID', 'NOMBRE JUGADOR', 'EQUIPO', 'LIGA',
                 'VALORACION DEFENSIVA', 'VALORACION OFENSIVA', 'NOTA']])

    # Mostrar los comentarios de cada jugador
    jugador_seleccionado = st.selectbox(
        'Selecciona un jugador para ver los comentarios', df_filtrado['NOMBRE JUGADOR'].unique())

    # Filtrar los comentarios para el jugador seleccionado
    comentarios = df_filtrado[df_filtrado['NOMBRE JUGADOR'] ==
                              jugador_seleccionado]['COMENTARIOS_UNIFICADOS'].values

    if len(comentarios) > 0:
        comentarios_separados = comentarios[0].split('%')
        st.subheader(f"Comentarios para {jugador_seleccionado}")
        for comentario in comentarios_separados:
            st.write(comentario)
    else:
        st.warning('No hay comentarios disponibles para este jugador.')
