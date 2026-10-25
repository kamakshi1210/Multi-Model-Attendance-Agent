import React from 'react';
import { Play, Square, Pause, Settings, Users, Clock } from 'lucide-react';

const Sidebar = ({ sessionActive, peopleCount, duration, onStart, onStop }) => {
    return (
        <div className="w-64 bg-slate-900 border-r border-slate-700 p-4 flex flex-col h-full text-white">
            <div className="mb-8">
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                    Attendance Agent
                </h1>
                <p className="text-slate-400 text-sm">Multimodal AI Engagement</p>
            </div>

            {/* Session Status */}
            <div className="mb-6 p-4 bg-slate-800 rounded-lg">
                <div className="flex items-center space-x-2 mb-2">
                    <div className={`w-3 h-3 rounded-full ${sessionActive ? 'bg-green-500 animate-pulse' : 'bg-slate-500'}`} />
                    <span className="font-semibold text-slate-200">
                        {sessionActive ? 'SESSION ACTIVE' : 'IDLE'}
                    </span>
                </div>
                <div className="flex items-center space-x-2 text-slate-300">
                    <Clock size={16} />
                    <span className="font-mono text-lg">{formatTime(duration)}</span>
                </div>
            </div>

            {/* People Counter */}
            <div className="mb-6 p-4 bg-slate-800 rounded-lg border border-slate-700">
                <div className="flex items-center justify-between mb-1">
                    <span className="text-slate-400 text-sm">Students Present</span>
                    <Users size={16} className="text-blue-400" />
                </div>
                <div className="text-4xl font-bold text-white">{peopleCount}</div>
            </div>

            {/* Controls */}
            <div className="space-y-3 flex-1">
                {!sessionActive ? (
                    <button
                        onClick={onStart}
                        className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-lg font-medium transition-all shadow-lg shadow-blue-900/20"
                    >
                        <Play size={20} />
                        <span>Start Session</span>
                    </button>
                ) : (
                    <button
                        onClick={onStop}
                        className="w-full flex items-center justify-center space-x-2 bg-red-600 hover:bg-red-500 text-white py-3 rounded-lg font-medium transition-all shadow-lg shadow-red-900/20"
                    >
                        <Square size={20} />
                        <span>End Session</span>
                    </button>
                )}
            </div>

            <div className="mt-auto pt-4 border-t border-slate-700">
                <button className="flex items-center space-x-2 text-slate-400 hover:text-white transition-colors">
                    <Settings size={18} />
                    <span>Settings</span>
                </button>
            </div>
        </div>
    );
};

const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export default Sidebar;
