from datetime import datetime
import pytz

class EventNormalizer:
    def __init__(self, timezone='UTC'):
        self.timezone = pytz.timezone(timezone)
        self.event_types = {
            'exam': ['exam', 'test', 'quiz', 'assessment'],
            'meeting': ['meeting', 'call', 'standup', 'sync', 'conference'],
            'deadline': ['deadline', 'due', 'submit', 'finish'],
            'personal': ['personal', 'birthday', 'appointment'],
            'travel': ['travel', 'flight', 'trip', 'drive']
        }
    
    def normalize(self, events):
        normalized = []
        for event in events:
            normalized.append(self._normalize_single(event))
        return normalized
    
    def _normalize_single(self, event):
        title = event.get('summary', 'Untitled')
        
        start = self._parse_datetime(event.get('start', {}))
        end = self._parse_datetime(event.get('end', {}))
        
        event_type = self._categorize(title)
        priority = self._calculate_priority(event_type, title)
        days_left = self._days_until(start)
        
        return {
            'id': event.get('id'),
            'title': title,
            'start': start,
            'end': end,
            'description': event.get('description', ''),
            'location': event.get('location', ''),
            'type': event_type,
            'priority': priority,
            'days_left': days_left,
            'duration_minutes': self._calculate_duration(start, end),
            'all_day': 'dateTime' not in event.get('start', {})
        }
    
    def _parse_datetime(self, time_obj):
        if 'dateTime' in time_obj:
            dt = datetime.fromisoformat(time_obj['dateTime'].replace('Z', '+00:00'))
            return dt.astimezone(self.timezone)
        elif 'date' in time_obj:
            return datetime.strptime(time_obj['date'], '%Y-%m-%d')
        return None
    
    def _categorize(self, title):
        title_lower = title.lower()
        for category, keywords in self.event_types.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        return 'unknown'
    
    def _calculate_priority(self, event_type, title):
        if event_type in ['exam', 'deadline']:
            return 'high'
        elif event_type == 'meeting':
            return 'medium'
        else:
            return 'low'
    
    def _days_until(self, date):
        if not date:
            return None
        today = datetime.now(self.timezone).replace(hour=0, minute=0, second=0, microsecond=0)
        target = date.replace(hour=0, minute=0, second=0, microsecond=0) if hasattr(date, 'replace') else date
        delta = (target - today).days
        return delta if delta >= 0 else 0
    
    def _calculate_duration(self, start, end):
        if not start or not end:
            return 0
        delta = end - start
        return int(delta.total_seconds() / 60)