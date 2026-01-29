import os
from dotenv import load_dotenv
from calendar_collector import CalendarCollector
from event_normalizer import EventNormalizer
from context_builder import ContextBuilder
from ai_reasoning import AIReasoning
from reminder_output import ReminderOutput

load_dotenv()

def main():
    print("🔄 Reminder-Time AI Starting...\n")
    
    try:
        collector = CalendarCollector()
        events = collector.fetch_events(days_ahead=7)
        
        if not events:
            print("No upcoming events found.")
            return
        
        print(f"✓ Fetched {len(events)} events\n")
        
        normalizer = EventNormalizer()
        normalized_events = normalizer.normalize(events)
        
        print("✓ Events normalized\n")
        
        context_builder = ContextBuilder()
        context = context_builder.build(normalized_events)
        
        print("✓ Context built\n")
        
        ai = AIReasoning()
        reasoning = ai.get_intelligence(context, normalized_events)
        
        print("✓ AI reasoning complete\n")
        
        output = ReminderOutput()
        output.display(reasoning, normalized_events)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()