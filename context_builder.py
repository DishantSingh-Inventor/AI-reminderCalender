from datetime import datetime, timedelta
import pytz

class ContextBuilder:
    def __init__(self, timezone='UTC'):
        self.timezone = pytz.timezone(timezone)
    
    def build(self, normalized_events):
        now = datetime.now(pytz.timezone(self.timezone))
        
        upcoming_7_days = [e for e in normalized_events if e['days_left'] <= 7 and e['days_left'] >= 0]
        high_priority = [e for e in upcoming_7_days if e['priority'] == 'high']
        exams = [e for e in upcoming_7_days if e['type'] == 'exam']
        deadlines = [e for e in upcoming_7_days if e['type'] == 'deadline']
        
        context = {
            'current_datetime': now.isoformat(),
            'day_of_week': now.strftime('%A'),
            'total_upcoming_events': len(upcoming_7_days),
            'high_priority_count': len(high_priority),
            'exam_count': len(exams),
            'deadline_count': len(deadlines),
            'busiest_day': self._find_busiest_day(normalized_events),
            'free_slots': self._find_free_slots(normalized_events),
            'conflicts': self._find_conflicts(normalized_events),
            'events_by_type': self._group_by_type(upcoming_7_days),
            'next_critical_event': high_priority[0] if high_priority else None,
            'timeline_summary': self._build_timeline_summary(upcoming_7_days),
        }
        
        return context
    
    def _find_busiest_day(self, events):
        if not events:
            return None
        
        day_counts = {}
        for event in events:
            day_key = event['start'].strftime('%Y-%m-%d') if event['start'] else None
            if day_key:
                day_counts[day_key] = day_counts.get(day_key, 0) + 1
        
        if not day_counts:
            return None
        
        busiest = max(day_counts.items(), key=lambda x: x[1])
        return {'date': busiest[0], 'event_count': busiest[1]}
    
    def _find_free_slots(self, events):
        sorted_events = sorted(
            [e for e in events if e['start'] and e['end']], 
            key=lambda x: x['start']
        )
        
        free_slots = []
        now = datetime.now(pytz.timezone(self.timezone))
        
        for i, event in enumerate(sorted_events[:-1]):
            gap_start = event['end']
            gap_end = sorted_events[i + 1]['start']
            gap_minutes = int((gap_end - gap_start).total_seconds() / 60)
            
            if gap_minutes >= 60 and gap_start >= now:
                free_slots.append({
                    'start': gap_start.isoformat(),
                    'end': gap_end.isoformat(),
                    'duration_minutes': gap_minutes
                })
        
        return free_slots[:3]
    
    def _find_conflicts(self, events):
        sorted_events = sorted(
            [e for e in events if e['start'] and e['end']], 
            key=lambda x: x['start']
        )
        
        conflicts = []
        for i in range(len(sorted_events) - 1):
            if sorted_events[i]['end'] > sorted_events[i + 1]['start']:
                conflicts.append({
                    'event1': sorted_events[i]['title'],
                    'event2': sorted_events[i + 1]['title'],
                    'time': sorted_events[i + 1]['start'].isoformat()
                })
        
        return conflicts
    
    def _group_by_type(self, events):
        grouped = {}
        for event in events:
            event_type = event['type']
            if event_type not in grouped:
                grouped[event_type] = []
            grouped[event_type].append(event['title'])
        
        return {k: len(v) for k, v in grouped.items()}
    
    def _build_timeline_summary(self, events):
        if not events:
            return "No upcoming events."
        
        summary_parts = []
        for event in events[:5]:
            days_text = "today" if event['days_left'] == 0 else f"in {event['days_left']} days"
            priority_emoji = "🔴" if event['priority'] == 'high' else "🟡" if event['priority'] == 'medium' else "🟢"
            summary_parts.append(
                f"{priority_emoji} {event['title']} — {days_text}"
            )
        
        return "\n".join(summary_parts)