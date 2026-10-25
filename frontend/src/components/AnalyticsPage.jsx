import React, { useState, useEffect } from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { Download, Sparkles, X, BrainCircuit, Activity, Volume2 } from 'lucide-react';
import { API_BASE } from '../config';

const AnalyticsPage = ({ sessionId }) => {
    const [trendData, setTrendData] = useState([]);
    const [attendanceData, setAttendanceData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedStudent, setSelectedStudent] = useState(null);
    const [studentReflection, setStudentReflection] = useState(null);
    const [reflectionLoading, setReflectionLoading] = useState(false);

    useEffect(() => {
        if (sessionId) {
            fetchTrends(sessionId);
            fetchAttendance(sessionId);
        }
    }, [sessionId]);

    const fetchTrends = async (sid) => {
        try {
            const res = await fetch(`${API_BASE}/api/analytics/trends/${sid}`);
            const data = await res.json();
            setTrendData(data);
        } catch (e) {
            console.error("Failed to fetch trends", e);
        } finally {
            setLoading(false);
        }
    };

    const fetchAttendance = async (sid) => {
        try {
            const res = await fetch(`${API_BASE}/api/analytics/attendance/${sid}`);
            const data = await res.json();
            setAttendanceData(data);
        } catch (e) {
            console.error("Failed to fetch attendance", e);
        }
    };

    const handleExport = (type) => {
        window.location.href = `${API_BASE}/api/reports/export/${sessionId}/${type}`;
    };

    const handleViewReflection = async (studentId) => {
        setSelectedStudent(studentId);
        setReflectionLoading(true);
        setStudentReflection(null);
        try {
            const res = await fetch(`${API_BASE}/api/insights/student/${studentId}`);
            const data = await res.json();
            setStudentReflection(data.reflection || null);
        } catch (e) {
            console.error("Failed to fetch student reflection", e);
        } finally {
            setReflectionLoading(false);
        }
    };

    if (loading) return <div className="p-8 text-white">Loading Multimodal Analytics...</div>;

    return (
        <div className="p-6 bg-slate-950 min-h-screen text-white">
            <header className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-500 bg-clip-text text-transparent">
                        Multimodal Session Analytics
                    </h1>
                    <p className="text-slate-400 text-sm mt-1">Grounded telemetry and explainable participant reflections</p>
                </div>
                <div className="flex gap-4">
                    <button onClick={() => handleExport('pdf')} className="flex items-center gap-2 px-4 py-2 bg-red-600/90 rounded-lg hover:bg-red-500 transition text-sm font-semibold shadow">
                        <Download size={16} /> PDF Report
                    </button>
                    <button onClick={() => handleExport('csv')} className="flex items-center gap-2 px-4 py-2 bg-emerald-600/90 rounded-lg hover:bg-emerald-500 transition text-sm font-semibold shadow">
                        <Download size={16} /> CSV Data
                    </button>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Visual Attention Trend */}
                <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-lg">
                    <h3 className="text-base font-semibold mb-1 flex items-center gap-2">
                        <Activity size={18} className="text-indigo-400" /> Visual Attention Trend
                    </h3>
                    <p className="text-xs text-slate-400 mb-4">Gaze tracking and head pose stability over session timeline</p>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={trendData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="time" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" domain={[0, 100]} />
                                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }} />
                                <Legend />
                                <Line type="monotone" dataKey="avg_attention" name="Avg Attention %" stroke="#818cf8" strokeWidth={2.5} dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Multimodal Audio Dynamics */}
                <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-lg">
                    <h3 className="text-base font-semibold mb-1 flex items-center gap-2">
                        <Volume2 size={18} className="text-blue-400" /> Audio & Speech Dynamics
                    </h3>
                    <p className="text-xs text-slate-400 mb-4">Calibrated ambient sound pressure (dB SPL) and speech ratio</p>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={trendData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="time" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }} />
                                <Legend />
                                <Line type="monotone" dataKey="noise_db" name="Noise Level (dB)" stroke="#38bdf8" strokeWidth={2} dot={false} />
                                <Line type="monotone" dataKey="speech_ratio" name="Speech Ratio %" stroke="#34d399" strokeWidth={2} dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Attendance & Presence Table */}
            <div className="mt-8 bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-lg">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h3 className="text-lg font-semibold">Presence-Based Attendance Summary</h3>
                        <p className="text-xs text-slate-400 mt-0.5">Thresholds: Present (&ge; 75%), Partial (40% - 74%), Absent (&lt; 40%)</p>
                    </div>
                    <div className="text-xs text-slate-400 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
                        Anonymous Participant Identifiers Only
                    </div>
                </div>
                
                {attendanceData.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse text-sm">
                            <thead>
                                <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
                                    <th className="py-3 px-4">Participant ID</th>
                                    <th className="py-3 px-4">Active Duration</th>
                                    <th className="py-3 px-4">Presence %</th>
                                    <th className="py-3 px-4">Attendance Status</th>
                                    <th className="py-3 px-4">Avg Attention</th>
                                    <th className="py-3 px-4 text-right">Explainability</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/60">
                                {attendanceData.map((student, idx) => (
                                    <tr key={idx} className="hover:bg-slate-800/40 transition">
                                        <td className="py-3 px-4 font-mono font-medium text-slate-200">{student.id}</td>
                                        <td className="py-3 px-4 text-slate-300">{student.presence_seconds}s</td>
                                        <td className="py-3 px-4 text-slate-300">{student.presence_percentage}%</td>
                                        <td className="py-3 px-4">
                                            <span className={`px-2.5 py-1 rounded-full text-xs font-semibold
                                                ${student.attendance_status === 'Present' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                                                  student.attendance_status === 'Partial' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
                                                  'bg-red-500/20 text-red-400 border border-red-500/30'}`}>
                                                {student.attendance_status}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-slate-300">{student.attention}%</td>
                                        <td className="py-3 px-4 text-right">
                                            <button
                                                onClick={() => handleViewReflection(student.id)}
                                                className="inline-flex items-center gap-1.5 px-3 py-1 bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/40 rounded-lg text-xs font-medium transition"
                                            >
                                                <Sparkles size={13} />
                                                Explain Reflection
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="text-slate-500 text-sm py-4 italic">No individual participant records found for this session.</div>
                )}
            </div>

            {/* Student Reflection Modal (Epic 5.2) */}
            {selectedStudent && (
                <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-slate-900 border border-slate-700 max-w-lg w-full rounded-2xl p-6 shadow-2xl relative">
                        <button
                            onClick={() => setSelectedStudent(null)}
                            className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
                        >
                            <X size={20} />
                        </button>

                        <div className="flex items-center gap-2 mb-4 text-indigo-400">
                            <BrainCircuit size={22} />
                            <h2 className="text-lg font-bold text-white">
                                Student AI Reflection — {selectedStudent}
                            </h2>
                        </div>

                        {reflectionLoading ? (
                            <div className="py-12 text-center text-slate-400">
                                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mb-3"></div>
                                <p className="text-sm">Generating personalized reflection via Gemini...</p>
                            </div>
                        ) : studentReflection ? (
                            <div className="space-y-4">
                                <div className="bg-slate-800/60 p-4 rounded-xl border border-slate-700/60">
                                    <div className="text-xs text-indigo-400 font-semibold uppercase tracking-wider mb-1">
                                        Presence Summary
                                    </div>
                                    <p className="text-sm text-slate-200 leading-relaxed">
                                        {studentReflection.presence_summary}
                                    </p>
                                </div>

                                <div className="bg-slate-800/60 p-4 rounded-xl border border-slate-700/60">
                                    <div className="text-xs text-purple-400 font-semibold uppercase tracking-wider mb-1">
                                        Engagement Pattern
                                    </div>
                                    <p className="text-sm text-slate-200 leading-relaxed">
                                        {studentReflection.engagement_pattern}
                                    </p>
                                </div>

                                <div className="bg-slate-800/60 p-4 rounded-xl border border-slate-700/60">
                                    <div className="text-xs text-emerald-400 font-semibold uppercase tracking-wider mb-1">
                                        Constructive Reflection & Recommendation
                                    </div>
                                    <p className="text-sm text-slate-200 leading-relaxed">
                                        {studentReflection.constructive_reflection}
                                    </p>
                                </div>

                                <div className="text-xs text-slate-500 italic pt-2">
                                    Privacy Note: Generated from anonymous session telemetry without facial recognition.
                                </div>
                            </div>
                        ) : (
                            <div className="py-6 text-center text-slate-400 text-sm">
                                No reflection available for this participant.
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default AnalyticsPage;
