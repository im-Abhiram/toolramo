"""
Ramonet Login Rate Limiting & Brute-Force Protection Subsystem.
Tracks failed authentication attempts per IP and username to mitigate credential stuffing.
"""
import time
from collections import defaultdict
from threading import Lock
from typing import Tuple

class LoginRateLimiter:
    """
    In-memory rate limiter with thread-safe sliding window tracking.
    Enforces a maximum threshold of consecutive failed login attempts.
    """
    def __init__(self, max_attempts: int = 5, lockout_seconds: int = 300):
        self.max_attempts = max_attempts
        self.lockout_seconds = lockout_seconds
        self.attempts = defaultdict(list)  # key -> list of timestamps
        self.lock = Lock()

    def _clean_old_attempts(self, now: float, key: str):
        cutoff = now - self.lockout_seconds
        self.attempts[key] = [t for t in self.attempts[key] if t > cutoff]

    def is_locked_out(self, ip: str, username: str = '') -> Tuple[bool, int]:
        """
        Checks if the IP or username is currently locked out.
        Returns (is_locked, seconds_remaining).
        """
        now = time.time()
        with self.lock:
            # Check by IP
            self._clean_old_attempts(now, f"ip:{ip}")
            ip_attempts = self.attempts[f"ip:{ip}"]
            if len(ip_attempts) >= self.max_attempts:
                oldest = ip_attempts[0]
                remaining = int(self.lockout_seconds - (now - oldest))
                return True, max(1, remaining)

            # Check by username if provided
            if username:
                u_key = f"user:{username.strip().lower()}"
                self._clean_old_attempts(now, u_key)
                user_attempts = self.attempts[u_key]
                if len(user_attempts) >= self.max_attempts:
                    oldest = user_attempts[0]
                    remaining = int(self.lockout_seconds - (now - oldest))
                    return True, max(1, remaining)

        return False, 0

    def record_failure(self, ip: str, username: str = ''):
        """Records a failed authentication attempt."""
        now = time.time()
        with self.lock:
            if ip:
                self.attempts[f"ip:{ip}"].append(now)
            if username:
                self.attempts[f"user:{username.strip().lower()}"].append(now)

    def record_success(self, ip: str, username: str = ''):
        """Resets failed attempt counters upon successful authentication."""
        with self.lock:
            if ip:
                self.attempts.pop(f"ip:{ip}", None)
            if username:
                self.attempts.pop(f"user:{username.strip().lower()}", None)

    def reset_all(self):
        """Clears all rate limit state (primarily for test tearDown)."""
        with self.lock:
            self.attempts.clear()

# Global singleton rate limiter instance
login_rate_limiter = LoginRateLimiter(max_attempts=5, lockout_seconds=300)
