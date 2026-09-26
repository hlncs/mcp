import asyncio
import logging
import time
from typing import Callable, Any, Optional, TypeVar, Coroutine
from enum import Enum
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger('resilience')

T = TypeVar('T')

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker '{self.name}' entering HALF_OPEN state")
            else:
                raise Exception(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Service unavailable. Retry in {self._time_until_retry()}s"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker '{self.name}' entering HALF_OPEN state")
            else:
                raise Exception(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Service unavailable. Retry in {self._time_until_retry()}s"
                )
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info(f"Circuit breaker '{self.name}' CLOSED (recovered)")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker '{self.name}' OPEN after {self.failure_count} failures"
            )
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time passed to retry"""
        if not self.last_failure_time:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def _time_until_retry(self) -> int:
        """Time remaining until next retry"""
        if not self.last_failure_time:
            return 0
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        remaining = max(0, self.recovery_timeout - elapsed)
        return int(remaining)
    
    def get_status(self) -> dict:
        """Get circuit breaker status"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "time_until_retry": self._time_until_retry()
        }

def retry_async(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_multiplier: float = 2.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,)
):
    """Async retry decorator with exponential backoff"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                
                except exceptions as e:
                    attempt += 1
                    
                    if attempt >= max_attempts:
                        logger.error(
                            f"Failed after {max_attempts} attempts: {str(e)}",
                            exc_info=True
                        )
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed. "
                        f"Retrying in {current_delay}s: {str(e)}"
                    )
                    
                    await asyncio.sleep(current_delay)
                    current_delay = min(current_delay * backoff_multiplier, max_delay)
        
        return wrapper
    return decorator

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_multiplier: float = 2.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,)
):
    """Sync retry decorator with exponential backoff"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    attempt += 1
                    
                    if attempt >= max_attempts:
                        logger.error(
                            f"Failed after {max_attempts} attempts: {str(e)}",
                            exc_info=True
                        )
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed. "
                        f"Retrying in {current_delay}s: {str(e)}"
                    )
                    
                    time.sleep(current_delay)
                    current_delay = min(current_delay * backoff_multiplier, max_delay)
        
        return wrapper
    return decorator

class TimeoutManager:
    """Manage timeouts for operations"""
    
    def __init__(self, timeout_seconds: float, operation_name: str = "Operation"):
        self.timeout_seconds = timeout_seconds
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        if elapsed > self.timeout_seconds:
            logger.warning(
                f"{self.operation_name} exceeded timeout: "
                f"{elapsed:.2f}s > {self.timeout_seconds}s"
            )
    
    def check(self) -> bool:
        """Check if timeout exceeded"""
        if not self.start_time:
            return False
        
        elapsed = time.time() - self.start_time
        return elapsed > self.timeout_seconds
    
    def remaining(self) -> float:
        """Get remaining time"""
        if not self.start_time:
            return self.timeout_seconds
        
        elapsed = time.time() - self.start_time
        return max(0, self.timeout_seconds - elapsed)

class ServiceHealthCheck:
    """Monitor service health"""
    
    def __init__(
        self,
        name: str,
        check_interval: int = 30,
        unhealthy_threshold: int = 3
    ):
        self.name = name
        self.check_interval = check_interval
        self.unhealthy_threshold = unhealthy_threshold
        
        self.is_healthy = True
        self.last_check = None
        self.consecutive_failures = 0
    
    async def check_health(self, check_func: Callable) -> bool:
        """Check service health"""
        try:
            result = await check_func()
            
            if result:
                self.is_healthy = True
                self.consecutive_failures = 0
                self.last_check = datetime.now()
                return True
            else:
                raise Exception("Health check returned False")
        
        except Exception as e:
            self.consecutive_failures += 1
            logger.warning(
                f"Health check failed for '{self.name}': {str(e)} "
                f"({self.consecutive_failures}/{self.unhealthy_threshold})"
            )
            
            if self.consecutive_failures >= self.unhealthy_threshold:
                self.is_healthy = False
            
            return False
    
    def get_status(self) -> dict:
        """Get health status"""
        return {
            "name": self.name,
            "is_healthy": self.is_healthy,
            "consecutive_failures": self.consecutive_failures,
            "last_check": self.last_check.isoformat() if self.last_check else None
        }