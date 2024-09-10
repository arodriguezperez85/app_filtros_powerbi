import streamlit as st
import pandas as pd

# Cargar el archivo Excel
@st.cache_data
def load_data():
    return pd.read_excel("dataset_for_streamlit.xlsx")

# Cargar los datos
df = load_data()

# Obtener posiciones disponibles y permitir selección múltiple
posiciones_disponibles = df['POSICION_POWERBI'].dropna().unique()
posicion = st.multiselect('Selecciona la posición', posiciones_disponibles)

# Obtener ligas disponibles y permitir selección múltiple
ligas_disponibles = df['LIGA'].dropna().unique()
ligas_seleccionadas = st.multiselect('Selecciona las ligas', ligas_disponibles)

# Filtrar jugadores por posición y liga seleccionadas
if ligas_seleccionadas and posicion:
    df_filtrado = df[(df['POSICION_POWERBI'].isin(posicion)) & (df['LIGA'].isin(ligas_seleccionadas))]
else:
    st.warning('Por favor, selecciona al menos una posición y una liga.')
    df_filtrado = pd.DataFrame()  # Crear un DataFrame vacío para evitar errores posteriores

# Si no hay jugadores después de filtrar, mostrar un mensaje
if df_filtrado.empty:
    st.warning('No se encontraron jugadores con los filtros seleccionados.')
else:
    # Definir las categorías de métricas
    metricas_fisicas = ['VELOCIDAD', 'COMPLEXIÓN', 'POTENCIA']
    metricas_defensivas = ['DUELOS DEFENSIVOS', 'TÁCTICA DEFENSIVA', '1x1', 'JUEGO AÉREO DEF.', 'MARCAJE EN ÁREA',
                           'CAPACIDAD DE JUEGO', 'MARCAJES EN ÁREA', 'COMUNICACIÓN', 'LECTURA DEFENSIVA']
    metricas_ofensivas = ['CAPACIDAD OFENSIVA', 'CALIDAD OFENSIVA', 'SAQUE DE BANDA', 'JUEGO AÉREO OF.',
                          'CALIDAD DE JUEGO CORTO', 'CALIDAD DE JUEGO LARGO', 'TOMA DE DECISIONES', 'RUPTURA', 'JUEGO DE ESPALDAS']
    metricas_generales = ['VALORACION AJUSTADA DEFENSIVA', 'VALORACION DEFENSIVA',
                          'VALORACION AJUSTADA OFENSIVA', 'VALORACION OFENSIVA', 'NOTA AJUSTADA', 'NOTA']

    # Función para crear sliders solo para métricas con valores distintos de 0
    def crear_sliders(df, metricas, categoria):
        st.subheader(f"Filtros {categoria}")
        filtros = {}
        for metrica in metricas:
            if df[metrica].notna().any() and (df[metrica] != 0).any():
                filtros[metrica] = st.slider(f'{metrica}', 0, 10, (0, 10))
        return filtros

    # Crear sliders para métricas Físicas, Defensivas, Ofensivas y Generales
    filtros_fisicos = crear_sliders(df_filtrado, metricas_fisicas, "Físicos")
    filtros_defensivos = crear_sliders(df_filtrado, metricas_defensivas, "Defensivos")
    filtros_ofensivos = crear_sliders(df_filtrado, metricas_ofensivas, "Ofensivos")
    filtros_generales = crear_sliders(df_filtrado, metricas_generales, "Generales")

    # Aplicar los filtros seleccionados a los jugadores filtrados
    def aplicar_filtros(df, filtros):
        for metrica, (min_val, max_val) in filtros.items():
            df = df[(df[metrica] >= min_val) & (df[metrica] <= max_val)]
        return df

    df_filtrado = aplicar_filtros(df_filtrado, filtros_fisicos)
    df_filtrado = aplicar_filtros(df_filtrado, filtros_defensivos)
    df_filtrado = aplicar_filtros(df_filtrado, filtros_ofensivos)
    df_filtrado = aplicar_filtros(df_filtrado, filtros_generales)

    # Renombrar las columnas en el DataFrame filtrado
    nuevos_nombres_columnas = {
        'NOMBRE JUGADOR': 'NOMBRE',
        'VALORACION DEFENSIVA': 'NOTA DEF.',
        'VALORACION OFENSIVA': 'NOTA OF.',
        'NOTA': 'NOTA',
        'Fecha Fin Contrato': 'FIN CONTRATO',
        'Fecha nacimiento': 'AÑO NACIMIENTO'
    }
    df_filtrado = df_filtrado.rename(columns=nuevos_nombres_columnas)

    # Mostrar jugadores filtrados
    st.dataframe(df_filtrado[['NOMBRE', 'EQUIPO', 'FIN CONTRATO', 'AÑO NACIMIENTO', 'NOTA DEF.', 'NOTA OF.', 'NOTA']])

    # Mostrar los comentarios de cada jugador
    jugador_seleccionado = st.selectbox('Selecciona un jugador para ver los comentarios', df_filtrado['NOMBRE'].unique())
    comentarios = df_filtrado[df_filtrado['NOMBRE'] == jugador_seleccionado]['COMENTARIOS_UNIFICADOS'].values

    if len(comentarios) > 0:
        comentarios_separados = comentarios[0].split('%')
        st.subheader(f"Comentarios para {jugador_seleccionado}")
        for comentario in comentarios_separados:
            st.write(comentario)
    else:
        st.warning('No hay comentarios disponibles para este jugador.')
