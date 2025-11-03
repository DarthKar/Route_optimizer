import osmnx as ox
import networkx as nx
import folium
import geocoder
import time

# --- 1. Obtener ubicación actual (por IP o GPS) ---
g = geocoder.ip('me')
if g.ok:
    start_coords = g.latlng
else:
    # Si no se puede obtener por IP, usa una fija (ej: Medellín)
    start_coords = (6.2442, -75.5812)

goal_coords = (6.2476, -75.5658)  # destino fijo

print(f"Ubicación actual: {start_coords}")
print(f"Destino: {goal_coords}")

# --- 2. Cargar grafo de calles ---
G = ox.graph_from_point(start_coords, dist=3000, network_type='drive')

# --- 3. Encontrar nodos más cercanos ---
orig = ox.distance.nearest_nodes(G, start_coords[1], start_coords[0])
dest = ox.distance.nearest_nodes(G, goal_coords[1], goal_coords[0])

# --- 4. Calcular la ruta más corta ---
route = nx.shortest_path(G, orig, dest, weight='length')

# --- 5. Visualizar en mapa ---
m = ox.plot_route_folium(G, route, route_map=folium.Map(location=start_coords, zoom_start=14))

# Agregar marcador de posición actual
folium.Marker(location=start_coords, popup="Inicio", icon=folium.Icon(color='green')).add_to(m)
folium.Marker(location=goal_coords, popup="Destino", icon=folium.Icon(color='red')).add_to(m)

m.save("ruta_tiempo_real.html")
print("✅ Mapa guardado como ruta_tiempo_real.html")

# --- 6. Simulación de movimiento ---
for i in range(1, 4):
    # Simula moverte a lo largo del camino
    current = ox.utils_geo.graph_to_gdfs(G).nodes.loc[route[min(i, len(route)-1)]]
    print(f"Moviéndote a: ({current.y}, {current.x})")
    time.sleep(2)
