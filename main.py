import os
import osmnx as ox
import networkx as nx
import folium
import streamlit as st
from streamlit_folium import st_folium
from geopy.geocoders import ArcGIS, Photon, Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import shapely.geometry as geom

st.set_page_config(page_title="Optimizador de Rutas Medellín", layout="wide")
st.title("🚚 Optimizador de Rutas de Entregas - Medellín")
st.markdown("Introduce la dirección de inicio y las entregas para visualizar la mejor ruta 🗺️")

@st.cache_resource
def cargar_grafo():
    nombre_archivo = "medellin.graphml"
    if os.path.exists(nombre_archivo):
        G = ox.load_graphml(nombre_archivo)
    else:
        st.info("🌐 Descargando grafo de Medellín (solo la primera vez)...")
        G = ox.graph_from_place("Medellín, Colombia", network_type='drive')
        ox.save_graphml(G, nombre_archivo)
    return G

with st.spinner("🗺️ Cargando grafo de Medellín..."):
    G = cargar_grafo()

# Polígono real de Medellín
AREA_MEDELLIN = ox.geocode_to_gdf("Medellín, Colombia").geometry.iloc[0]

def dentro_de_medellin(lat, lon):
    punto = geom.Point(lon, lat)
    return AREA_MEDELLIN.covers(punto)


from geopy.geocoders import ArcGIS, Photon, Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def obtener_coordenadas(direccion):
    try:
        if "," in direccion:
            lat_str, lon_str = direccion.split(",")
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            if dentro_de_medellin(lat, lon):
                return (lat, lon)
            else:
                st.warning(f"⚠️ Las coordenadas {direccion} están fuera del área de Medellín.")
                return None
    except:
        pass

    geoloc_arcgis = ArcGIS(timeout=10)
    geoloc_photon = Photon(user_agent="route_optimizer_app")
    geoloc_nominatim = Nominatim(user_agent="route_optimizer_app_nominatim", timeout=10)

    try:
        loc = geoloc_arcgis.geocode(direccion)
        if loc:
            lat, lon = loc.latitude, loc.longitude
            addr = (getattr(loc, "address", "") or "").lower()
            if any(x in addr for x in ["medellín","medellin","antioquia"]) and dentro_de_medellin(lat, lon):
                return (lat, lon)
            st.warning(f"⚠️ '{direccion}' no fue confirmada en Medellín por ArcGIS. Intentando Photon...")

        loc = geoloc_photon.geocode(direccion)
        if loc:
            lat, lon = loc.latitude, loc.longitude
            addr = (getattr(loc, "address", "") or "").lower()
            if any(x in addr for x in ["medellín","medellin","antioquia"]) and dentro_de_medellin(lat, lon):
                return (lat, lon)
            st.warning(f"⚠️ '{direccion}' no fue confirmada en Medellín por Photon. Intentando Nominatim...")

        loc = geoloc_nominatim.geocode(direccion)
        if loc:
            lat, lon = loc.latitude, loc.longitude
            addr = (getattr(loc, "address", "") or "").lower()
            if any(x in addr for x in ["medellín","medellin","antioquia"]) and dentro_de_medellin(lat, lon):
                return (lat, lon)
            st.warning(f"⚠️ '{direccion}' no fue confirmada en Medellín por Nominatim.")
    except (GeocoderTimedOut, GeocoderServiceError):
        st.error("❌ Error en geocodificación")

    st.error(f"❌ No se pudo obtener coordenadas para '{direccion}'.")
    return None


with st.sidebar:
    st.header("📍 Puntos de la ruta")
    inicio = st.text_input("Dirección de inicio (punto de salida)", placeholder="Ej: Carrera 45 #56-12, Medellín")
    num_entregas = st.number_input("Número de entregas:", min_value=1, max_value=10, value=3)
    entregas = [st.text_input(f"Entrega {i+1}", key=f"entrega_{i}") for i in range(num_entregas)]
    calcular = st.button("🚀 Calcular ruta")

if calcular:
    if not inicio.strip():
        st.error("❌ Debes ingresar una dirección de inicio.")
        st.stop()
    entregas = [e for e in entregas if e.strip()]
    if len(entregas) < 1:
        st.error("❌ Debes ingresar al menos una entrega válida.")
        st.stop()

    st.subheader("📍 Coordenadas obtenidas")
    coords_list = []
    inicio_coords = obtener_coordenadas(inicio)
    if inicio_coords:
        st.write(f"🏁 Inicio → {inicio_coords}")
        coords_list.append(("Inicio", inicio_coords))
    else:
        st.error("❌ No se pudo obtener la dirección de inicio.")
        st.stop()
    for entrega in entregas:
        coords = obtener_coordenadas(entrega)
        if coords:
            st.write(f"✅ {entrega} → {coords}")
            coords_list.append((entrega, coords))
    if len(coords_list) < 2:
        st.error("⚠️ No se obtuvieron suficientes coordenadas válidas.")
        st.stop()

    st.subheader("🧭 Cálculo de rutas")
    full_route = []
    for i in range(len(coords_list) - 1):
        start_coords = coords_list[i][1]
        goal_coords = coords_list[i + 1][1]
        st.write(f"**Ruta {i+1}:** {coords_list[i][0]} ➜ {coords_list[i+1][0]}")
        orig = ox.distance.nearest_nodes(G, start_coords[1], start_coords[0])
        dest = ox.distance.nearest_nodes(G, goal_coords[1], goal_coords[0])
        try:
            route_segment = nx.shortest_path(G, orig, dest, weight='length')
            full_route.extend(route_segment if i == 0 else route_segment[1:])
        except nx.NetworkXNoPath:
            st.warning(f"⚠️ No hay ruta entre {coords_list[i][0]} y {coords_list[i+1][0]}.")

    if not full_route:
        st.error("❌ No se pudo calcular ninguna ruta.")
        st.stop()

    st.session_state["coords_list"] = coords_list
    st.session_state["G"] = G
    st.session_state["full_route"] = full_route
    st.success("✅ Ruta calculada correctamente. ¡Ahora puedes usar el slider para simular el carro!")

if "full_route" in st.session_state:
    coords_list = st.session_state["coords_list"]
    G = st.session_state["G"]
    full_route = st.session_state["full_route"]
    nodes, _ = ox.graph_to_gdfs(G)

    st.subheader("🗺️ Mapa de la ruta")
    pos = st.slider("Posición del carro en la ruta", 0, len(full_route)-1, 0)

    base_map = folium.Map(location=coords_list[0][1], zoom_start=13)
    base_map = ox.plot_route_folium(G, full_route, route_map=base_map, color="blue", weight=5, opacity=0.8)

    for j, (direccion, coords) in enumerate(coords_list):
        color = "green" if j==0 else "red" if j==len(coords_list)-1 else "blue"
        folium.Marker(location=coords, popup=f"{j}. {direccion}", icon=folium.Icon(color=color)).add_to(base_map)

    coord = nodes.loc[full_route[pos]][["y","x"]].values.tolist()
    folium.Marker(location=coord, icon=folium.Icon(icon="car", prefix="fa", color="orange")).add_to(base_map)

    st_folium(base_map, width=1200, height=600)