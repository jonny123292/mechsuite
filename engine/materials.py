"""
Mechanical Engineering Materials & Section Properties Database
Provides standard engineering materials, physical/mechanical properties,
and cross-section geometric properties calculation.
"""

from typing import Dict, Any, Optional
import math

MATERIALS: Dict[str, Dict[str, Any]] = {
    "steel_a36": {
        "name": "Structural Steel (ASTM A36)",
        "category": "Ferrous Metals",
        "elastic_modulus_gpa": 200.0,
        "yield_strength_mpa": 250.0,
        "ultimate_strength_mpa": 400.0,
        "density_kg_m3": 7850.0,
        "poissons_ratio": 0.26,
        "thermal_conductivity_w_mk": 50.0,
        "description": "Standard low-carbon structural steel widely used in building and bridge construction."
    },
    "stainless_304": {
        "name": "Stainless Steel (AISI 304)",
        "category": "Stainless Steels",
        "elastic_modulus_gpa": 193.0,
        "yield_strength_mpa": 215.0,
        "ultimate_strength_mpa": 505.0,
        "density_kg_m3": 8000.0,
        "poissons_ratio": 0.29,
        "thermal_conductivity_w_mk": 16.2,
        "description": "Austenitic stainless steel with excellent corrosion resistance and formability."
    },
    "aluminum_6061_t6": {
        "name": "Aluminum Alloy (6061-T6)",
        "category": "Non-Ferrous Alloys",
        "elastic_modulus_gpa": 68.9,
        "yield_strength_mpa": 276.0,
        "ultimate_strength_mpa": 310.0,
        "density_kg_m3": 2700.0,
        "poissons_ratio": 0.33,
        "thermal_conductivity_w_mk": 167.0,
        "description": "Precipitation-hardened aluminum alloy used extensively in aerospace and structural frames."
    },
    "titanium_grade_5": {
        "name": "Titanium (Ti-6Al-4V Grade 5)",
        "category": "High-Performance Alloys",
        "elastic_modulus_gpa": 113.8,
        "yield_strength_mpa": 880.0,
        "ultimate_strength_mpa": 950.0,
        "density_kg_m3": 4430.0,
        "poissons_ratio": 0.34,
        "thermal_conductivity_w_mk": 6.7,
        "description": "High strength-to-weight ratio aerospace-grade titanium alloy with high fracture toughness."
    },
    "brass_c36000": {
        "name": "Free-Cutting Brass (C36000)",
        "category": "Copper Alloys",
        "elastic_modulus_gpa": 97.0,
        "yield_strength_mpa": 310.0,
        "ultimate_strength_mpa": 470.0,
        "density_kg_m3": 8500.0,
        "poissons_ratio": 0.31,
        "thermal_conductivity_w_mk": 115.0,
        "description": "Standard machining brass with outstanding machinability and good corrosion resistance."
    },
    "cast_iron_gray": {
        "name": "Gray Cast Iron (ASTM Class 30)",
        "category": "Cast Irons",
        "elastic_modulus_gpa": 100.0,
        "yield_strength_mpa": 130.0,
        "ultimate_strength_mpa": 214.0,
        "density_kg_m3": 7200.0,
        "poissons_ratio": 0.26,
        "thermal_conductivity_w_mk": 46.0,
        "description": "High damping capacity and wear resistance; commonly used for engine blocks and machine beds."
    }
}


def get_material(key: str) -> Optional[Dict[str, Any]]:
    """Retrieve material properties by key, or return None if not found."""
    return MATERIALS.get(key)


def calculate_section_properties(section_type: str, dims: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate cross-sectional area A (mm^2), moment of inertia I (mm^4),
    section modulus Z (mm^3), and y_max (mm).
    
    Supported section types:
    - 'rectangular': dims {'width': b, 'height': h}
    - 'circular': dims {'diameter': d}
    - 'pipe': dims {'outer_diameter': D, 'thickness': t}
    - 'i_beam': dims {'flange_width': bf, 'total_height': h, 'web_thickness': tw, 'flange_thickness': tf}
    """
    section = section_type.lower()
    
    if section == "rectangular":
        b = float(dims.get("width", 50.0))  # mm
        h = float(dims.get("height", 100.0))  # mm
        area = b * h
        i_xx = (b * (h ** 3)) / 12.0
        y_max = h / 2.0
        z_xx = i_xx / y_max
        return {
            "type": "rectangular",
            "width_mm": b,
            "height_mm": h,
            "area_mm2": area,
            "i_xx_mm4": i_xx,
            "z_xx_mm3": z_xx,
            "y_max_mm": y_max
        }

    elif section == "circular":
        d = float(dims.get("diameter", 60.0))  # mm
        r = d / 2.0
        area = math.pi * (r ** 2)
        i_xx = (math.pi * (d ** 4)) / 64.0
        y_max = r
        z_xx = (math.pi * (d ** 3)) / 32.0
        return {
            "type": "circular",
            "diameter_mm": d,
            "area_mm2": area,
            "i_xx_mm4": i_xx,
            "z_xx_mm3": z_xx,
            "y_max_mm": y_max
        }

    elif section == "pipe":
        d_outer = float(dims.get("outer_diameter", 80.0))  # mm
        t = float(dims.get("thickness", 5.0))  # mm
        d_inner = max(0.1, d_outer - 2 * t)
        area = (math.pi / 4.0) * (d_outer ** 2 - d_inner ** 2)
        i_xx = (math.pi / 64.0) * (d_outer ** 4 - d_inner ** 4)
        y_max = d_outer / 2.0
        z_xx = i_xx / y_max
        return {
            "type": "pipe",
            "outer_diameter_mm": d_outer,
            "inner_diameter_mm": d_inner,
            "thickness_mm": t,
            "area_mm2": area,
            "i_xx_mm4": i_xx,
            "z_xx_mm3": z_xx,
            "y_max_mm": y_max
        }

    elif section == "i_beam":
        bf = float(dims.get("flange_width", 100.0))  # mm
        h = float(dims.get("total_height", 150.0))  # mm
        tw = float(dims.get("web_thickness", 6.0))  # mm
        tf = float(dims.get("flange_thickness", 10.0))  # mm
        
        # Overall bounding box minus two cutout rectangles beside the web
        # Cutout height = h - 2*tf, cutout width = (bf - tw) / 2 on each side
        hw = max(0.1, h - 2 * tf)
        area = (2 * bf * tf) + (hw * tw)
        # I_xx = (bf * h^3 / 12) - ((bf - tw) * hw^3 / 12)
        i_xx = (bf * (h ** 3) / 12.0) - ((bf - tw) * (hw ** 3) / 12.0)
        y_max = h / 2.0
        z_xx = i_xx / y_max
        return {
            "type": "i_beam",
            "flange_width_mm": bf,
            "total_height_mm": h,
            "web_thickness_mm": tw,
            "flange_thickness_mm": tf,
            "area_mm2": area,
            "i_xx_mm4": i_xx,
            "z_xx_mm3": z_xx,
            "y_max_mm": y_max
        }

    else:
        raise ValueError(f"Unsupported section type: {section_type}")

