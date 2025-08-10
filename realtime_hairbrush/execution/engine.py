"""
Execution engine for the Realtime Hairbrush SDK.

This module provides an execution engine for real-time command execution.
"""

import time
from typing import Dict, Any, Optional, Union, List, Generator, Callable
import threading
import queue

from semantic_gcode.gcode.base import GCodeInstruction
from realtime_hairbrush.transport.airbrush_transport import AirbrushTransport


class ExecutionEngine:
    """
    Execution engine for real-time command execution.
    
    This class handles the execution of G-code instructions with precise timing control
    and state management.
    """
    
    def __init__(self, transport: AirbrushTransport, state_manager=None):
        """
        Initialize the execution engine.
        
        Args:
            transport: Transport for sending commands
            state_manager: Optional state manager for tracking machine state
        """
        self.transport = transport
        self.state_manager = state_manager
        self.command_queue = queue.Queue()
        self.timing_records = []
        self.running = False
        self.execution_thread = None
        self.last_execution_time = 0
        self.execution_callbacks = []
    
    def queue_instruction(self, instruction: GCodeInstruction) -> None:
        """
        Queue a single instruction for execution.
        
        Args:
            instruction: G-code instruction to queue
        """
        self.command_queue.put(instruction)
    
    def queue_instructions(self, instructions: List[GCodeInstruction]) -> None:
        """
        Queue multiple instructions for execution.
        
        Args:
            instructions: List of G-code instructions to queue
        """
        for instruction in instructions:
            self.command_queue.put(instruction)
    
    def queue_generator(self, generator: Generator[GCodeInstruction, None, None]) -> None:
        """
        Queue instructions from a generator.
        
        Args:
            generator: Generator yielding G-code instructions
        """
        for instruction in generator:
            self.command_queue.put(instruction)
    
    def add_execution_callback(self, callback: Callable[[GCodeInstruction, bool, Optional[str]], None]) -> None:
        """
        Add a callback to be called after each instruction execution.
        
        Args:
            callback: Function to call with (instruction, success, message)
        """
        self.execution_callbacks.append(callback)
    
    def start_execution(self) -> None:
        """
        Start the execution thread.
        """
        if self.running:
            return
            
        self.running = True
        self.execution_thread = threading.Thread(target=self._execution_loop)
        self.execution_thread.daemon = True
        self.execution_thread.start()
    
    def stop_execution(self) -> None:
        """
        Stop the execution thread.
        """
        self.running = False
        if self.execution_thread:
            self.execution_thread.join(timeout=1.0)
            self.execution_thread = None
    
    def clear_queue(self) -> None:
        """
        Clear the command queue.
        """
        while not self.command_queue.empty():
            try:
                self.command_queue.get_nowait()
                self.command_queue.task_done()
            except queue.Empty:
                break
    
    def _execution_loop(self) -> None:
        """
        Main execution loop that runs in a separate thread.
        """
        while self.running:
            try:
                # Get the next instruction from the queue with a timeout
                instruction = self.command_queue.get(timeout=0.1)
                
                # Execute the instruction
                success, message = self._execute_instruction(instruction)
                
                # Call callbacks
                for callback in self.execution_callbacks:
                    try:
                        callback(instruction, success, message)
                    except Exception as e:
                        print(f"Error in execution callback: {e}")
                
                # Mark the task as done
                self.command_queue.task_done()
            except queue.Empty:
                # No instructions in the queue, just continue
                pass
            except Exception as e:
                print(f"Error in execution loop: {e}")
    
    def _execute_instruction(self, instruction: GCodeInstruction) -> tuple[bool, Optional[str]]:
        """
        Execute a single instruction.
        
        Args:
            instruction: G-code instruction to execute
            
        Returns:
            tuple: (success, message)
        """
        start_time = time.time()
        
        # Validate the instruction against the current state if a state manager is available
        if self.state_manager:
            valid, message = self.state_manager.validate_command(instruction)
            if not valid:
                return False, message
        
        # Send the instruction to the device
        try:
            result = self.transport.send_line(str(instruction))
            if not result:
                return False, f"Failed to send: {instruction}"
        except Exception as e:
            return False, f"Error sending: {e}"
        
        # Record timing
        end_time = time.time()
        self.timing_records.append({
            'instruction': str(instruction),
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time
        })
        self.last_execution_time = end_time
        
        # Update state if a state manager is available
        if self.state_manager:
            self.state_manager.apply_command(instruction)
        
        # Special handling for timing-sensitive commands
        if instruction.code_type == "G" and instruction.code_number == 4:
            # This is a dwell command, no need for additional wait
            pass
        elif instruction.code_type == "M" and instruction.code_number == 106:
            # Air control command - ensure we wait for air to stabilize
            # Check if this is turning air on (S > 0)
            if "S" in instruction.parameters and instruction.parameters["S"] > 0:
                # Check if a dwell follows in the queue
                has_dwell = False
                try:
                    # Peek at the next item without removing it
                    next_item = self.command_queue.queue[0]
                    if next_item.code_type == "G" and next_item.code_number == 4:
                        has_dwell = True
                except (IndexError, AttributeError):
                    pass
                
                # If no dwell follows, add a small wait
                if not has_dwell:
                    time.sleep(0.05)  # 50ms
        
        return True, "Command executed successfully"
    
    def get_timing_report(self) -> Dict[str, Any]:
        """
        Generate a report of command execution timing.
        
        Returns:
            Dict[str, Any]: Timing report
        """
        if not self.timing_records:
            return {
                'total_commands': 0,
                'total_duration': 0,
                'average_command_time': 0,
                'commands': []
            }
            
        return {
            'total_commands': len(self.timing_records),
            'total_duration': sum(r['duration'] for r in self.timing_records),
            'average_command_time': sum(r['duration'] for r in self.timing_records) / len(self.timing_records),
            'commands': self.timing_records
        }
    
    def wait_for_queue_empty(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for the command queue to be empty.
        
        Args:
            timeout: Maximum time to wait in seconds, or None to wait indefinitely
            
        Returns:
            bool: True if the queue is empty, False if timed out
        """
        try:
            self.command_queue.join(timeout=timeout)
            return True
        except Exception:
            return False
    
    def get_queue_size(self) -> int:
        """
        Get the current size of the command queue.
        
        Returns:
            int: Number of commands in the queue
        """
        return self.command_queue.qsize() 