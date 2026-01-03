from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from io import StringIO
import csv
from camino_mas_corto import camino_mas_corto, generar_mapa
from datetime import datetime

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html") as f:
        return f.read()


@app.post("/api/caminos_mas_cortos")
async def caminos_mas_cortos(file: UploadFile = File(...)):
    response = []
    try:
        print("Comienzo:", datetime.now())
        if file.size == 0:
            raise Exception("No se especificó el archivo.")
        content = await file.read()
        myCsv = StringIO(content.decode('utf-8'))
        reader = csv.reader(myCsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        count = 0
        for row in reader:
            count += 1
            if (count % 50) == 0:
                print("count", count, "", datetime.now())
            source = [float(row[1]), float(row[2])]
            target = [float(row[4]), float(row[5])]
            caminos = camino_mas_corto(source, target)
            response.append({
                "origen": row[0].strip(),
                "origen_lon": row[1].strip(),
                "origen_lat": row[2].strip(),
                "destino": row[3].strip(),
                "destino_lon": row[4].strip(),
                "destino_lat": row[5].strip(),
                "ruta": caminos[0],
                "distancia": round(caminos[1], 2),
                "tiempo": round(caminos[2], 2)
            })
        print("Fin:", datetime.now())

        with StringIO() as csvfile:
            fieldnames = response[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(response)
            # Get the resulting CSV string
            csv_string = csvfile.getvalue()

        return PlainTextResponse(
            content=csv_string,
            headers={"Content-Disposition": "attachment;filename=rutas.csv"},
            media_type="text/plain",
            status_code=200
        )

        # return JSONResponse(
        #     content=response,
        #     headers={"Content-Disposition": "attachment;filename=rutas.json"},
        #     media_type="application/json",
        #     status_code=200)
    except Exception as e:
        return JSONResponse(content={
            "error": str(e)
        }, status_code=404)


@app.get("/mapa", response_class=HTMLResponse)
async def home():
    with open("static/mapa.html") as f:
        return f.read()


@app.get("/api/generar_mapa/")
async def api_generar_mapa(origen_lon: float, origen_lat: float, destino_lon: float, destino_lat: float):
    try:
        response = generar_mapa([origen_lon, origen_lat], [destino_lon, destino_lat])
        return JSONResponse(
            content=response,
            headers={"Content-Disposition": "attachment;filename=rutas.json"},
            media_type="application/json",
            status_code=200)
    except Exception as e:
        return JSONResponse(content={
            "error": str(e)
        }, status_code=404)
