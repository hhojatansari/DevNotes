import time

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse


app = FastAPI()

class InputData(BaseModel):
    value: float


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<html>
    <head>
        <title>FastAPI Service</title>
    </head>
    <body>
        <h1>Welcome to App Service</h1>
        <p>Use the <code>http://{{ ansible_all_ipv4_addresses[1] }}/process/</code> endpoint to process data.</p>
    </body>
</html>
    """


@app.post("/process/{value}")
async def process_data(value: float):
    time.sleep(value)
    return {"result": f"Processed value: {value}"}
