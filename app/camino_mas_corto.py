import psycopg2
import json


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
            # print(route_ids)

            # 5. Obtener la geometría de la ruta como un MultiLineString unificado
            query_route = """
                SELECT ST_AsEWKT(ST_Union(geom_way)), SUM(km), SUM(km / kmh)
                FROM chile_2po_4pgr
                WHERE id IN (%s);
            """ % ','.join(route_ids)
            cur.execute(query_route)
            route_geom_union = cur.fetchone()
            # print(route_geom_union)
            conn.close()
            return(list(route_geom_union))

    except:
        return ['MULTILINESTRING EMPTY', 0, 0]
