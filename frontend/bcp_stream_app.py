import streamlit as st
import requests
import pandas as pd
import re

# Interfaz de Streamlit
st.set_page_config(
    page_title="Buscador de Recursos RSGYAPE001",
    layout="centered"
)

st.title("Buscador de Recursos - RSGYAPE001")
st.info("Esta aplicación muestra recursos del grupo RSGYAPE001")

# Inicializar variables de estado para la selección de tipo
if 'recursos_mismo_nombre' not in st.session_state:
    st.session_state.recursos_mismo_nombre = []
    
if 'tipo_seleccionado' not in st.session_state:
    st.session_state.tipo_seleccionado = None
    
if 'search_original' not in st.session_state:
    st.session_state.search_original = ""
    
if 'resources_data' not in st.session_state:
    st.session_state.resources_data = []
    
if 'busqueda_realizada' not in st.session_state:
    st.session_state.busqueda_realizada = False

# Campo para buscar recursos específicos
search_term = st.text_input("Buscar recurso:", placeholder="Escriba el nombre del recurso a buscar")

# Añadir umbral de similitud
col1, col2 = st.columns([3, 1])
with col1:
    buscar_btn = st.button("Buscar Recursos", type="primary")
with col2:
    umbral_similitud = st.slider("Umbral:", min_value=0.0, max_value=1.0, value=0.3, step=0.1, format="%.1f")

# Función para manejar el cambio de tipo seleccionado
def on_tipo_change():
    # Forzar recálculo de similitudes
    st.session_state.busqueda_realizada = True

# Mostrar selector de tipo si hay recursos con el mismo nombre
if st.session_state.recursos_mismo_nombre:
    st.info(f"Se encontraron {len(st.session_state.recursos_mismo_nombre)} recursos con el nombre '{st.session_state.search_original}'. Por favor, seleccione el tipo de recurso:")
    tipos = [r['Tipo'] for r in st.session_state.recursos_mismo_nombre]
    tipo_seleccionado = st.selectbox("Seleccione el tipo:", tipos, key="selector_tipo", on_change=on_tipo_change)
    st.session_state.tipo_seleccionado = tipo_seleccionado

# Función simplificada para calcular similitud basada en subcadenas
def calcular_similitud(recurso, busqueda, tipo_filtro=None):
    if not busqueda:
        return 0
    
    # Convertir a minúsculas para comparación insensible a mayúsculas
    busqueda = busqueda.lower()
    nombre = recurso['Nombre'].lower()
    tipo = recurso['Tipo'].lower()
    ubicacion = recurso['Ubicación'].lower()
    
    # Si hay un filtro de tipo y no coincide, devolver 0
    if tipo_filtro and tipo_filtro.lower() != tipo:
        return 0
    
    # Calcular puntuación de similitud para diferentes casos
    score = 0
    
    # 1. Coincidencia exacta en nombre (máxima prioridad)
    if nombre == busqueda:
        if tipo_filtro and tipo == tipo_filtro.lower():
            return 1.0  # Coincidencia perfecta de nombre y tipo
        return 0.9  # Solo nombre coincide exactamente
    
    # 2. Nombre comienza con el término de búsqueda
    if nombre.startswith(busqueda):
        score = max(score, 0.8)
    
    # 3. El término es una palabra completa en el nombre
    if re.search(r'\b' + re.escape(busqueda) + r'\b', nombre):
        score = max(score, 0.7)
    
    # 4. El término está contenido en el nombre
    if busqueda in nombre:
        score = max(score, 0.6)
    
    # 5. Coincidencias en tipo (menor prioridad que el nombre)
    if busqueda in tipo:
        score = max(score, 0.5)
    
    # 6. Coincidencias en ubicación
    if busqueda in ubicacion:
        score = max(score, 0.4)
    
    # 7. Coincidencia parcial de caracteres en nombre
    chars_en_comun = sum(1 for c in busqueda if c in nombre)
    if len(busqueda) > 0:
        proporcion = chars_en_comun / len(busqueda)
        score = max(score, proporcion * 0.3)
    
    return score

