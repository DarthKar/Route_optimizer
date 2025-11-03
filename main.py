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

            location = geoloc_photon.geocode(direccion)
            if location:
                return (location.latitude, location.longitude)

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"⚠️ Error en intento {intento+1}: {e}. Reintentando...")
            time.sleep(2)

    raise ValueError(f"❌ No se pudo obtener coordenadas para la dirección: '{direccion}' después de varios intentos.")


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
    print("🚚 Bienvenido al optimizador de rutas de entregas en Medellín")
    print("Ejemplo de dirección: Carrera 43 #1 Sur - 150, Medellín, Colombia")

    # --- Pedir direcciones ---
    direcciones = []
    while True:
        direccion = input("Introduce una dirección (o escribe 'fin' para terminar): ").strip()
        if direccion.lower() == 'fin':
            break
        try:
            coords = obtener_coordenadas(direccion)
            direcciones.append((direccion, coords))
            print(f"✅ Dirección añadida: {direccion} ({coords})")
        except ValueError as e:
            print(e)

    if len(direcciones) < 2:
        print("❌ Se necesitan al menos dos direcciones para calcular una ruta.")
        return

    print("\n📍 Direcciones registradas:")
    for i, (direccion, coords) in enumerate(direcciones):
        print(f"{i+1}. {direccion} -> {coords}")

    # --- Cargar grafo ---
    G = cargar_grafo()

    # --- Calcular rutas consecutivas ---
    print("\n🧭 Calculando rutas entre puntos...")
    full_route = []

    for i in range(len(direcciones) - 1):
        start_coords = direcciones[i][1]
        goal_coords = direcciones[i + 1][1]
        print(f"Ruta {i+1}: {direcciones[i][0]} ➜ {direcciones[i+1][0]}")

        orig = ox.distance.nearest_nodes(G, start_coords[1], start_coords[0])
        dest = ox.distance.nearest_nodes(G, goal_coords[1], goal_coords[0])

        try:
            route_segment = nx.shortest_path(G, orig, dest, weight='length')
            full_route.extend(route_segment if i == 0 else route_segment[1:])
        except nx.NetworkXNoPath:
            print(f"⚠️ No hay ruta entre {direcciones[i][0]} y {direcciones[i+1][0]}.")

    # --- Crear mapa ---
    print("\n🗺️ Generando mapa con múltiples entregas...")
    m = ox.plot_route_folium(G, full_route, route_map=folium.Map(location=direcciones[0][1], zoom_start=13))

    for i, (direccion, coords) in enumerate(direcciones):
        color = "green" if i == 0 else "red" if i == len(direcciones) - 1 else "blue"
        folium.Marker(location=coords, popup=f"📍 {i+1}. {direccion}", icon=folium.Icon(color=color)).add_to(m)

    m.save("ruta_entregas_medellin.html")
    print("✅ Mapa guardado como 'ruta_entregas_medellin.html'.")

    # --- Simulación (opcional) ---
    print("\n🚗 Simulando movimiento...")
    nodes, _ = ox.graph_to_gdfs(G)
    for i in range(1, min(10, len(full_route))):
        current = nodes.loc[full_route[i]]
        print(f"📍 Moviéndote a: ({current.y}, {current.x})")
        time.sleep(1)

    print("🎯 Todas las entregas completadas.")


# --- Ejecutar programa ---
if __name__ == "__main__":
    Ruta()
