"""
M122: Diagnose

This command reports diagnostic information about the machine, including VIN,
MCU and driver temperatures, and other controller/driver stats. Output format
is firmware-dependent (RepRapFirmware provides a multi-line textual report).

References:
- See 098_M122__Diagnose.md for details
"""

from typing import Dict, Optional
from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction
from semantic_gcode.gcode.mixins import ExpectsAcknowledgement


@register_gcode_instruction
class M122_Diagnostics(GCodeInstruction, ExpectsAcknowledgement):
    """
    M122: Diagnose

    Parameters:
    - P: Optional parameter to specify a particular device or sub-report (firmware-dependent)

    Behavior:
    - Emits a multi-line diagnostic report. This class treats the command as
      expecting a response and provides a helper to parse key fields.
    """

    code_type = "M"
    code_number = 122

    # RRF supports optional parameters; we include P as a common selector
    valid_parameters = ["P"]

    @classmethod
    def create(cls, p: Optional[int] = None) -> "M122_Diagnostics":
        parameters: Dict[str, object] = {}
        if p is not None:
            parameters["P"] = p
        return cls(
            code_type="M",
            code_number=122,
            parameters=parameters,
            comment="Diagnose"
        )

    def validate_response(self, response: str) -> bool:
        """
        Consider any non-empty textual report as an acknowledgement for M122.
        """
        return bool(response and response.strip())

    def parse_diagnostics(self, response: str) -> Dict[str, object]:
        """
        Best-effort heuristic parsing of common fields from the M122 textual report.
        Returns keys like: vin, mcu_temp_c, driver_temp_c, overtemp_warning.
        """
        vin = None
        mcu_temp = None
        driver_temp = None
        overtemp = False
        for line in response.splitlines():
            ln = line.strip()
            if "VIN:" in ln:
                try:
                    vin = float(ln.split("VIN:")[-1].split()[0])
                except Exception:
                    pass
            if "MCU temperature" in ln or "MCU temp" in ln:
                try:
                    mcu_temp = float(ln.split(":")[-1].split()[0])
                except Exception:
                    pass
            if "driver" in ln and ("temp" in ln or "overtemp" in ln.lower()):
                if "warning" in ln.lower() or "overtemp" in ln.lower():
                    overtemp = True
                try:
                    driver_temp = float(ln.split(":")[-1].split()[0])
                except Exception:
                    pass
        out: Dict[str, object] = {}
        if vin is not None:
            out["vin"] = vin
        if mcu_temp is not None:
            out["mcu_temp_c"] = mcu_temp
        if driver_temp is not None:
            out["driver_temp_c"] = driver_temp
        if overtemp:
            out["overtemp_warning"] = True
        return out


def m122(p: Optional[int] = None) -> M122_Diagnostics:
    """
    Convenience function for M122: Diagnose
    """
    return M122_Diagnostics.create(p=p)


if __name__ == "__main__":
    print("GCode command: M122")
    instr = m122()
    print(str(instr))
