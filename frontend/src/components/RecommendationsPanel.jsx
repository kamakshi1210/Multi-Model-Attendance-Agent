import React, { useEffect, useState } from 'react';
import { AlertCircle, CheckCircle, Info } from 'lucide-react';

const RecommendationsPanel = ({ recommendations }) => {
    if (!recommendations || recommendations.length === 0) return null;

    return (
        <div className="absolute top-4 right-4 md:right-auto md:left-1/2 md:-translate-x-1/2 w-full max-w-md z-50 flex flex-col gap-2 pointer-events-none">
            {recommendations.map((rec, idx) => (
                <div
                    key={idx}
                    className={`p-4 rounded-lg shadow-2xl backdrop-blur-md border animate-in slide-in-from-top-4 pointer-events-auto flex items-start gap-3
                ${rec.type === 'alert' ? 'bg-red-500/90 border-red-400 text-white' :
                            rec.type === 'warning' ? 'bg-yellow-500/90 border-yellow-400 text-black' :
                                'bg-blue-500/90 border-blue-400 text-white'}`}
                >
                    <div className="mt-1">
                        {rec.type === 'alert' && <AlertCircle size={20} />}
                        {rec.type === 'warning' && <AlertCircle size={20} />}
                        {rec.type === 'info' && <Info size={20} />}
                        {rec.type === 'success' && <CheckCircle size={20} />}
                    </div>
                    <div>
                        <p className="font-bold text-sm uppercase tracking-wider">{rec.type}</p>
                        <p className="text-base font-medium">{rec.message}</p>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default RecommendationsPanel;
