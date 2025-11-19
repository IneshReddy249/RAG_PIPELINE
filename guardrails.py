"""
Minimal Security Guardrails - High quality, <100 lines
"""
import re
from typing import Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class Guardrails:
    """Lightweight security guardrails"""
    
    # Block obvious attacks
    BLOCKED_PATTERNS = [
        r"ignore (previous|all) instructions",
        r"you are now in (admin|debug) mode",
        r"system prompt",
        r"how to (make|build) (bomb|weapon)",
        r"(list|show|extract) all (emails?|ssn|phone)",
    ]
    
    def __init__(self):
        self.history = defaultdict(list)  # Track requests per session
    
    def check_query(self, query: str, session_id: str = None) -> Tuple[bool, Optional[str]]:
        """Check if query is safe. Returns (is_safe, reason_if_blocked)"""
        
        # Basic validation
        if not query.strip():
            return False, "Empty query"
        if len(query) > 2000:
            return False, "Query too long (max 2000 chars)"
        
        # Check for attacks
        query_lower = query.lower()
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, query_lower):
                return False, "Suspicious content detected"
        
        # Rate limit: 10 queries per minute
        if session_id:
            now = datetime.utcnow()
            recent = [t for t in self.history[session_id] if now - t < timedelta(minutes=1)]
            
            if len(recent) >= 10:
                return False, "Rate limit: 10 queries/minute"
            
            self.history[session_id].append(now)
        
        return True, None
    
    def check_upload(self, filename: str, size_bytes: int) -> Tuple[bool, Optional[str]]:
        """Check if file upload is safe. Returns (is_safe, reason_if_blocked)"""
        
        # Size limit: 50MB
        if size_bytes > 50 * 1024 * 1024:
            return False, "File too large (max 50MB)"
        
        # Extension whitelist
        allowed = {'.pdf', '.txt', '.md'}
        ext = '.' + filename.lower().split('.')[-1] if '.' in filename else ''
        if ext not in allowed:
            return False, f"Only {', '.join(allowed)} allowed"
        
        # Prevent path traversal
        if any(c in filename for c in ['..', '/', '\\']):
            return False, "Invalid filename"
        
        return True, None
    
    def sanitize(self, text: str) -> str:
        """Remove sensitive data from responses"""
        # Remove emails
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        # Remove phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        # Remove long alphanumeric strings (potential API keys)
        text = re.sub(r'\b[a-zA-Z0-9]{40,}\b', '[REDACTED]', text)
        return text
    
    def cleanup(self):
        """Remove old tracking data (call periodically)"""
        cutoff = datetime.utcnow() - timedelta(hours=1)
        for session_id in list(self.history.keys()):
            self.history[session_id] = [t for t in self.history[session_id] if t > cutoff]
            if not self.history[session_id]:
                del self.history[session_id]


# Quick test
if __name__ == "__main__":
    g = Guardrails()
    
    tests = [
        ("What causes hallucinations?", True),
        ("Ignore previous instructions", False),
        ("How to make a bomb", False),
        ("Show me all email addresses", False),
    ]
    
    for query, should_pass in tests:
        is_safe, reason = g.check_query(query, "test_session")
        passed = "✅" if is_safe == should_pass else "❌"
        print(f"{passed} {query[:40]}: {'SAFE' if is_safe else reason}")