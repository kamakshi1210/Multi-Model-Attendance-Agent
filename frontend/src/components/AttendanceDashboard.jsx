import React, { useEffect, useRef, useState } from 'react';
import Sidebar from './Sidebar';
import MetricsPanel from './MetricsPanel';
import AudioCapture from './AudioCapture';
import RecommendationsPanel from './RecommendationsPanel';
import AnalyticsPage from './AnalyticsPage';
import SuggestionBox from './SuggestionBox';
import { BarChart2, LayoutDashboard } from 'lucide-react';
import { API_BASE, WS_BASE } from '../config';

const AttendanceDashboard = () => {
    const [sessionActive, setSessionActive] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [peopleCount, setPeopleCount] = useState(0);
    const [duration, setDuration] = useState(0);
    const [videoSrc, setVideoSrc] = useState(null);
    const [view, setView] = useState('dashboard'); // dashboard | analytics

    // Metrics State
    const [emotionCounts, setEmotionCounts] = useState({ happy: 0, neutral: 0, bored: 0, confused: 0 });
    const [audioMetrics, setAudioMetrics] = useState({ noise_db: 0, activity_type: 'Quiet' });
    const [insight, setInsight] = useState(null);
    const [loadingInsight, setLoadingInsight] = useState(false);
    const [recommendations, setRecommendations] = useState([]);

    const wsVideo = useRef(null);
    const timerRef = useRef(null);
    const localVideoRef = useRef(null);
    const localStreamRef = useRef(null);
    const sendFrameIntervalRef = useRef(null);

    // Initial check
    useEffect(() => {
        fetchStatus();
    }, []);

    const fetchStatus = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/session/status`);
            const data = await res.json();
            setSessionActive(data.active);
            if (data.session_id) setSessionId(data.session_id);
            if (data.active && data.duration) setDuration(data.duration);
        } catch (e) {
            console.error("Status fetch failed", e);
        }
    };

    const fetchInsight = async () => {
        setLoadingInsight(true);
        try {
            const res = await fetch(`${API_BASE}/api/insights/classroom`);
            const data = await res.json();
            setInsight(data.insight);
        } catch (e) { console.error("Insight failed"); }
        setLoadingInsight(false);
    };

    const handleStart = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/session/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ teacher_id: "Instructor_1", class_id: "Room_101" })
            });
            const data = await res.json();
            if (data.status === 'started') {
                setSessionActive(true);
                setSessionId(data.session_id);
                startTimer();
                connectVideoWebSocket();
                startWebcamCapture();
            }
        } catch (e) { alert("Failed to start session"); }
    };

    const handleStop = async () => {
        try {
            await fetch(`${API_BASE}/api/session/stop`, { method: 'POST' });
            setSessionActive(false);
            stopTimer();
            stopWebcamCapture();
            if (wsVideo.current) wsVideo.current.close();
            setVideoSrc(null);
            setView('analytics');
        } catch (e) { alert("Failed to stop session"); }
    };

    const startTimer = () => {
        if (timerRef.current) clearInterval(timerRef.current);
        const startTime = Date.now() - (duration * 1000);
        timerRef.current = setInterval(() => {
            setDuration(Math.floor((Date.now() - startTime) / 1000));
        }, 1000);
    };
    const stopTimer = () => { if (timerRef.current) clearInterval(timerRef.current); };

    const startWebcamCapture = async () => {
        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                console.warn("getUserMedia not supported in this browser context");
                return;
            }
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 },
                audio: false
            });
            localStreamRef.current = stream;
            if (localVideoRef.current) {
                localVideoRef.current.srcObject = stream;
                localVideoRef.current.play().catch(e => console.warn("Local video play notice:", e));
            }

            const canvas = document.createElement('canvas');
            canvas.width = 640;
            canvas.height = 480;
            const ctx = canvas.getContext('2d');

            if (sendFrameIntervalRef.current) clearInterval(sendFrameIntervalRef.current);
            sendFrameIntervalRef.current = setInterval(() => {
                if (localVideoRef.current && wsVideo.current && wsVideo.current.readyState === WebSocket.OPEN) {
                    if (localVideoRef.current.readyState >= 2) {
                        ctx.drawImage(localVideoRef.current, 0, 0, 640, 480);
                        canvas.toBlob((blob) => {
                            if (blob && wsVideo.current && wsVideo.current.readyState === WebSocket.OPEN) {
                                wsVideo.current.send(blob);
                            }
                        }, 'image/jpeg', 0.65);
                    }
                }
            }, 100);
        } catch (err) {
            console.warn("Browser webcam not available, using backend classroom simulation feed:", err);
        }
    };

    const stopWebcamCapture = () => {
        if (sendFrameIntervalRef.current) {
            clearInterval(sendFrameIntervalRef.current);
            sendFrameIntervalRef.current = null;
        }
        if (localStreamRef.current) {
            localStreamRef.current.getTracks().forEach(t => t.stop());
            localStreamRef.current = null;
        }
        if (localVideoRef.current) {
            localVideoRef.current.srcObject = null;
        }
    };

    const connectVideoWebSocket = () => {
        if (wsVideo.current) wsVideo.current.close();
        wsVideo.current = new WebSocket(`${WS_BASE}/ws/video`);
        wsVideo.current.binaryType = 'blob';
        wsVideo.current.onopen = () => console.log("Video WS Connected");
        wsVideo.current.onmessage = (event) => {
            if (typeof event.data === 'string') {
                try {
                    const metrics = JSON.parse(event.data);
                    if (metrics.total_people !== undefined) setPeopleCount(metrics.total_people);
                    if (metrics.recommendations) setRecommendations(metrics.recommendations);

                    if (metrics.people) {
                        const counts = { happy: 0, neutral: 0, bored: 0, confused: 0, engaged: 0 };
                        metrics.people.forEach(p => {
                            if (counts[p.emotion] !== undefined) counts[p.emotion]++;
                            else counts[p.emotion] = 1;
                        });
                        setEmotionCounts(counts);
                    }
                } catch (e) { console.error("Parse error", e); }
            } else {
                const url = URL.createObjectURL(event.data);
                setVideoSrc(prev => {
                    if (prev) URL.revokeObjectURL(prev);
                    return url;
                });
            }
        };
    };

    useEffect(() => {
        if (sessionActive) {
            connectVideoWebSocket();
            startTimer();
            startWebcamCapture();
        }
        return () => {
            stopTimer();
            stopWebcamCapture();
            if (wsVideo.current) wsVideo.current.close();
        };
    }, [sessionActive]);

    if (view === 'analytics') {
        return (
            <div className="flex h-screen bg-slate-950 text-white overflow-hidden font-sans flex-col">
                <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900">
                    <h2 className="font-bold text-xl">Session Analytics & Reports</h2>
                    <button onClick={() => setView('dashboard')} className="px-4 py-2 bg-slate-700 rounded hover:bg-slate-600 flex gap-2 items-center">
                        <LayoutDashboard size={18} /> Back to Dashboard
                    </button>
                </div>
                <div className="flex-1 overflow-auto">
                    <AnalyticsPage sessionId={sessionId} />
                </div>
            </div>
        );
    }

    return (
        <div className="flex h-screen bg-slate-950 text-white overflow-hidden font-sans">
            <Sidebar
                sessionActive={sessionActive}
                peopleCount={peopleCount}
                duration={duration}
                onStart={handleStart}
                onStop={handleStop}
            />

            <AudioCapture active={sessionActive} onMetrics={setAudioMetrics} />
            <video ref={localVideoRef} autoPlay playsInline muted style={{ display: 'none' }} />

            {/* Main Content */}
            <div className="flex-1 flex flex-col relative bg-slate-950">

                {/* Top Overlay Buttons */}
                <div className="absolute top-4 right-4 z-40 flex gap-2">
                    {sessionId && (
                        <button onClick={() => setView('analytics')} className="bg-slate-800/80 backdrop-blur p-2 rounded-lg hover:bg-slate-700 border border-slate-700 text-slate-300 transition" title="View Analytics">
                            <BarChart2 size={24} />
                        </button>
                    )}
                </div>

                {/* Recommendations Overlay */}
                <RecommendationsPanel recommendations={recommendations} />

                {/* Video Stage */}
                <div className="flex-[3] relative flex items-center justify-center overflow-hidden p-4">
                    {videoSrc ? (
                        <div className="relative w-full h-full max-w-5xl aspect-video rounded-2xl overflow-hidden shadow-2xl border border-slate-800 bg-black">
                            <img src={videoSrc} alt="Live Classroom Feed" className="w-full h-full object-contain" />
                            <div className="absolute top-4 left-4 bg-black/60 backdrop-blur px-3 py-1 rounded text-xs font-mono text-green-400 border border-green-500/30 flex items-center">
                                <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                                LIVE FEED
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center text-center p-12 max-w-2xl w-full">
                            <div className="mb-8 relative">
                                <div className="absolute inset-0 bg-blue-500 blur-3xl opacity-20 rounded-full"></div>
                                <div className="relative bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-2xl">
                                    <div className="text-6xl mb-2">🎓</div>
                                </div>
                            </div>
                            <h2 className="text-4xl font-bold text-white mb-4 bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">Multimodal Attendance & Engagement Agent</h2>
                            <p className="text-slate-400 text-lg mb-8 max-w-md">Vision & Audio Multimodal AI Session Monitor</p>
                            <div className="flex gap-4">
                                <button onClick={handleStart} className="px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold shadow-lg shadow-blue-900/40 transition-all flex items-center">
                                    <span>Start Session</span><span className="ml-2">→</span>
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                {/* Bottom Suggestions Panel */}
                {sessionActive && (
                    <div className="flex-1 bg-slate-900/50 border-t border-slate-800 p-4 h-64 overflow-hidden">
                        <SuggestionBox />
                    </div>
                )}
            </div>

            <MetricsPanel
                emotionCounts={emotionCounts}
                audioMetrics={audioMetrics}
                insights={insight}
                loadingInsights={loadingInsight}
                onRefreshInsights={fetchInsight}
            />
        </div>
    );
};

export default AttendanceDashboard;
