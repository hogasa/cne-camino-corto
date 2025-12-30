import psycopg2
import json
import folium
import shapely
from datetime import datetime

def camino_mas_corto(source, target):
    conn = psycopg2.connect(
        dbname="cne",
        user="postgres",
        password="kzwip43",
        host="db",
        port="5432"
    )
    try:
        with conn.cursor() as cur:
            query_edge = """
                WITH ce AS (
                    SELECT id, source, target,
                        ST_Distance(geom_way, punto) AS dist
                    FROM (
                        SELECT id, source, target, geom_way, punto
                        FROM (SELECT *, ST_SetSRID(ST_MakePoint(%s, %s), 4326) AS punto FROM chile_2po_4pgr)
                        WHERE ST_DWithin(punto, geom_way, 0.1))
                    ORDER BY dist
                    LIMIT 1
                )
                SELECT id, source, target FROM ce;
            """

            # 1. Obtener el edge más cercano a A
            cur.execute(query_edge, (source[0], source[1]))
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

            # 5. Obtener la geometría de la ruta como un MultiLineString unificado
            if not route_ids:
                raise Exception
            query_route = """
                SELECT ST_AsText(ST_Union(geom_way)), SUM(km), SUM(km / kmh)
                FROM chile_2po_4pgr
                WHERE id IN (%s);
            """ % ','.join(route_ids)
            cur.execute(query_route)
            route_geom_union = cur.fetchone()
            conn.close()
            return(list(route_geom_union))

    except Exception as e:
        print(e)
        return ['MULTILINESTRING EMPTY', 0, 0]


def generar_mapa(source, target):
    # Calcular ruta
    ruta = camino_mas_corto(source, target)

    # Cambiar lon/lat por lat/lon
    source.reverse()
    target.reverse()

    # Crear mapa
    m = folium.Map(location=source, zoom_start=13)

    # Agregar marcador origen
    folium.Marker(
        location=source,
        popup="Origen",
        icon=folium.Icon(color="green")
    ).add_to(m)

    # Agregar marcador destino
    folium.Marker(
        location=target,
        popup="Destino",
        icon=folium.Icon(color="red")
    ).add_to(m)

    # Convertir  WKT en geojson
    geometry = shapely.from_wkt(ruta[0])
    geojson_string = shapely.to_geojson(geometry)

    popup_text = f"<b>Distancia:</b> {round(ruta[1], 2)} Km<br><b>Tiempo:</b> {num2hour(ruta[2])}"

    # Agregar ruta
    folium.GeoJson(
        geojson_string,
        name='Ruta',
        weight=3,
        popup=folium.Popup(popup_text, min_width=120, max_width=120)
    ).add_to(m)

    folium.FitOverlays().add_to(m)

    # Agregar controles de capas
    folium.LayerControl().add_to(m)

    full_html_code = m.get_root().render()
    return full_html_code
    # # 9. Guardar el mapa en un archivo HTML
    # m.save("./static/ruta.html")


def num2hour(time):
    hours = int(time)
    minutes = (time*60) % 60
    seconds = (time*3600) % 60

    return("%d:%02d.%02d" % (hours, minutes, seconds))