# Función para procesar datos y mostrar resultados
def procesar_resultados(search_original, resources_data, tipo_seleccionado, umbral_similitud):
    # Si hay un término de búsqueda, calculamos similitud
    recursos_similitud = []
    
    # Calcular similitud para cada recurso con la función simplificada
    for i, resource in enumerate(resources_data):
        # Calcular similitud considerando el tipo seleccionado
        similitud = calcular_similitud(resource, search_original, tipo_seleccionado)
        
        # Guardar índice y similitud
        recursos_similitud.append((i, similitud))
    
    # Ordenar por similitud (mayor a menor)
    recursos_similitud.sort(key=lambda x: x[1], reverse=True)
    
    # Añadir columna de similitud al DataFrame
    similitudes_dict = {i: sim for i, sim in recursos_similitud}
    
    # Crear nuevo DataFrame con similitud
    recursos_con_similitud = []
    for i, resource in enumerate(resources_data):
        sim = similitudes_dict.get(i, 0)
        recurso_con_sim = resource.copy()
        # Mostrar similitud como porcentaje redondeado
        recurso_con_sim["Similitud"] = f"{sim:.2f}"
        # Indicar si supera el umbral
        recurso_con_sim["Coincide"] = "✓" if sim >= umbral_similitud else ""
        recursos_con_similitud.append(recurso_con_sim)
    
    # Si hay resultados con alguna similitud por encima del umbral
    recursos_coincidentes = [r for r in recursos_con_similitud if float(r["Similitud"]) >= umbral_similitud]
    
    if recursos_coincidentes:
        if tipo_seleccionado:
            st.success(f"Se encontraron {len(recursos_coincidentes)} recursos de tipo '{tipo_seleccionado}' con similitud ≥{umbral_similitud}")
        else:
            st.success(f"Se encontraron {len(recursos_coincidentes)} recursos con similitud ≥{umbral_similitud} de un total de {len(resources_data)}")
    else:
        st.warning(f"No se encontraron recursos con similitud ≥{umbral_similitud}, mostrando todos los recursos ({len(resources_data)})")
    
    # Crear DataFrame final
    df = pd.DataFrame(recursos_con_similitud)
    
    # Ordenar por similitud
    if "Similitud" in df.columns:
        df["Similitud"] = df["Similitud"].astype(float)
        df = df.sort_values(by="Similitud", ascending=False)
    
    # Función para aplicar estilos según la similitud
    def highlight_matches(row):
        # Convertir valor de similitud a float
        sim = float(row["Similitud"])
        
        # Si supera el umbral, aplicar estilo
        if sim >= umbral_similitud:
            return ['background-color: #2c3e50; color: white'] * len(row)
        else:
            return [''] * len(row)
    
    # Mostrar DataFrame con estilos
    st.dataframe(df.style.apply(highlight_matches, axis=1), use_container_width=True)
    
    # Añadir botón para copiar solo el recurso con mayor similitud
    if recursos_coincidentes:
        st.subheader("Recurso con mayor similitud:")
        mejor_recurso = recursos_coincidentes[0]  # El primero es el de mayor similitud
        
        # Mostrar información más completa del recurso
        st.markdown(f"""
        **Nombre:** {mejor_recurso['Nombre']}  
        **Tipo:** {mejor_recurso['Tipo']}  
        **Ubicación:** {mejor_recurso['Ubicación']}  
        **Similitud:** {mejor_recurso['Similitud']}
        """)
        
        # Código para copiar
        st.code(mejor_recurso['Nombre'], language="bash")
    
    return recursos_coincidentes

if buscar_btn:
    # Reiniciar algunos valores al hacer una nueva búsqueda
    st.session_state.tipo_seleccionado = None
    st.session_state.recursos_mismo_nombre = []
    st.session_state.search_original = search_term
    
    with st.spinner("Buscando recursos..."):
        try:
            # Siempre obtener todos los recursos
            url = "http://127.0.0.1:8000/azure-resources/"
            
            # Primero hacemos la búsqueda sin filtro para obtener todos los recursos
            response = requests.get(url, timeout=10)
            data_all = response.json()
            
            # Mostrar resultados
            if "error" in data_all:
                st.error(f"Error: {data_all['error']}")
            else:
                if not data_all["resources"]:
                    st.warning("No se encontraron recursos")
                else:
                    # Crear una tabla para mostrar todos los recursos
                    resources_data = []
                    for resource in data_all['resources']:
                        resources_data.append({
                            "Nombre": resource['name'],
                            "Tipo": resource['type'],
                            "Ubicación": resource.get('location', 'N/A')
                        })
                    
                    st.session_state.resources_data = resources_data
                    
                    if search_term:
                        # Verificar si hay recursos con nombres idénticos
                        nombres_recursos = [r['Nombre'].lower() for r in resources_data]
                        nombres_repetidos = {nombre for nombre in nombres_recursos if nombres_recursos.count(nombre) > 1}
                        
                        # Comprobar si la búsqueda coincide exactamente con algún nombre repetido
                        if search_term.lower() in nombres_repetidos:
                            # Encontrar todos los recursos con ese nombre
                            recursos_mismo_nombre = [r for r in resources_data if r['Nombre'].lower() == search_term.lower()]
                            st.session_state.recursos_mismo_nombre = recursos_mismo_nombre
                    
                    st.session_state.busqueda_realizada = True
        
        except requests.exceptions.ConnectionError:
            st.error("Error de conexión: No se pudo conectar con el servidor backend")
        except Exception as e:
            st.error(f"Error inesperado: {str(e)}")

# Procesar resultados si hay una búsqueda realizada o si se ha cambiado el tipo
if st.session_state.busqueda_realizada and st.session_state.resources_data:
    procesar_resultados(
        st.session_state.search_original, 
        st.session_state.resources_data, 
        st.session_state.tipo_seleccionado, 
        umbral_similitud
    )