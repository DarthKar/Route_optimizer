import os
import osmnx as ox
import networkx as nx
import folium
import time
from geopy.geocoders import ArcGIS, Photon
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


# --- Función auxiliar: obtener coordenadas de una dirección ---
def obtener_coordenadas(direccion):
    """Convierte una dirección en coordenadas (lat, lon) usando ArcGIS o Photon como respaldo."""
    geoloc_arcgis = ArcGIS(timeout=10)
    geoloc_photon = Photon(user_agent="route_optimizer_app")

    for intento in range(3):
        try:
            location = geoloc_arcgis.geocode(direccion)
            if location:
                return (location.latitude, location.longitude)

            # Si ArcGIS falla, usar Photon
            location = geoloc_photon.geocode(direccion)
            if location:
                return (location.latitude, location.longitude)

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"⚠️ Error en intento {intento+1}: {e}. Reintentando...")
            time.sleep(2)

    raise ValueError(f"❌ No se pudo obtener coordenadas para la dirección: '{direccion}' después de varios intentos.")


# --- Pedir dirección de inicio ---
def inicio():    
    print('Introduce la dirección de la forma en la que se muestra a continuación:')
    print("Ejemplo: Carrera 70 #45-15, Medellín, Colombia")
    direccion = input('Introduce la dirección de inicio: ')
    coords = obtener_coordenadas(direccion)
    print(f"✅ Dirección aprobada ({coords})")
    return coords


# --- Pedir dirección de destino ---
def destino():    
    print('Introduce la dirección de destino de la forma en la que se muestra a continuación:')
    print("Ejemplo: Carrera 43 #1 Sur - 150, Medellín, Colombia")
    direccion = input('Introduce la dirección de destino: ')
    coords = obtener_coordenadas(direccion)
    print(f"✅ Dirección aprobada ({coords})")
    return coords


# --- Cargar grafo de Medellín con caché ---
def cargar_grafo():
    """Carga el grafo de Medellín desde caché o lo descarga si no existe."""
    nombre_archivo = "medellin.graphml"

    if os.path.exists(nombre_archivo):
        print("📂 Cargando grafo desde caché local...")
        G = ox.load_graphml(nombre_archivo)
    else:
        print("🌐 Descargando grafo de Medellín (solo la primera vez)...")
        G = ox.graph_from_place("Medellín, Colombia", network_type='drive')
        ox.save_graphml(G, nombre_archivo)
        print("💾 Grafo guardado en caché como 'medellin.graphml'.")

    return G


# --- Función principal ---
def Ruta():
    start_coords = inicio()
    goal_coords = destino()

    print(f"Ubicación actual: {start_coords}")
    print(f"Destino: {goal_coords}")

    # --- 1. Cargar grafo ---
    G = cargar_grafo()

    # --- 2. Encontrar nodos más cercanos ---
    print("📍 Localizando puntos en el mapa...")
    orig = ox.distance.nearest_nodes(G, start_coords[1], start_coords[0])
    dest = ox.distance.nearest_nodes(G, goal_coords[1], goal_coords[0])

    # --- 3. Calcular la ruta más corta ---
    print("🧭 Calculando la ruta óptima...")
    try:
        route = nx.shortest_path(G, orig, dest, weight='length')
    except nx.NetworkXNoPath:
        raise ValueError("❌ No existe un camino entre los puntos seleccionados dentro del grafo cargado.")

    # --- 4. Visualizar en mapa ---
    print("🗺️ Generando mapa interactivo...")
    m = ox.plot_route_folium(G, route, route_map=folium.Map(location=start_coords, zoom_start=13))
    folium.Marker(location=start_coords, popup="Inicio", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(location=goal_coords, popup="Destino", icon=folium.Icon(color='red')).add_to(m)

    m.save("ruta_tiempo_real.html")
    print("✅ Mapa guardado como ruta_tiempo_real.html")

    # --- 5. Simulación de movimiento ---
    print("🚗 Simulando movimiento en la ruta...")
    nodes, _ = ox.graph_to_gdfs(G)
    for i in range(1, min(5, len(route))):
        current = nodes.loc[route[i]]
        print(f"📍 Moviéndote a: ({current.y}, {current.x})")
        time.sleep(5)

    print("🎯 Llegaste a destino.")


# --- Ejecutar programa ---
if __name__ == "__main__":
    Ruta()
