# import time

# from fastapi import FastAPI
# from pydantic import BaseModel
# from fastapi.responses import HTMLResponse


# app = FastAPI()

# class InputData(BaseModel):
#     value: float


# @app.get("/", response_class=HTMLResponse)
# async def home():
#     return """
# <html>
#     <head>
#         <title>FastAPI Service</title>
#     </head>
#     <body>
#         <h1>Welcome to App Service</h1>
#         <p>Use the <code>http://{{ ansible_all_ipv4_addresses[1] }}/process/</code> endpoint to process data.</p>
#     </body>
# </html>
#     """


# @app.post("/process/{value}")
# async def process_data(value: float):
#     time.sleep(value)
#     return {"result": f"Processed value: {value}"}


from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket
from pymongo import MongoClient

import json
import time
import datetime

app = FastAPI()

client = MongoClient("mongodb://192.168.56.154:27017")
db = client["app_db"]
requests_collection = db["requests"]

# app.mount("/static", StaticFiles(directory="static"), name="static")

active_connections = []

class InputData(BaseModel):
    process_time: float

@app.post("/process/{process_time}")
async def process_data(process_time: float):
    time.sleep(process_time)
    request_data = {"timestamp": datetime.datetime.utcnow(), "process_time": process_time, "app": "{{ ansible_hostname }}"}
    requests_collection.insert_one(request_data)
    
    for connection in active_connections:
        await connection.send_text(f"{request_data}")
    
    return {"result": "Ok!", "process_time": process_time, "app": "{{ ansible_hostname }}"}

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>FastAPI Service</title>
            <script>
                var ws = new WebSocket("ws://{{ ansible_all_ipv4_addresses[1] }}:{{ app_port }}/ws");
                ws.onmessage = function(event) {
                    var newItem = document.createElement("li");
                    newItem.textContent = event.data;
                    document.getElementById("requests").appendChild(newItem);
                };
            </script>
        </head>
        <body>
            <h1>Welcome to FastAPI Service</h1>
            <p>Use the <code>http://192.168.56.151/process/&lt;value&gt;</code> endpoint to process data.</p>
            <h2>Request History</h2>
            <ul id="requests">
            </ul>
        </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        active_connections.remove(websocket)
