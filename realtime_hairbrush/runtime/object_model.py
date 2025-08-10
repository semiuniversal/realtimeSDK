from __future__ import annotations

from typing import Any, Dict, Optional


def parse_object_model(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Best-effort parser for RepRapFirmware object model (as returned by M408 S2).
    Extracts:
      - modal.movement_mode: 'absolute' or 'relative'
      - modal.workspace: e.g., 'G54' if present
      - coords.work_position, coords.machine_position: lists [x,y,z,...] if present
    The schema varies across RRF versions; all fields are optional.
    """
    out: Dict[str, Any] = {}

    # Movement mode (absolute/relative)
    movement_mode: Optional[str] = None
    try:
        # RRF often exposes position in 'coords' or 'move' sections; mode might be in 'gcodes' or 'move'
        # Heuristics: Look for a flag like 'relative' or a modal code list
        # If 'gcodes' present and contains last modal; else check 'move' for 'axesRelative'
        # axesRelative can be a list of bools per axis; if any True, we treat as relative for display
        move = data.get('move') or {}
        axes_rel = move.get('axesRelative')
        if isinstance(axes_rel, list) and any(bool(x) for x in axes_rel):
            movement_mode = 'relative'
        # Some models may include a direct 'relative' flag
        if movement_mode is None:
            rel_flag = move.get('relative')
            if isinstance(rel_flag, bool):
                movement_mode = 'relative' if rel_flag else 'absolute'
        # As fallback, if nothing found, default to absolute
        if movement_mode is None:
            movement_mode = 'absolute'
    except Exception:
        movement_mode = None

    if movement_mode:
        out.setdefault('modal', {})['movement_mode'] = movement_mode

    # Active workspace (G54..G59) if available
    try:
        # Heuristic: often in 'move' as 'workspaceNumber' (0-based) or 'workspace' code
        move = data.get('move') or {}
        ws_num = move.get('workspaceNumber')
        ws_code = None
        if isinstance(ws_num, int):
            ws_code = f"G5{4 + ws_num}"
        else:
            ws_str = move.get('workspace')
            if isinstance(ws_str, str):
                ws_code = ws_str
        if ws_code:
            out.setdefault('modal', {})['workspace'] = ws_code
    except Exception:
        pass

    # Coordinates: work/machine positions
    try:
        coords = data.get('coords') or data.get('move') or {}
        # 'coords' may provide 'xyz' or 'work' vs 'machine'
        work_pos = coords.get('xyz') or coords.get('work') or coords.get('workPosition')
        mach_pos = coords.get('machine') or coords.get('machinePosition') or data.get('pos')
        if isinstance(work_pos, list):
            out.setdefault('coords', {})['work_position'] = work_pos
        if isinstance(mach_pos, list):
            out.setdefault('coords', {})['machine_position'] = mach_pos
    except Exception:
        pass

    return out 