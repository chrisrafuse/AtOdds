"""
Basic run trace/logging with CR_ prefix compliance
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional


def create_CR_trace_session(
    CR_session_id: str,
    CR_start_time: datetime,
    CR_end_time: Optional[datetime] = None,
    CR_steps: Optional[List[Dict[str, Any]]] = None,
    CR_tool_calls: Optional[List[Dict[str, Any]]] = None,
    CR_errors: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Create CR_ trace session dictionary
    
    Args:
        CR_session_id: Session identifier
        CR_start_time: Session start time
        CR_end_time: Optional session end time
        CR_steps: List of CR_ step dictionaries
        CR_tool_calls: List of CR_ tool call dictionaries
        CR_errors: List of CR_ error dictionaries
    
    Returns:
        CR_ trace session dictionary
    """
    return {
        'CR_session_id': CR_session_id,
        'CR_start_time': CR_start_time,
        'CR_end_time': CR_end_time,
        'CR_steps': CR_steps or [],
        'CR_tool_calls': CR_tool_calls or [],
        'CR_errors': CR_errors or []
    }


class CR_Tracer:
    """
    Simple tracer for system execution with CR_ prefix compliance
    """
    
    def __init__(self, CR_log_dir: str = None):
        """
        Initialize CR_ tracer
        
        Args:
            CR_log_dir: Directory to store trace logs
        """
        self.CR_log_dir = CR_log_dir or os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
        self.CR_current_session: Optional[Dict[str, Any]] = None
        
        # Ensure log directory exists
        os.makedirs(self.CR_log_dir, exist_ok=True)
    
    def start_CR_session(self, CR_session_id: str = None) -> str:
        """
        Start a new CR_ trace session
        
        Args:
            CR_session_id: Optional session ID, auto-generated if None
            
        Returns:
            Session ID
        """
        if CR_session_id is None:
            CR_session_id = f"CR_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.CR_current_session = create_CR_trace_session(
            CR_session_id=CR_session_id,
            CR_start_time=datetime.now()
        )
        
        self.log_CR_step("CR_session_start", "Started CR_ trace session")
        return CR_session_id
    
    def end_CR_session(self) -> Optional[Dict[str, Any]]:
        """
        End current CR_ session and save trace
        
        Returns:
            Session summary or None if no active session
        """
        if self.CR_current_session is None:
            return None
        
        self.CR_current_session['CR_end_time'] = datetime.now()
        self.log_CR_step("CR_session_end", "Ended CR_ trace session")
        
        # Save trace to file
        CR_trace_data = self._serialize_CR_session()
        self._save_CR_trace(CR_trace_data)
        
        # Generate summary
        CR_summary = self._generate_CR_summary()
        
        self.CR_current_session = None
        return CR_summary
    
    def log_CR_step(self, CR_step_name: str, CR_description: str, CR_details: Dict[str, Any] = None) -> None:
        """
        Log a CR_ step in the current session
        
        Args:
            CR_step_name: Name of the step
            CR_description: Description of the step
            CR_details: Additional details
        """
        if self.CR_current_session is None:
            return
        
        CR_step = {
            'CR_name': CR_step_name,
            'CR_timestamp': datetime.now().isoformat(),
            'CR_description': CR_description,
            'CR_duration_ms': 0,  # Will be calculated when step ends
            'CR_status': "success",
            'CR_details': CR_details or {}
        }
        
        self.CR_current_session['CR_steps'].append(CR_step)
    
    def log_CR_tool_call(self, CR_tool_name: str, CR_inputs: Dict[str, Any], 
                     CR_outputs: Dict[str, Any], CR_duration_ms: int, 
                     CR_status: str = "success") -> None:
        """
        Log a CR_ tool call
        
        Args:
            CR_tool_name: Name of the tool
            CR_inputs: Tool inputs
            CR_outputs: Tool outputs
            CR_duration_ms: Duration in milliseconds
            CR_status: Status of the call
        """
        if self.CR_current_session is None:
            return
        
        CR_tool_call = {
            'CR_tool_name': CR_tool_name,
            'CR_timestamp': datetime.now().isoformat(),
            'CR_inputs': CR_inputs,
            'CR_outputs': CR_outputs,
            'CR_duration_ms': CR_duration_ms,
            'CR_status': CR_status
        }
        
        self.CR_current_session['CR_tool_calls'].append(CR_tool_call)
    
    def log_CR_error(self, CR_error: Exception, CR_context: Dict[str, Any] = None) -> None:
        """
        Log a CR_ error
        
        Args:
            CR_error: Exception that occurred
            CR_context: Additional context
        """
        if self.CR_current_session is None:
            return
        
        CR_error_data = {
            'CR_timestamp': datetime.now().isoformat(),
            'CR_error_type': type(CR_error).__name__,
            'CR_error_message': str(CR_error),
            'CR_context': CR_context or {}
        }
        
        self.CR_current_session['CR_errors'].append(CR_error_data)
    
    def _serialize_CR_session(self) -> Dict[str, Any]:
        """Serialize current CR_ session to dictionary"""
        if self.CR_current_session is None:
            return {}
        
        CR_session = self.CR_current_session
        CR_start_time = CR_session.get('CR_start_time')
        CR_end_time = CR_session.get('CR_end_time')
        
        return {
            'CR_session_id': CR_session.get('CR_session_id'),
            'CR_start_time': CR_start_time.isoformat() if isinstance(CR_start_time, datetime) else CR_start_time,
            'CR_end_time': CR_end_time.isoformat() if isinstance(CR_end_time, datetime) else CR_end_time,
            'CR_steps': CR_session.get('CR_steps', []),
            'CR_tool_calls': CR_session.get('CR_tool_calls', []),
            'CR_errors': CR_session.get('CR_errors', [])
        }
    
    def _save_CR_trace(self, CR_trace_data: Dict[str, Any]) -> None:
        """Save CR_ trace data to file"""
        CR_filename = f"CR_trace_{CR_trace_data.get('CR_session_id', 'unknown')}.json"
        CR_filepath = os.path.join(self.CR_log_dir, CR_filename)
        
        try:
            with open(CR_filepath, 'w') as CR_file:
                json.dump(CR_trace_data, CR_file, indent=2)
        except Exception as CR_exception:
            print(f"Failed to save CR_ trace: {CR_exception}")
    
    def _generate_CR_summary(self) -> Dict[str, Any]:
        """Generate CR_ session summary"""
        if self.CR_current_session is None:
            return {}
        
        CR_session = self.CR_current_session
        CR_start_time = CR_session.get('CR_start_time')
        CR_end_time = CR_session.get('CR_end_time')
        
        if isinstance(CR_start_time, datetime) and isinstance(CR_end_time, datetime):
            CR_duration = (CR_end_time - CR_start_time).total_seconds()
        else:
            CR_duration = 0
        
        # Count steps by status
        CR_step_counts = {}
        for CR_step in CR_session.get('CR_steps', []):
            CR_status = CR_step.get('CR_status', 'unknown')
            CR_step_counts[CR_status] = CR_step_counts.get(CR_status, 0) + 1
        
        # Count tool calls by status and type
        CR_tool_counts = {}
        CR_tool_durations = {}
        for CR_call in CR_session.get('CR_tool_calls', []):
            CR_status = CR_call.get('CR_status', 'unknown')
            CR_tool_counts[CR_status] = CR_tool_counts.get(CR_status, 0) + 1
            
            CR_tool_name = CR_call.get('CR_tool_name', 'unknown')
            if CR_tool_name not in CR_tool_durations:
                CR_tool_durations[CR_tool_name] = []
            CR_tool_durations[CR_tool_name].append(CR_call.get('CR_duration_ms', 0))
        
        # Calculate average durations
        CR_avg_durations = {}
        for CR_tool_name, CR_durations in CR_tool_durations.items():
            if CR_durations:
                CR_avg_durations[CR_tool_name] = sum(CR_durations) / len(CR_durations)
        
        # Get error types
        CR_error_types = []
        for CR_error in CR_session.get('CR_errors', []):
            CR_error_type = CR_error.get('CR_error_type', 'unknown')
            if CR_error_type not in CR_error_types:
                CR_error_types.append(CR_error_type)
        
        return {
            'CR_session_id': CR_session.get('CR_session_id'),
            'CR_duration_seconds': CR_duration,
            'CR_total_steps': len(CR_session.get('CR_steps', [])),
            'CR_step_counts': CR_step_counts,
            'CR_total_tool_calls': len(CR_session.get('CR_tool_calls', [])),
            'CR_tool_counts': CR_tool_counts,
            'CR_average_tool_durations_ms': CR_avg_durations,
            'CR_total_errors': len(CR_session.get('CR_errors', [])),
            'CR_error_types': CR_error_types
        }


