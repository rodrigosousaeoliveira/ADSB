from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import eventlet
import time
import threading
from datetime import datetime
import random

# Configuração do Flask e SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave'

def allow_local_network(origin):
    """Permite qualquer IP da rede local 192.168.x.x"""
    # Lista de origens fixas
    fixed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    
    if origin in fixed_origins:
        return True
    
    # Verifica se é um IP da rede 192.168.x.x
    if origin.startswith("http://192.168."):
        # Pode adicionar validações extras aqui
        return True
        
    return False


ac_data = []

# Configuração CORS para permitir conexões do React
socketio = SocketIO(app, cors_allowed_origins=allow_local_network)

# Rota básica para testar se o servidor está funcionando
@app.route('/')
def index():
    return "Servidor Socket.IO funcionando!"

@app.route('/api/health')
def health():
    return {"status": "online", "message": "Servidor operacional"}

@app.route('/api/senddata', methods=['POST'])
def receivedata():
    ac_data = request.get_json()
    socketio.emit('real-time-data', ac_data)
    print(f"Received New Data:\n{ac_data}")
    return {"status": "online", "message": "Servidor operacional"}

# Evento quando cliente se conecta
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')
    # Envia dados imediatamente ao conectar
    emit('connected', {'message': 'Conectado ao servidor!', 'status': 'success'})
    
    # Envia dados iniciais
    initial_data = ac_data
    emit('real-time-data', initial_data)

# Evento quando cliente se desconecta
@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

# Evento para receber mensagens do cliente
@socketio.on('client-message')
def handle_client_message(data):
    print(f'Mensagem do cliente: {data}')
    # Responde ao cliente
    emit('server-response', {
        'message': 'Mensagem recebida!', 
        'your_data': data,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# Evento para solicitar dados específicos
@socketio.on('request-data')
def handle_data_request(data):
    data_type = data.get('type', 'all')
    response = [generateData()]
    emit('real-time-data', response)

# Função para enviar dados em intervalos regulares
def broadcast_updates():
    """Envia atualizações periódicas para todos os clientes conectados"""
    while True:
        try:
            # Simula dados em tempo real
            new_data = ac_data
                
            # Envia para todos os clientes conectados
            socketio.emit('real-time-data', ac_data)
            print(f"Dados enviados: {ac_data}")
            #print(f"Dados enviados: {new_data[0]['time']}")
            
            # Espera 2 segundos
            socketio.sleep(2)
            
        except Exception as e:
            print(f"Erro no broadcast: {e}")
            socketio.sleep(5)

# Inicia a thread de broadcast quando o servidor inicia
@socketio.on('start-broadcast')
def start_broadcast():
    print("Iniciando broadcast de dados...")
    #socketio.start_background_task(broadcast_updates)
    
def generateData():
    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "icao": hex( random.randint(99999,999999)),
        "altitude": round(30000 + random.random() * 30, 2),
        "latitude": round(45 + random.random(), 2),
        "longitude": round(14 + random.random(), 2),
        "speed": round(220 + random.random(), 2)}
    
if __name__ == '__main__':
    print("Servidor Socket.IO iniciando na porta 3001...")
    print("Frontend deve conectar em: http://localhost:3001")
    
    # Inicia o servidor
    socketio.run(app, host='192.168.12.1', port=3001, debug=True)
