// Centralized API and WebSocket Configuration
// Automatically detects environment (local dev vs deployed production)

const isLocalhost = Boolean(
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname === '[::1]'
);

export const API_BASE = import.meta.env.VITE_API_BASE || (
    isLocalhost ? 'http://localhost:8000' : `${window.location.protocol}//${window.location.host}`
);

const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
export const WS_BASE = import.meta.env.VITE_WS_BASE || (
    isLocalhost ? 'ws://localhost:8000' : `${wsProtocol}//${window.location.host}`
);
