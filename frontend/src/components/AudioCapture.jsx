import React, { useEffect, useRef, useState } from 'react';
import { WS_BASE } from '../config';

const AudioCapture = ({ active, onMetrics }) => {
    const [isRecording, setIsRecording] = useState(false);
    const wsRef = useRef(null);
    const audioContextRef = useRef(null);
    const processorRef = useRef(null);
    const inputRef = useRef(null);

    useEffect(() => {
        if (active) {
            startCapture();
        } else {
            stopCapture();
        }
        return () => stopCapture();
    }, [active]);

    const startCapture = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            setIsRecording(true);

            // Connect WS
            const ws = new WebSocket(`${WS_BASE}/ws/audio`);
            wsRef.current = ws;

            ws.onmessage = (event) => {
                const metrics = JSON.parse(event.data);
                if (onMetrics) onMetrics(metrics);
            };

            ws.onopen = () => {
                console.log("Audio WS Connected");
                // Start Audio Processing
                audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
                const ctx = audioContextRef.current;
                inputRef.current = ctx.createMediaStreamSource(stream);

                // Use ScriptProcessor for raw data (simple approach) or AudioWorklet (better but more complex setup in Vite)
                // For prototype: ScriptProcessor with buffer size 4096 (~0.25s)
                processorRef.current = ctx.createScriptProcessor(4096, 1, 1);

                processorRef.current.onaudioprocess = (e) => {
                    if (ws.readyState === WebSocket.OPEN) {
                        const inputData = e.inputBuffer.getChannelData(0);
                        // Convert to Float32 bytes
                        ws.send(inputData.buffer);
                    }
                };

                inputRef.current.connect(processorRef.current);
                processorRef.current.connect(ctx.destination); // Needed for Chrome to activate it
            };

        } catch (err) {
            console.error("Microphone access denied:", err);
            setIsRecording(false);
        }
    };

    const stopCapture = () => {
        if (processorRef.current) {
            processorRef.current.disconnect();
            processorRef.current = null;
        }
        if (inputRef.current) {
            inputRef.current.disconnect();
            inputRef.current = null;
        }
        if (audioContextRef.current) {
            audioContextRef.current.close();
            audioContextRef.current = null;
        }
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        setIsRecording(false);
    };

    return (
        <div className="hidden">
            {/* Audio Capture Logic (Headless) */}
        </div>
    );
};

export default AudioCapture;
