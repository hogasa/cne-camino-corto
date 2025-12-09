from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/api/camino_mas_corto")
async def camino_mas_corto(file: UploadFile = File(...)):
    try:
        with open(file.filename, "wb") as myFile:
            content = await file.read()
            myFile.write(content)
            myFile.close()
            print(file.filename)
            return JSONResponse(content={
                "saved": True
            }, status_code=200)
    except FileNotFoundError as e:
        print(e)
        return JSONResponse(content={
            "saved": False
        }, status_code=404)
