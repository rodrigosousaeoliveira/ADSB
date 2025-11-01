import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

const socket = io('http://localhost:3001');

const RealTimeDataComponent = () => {
    const [data, setData] = useState(null);
    const [connectionStatus, setConnectionStatus] = useState('connecting');
    const [message, setMessage] = useState('');

    useEffect(() => {
        // Evento quando conecta
        socket.on('connect', () => {
            console.log('Conectado ao servidor');
            setConnectionStatus('connected');
        });

        // Evento quando desconecta
        socket.on('disconnect', () => {
            console.log('Desconectado do servidor');
            setConnectionStatus('disconnected');
        });

        // Recebe dados em tempo real
        socket.on('real-time-data', (newData) => {
            console.log('Novos dados recebidos:', newData);
            setData(newData);
        });

        // Recebe confirmação de conexão
        socket.on('connected', (data) => {
            console.log('Mensagem do servidor:', data);
        });

        // Recebe respostas do servidor
        socket.on('server-response', (response) => {
            console.log('Resposta do servidor:', response);
        });

        // Cleanup na desmontagem do componente
        return () => {
            socket.off('connect');
            socket.off('disconnect');
            socket.off('real-time-data');
            socket.off('connected');
            socket.off('server-response');
        };
    }, []);

    // Função para solicitar dados específicos
    const requestData = (type) => {
        socket.emit('request-data', { type });
    };

    // Função para enviar mensagem ao servidor
    const sendMessage = () => {
        if (message.trim()) {
            socket.emit('client-message', {
                text: message,
                timestamp: new Date().toISOString()
            });
            setMessage('');
        }
    };

    // Função para iniciar broadcast automático
    const startBroadcast = () => {
        socket.emit('start-broadcast');
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h1>Dados em Tempo Real</h1>
            
            {/* Status da conexão */}
            <div style={{ 
                padding: '10px', 
                marginBottom: '20px',
                backgroundColor: connectionStatus === 'connected' ? '#d4edda' : '#f8d7da',
                border: `1px solid ${connectionStatus === 'connected' ? '#c3e6cb' : '#f5c6cb'}`,
                borderRadius: '4px',
                color: connectionStatus === 'connected' ? '#155724' : '#721c24'
            }}>
                Status: {connectionStatus === 'connected' ? 'Conectado' : 
                        connectionStatus === 'connecting' ? 'Conectando...' : 'Desconectado'}
            </div>

            {/* Dados recebidos */}
            <div style={{ 
                padding: '15px', 
                backgroundColor: '#f8f9fa',
                border: '1px solid #dee2e6',
                borderRadius: '4px',
                marginBottom: '20px'
            }}>
                <h3>Dados Atuais:</h3>
                {data ? (
                    <pre style={{ fontSize: '14px' }}>
                        {JSON.stringify(data, null, 2)}
                    </pre>
                ) : (
                    <p>Carregando dados...</p>
                )}
            </div>

            {/* Controles */}
            <div style={{ marginBottom: '20px' }}>
                <h3>Controles:</h3>
                <div style={{ gap: '10px', display: 'flex', flexWrap: 'wrap', marginBottom: '15px' }}>
                    <button 
                        onClick={() => requestData('all')}
                        style={{ padding: '8px 16px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}
                    >
                        Buscar Todos os Dados
                    </button>
                    <button 
                        onClick={() => requestData('weather')}
                        style={{ padding: '8px 16px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px' }}
                    >
                        Dados Meteorológicos
                    </button>
                    <button 
                        onClick={() => requestData('time')}
                        style={{ padding: '8px 16px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px' }}
                    >
                        Apenas Horário
                    </button>
                    <button 
                        onClick={startBroadcast}
                        style={{ padding: '8px 16px', backgroundColor: '#ffc107', color: 'black', border: 'none', borderRadius: '4px' }}
                    >
                        Iniciar Broadcast Automático
                    </button>
                </div>

                {/* Enviar mensagem */}
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <input
                        type="text"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Digite uma mensagem..."
                        style={{ padding: '8px', flex: 1, border: '1px solid #ccc', borderRadius: '4px' }}
                        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    />
                    <button 
                        onClick={sendMessage}
                        style={{ padding: '8px 16px', backgroundColor: '#17a2b8', color: 'white', border: 'none', borderRadius: '4px' }}
                    >
                        Enviar
                    </button>
                </div>
            </div>

            {/* Informações específicas se disponíveis */}
            {data && (
                <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                    gap: '15px',
                    marginTop: '20px'
                }}>

                    {data[2].icao && (
                        <div style={{ padding: '15px', backgroundColor: '#e7f3ff', borderRadius: '4px' }}>
                            <strong>ICAO</strong><br />
                            {data[2].icao}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default RealTimeDataComponent;