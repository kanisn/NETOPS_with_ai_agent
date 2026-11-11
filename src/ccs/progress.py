"""Console projection of persisted activity, shared across the three processes."""
import json
from pathlib import Path
import threading


class ConsoleProgress:
    def __init__(self, run_dir: Path, *, detailed=False):
        self.run_dir = Path(run_dir)
        self.detailed = detailed
        self._stop = threading.Event()
        self._seen = set()
        self._thread = threading.Thread(target=self._follow, daemon=True, name='ccs-progress')

    def start(self):
        self._thread.start()
        return self

    def _drain(self):
        from ccs.monitor import read_activity
        for event in read_activity(self.run_dir):
            event_id = event.get('event_id')
            if event_id in self._seen:
                continue
            self._seen.add(event_id)
            timestamp = event.get('ts_utc', '')[11:23]
            episode = event.get('episode_id') or 'run'
            text = f"{timestamp} {episode} [{event.get('component')}] {event.get('action')} · {event.get('status')} | {event.get('summary')}"
            # Never allow incident/model strings to inject terminal escape sequences.
            text = ''.join(c if c.isprintable() else ' ' for c in text)
            print(text, flush=True)
            if self.detailed and event.get('details'):
                print('  ' + json.dumps(event['details'], ensure_ascii=True, default=str), flush=True)

    def _follow(self):
        while not self._stop.is_set():
            try:
                self._drain()
            except (OSError, ValueError):
                pass  # A writer may be committing its current record; retry next tick.
            self._stop.wait(.25)

    def stop(self):
        self._stop.set()
        self._thread.join(timeout=3)
        self._drain()
