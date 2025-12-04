import psycopg2
# import folium
import json

# Datos de conexión a la BD
conn = psycopg2.connect(
    dbname="cne",
    user="postgres",
    password="kzwip43",
    host="db",
    port="5432"
)

# Coordenadas A y B en EPSG:4326 (lon, lat)
#  SANTIAGO AUTOPISTA
# A_lng, A_lat = -70.745895, -33.411651
# B_lng, B_lat = -70.6093343, -33.5087204

#  SANTIAGO AUTOPISTA
#A_lng, A_lat = -70.745895, -33.411651
#B_lng, B_lat = -70.6093343, -33.5087204

#  Puerto Valparaiso
#A_lng, A_lat = -71.629787, -33.033841


#  Puerto coquimbo
A_lng, A_lat=-71.336852, -29.947497

#Subestacion el Peñon
B_lng, B_lat = -71.227872, -30.143531

#Subestacion  Lo Aguirre
#B_lng, B_lat = -70.888373, -33.453428

#Subestacion Ancoa
#B_lng, B_lat = -71.381378, -35.680781,

with conn.cursor() as cur:
    # 1. Obtener el edge más cercano a A
    cur.execute("""
        WITH ce AS (
            SELECT id, source, target, 
                   ST_Distance(geom_way, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) AS dist
            FROM chile_2po_4pgr
            ORDER BY dist
            LIMIT 1
        )
        SELECT id, source, target FROM ce;
    """, (A_lng, A_lat))
    edgeA_id, edgeA_source, edgeA_target = cur.fetchone()

    # 2. Obtener el edge más cercano a B
    cur.execute("""
        WITH ce AS (
            SELECT id, source, target, 
                   ST_Distance(geom_way, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) AS dist
            FROM chile_2po_4pgr
            ORDER BY dist
            LIMIT 1
        )
        SELECT id, source, target FROM ce;
    """, (B_lng, B_lat))
    edgeB_id, edgeB_source, edgeB_target = cur.fetchone()

    # 3. Definir el nodo inicio y final (simplificación: usemos el source del edge más cercano a A y el target del edge más cercano a B)
    nodo_inicio = edgeA_source
    nodo_fin = edgeB_target

    # 4. Ejecutar pgr_dijkstra para obtener el camino
    cur.execute("""
        SELECT seq, node, edge, cost 
        FROM pgr_dijkstra(
            'SELECT id, source, target, cost, reverse_cost FROM chile_2po_4pgr',
            %s,
            %s
        );
    """, (nodo_inicio, nodo_fin))
    path = cur.fetchall()

    # 5. Obtener la geometría de la ruta como un MultiLineString unificado
    cur.execute("""
        SELECT ST_Union(geom_way)
        FROM chile_2po_4pgr
        WHERE id IN (
            SELECT edge FROM pgr_dijkstra(
                'SELECT id, source, target, cost, reverse_cost FROM chile_2po_4pgr',
                %s,
                %s
            ) WHERE edge <> -1
        );
    """, (nodo_inicio, nodo_fin))
    route_geom_union = cur.fetchone()[0]

    # 6. Calcular la distancia total en metros reproyectando a EPSG:3857 (web mercator)
    #    ST_Length con 3857 da una aproximación de la longitud en metros
    cur.execute("""
        SELECT ST_Length(ST_Transform(%s, 3857)) AS length_meters;
    """, (route_geom_union,))
    route_length_m = cur.fetchone()[0]

    # Imprimir la distancia total en metros
    print("Distancia total de la ruta (m):", route_length_m)

    # 7. Obtener la geometría en GeoJSON para dibujarla con folium
    #    ST_AsGeoJSON devuelve un objeto GeoJSON
    cur.execute("""
        SELECT ST_AsGeoJSON(%s);
    """, (route_geom_union,))
    route_geojson = cur.fetchone()[0]

conn.close()

# Convertir la cadena GeoJSON a un objeto Python para folium
route_geojson_obj = json.loads(route_geojson)

# 8. Crear un mapa con folium centrado en el punto inicial
# m = folium.Map(location=[A_lat, A_lng], zoom_start=13)

# # Agregar marcador en A
# folium.Marker(
#     location=[A_lat, A_lng],
#     popup="Punto A",
#     icon=folium.Icon(color="green")
# ).add_to(m)

# # Agregar marcador en B
# folium.Marker(
#     location=[B_lat, B_lng],
#     popup="Punto B",
#     icon=folium.Icon(color="red")
# ).add_to(m)

# # Agregar la ruta como un objeto GeoJSON
# folium.GeoJson(
#     route_geojson_obj,
#     name='Ruta'
# ).add_to(m)

# # Agregar un Popup mostrando la distancia total
# folium.Marker(
#     location=[(A_lat + B_lat) / 2, (A_lng + B_lng) / 2],  # punto intermedio
#     popup=f"Distancia total: {round(route_length_m, 2)} m",
#     icon=folium.Icon(color="blue")
# ).add_to(m)

# # Agregar controles de capas
# folium.LayerControl().add_to(m)

# # 9. Guardar el mapa en un archivo HTML
# m.save("ruta.html")

# print("Mapa guardado en ruta.html")

