import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import paho.mqtt.client as mqtt
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = sqlite3.connect("estacionamento.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS historico_vaga (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    distancia INTEGER,
    status TEXT,
    horario_entrada DATETIME
)
""")
conn.commit()
conn.close()

estado_atual = {
    "id": 0,
    "distancia": 0,
    "status": "STATUS: Vaga Livre.",
    "status_code": 0
}

ultimo_codigo_salvo = -1

def on_connect(client, userdata, flags, rc):
    print("Conectado ao Broker Mosquitto com sucesso!")
    client.subscribe("garagem/sensor/distancia")

def on_message(client, userdata, msg):
    global estado_atual, ultimo_codigo_salvo
    try:
        distancia = int(msg.payload.decode())
        if distancia > 100:
            status_texto = "STATUS: Vaga Livre."
            status_code = 0
        elif 30 <= distancia <= 100:
            status_texto = "STATUS: Manobrando."
            status_code = 1
        elif 10 <= distancia < 30:
            status_texto = "STATUS: Estacionado."
            status_code = 2
        else:
            status_texto = "STATUS: PERIGO! PARE O CARRO!"
            status_code = 3
            
        estado_atual = {
            "id": 1,
            "distancia": distancia,
            "status": status_texto,
            "status_code": status_code
        }
        
        if status_code != ultimo_codigo_salvo:
            conn = sqlite3.connect("estacionamento.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO historico_vaga (distancia, status, horario_entrada) VALUES (?, ?, datetime('now', 'localtime'))",
                (distancia, status_texto)
            )
            conn.commit()
            conn.close()
            ultimo_codigo_salvo = status_code
            print(f"SALVO NO SQL: {status_texto} ({distancia} cm)")
            
    except Exception as e:
        print(f"Erro ao processar mensagem do Arduino: {e}")

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("192.168.137.154", 1883, 60)
mqtt_client.loop_start()

@app.get("/leituras")
def get_leituras():
    conn = sqlite3.connect("estacionamento.db")
    cursor = conn.cursor()
    cursor.execute("SELECT horario_entrada, distancia, status FROM historico_vaga ORDER BY id DESC LIMIT 10")
    registros = cursor.fetchall()
    conn.close()
    
    historico_alertas = []
    for r in registros:
        historico_alertas.append({
            "horario": r[0],
            "distancia": r[1],
            "status": r[2]
        })
        
    return JSONResponse(content={
        "atual": estado_atual,
        "historico": historico_alertas
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
