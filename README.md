# MechSuite - Mechanical Engineering Analysis Platform

MechSuite is an interactive engineering design and analysis tool with a **Python** computation core and a modern **HTML5 / CSS / JavaScript** frontend.

---

## 🚀 Quick Start

### 1. Run with Python Launcher (Auto-opens browser):
```powershell
& ".\.venv\Scripts\python.exe" run.py
```
Or with standard python:
```bash
python run.py
```
The server will start at `http://127.0.0.1:5000` and open your default browser automatically.

### 2. Run Tests:
```powershell
& ".\.venv\Scripts\python.exe" -m unittest discover -s tests -p "test_*.py" -v
```

---

## 🛠️ Features & Engineering Modules

### 1. Structural & Beam Mechanics
- **Support Types**: Simply Supported, Cantilever (Fixed-Free).
- **Loading Options**: Multiple concentrated point loads ($P$), uniformly distributed loads (UDL, $w$).
- **Cross-Section Geometries**:
  - Rectangular bar ($b \times h$)
  - Solid circular shaft ($d$)
  - Hollow circular pipe ($D \times t$)
  - Standard I-Beam ($b_f \times h \times t_w \times t_f$)
- **Automated Calculations**:
  - Reaction forces ($R_A, R_B$) and wall moments ($M_A$)
  - Maximum Bending Moment ($M_{max}$) and Maximum Shear Force ($V_{max}$)
  - Extreme fiber bending stress $\sigma = \frac{M \cdot y}{I} = \frac{M}{Z}$
  - Factor of Safety ($FoS = \frac{\sigma_{yield}}{\sigma_{max}}$) with Safe / Marginal / Yield indicators
  - Elastic deflection curve numerical integration with $L/250$ deflection serviceability check
- **Canvas Visualizers**:
  - Technical blueprint beam loading schematic with supports and force arrows
  - Shear Force Diagram (SFD)
  - Bending Moment Diagram (BMD)
  - Elastic deflection profile $y(x)$

### 2. Fluid Mechanics & Pipe Hydraulics
- **Working Fluids**: Water (20°C), Engine Oil (SAE 30), Air (1 atm), Diesel Fuel, or Custom Fluid ($\rho, \mu$).
- **Pipe Roughness**: Commercial Steel, Drawn Copper, PVC/Plastic, Cast Iron, Galvanized Iron.
- **Calculations**:
  - Mean velocity $v$ and Reynolds number $Re = \frac{\rho v D}{\mu}$
  - Flow regime classification (Laminar, Transition, Turbulent)
  - Darcy friction factor $f$ (Hagen-Poiseuille $64/Re$ and Swamee-Jain explicit equation)
  - Major friction loss and minor fitting losses via Darcy-Weisbach equation
  - Total pressure drop ($\text{kPa}$ and $\text{bar}$)
  - Hydraulic power and required pump shaft electrical power ($\text{kW}$)

### 3. Thermodynamics & Power Cycles
- **Carnot Engine**: Maximum theoretical efficiency limit $\eta = 1 - \frac{T_L}{T_H}$, net work, heat rejection, and reverse cycle COPs.
- **Rankine Steam Power Plant**: Superheated steam expansion, isentropic turbine & pump efficiencies, net power output (MW), specific steam consumption, and exhaust steam quality.
- **Heat Exchanger Analysis**: Counter-flow vs. Parallel-flow Log Mean Temperature Difference (LMTD) and heat transfer duty $Q = U \cdot A \cdot \Delta T_{lm}$.

### 4. Engineering Materials Catalog & Section Calculator
- Standard database with Young's Modulus ($E$), Yield Strength ($\sigma_y$), Ultimate Tensile Strength ($\sigma_{uts}$), Density ($\rho$), and Poisson's ratio ($\nu$).
- Live cross-sectional geometric property calculator ($A, I_{xx}, Z_{xx}, y_{max}$).

---

## 📁 Project Structure

```
Python Project/
├── app.py                      # Flask REST API server and static asset routing
├── run.py                      # One-click startup script with browser launch
├── requirements.txt            # Python dependencies
├── engine/                     # Core engineering calculation modules
│   ├── __init__.py
│   ├── materials.py            # Material database & cross-section calculator
│   ├── beam_analyzer.py        # Beam mechanics, SFD, BMD, deflection, FoS
│   ├── fluid_mechanics.py      # Pipe hydraulics, Reynolds, head loss
│   └── thermodynamics.py       # Carnot, Rankine, and Heat Exchanger LMTD
├── frontend/                   # Web user interface
│   ├── Index.html              # Main engineering dashboard
│   ├── css/
│   │   └── style.css           # High-tech engineering dark theme
│   └── javascript/
│       ├── app.js              # UI interaction and REST API controller
│       └── visualizer.js       # HTML5 Canvas plotting and beam schematic renderer
└── tests/                      # Automated test suite (17 unit & integration tests)
    ├── __init__.py
    ├── test_beam.py            # Beam analytical benchmarks
    ├── test_fluids.py          # Fluid hydraulics validation
    ├── test_thermo.py          # Thermodynamic cycle validation
    └── test_api_endpoints.py   # Full REST API & frontend serving tests
```

