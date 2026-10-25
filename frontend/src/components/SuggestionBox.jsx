import React, { useState, useEffect } from 'react';
import { Lightbulb, Clock, CheckCircle } from 'lucide-react';
import { API_BASE } from '../config';

const SuggestionBox = () => {
    const [suggestions, setSuggestions] = useState([]);
    const [loading, setLoading] = useState(false);

    // Poll for suggestions every 30s
    useEffect(() => {
        fetchSuggestions();
        const interval = setInterval(fetchSuggestions, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchSuggestions = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/api/suggestions/current`);
            const data = await res.json();
            if (Array.isArray(data) && data.length > 0) {
                setSuggestions(data);
            }
        } catch (e) {
            console.error("Failed to fetch suggestions", e);
        } finally {
            setLoading(false);
        }
    };

    if (suggestions.length === 0 && !loading) return null;

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 h-full flex flex-col">
            <h3 className="text-sm font-bold uppercase tracking-widest text-purple-400 mb-4 flex items-center gap-2">
                <Lightbulb size={16} /> AI Suggestion Box
            </h3>

            <div className="flex-1 space-y-4 overflow-auto">
                {suggestions.map((s, i) => (
                    <div key={i} className={`p-4 rounded-lg border flex flex-col gap-2
                    ${s.priority === 'High' ? 'bg-red-900/20 border-red-800/50' :
                            s.priority === 'Med' ? 'bg-yellow-900/20 border-yellow-800/50' :
                                'bg-slate-800 border-slate-700'}`}>

                        <div className="flex justify-between items-start">
                            <span className={`text-xs font-bold px-2 py-0.5 rounded
                             ${s.priority === 'High' ? 'bg-red-500 text-white' :
                                    s.priority === 'Med' ? 'bg-yellow-500 text-black' :
                                        'bg-slate-600 text-slate-300'}`}>
                                {s.priority} Priority
                            </span>
                            <span className="text-xs text-slate-500 flex items-center gap-1">
                                <Clock size={10} /> 2m
                            </span>
                        </div>

                        <p className="font-semibold text-sm text-slate-200">{s.action}</p>
                        <p className="text-xs text-slate-400 flex items-center gap-1">
                            <TrendingUpIcon size={10} /> Impact: {s.impact}
                        </p>
                    </div>
                ))}
            </div>

            <button onClick={fetchSuggestions} className="mt-4 w-full py-2 bg-slate-800 hover:bg-slate-700 rounded text-xs text-slate-400 transition">
                Refresh Suggestions
            </button>
        </div>
    );
};

const TrendingUpIcon = ({ size }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
)

export default SuggestionBox;
