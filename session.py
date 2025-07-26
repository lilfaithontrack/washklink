import threading
from typing import Optional
import logging

logger = logging.getLogger(__name__)

SESSION_LOCK = threading.Lock()

class SessionStore:
    def __init__(self):
        self.store = {}
    
    def get(self, session_id: str) -> Optional[int]:
        return self.store.get(session_id)
    
    def set(self, session_id: str, user_id: int):
        self.store[session_id] = user_id
    
    def delete(self, session_id: str):
        self.store.pop(session_id, None)
    
    def clear_all(self):
        self.store.clear()

SESSION_STORE = SessionStore() 