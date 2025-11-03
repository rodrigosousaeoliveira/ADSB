import React, { useState, useEffect } from 'react';
import MapComponent from './MapComponent';
import io from 'socket.io-client';

const socket = io('http://localhost:3001');
const acData0 = [{altitude:3000,callsign:"TEST123",icao:"ABCDEF",latitude:46.1,longitude:14.5,speed:250}];

const RealTimeDataComponent = () => {
    const [data, setData] = useState(acData0);
    const [connectionStatus, setConnectionStatus] = useState('connecting');
    const [message, setMessage] = useState('');

    useEffect(() => {
        // Evento quando conecta
        socket.on('connect', () => {
            console.log('Conectado ao servidor');
            setConnectionStatus('connected');
            // startBroadcast()
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
            <MapComponent acData={data}/>
    );
};

export default RealTimeDataComponent;