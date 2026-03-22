from typing import List, Dict
from collections import deque

class ReplayBuffer:
    def __init__(self, max_seconds: int = 20):
        self.max_frames = max_seconds
        self.buffer = deque(maxlen=self.max_frames)
        
    def add_state(self, current_time: float, drone_states: List[Dict]):
        # Deep copy to ensure history isn't modified
        states_copy = [d.copy() for d in drone_states]
        self.buffer.append({
            "time": current_time,
            "states": states_copy
        })
        
    def get_replay(self) -> List[Dict]:
        """Returns ordered historical states."""
        return list(self.buffer)
        
    def get_state_at_index(self, index: int) -> Dict:
        """Fetch a specific frame from the buffer, negative index allowed."""
        if not self.buffer:
            return None
        idx = max(0, min(len(self.buffer) - 1, index)) if index >= 0 else max(-len(self.buffer), min(-1, index))
        return self.buffer[idx]
        
    def clear(self):
        self.buffer.clear()
