import psycopg2
import json

def camino_mas_corto(source, target):
    #  Puerto coquimbo
    source = [-71.336852, -29.947497]
    #Subestacion el Peñon
    target = [-71.227872, -30.143531]
    target = [-71.381378, -35.680781]

    # source = [-71.338343, -29.957733]
    # target = [-71.347033, -29.956051]

    conn = psycopg2.connect(
        dbname="cne",
        user="postgres",
        password="kzwip43",
        host="db",
        port="5432"
    )

    with conn.cursor() as cur:
        query_edge = """
            WITH ce AS (
                SELECT id, source, target, 
                    ST_Distance(geom_way, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) AS dist
                FROM chile_2po_4pgr
                ORDER BY dist
                LIMIT 1
            )
            SELECT id, source, target FROM ce;
        """

        # 1. Obtener el edge más cercano a A
        cur.execute(query_edge , (source[0], source[1]))
        edgeA_id, edgeA_source, edgeA_target = cur.fetchone()

        # 2. Obtener el edge más cercano a B
        cur.execute(query_edge, (target[0], target[1]))
        edgeB_id, edgeB_source, edgeB_target = cur.fetchone()

        # 3. Definir el nodo inicio y final (simplificación: usemos el source del edge más cercano a A y el target del edge más cercano a B)
        nodo_inicio = edgeA_source
        nodo_fin = edgeB_target

        # 4. Obtener los ejes del camino mas corto (dijkstra)
        query_dijkstra = """
            SELECT edge FROM pgr_dijkstra(
                'SELECT id, source, target, cost, reverse_cost FROM chile_2po_4pgr',
                %s,
                %s
            ) WHERE edge <> -1
        """
        cur.execute(query_dijkstra, (nodo_inicio, nodo_fin))
        rows = cur.fetchall()
        route_ids = list(map(lambda x: str(x[0]), rows))
        print(route_ids)

        # 5. Obtener la geometría de la ruta como un MultiLineString unificado
        query_route = """
            SELECT ST_AsEWKT(ST_Union(geom_way)), SUM(km), SUM(km / kmh)
            FROM chile_2po_4pgr
            WHERE id IN (%s);
        """ % ','.join(route_ids)
        cur.execute(query_route)
        route_geom_union = cur.fetchone()
        print(route_geom_union)

        # 6. Calcular la distancia total en metros reproyectando a EPSG:3857 (web mercator)
        #    ST_Length con 3857 da una aproximación de la longitud en metros
        cur.execute("""
            SELECT ST_Length(ST_Transform(%s, 3857)) AS length_meters;
        """, (route_geom_union[0],))
        route_length_m = cur.fetchone()[0]
        print(route_length_m)

#     # Imprimir la distancia total en metros
#     print("Distancia total de la ruta (m):", route_length_m)

#     # 7. Obtener la geometría en GeoJSON para dibujarla con folium
#     #    ST_AsGeoJSON devuelve un objeto GeoJSON
#     cur.execute("""
#         SELECT ST_AsGeoJSON(%s);
#     """, (route_geom_union,))
#     route_geojson = cur.fetchone()[0]

        conn.close()

# # Convertir la cadena GeoJSON a un objeto Python para folium
# route_geojson_obj = json.loads(route_geojson)

        # return route_geom_union
