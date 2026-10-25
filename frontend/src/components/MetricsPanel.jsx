import React, { useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, Legend } from 'recharts';
import { Activity, Volume2, Lightbulb, RefreshCw } from 'lucide-react';

const COLORS = ['#4ade80', '#fbbf24', '#f87171', '#a78bfa', '#60a5fa'];

const MetricsPanel = ({ emotionCounts, audioMetrics, insights, loadingInsights, onRefreshInsights }) => {

    const data = Object.keys(emotionCounts).map((key, index) => ({
        name: key,
        value: emotionCounts[key],
        color: COLORS[index % COLORS.length]
    })).filter(d => d.value > 0);

    return (
        <div className="w-80 bg-slate-900 border-l border-slate-700 p-4 overflow-y-auto h-full text-white">

            {/* Emotion Distribution */}
            <div className="mb-6 bg-slate-800 rounded-lg p-4">
                <h3 className="text-slate-200 font-semibold mb-3 flex items-center">
                    <Activity size={18} className="mr-2 text-purple-400" /> Emotion Live
                </h3>
                <div className="h-48 w-full">
                    {data.length > 0 ? (
                        <ResponsiveContainer>
                            <PieChart>
                                <Pie
                                    data={data}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={40}
                                    outerRadius={70}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {data.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
                                <Legend layout="horizontal" verticalAlign="bottom" align="center" wrapperStyle={{ fontSize: '12px' }} />
                            </PieChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="h-full flex items-center justify-center text-slate-500 text-sm">
                            No data yet
                        </div>
                    )}
                </div>
            </div>

            {/* Audio Cloud */}
            <div className="mb-6 bg-slate-800 rounded-lg p-4">
                <h3 className="text-slate-200 font-semibold mb-3 flex items-center">
                    <Volume2 size={18} className="mr-2 text-blue-400" /> Audio Context
                </h3>
                <div className="grid grid-cols-3 gap-2">
                    <div className="bg-slate-700/50 p-2 rounded">
                        <div className="text-[11px] text-slate-400">Noise Level</div>
                        <div className="text-base font-mono font-bold text-slate-200">
                            {audioMetrics?.noise_db ? `${audioMetrics.noise_db.toFixed(1)} dB` : '--'}
                        </div>
                    </div>
                    <div className="bg-slate-700/50 p-2 rounded">
                        <div className="text-[11px] text-slate-400">Speech Ratio</div>
                        <div className="text-base font-mono font-bold text-slate-200">
                            {audioMetrics?.speech_ratio !== undefined ? `${Math.round(audioMetrics.speech_ratio * 100)}%` : '--'}
                        </div>
                    </div>
                    <div className="bg-slate-700/50 p-2 rounded">
                        <div className="text-[11px] text-slate-400">Activity</div>
                        <div className="text-xs font-semibold capitalize text-slate-200 truncate" title={audioMetrics?.activity_type}>
                            {audioMetrics?.activity_type ? audioMetrics.activity_type.replace('_', ' ') : 'Scanning'}
                        </div>
                    </div>
                </div>
            </div>

            {/* AI Insights */}
            <div className="bg-gradient-to-br from-indigo-900 to-slate-800 rounded-lg p-4 border border-indigo-500/30">
                <div className="flex items-center justify-between mb-3">
                    <h3 className="text-indigo-200 font-semibold flex items-center">
                        <Lightbulb size={18} className="mr-2 text-yellow-400" /> AI Insights
                    </h3>
                    <button
                        onClick={onRefreshInsights}
                        className={`text-slate-400 hover:text-white ${loadingInsights ? 'animate-spin' : ''}`}
                    >
                        <RefreshCw size={14} />
                    </button>
                </div>

                {insights ? (
                    <div className="text-sm text-slate-300 leading-relaxed bg-slate-900/50 p-3 rounded border border-slate-700">
                        {insights}
                    </div>
                ) : (
                    <div className="text-xs text-slate-500 italic">
                        Start session to generate insights...
                    </div>
                )}
            </div>

        </div>
    );
};

export default MetricsPanel;
