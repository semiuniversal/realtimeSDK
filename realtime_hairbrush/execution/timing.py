"""
Timing module for the Realtime Hairbrush SDK.

This module provides utilities for timing control and monitoring.
"""

import time
from typing import Dict, Any, Optional, List, Callable
import threading


class TimingMonitor:
    """
    Monitor for tracking and analyzing command execution timing.
    """
    
    def __init__(self):
        """
        Initialize the timing monitor.
        """
        self.timing_records = []
        self.start_time = None
        self.end_time = None
        self.is_monitoring = False
        self.monitoring_thread = None
        self.monitoring_interval = 0.1  # seconds
        self.callbacks = []
    
    def start_monitoring(self) -> None:
        """
        Start monitoring timing.
        """
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.start_time = time.time()
        self.timing_records = []
        
        # Start the monitoring thread if needed
        if self.monitoring_thread is None:
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
    
    def stop_monitoring(self) -> None:
        """
        Stop monitoring timing.
        """
        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        self.end_time = time.time()
        
        # Wait for the monitoring thread to stop
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
            self.monitoring_thread = None
    
    def record_event(self, event_type: str, details: Dict[str, Any] = None) -> None:
        """
        Record a timing event.
        
        Args:
            event_type: Type of event
            details: Additional details about the event
        """
        event_time = time.time()
        event = {
            'time': event_time,
            'type': event_type,
            'details': details or {}
        }
        
        if self.start_time:
            event['elapsed'] = event_time - self.start_time
            
        self.timing_records.append(event)
        
        # Notify callbacks
        for callback in self.callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in timing callback: {e}")
    
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a callback to be called for each timing event.
        
        Args:
            callback: Function to call with the event data
        """
        self.callbacks.append(callback)
    
    def get_timing_report(self) -> Dict[str, Any]:
        """
        Generate a timing report.
        
        Returns:
            Dict[str, Any]: Timing report
        """
        if not self.timing_records:
            return {
                'total_events': 0,
                'total_duration': 0,
                'events': []
            }
            
        end = self.end_time or time.time()
        start = self.start_time or end
            
        return {
            'total_events': len(self.timing_records),
            'total_duration': end - start,
            'start_time': start,
            'end_time': end,
            'events': self.timing_records
        }
    
    def _monitoring_loop(self) -> None:
        """
        Main monitoring loop that runs in a separate thread.
        """
        while self.is_monitoring:
            # Record a monitoring event
            self.record_event('monitor_tick', {
                'queue_size': 0,  # This would be filled in by the execution engine
                'time': time.time()
            })
            
            # Sleep for the monitoring interval
            time.sleep(self.monitoring_interval)


class TimingConstraint:
    """
    Constraint for timing requirements.
    """
    
    def __init__(self, min_time: Optional[float] = None, max_time: Optional[float] = None):
        """
        Initialize the timing constraint.
        
        Args:
            min_time: Minimum time in seconds
            max_time: Maximum time in seconds
        """
        self.min_time = min_time
        self.max_time = max_time
    
    def validate(self, actual_time: float) -> tuple[bool, Optional[str]]:
        """
        Validate the actual time against the constraint.
        
        Args:
            actual_time: Actual time in seconds
            
        Returns:
            tuple: (is_valid, message)
        """
        if self.min_time is not None and actual_time < self.min_time:
            return False, f"Time {actual_time:.3f}s is less than minimum {self.min_time:.3f}s"
            
        if self.max_time is not None and actual_time > self.max_time:
            return False, f"Time {actual_time:.3f}s is greater than maximum {self.max_time:.3f}s"
            
        return True, None


def measure_execution_time(func: Callable) -> Callable:
    """
    Decorator for measuring the execution time of a function.
    
    Args:
        func: Function to measure
        
    Returns:
        Callable: Wrapped function
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} executed in {end_time - start_time:.3f} seconds")
        return result
    return wrapper 