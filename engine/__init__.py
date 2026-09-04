"""
MechSuite: Mechanical Engineering Core Engine
Modules:
- materials: Standard materials and cross-section property calculations
- beam_analyzer: Shear force, bending moment, stress, and deflection analysis
- fluid_mechanics: Pipe flow, friction factor, Reynolds number, head loss
- thermodynamics: Carnot, Rankine cycles, and heat exchanger LMTD analysis
"""

from .materials import MATERIALS, get_material, calculate_section_properties
from .beam_analyzer import analyze_beam
from .fluid_mechanics import analyze_pipe_flow
from .thermodynamics import analyze_carnot_cycle, analyze_rankine_cycle, analyze_heat_exchanger

__all__ = [
    "MATERIALS",
    "get_material",
    "calculate_section_properties",
    "analyze_beam",
    "analyze_pipe_flow",
    "analyze_carnot_cycle",
    "analyze_rankine_cycle",
    "analyze_heat_exchanger",
]

