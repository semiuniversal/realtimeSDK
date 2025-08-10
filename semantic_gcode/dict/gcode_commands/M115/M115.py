"""
M115: Get Firmware Version and Capabilities

Reports firmware information such as firmware name, version, and electronics.
Output is typically a single line in RepRapFirmware but may vary across firmware.
"""

from typing import Dict
from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction
from semantic_gcode.gcode.mixins import ExpectsAcknowledgement


@register_gcode_instruction
class M115_GetFirmwareInfo(GCodeInstruction, ExpectsAcknowledgement):
    """
    M115: Get Firmware Version and Capabilities

    Behavior:
    - Expects a response including fields like FIRMWARE_NAME, FIRMWARE_VERSION,
      and ELECTRONICS. Provides a helper to parse these fields.
    """

    code_type = "M"
    code_number = 115

    valid_parameters: list[str] = []

    @classmethod
    def create(cls) -> "M115_GetFirmwareInfo":
        return cls(code_type="M", code_number=115, parameters={}, comment="Get firmware info")

    def validate_response(self, response: str) -> bool:
        return bool(response and response.strip())

    def parse_info(self, response: str) -> Dict[str, str]:
        """
        Parse common key=value pairs from the response line(s).
        Returns keys like: firmware_name, firmware_version, electronics.
        """
        info: Dict[str, str] = {}
        # Flatten newlines
        text = " ".join(line.strip() for line in response.splitlines() if line.strip())
        parts = text.split()
        # Look for tokens like KEY: or KEY:
        pairs: Dict[str, str] = {}
        # RRF often uses tokens like FIRMWARE_NAME:, FIRMWARE_VERSION:
        for token in parts:
            if ":" in token:
                k, v = token.split(":", 1)
                pairs[k.strip().upper()] = v.strip()
        # Map into structured fields
        if "FIRMWARE_NAME" in pairs:
            info["firmware_name"] = pairs["FIRMWARE_NAME"]
        if "FIRMWARE_VERSION" in pairs:
            info["firmware_version"] = pairs["FIRMWARE_VERSION"]
        if "ELECTRONICS" in pairs:
            info["electronics"] = pairs["ELECTRONICS"]
        return info


def m115() -> M115_GetFirmwareInfo:
    """Convenience function for M115."""
    return M115_GetFirmwareInfo.create()

if __name__ == "__main__":
    print("GCode command: M115")
    
    # Get firmware info for main board
    instruction = m115()
    print(str(instruction))
    
    # Get firmware info for board at CAN address 1
    instruction = m115(board_number=1)
    print(str(instruction))
    
    # Test firmware type detection
    duet_response = "FIRMWARE_NAME: RepRapFirmware for Duet 2 WiFi/Ethernet FIRMWARE_VERSION: 3.4.0"
    marlin_response = "FIRMWARE_NAME:Marlin V1 FIRMWARE_VERSION:1.0.0"
    smoothie_response = "Build version: Smoothieware version 1.0.0"
    
    instruction = m115()
    print(f"Duet detected: {instruction.is_duet_firmware(duet_response)}")
    print(f"Marlin detected: {instruction.is_marlin_firmware(marlin_response)}")
    print(f"Smoothieware detected: {instruction.is_smoothieware(smoothie_response)}")
    
    print(f"Firmware type (Duet): {instruction.get_firmware_type(duet_response)}")
    print(f"Firmware type (Marlin): {instruction.get_firmware_type(marlin_response)}")
    print(f"Firmware type (Smoothieware): {instruction.get_firmware_type(smoothie_response)}")
    
    # Help information
    print("\nHelp information:")
    print(instruction.get_help())
