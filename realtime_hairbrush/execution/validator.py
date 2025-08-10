"""
Validator module for the Realtime Hairbrush SDK.

This module provides utilities for validating command sequences.
"""

from typing import Dict, Any, Optional, List, Tuple, Generator
import time

from semantic_gcode.gcode.base import GCodeInstruction


class SequenceValidator:
    """
    Validator for command sequences.
    """
    
    def __init__(self):
        """
        Initialize the sequence validator.
        """
        self.validation_rules = []
    
    def add_rule(self, rule: 'ValidationRule') -> None:
        """
        Add a validation rule.
        
        Args:
            rule: Validation rule to add
        """
        self.validation_rules.append(rule)
    
    def validate_sequence(self, sequence: List[GCodeInstruction]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate a sequence of instructions.
        
        Args:
            sequence: List of G-code instructions
            
        Returns:
            Tuple[bool, List[Dict[str, Any]]]: (is_valid, issues)
        """
        all_valid = True
        issues = []
        
        # Apply each validation rule
        for rule in self.validation_rules:
            rule_valid, rule_issues = rule.validate(sequence)
            if not rule_valid:
                all_valid = False
                issues.extend(rule_issues)
        
        return all_valid, issues
    
    def validate_generator(self, generator: Generator[GCodeInstruction, None, None]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate a generator of instructions.
        
        Args:
            generator: Generator yielding G-code instructions
            
        Returns:
            Tuple[bool, List[Dict[str, Any]]]: (is_valid, issues)
        """
        # Convert the generator to a list
        sequence = list(generator)
        return self.validate_sequence(sequence)


class ValidationRule:
    """
    Base class for validation rules.
    """
    
    def validate(self, sequence: List[GCodeInstruction]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate a sequence of instructions.
        
        Args:
            sequence: List of G-code instructions
            
        Returns:
            Tuple[bool, List[Dict[str, Any]]]: (is_valid, issues)
        """
        raise NotImplementedError("Subclasses must implement validate()")


class SafeZHeightRule(ValidationRule):
    """
    Rule for ensuring Z is at safe height before XY movement.
    """
    
    def __init__(self, safe_z_height: float = 5.0):
        """
        Initialize the safe Z height rule.
        
        Args:
            safe_z_height: Safe Z height
        """
        self.safe_z_height = safe_z_height
    
    def validate(self, sequence: List[GCodeInstruction]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate that Z is at safe height before XY movement.
        
        Args:
            sequence: List of G-code instructions
            
        Returns:
            Tuple[bool, List[Dict[str, Any]]]: (is_valid, issues)
        """
        valid = True
        issues = []
        current_z = self.safe_z_height  # Assume starting at safe height
        
        for i, instruction in enumerate(sequence):
            # Update current Z if this is a Z move
            if instruction.code_type == "G" and instruction.code_number in [0, 1]:
                if "Z" in instruction.parameters:
                    current_z = instruction.parameters["Z"]
            
            # Check if this is an XY move and Z is not at safe height
            if instruction.code_type == "G" and instruction.code_number in [0, 1]:
                if ("X" in instruction.parameters or "Y" in instruction.parameters) and current_z < self.safe_z_height:
                    valid = False
                    issues.append({
                        'rule': 'SafeZHeightRule',
                        'index': i,
                        'instruction': str(instruction),
                        'message': f"XY movement at unsafe Z height: {current_z} (should be >= {self.safe_z_height})"
                    })
        
        return valid, issues


class AirBeforePaintRule(ValidationRule):
    """
    Rule for ensuring air is on before paint flow.
    """
    
    def validate(self, sequence: List[GCodeInstruction]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate that air is on before paint flow.
        
        Args:
            sequence: List of G-code instructions
            
        Returns:
            Tuple[bool, List[Dict[str, Any]]]: (is_valid, issues)
        """
        valid = True
        issues = []
        air_on = False
        
        for i, instruction in enumerate(sequence):
            # Check if this is an air control command
            if instruction.code_type == "M" and instruction.code_number == 106:
                if "S" in instruction.parameters:
                    air_on = instruction.parameters["S"] > 0
            
            # Check if this is a paint flow command
            if instruction.code_type == "G" and instruction.code_number == 1:
                if "U" in instruction.parameters or "V" in instruction.parameters:
                    if not air_on:
                        valid = False
                        issues.append({
                            'rule': 'AirBeforePaintRule',
                            'index': i,
                            'instruction': str(instruction),
                            'message': "Paint flow started before air is on"
                        })
        
        return valid, issues


class PaintBeforeAirOffRule(ValidationRule):
    """
    Rule for ensuring paint is off before air is turned off.
    """
    
    def validate(self, sequence: List[GCodeInstruction]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate that paint is off before air is turned off.
        
        Args:
            sequence: List of G-code instructions
            
        Returns:
            Tuple[bool, List[Dict[str, Any]]]: (is_valid, issues)
        """
        valid = True
        issues = []
        paint_flowing = {"U": False, "V": False}
        
        for i, instruction in enumerate(sequence):
            # Check if this is a paint flow start command
            if instruction.code_type == "G" and instruction.code_number == 1:
                if "U" in instruction.parameters:
                    paint_flowing["U"] = True
                if "V" in instruction.parameters:
                    paint_flowing["V"] = True
            
            # Check if this is a paint flow stop command
            if instruction.code_type == "M" and instruction.code_number == 18:
                if "U" in instruction.parameters:
                    paint_flowing["U"] = False
                if "V" in instruction.parameters:
                    paint_flowing["V"] = False
            
            # Check if this is an air off command
            if instruction.code_type == "M" and instruction.code_number == 106:
                if "S" in instruction.parameters and instruction.parameters["S"] == 0:
                    if paint_flowing["U"] or paint_flowing["V"]:
                        valid = False
                        issues.append({
                            'rule': 'PaintBeforeAirOffRule',
                            'index': i,
                            'instruction': str(instruction),
                            'message': "Air turned off while paint is still flowing"
                        })
        
        return valid, issues


class ToolOffsetRule(ValidationRule):
    """
    Rule for ensuring tool offsets are properly applied and removed.
    """
    
    def validate(self, sequence: List[GCodeInstruction]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate that tool offsets are properly applied and removed.
        
        Args:
            sequence: List of G-code instructions
            
        Returns:
            Tuple[bool, List[Dict[str, Any]]]: (is_valid, issues)
        """
        valid = True
        issues = []
        current_tool = None
        offset_applied = False
        bounds_disabled = False
        
        for i, instruction in enumerate(sequence):
            # Check if this is a tool selection command
            if instruction.code_type == "T":
                current_tool = instruction.code_number
                
                # If we switch to T0 and offset is still applied, that's an issue
                if current_tool == 0 and offset_applied:
                    valid = False
                    issues.append({
                        'rule': 'ToolOffsetRule',
                        'index': i,
                        'instruction': str(instruction),
                        'message': "Switched to T0 without removing T1 offset"
                    })
            
            # Check if this is a bounds checking command
            if instruction.code_type == "M" and instruction.code_number == 120:
                bounds_disabled = True
            if instruction.code_type == "M" and instruction.code_number == 121:
                bounds_disabled = False
            
            # Check if this is an offset application/removal
            if instruction.code_type == "G" and instruction.code_number == 1:
                # This is a rough heuristic - a more sophisticated check would be needed
                # for a real implementation
                if "X" in instruction.parameters and "Y" in instruction.parameters:
                    if instruction.parameters["X"] == 100 and instruction.parameters["Y"] == -25:
                        offset_applied = True
                    elif instruction.parameters["X"] == -100 and instruction.parameters["Y"] == 25:
                        offset_applied = False
        
        # Check final state
        if offset_applied:
            valid = False
            issues.append({
                'rule': 'ToolOffsetRule',
                'index': len(sequence) - 1,
                'instruction': str(sequence[-1]) if sequence else "",
                'message': "Tool offset not removed at end of sequence"
            })
        
        if bounds_disabled:
            valid = False
            issues.append({
                'rule': 'ToolOffsetRule',
                'index': len(sequence) - 1,
                'instruction': str(sequence[-1]) if sequence else "",
                'message': "Bounds checking not re-enabled at end of sequence"
            })
        
        return valid, issues


def create_default_validator() -> SequenceValidator:
    """
    Create a validator with default rules.
    
    Returns:
        SequenceValidator: Validator with default rules
    """
    validator = SequenceValidator()
    validator.add_rule(SafeZHeightRule())
    validator.add_rule(AirBeforePaintRule())
    validator.add_rule(PaintBeforeAirOffRule())
    validator.add_rule(ToolOffsetRule())
    return validator 