# Global CR_ tracer instance
_CR_global_tracer: Optional[CR_Tracer] = None


def get_CR_tracer() -> CR_Tracer:
    """Get global CR_ tracer instance"""
    global _CR_global_tracer
    if _CR_global_tracer is None:
        _CR_global_tracer = CR_Tracer()
    return _CR_global_tracer


def trace_CR_tool_call(CR_tool_name: str):
    """
    Decorator to automatically trace CR_ tool calls
    
    Args:
        CR_tool_name: Name of the tool for tracing
    """
    def CR_decorator(CR_func):
        def CR_wrapper(*CR_args, **CR_kwargs):
            CR_tracer = get_CR_tracer()
            CR_start_time = datetime.now()
            
            try:
                # Call the function
                CR_result = CR_func(*CR_args, **CR_kwargs)
                
                # Calculate duration
                CR_end_time = datetime.now()
                CR_duration_ms = int((CR_end_time - CR_start_time).total_seconds() * 1000)
                
                # Log successful call
                CR_tracer.log_CR_tool_call(
                    CR_tool_name=CR_tool_name,
                    CR_inputs={'CR_args': str(CR_args), 'CR_kwargs': str(CR_kwargs)},
                    CR_outputs={'CR_result': str(CR_result)[:200]},  # Limit output size
                    CR_duration_ms=CR_duration_ms,
                    CR_status='success'
                )
                
                return CR_result
                
            except Exception as CR_exception:
                # Calculate duration
                CR_end_time = datetime.now()
                CR_duration_ms = int((CR_end_time - CR_start_time).total_seconds() * 1000)
                
                # Log failed call
                CR_tracer.log_CR_tool_call(
                    CR_tool_name=CR_tool_name,
                    CR_inputs={'CR_args': str(CR_args), 'CR_kwargs': str(CR_kwargs)},
                    CR_outputs={'CR_error': str(CR_exception)},
                    CR_duration_ms=CR_duration_ms,
                    CR_status='error'
                )
                
                CR_tracer.log_CR_error(CR_exception, {'CR_tool': CR_tool_name, 'CR_args': CR_args, 'CR_kwargs': CR_kwargs})
                
                raise
        
        return CR_wrapper
    return CR_decorator


def trace_CR_step(CR_step_name: str):
    """
    Decorator to automatically trace CR_ steps
    
    Args:
        CR_step_name: Name of the step for tracing
    """
    def CR_decorator(CR_func):
        def CR_wrapper(*CR_args, **CR_kwargs):
            CR_tracer = get_CR_tracer()
            
            CR_tracer.log_CR_step(CR_step_name, f"Starting {CR_step_name}")
            
            try:
                CR_result = CR_func(*CR_args, **CR_kwargs)
                CR_tracer.log_CR_step(CR_step_name, f"Completed {CR_step_name}")
                return CR_result
            except Exception as CR_exception:
                CR_tracer.log_CR_error(CR_exception, {'CR_step': CR_step_name})
                raise
        
        return CR_wrapper
    return CR_decorator
