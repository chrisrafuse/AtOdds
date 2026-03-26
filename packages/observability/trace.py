"""
Basic run trace/logging
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from data.contracts import CR_step, CR_tool_call


@dataclass
class TraceSession:
    """Trace session for a single run"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    steps: List[CR_step] = None
    tool_calls: List[CR_tool_call] = None
    errors: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []
        if self.tool_calls is None:
            self.tool_calls = []
        if self.errors is None:
            self.errors = []


class Tracer:
    """
    Simple tracer for system execution
    """
    
    def __init__(self, log_dir: str = None):
        """
        Initialize tracer
        
        Args:
            log_dir: Directory to store trace logs
        """
        self.log_dir = log_dir or os.path.join(os.path.dirname(__file__), '..', '..', '..', 'logs')
        self.current_session: Optional[TraceSession] = None
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
    
    def start_session(self, session_id: str = None) -> str:
        """
        Start a new trace session
        
        Args:
            session_id: Optional session ID, auto-generated if None
            
        Returns:
            Session ID
        """
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = TraceSession(
            session_id=session_id,
            start_time=datetime.now()
        )
        
        self.log_step("session_start", "Started trace session")
        return session_id
    
    def end_session(self) -> Optional[Dict[str, Any]]:
        """
        End current session and save trace
        
        Returns:
            Session summary or None if no active session
        """
        if self.current_session is None:
            return None
        
        self.current_session.end_time = datetime.now()
        self.log_step("session_end", "Ended trace session")
        
        # Save trace to file
        trace_data = self._serialize_session()
        self._save_trace(trace_data)
        
        # Generate summary
        summary = self._generate_summary()
        
        self.current_session = None
        return summary
    
    def log_step(self, step_name: str, description: str, details: Dict[str, Any] = None) -> None:
        """
        Log a step in the current session
        
        Args:
            step_name: Name of the step
            description: Description of the step
            details: Additional details
        """
        if self.current_session is None:
            return
        
        step = CR_step(
            name=step_name,
            timestamp=datetime.now(),
            duration_ms=0,  # Will be calculated when step ends
            status="success",
            details=details or {}
        )
        
        self.current_session.steps.append(step)
    
    def log_tool_call(self, tool_name: str, inputs: Dict[str, Any], 
                     outputs: Dict[str, Any], duration_ms: int, 
                     status: str = "success") -> None:
        """
        Log a tool call
        
        Args:
            tool_name: Name of the tool
            inputs: Tool inputs
            outputs: Tool outputs
            duration_ms: Duration in milliseconds
            status: Status of the call
        """
        if self.current_session is None:
            return
        
        tool_call = CR_tool_call(
            tool_name=tool_name,
            timestamp=datetime.now(),
            inputs=inputs,
            outputs=outputs,
            duration_ms=duration_ms,
            status=status
        )
        
        self.current_session.tool_calls.append(tool_call)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """
        Log an error
        
        Args:
            error: Exception that occurred
            context: Additional context
        """
        if self.current_session is None:
            return
        
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        self.current_session.errors.append(error_data)
    
    def _serialize_session(self) -> Dict[str, Any]:
        """Serialize current session to dictionary"""
        if self.current_session is None:
            return {}
        
        return {
            'session_id': self.current_session.session_id,
            'start_time': self.current_session.start_time.isoformat(),
            'end_time': self.current_session.end_time.isoformat() if self.current_session.end_time else None,
            'steps': [asdict(step) for step in self.current_session.steps],
            'tool_calls': [asdict(call) for call in self.current_session.tool_calls],
            'errors': self.current_session.errors
        }
    
    def _save_trace(self, trace_data: Dict[str, Any]) -> None:
        """Save trace data to file"""
        filename = f"trace_{trace_data['session_id']}.json"
        filepath = os.path.join(self.log_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(trace_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save trace: {e}")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate session summary"""
        if self.current_session is None:
            return {}
        
        session = self.current_session
        duration = (session.end_time - session.start_time).total_seconds() if session.end_time else 0
        
        # Count steps by status
        step_counts = {}
        for step in session.steps:
            step_counts[step.status] = step_counts.get(step.status, 0) + 1
        
        # Count tool calls by status and type
        tool_counts = {}
        tool_durations = {}
        for call in session.tool_calls:
            tool_counts[call.status] = tool_counts.get(call.status, 0) + 1
            
            tool_name = call.tool_name
            if tool_name not in tool_durations:
                tool_durations[tool_name] = []
            tool_durations[tool_name].append(call.duration_ms)
        
        # Calculate average durations
        avg_durations = {}
        for tool_name, durations in tool_durations.items():
            avg_durations[tool_name] = sum(durations) / len(durations)
        
        return {
            'session_id': session.session_id,
            'duration_seconds': duration,
            'total_steps': len(session.steps),
            'step_counts': step_counts,
            'total_tool_calls': len(session.tool_calls),
            'tool_counts': tool_counts,
            'average_tool_durations_ms': avg_durations,
            'total_errors': len(session.errors),
            'error_types': list(set(error['error_type'] for error in session.errors))
        }


# Global tracer instance
_global_tracer: Optional[Tracer] = None


def get_tracer() -> Tracer:
    """Get global tracer instance"""
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = Tracer()
    return _global_tracer


def trace_tool_call(tool_name: str):
    """
    Decorator to automatically trace tool calls
    
    Args:
        tool_name: Name of the tool for tracing
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            start_time = datetime.now()
            
            try:
                # Call the function
                result = func(*args, **kwargs)
                
                # Calculate duration
                end_time = datetime.now()
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Log successful call
                tracer.log_tool_call(
                    tool_name=tool_name,
                    inputs={'args': str(args), 'kwargs': str(kwargs)},
                    outputs={'result': str(result)[:200]},  # Limit output size
                    duration_ms=duration_ms,
                    status='success'
                )
                
                return result
                
            except Exception as e:
                # Calculate duration
                end_time = datetime.now()
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Log failed call
                tracer.log_tool_call(
                    tool_name=tool_name,
                    inputs={'args': str(args), 'kwargs': str(kwargs)},
                    outputs={'error': str(e)},
                    duration_ms=duration_ms,
                    status='error'
                )
                
                tracer.log_error(e, {'tool': tool_name, 'args': args, 'kwargs': kwargs})
                
                raise
        
        return wrapper
    return decorator


def trace_step(step_name: str):
    """
    Decorator to automatically trace steps
    
    Args:
        step_name: Name of the step for tracing
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            
            tracer.log_step(step_name, f"Starting {step_name}")
            
            try:
                result = func(*args, **kwargs)
                tracer.log_step(step_name, f"Completed {step_name}")
                return result
            except Exception as e:
                tracer.log_error(e, {'step': step_name})
                raise
        
        return wrapper
    return decorator
