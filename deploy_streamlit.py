import streamlit as st
import pandas as pd
import ast


# Ocultamos el header y el menú de Streamlit (opcional)
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .logo-container {
        position: fixed;
        top: 200px;
        left: 200px;
        z-index: 100;
    }
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Insertamos la imagen como logotipo en la esquina superior izquierda usando solo Streamlit
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.image("BannerRCD (1).jpg", width=700)
st.markdown('</div>', unsafe_allow_html=True)


# Contenido de la app
st.markdown("<h1 style='text-align: center; color: rgb(0,94,164);'>Búsqueda de jugadores S.T.</h1>", unsafe_allow_html=True)

# Cargar el archivo Excel
@st.cache_data
def load_data():
    return pd.read_excel("dataset_for_streamlit.xlsx")

# Cargar los datos
df = load_data()



# Función para extraer todas las direcciones de correo en la columna USUARIO
def extraer_scouts(df):
    scouts = set()  # Usamos un conjunto para evitar duplicados
    for usuarios in df['USUARIO'].dropna():
        usuarios_lista = ast.literal_eval(usuarios)  # Convertir la cadena de lista en una lista real
        scouts.update(usuarios_lista)  # Añadir todos los scouts a la lista
    return sorted(list(scouts))  # Devolver una lista ordenada

# Verificar si la columna 'USUARIO' existe
if 'USUARIO' in df.columns:
    # Obtener todos los scouts disponibles
    scouts_disponibles = extraer_scouts(df)

    # Permitir selección múltiple de scouts
    scouts_seleccionados = st.multiselect('Selecciona el SCOUT', scouts_disponibles)

    # Obtener posiciones disponibles y permitir selección múltiple
    posiciones_disponibles = df['POSICION_POWERBI'].dropna().unique()
    posicion = st.multiselect('Selecciona la posición', posiciones_disponibles)

    # Obtener ligas disponibles y permitir selección múltiple
    ligas_disponibles = df['LIGA'].dropna().unique()
    ligas_seleccionadas = st.multiselect('Selecciona las ligas', ligas_disponibles)

    # Aplicar los filtros solo si hay selección, si no, mostrar todos los jugadores
    df_filtrado = df.copy()

    # Filtrar por scouts seleccionados (si hay alguno seleccionado)
    if scouts_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['USUARIO'].apply(lambda x: any(scout in ast.literal_eval(x) for scout in scouts_seleccionados))]

    # Filtrar por posiciones seleccionadas (si hay alguna seleccionada)
    if posicion:
        df_filtrado = df_filtrado[df_filtrado['POSICION_POWERBI'].isin(posicion)]

    # Filtrar por ligas seleccionadas (si hay alguna seleccionada)
    if ligas_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado['LIGA'].isin(ligas_seleccionadas)]

    # Si no se seleccionan filtros, df_filtrado contendrá todos los jugadores
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
            'Fecha nacimiento': 'AÑO'
        }
        df_filtrado = df_filtrado.rename(columns=nuevos_nombres_columnas)

        # Mostrar jugadores filtrados
        df_filtrado['FIN CONTRATO'] = pd.to_datetime(df_filtrado['FIN CONTRATO'], errors='coerce').dt.strftime('%d/%m/%Y')

        # Convertir la columna 'AÑO' a datetime y formatearla
        df_filtrado['AÑO'] = pd.to_datetime(df_filtrado['AÑO'], errors='coerce').dt.strftime('%Y')
        df_filtrado['NOTA'] = df_filtrado['NOTA'].round(2)
        df_filtrado['NOTA DEF.'] = df_filtrado['NOTA DEF.'].round(2)
        df_filtrado['NOTA OF.'] = df_filtrado['NOTA OF.'].round(2)

        st.dataframe(df_filtrado[['NOMBRE', 'EQUIPO', 'FIN CONTRATO', 'AÑO', 'NOTA DEF.', 'NOTA OF.', 'NOTA']])

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
else:
    st.error("La columna 'USUARIO' no está presente en el archivo.")
