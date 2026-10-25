"""
Real-time rule-based recommendations engine grounded in multimodal signals.
Flags low engagement and individual distraction without emotion pseudoscience.
"""

class RecommendationsEngine:
    def generate_realtime_recommendations(self, metrics: dict):
        """
        Rule-based recommendations for immediate teacher feedback.
        Input: metrics dictionary with 'people', 'engagement_score', 'engagement_state'
        Output: List of { type: 'alert'|'warning'|'info'|'success', message: str }
        """
        recs = []
        people = metrics.get('people', [])
        engagement_score = metrics.get('engagement_score', 0)
        
        # 1. Distraction alert for individual anonymous participants
        for p in people:
            pid = p.get('id', 'Participant')
            att = p.get('attention', 100)
            if att < 35:
                recs.append({
                    'type': 'alert',
                    'message': f"{pid} attention low ({int(att)}%). Consider directing an interactive prompt."
                })
        
        # 2. Global Engagement checks
        if people and engagement_score < 45:
            recs.append({
                'type': 'warning',
                'message': f"Classroom engagement dropping ({int(engagement_score)}/100). Consider a brief interactive check-in."
            })
        elif people and engagement_score >= 75:
            recs.append({
                'type': 'success',
                'message': f"Classroom engagement is optimal ({int(engagement_score)}/100). Maintain current lecture pacing."
            })
            
        return recs
