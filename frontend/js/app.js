/**
 * MechSuite - Frontend Controller & API Integration
 */

const AppState = {
  activeTab: "beam",
  materials: {},
  pointLoads: [{ position_m: 2.5, magnitude_kn: 15.0 }],
  udlLoads: [{ start_m: 0.0, end_m: 5.0, magnitude_kn_m: 4.0 }]
};

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initMaterials();
  initBeamListeners();
  initFluidsListeners();
  initThermoListeners();
  initSectionPreview();

  // Initial runs with default values
  setTimeout(() => {
    updateSectionPreview();
    solveBeam();
    solveFluids();
    solveCarnot();
    solveRankine();
    solveHeatExchanger();
  }, 300);

  // Resize handler for responsive canvas diagrams
  window.addEventListener("resize", debounce(() => {
    if (AppState.activeTab === "beam" && AppState.lastBeamResult) {
      renderBeamDiagrams(AppState.lastBeamResult);
    }
  }, 250));
});

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// ---------------- Navigation Tabs ----------------
function initTabs() {
  const tabBtns = document.querySelectorAll(".nav-tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const tabId = btn.getAttribute("data-tab");
      const targetPane = document.getElementById(tabId);
      if (targetPane) targetPane.classList.add("active");
      AppState.activeTab = tabId;

      if (tabId === "beam" && AppState.lastBeamResult) {
        setTimeout(() => renderBeamDiagrams(AppState.lastBeamResult), 50);
      }
    });
  });

  // Thermo sub-tabs
  const subTabBtns = document.querySelectorAll(".sub-tab-btn");
  subTabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const parent = btn.closest(".card");
      parent.querySelectorAll(".sub-tab-btn").forEach(b => b.classList.remove("active"));
      parent.querySelectorAll(".sub-tab-content").forEach(c => c.style.display = "none");

      btn.classList.add("active");
      const subTabId = btn.getAttribute("data-subtab");
      const target = document.getElementById(subTabId);
      if (target) target.style.display = "block";
    });
  });
}

// ---------------- Materials Catalog ----------------
async function initMaterials() {
  try {
    const res = await fetch("/api/materials");
    const data = await res.json();
    if (data.success) {
      AppState.materials = data.materials;
      populateMaterialDropdowns();
      populateMaterialsTable();
    }
  } catch (err) {
    console.warn("Could not fetch materials list from backend:", err);
  }
}

function populateMaterialDropdowns() {
  const selects = document.querySelectorAll(".material-select");
  selects.forEach(sel => {
    sel.innerHTML = "";
    Object.keys(AppState.materials).forEach(key => {
      const opt = document.createElement("option");
      opt.value = key;
      opt.textContent = AppState.materials[key].name;
      if (key === "steel_a36") opt.selected = true;
      sel.appendChild(opt);
    });
  });
}

function populateMaterialsTable() {
  const tbody = document.getElementById("materials-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  Object.keys(AppState.materials).forEach(key => {
    const m = AppState.materials[key];
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${m.name}</strong><br><small style="color:var(--text-muted)">${m.category}</small></td>
      <td>${m.elastic_modulus_gpa} GPa</td>
      <td>${m.yield_strength_mpa} MPa</td>
      <td>${m.ultimate_strength_mpa} MPa</td>
      <td>${m.density_kg_m3} kg/m³</td>
      <td>${m.poissons_ratio}</td>
      <td><small>${m.description}</small></td>
    `;
    tbody.appendChild(tr);
  });
}

// ---------------- Cross-Section Geometries ----------------
function initSectionPreview() {
  const secTypeSelect = document.getElementById("sec-type");
  if (secTypeSelect) {
    secTypeSelect.addEventListener("change", () => {
      updateSectionInputsVisibility();
      updateSectionPreview();
    });
  }

  const dimInputs = document.querySelectorAll(".dim-input");
  dimInputs.forEach(input => {
    input.addEventListener("input", () => {
      updateSectionPreview();
    });
  });
}

function updateSectionInputsVisibility() {
  const secType = document.getElementById("sec-type").value;
  document.getElementById("sec-dims-rect").style.display = secType === "rectangular" ? "grid" : "none";
  document.getElementById("sec-dims-circ").style.display = secType === "circular" ? "grid" : "none";
  document.getElementById("sec-dims-pipe").style.display = secType === "pipe" ? "grid" : "none";
  document.getElementById("sec-dims-ibeam").style.display = secType === "i_beam" ? "grid" : "none";
}

async function updateSectionPreview() {
  const secType = document.getElementById("sec-type").value;
  const dims = getSectionDimensions(secType);

  // Draw on mini canvas
  const canvas = document.getElementById("section-canvas");
  if (canvas && window.MechVisualizer) {
    MechVisualizer.drawCrossSection(canvas, secType, dims);
  }

  // Fetch properties from backend
  try {
    const res = await fetch("/api/section/properties", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: secType, ...dims })
    });
    const data = await res.json();
    if (data.success && data.properties) {
      const p = data.properties;
      document.getElementById("prop-area").textContent = `${p.area_mm2.toLocaleString()} mm²`;
      document.getElementById("prop-ixx").textContent = `${p.i_xx_mm4.toExponential(3)} mm⁴`;
      document.getElementById("prop-zxx").textContent = `${p.z_xx_mm3.toLocaleString(undefined, {maximumFractionDigits: 1})} mm³`;
      document.getElementById("prop-ymax").textContent = `${p.y_max_mm.toFixed(1)} mm`;
    }
  } catch (err) {
    console.error("Section properties calculation failed:", err);
  }
}

function getSectionDimensions(secType) {
  if (secType === "rectangular") {
    return {
      width: parseFloat(document.getElementById("rect-b").value) || 50,
      height: parseFloat(document.getElementById("rect-h").value) || 100
    };
  } else if (secType === "circular") {
    return {
      diameter: parseFloat(document.getElementById("circ-d").value) || 60
    };
  } else if (secType === "pipe") {
    return {
      outer_diameter: parseFloat(document.getElementById("pipe-d").value) || 80,
      thickness: parseFloat(document.getElementById("pipe-t").value) || 5
    };
  } else if (secType === "i_beam") {
    return {
      flange_width: parseFloat(document.getElementById("ib-bf").value) || 100,
      total_height: parseFloat(document.getElementById("ib-h").value) || 150,
      web_thickness: parseFloat(document.getElementById("ib-tw").value) || 6,
      flange_thickness: parseFloat(document.getElementById("ib-tf").value) || 10
    };
  }
  return {};
}

// ---------------- Beam Mechanics Module ----------------
function initBeamListeners() {
  document.getElementById("btn-solve-beam").addEventListener("click", solveBeam);
  document.getElementById("btn-add-point-load").addEventListener("click", () => {
    const len = parseFloat(document.getElementById("beam-len").value) || 5.0;
    AppState.pointLoads.push({ position_m: Number((len / 2).toFixed(2)), magnitude_kn: 10.0 });
    renderPointLoadsUI();
  });

  document.getElementById("btn-add-udl").addEventListener("click", () => {
    const len = parseFloat(document.getElementById("beam-len").value) || 5.0;
    AppState.udlLoads.push({ start_m: 0.0, end_m: Number(len.toFixed(2)), magnitude_kn_m: 3.0 });
    renderUdlUI();
  });

  // Presets
  document.querySelectorAll("[data-beam-preset]").forEach(btn => {
    btn.addEventListener("click", () => {
      applyBeamPreset(btn.getAttribute("data-beam-preset"));
    });
  });

  renderPointLoadsUI();
  renderUdlUI();
}

function renderPointLoadsUI() {
  const container = document.getElementById("point-loads-list");
  container.innerHTML = "";

  AppState.pointLoads.forEach((load, idx) => {
    const div = document.createElement("div");
    div.className = "load-item";
    div.innerHTML = `
      <div class="load-item-header">
        <span>Point Load #${idx + 1}</span>
        <button type="button" class="btn-remove" onclick="removePointLoad(${idx})">✕ Remove</button>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Position (x)</label>
          <div class="input-with-unit">
            <input type="number" step="0.1" class="form-input has-unit" value="${load.position_m}" onchange="updatePointLoad(${idx}, 'position_m', this.value)">
            <span class="input-unit">m</span>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Magnitude (P)</label>
          <div class="input-with-unit">
            <input type="number" step="0.5" class="form-input has-unit" value="${load.magnitude_kn}" onchange="updatePointLoad(${idx}, 'magnitude_kn', this.value)">
            <span class="input-unit">kN</span>
          </div>
        </div>
      </div>
    `;
    container.appendChild(div);
  });
}

function renderUdlUI() {
  const container = document.getElementById("udl-loads-list");
  container.innerHTML = "";

  AppState.udlLoads.forEach((udl, idx) => {
    const div = document.createElement("div");
    div.className = "load-item";
    div.innerHTML = `
      <div class="load-item-header">
        <span>Distributed Load (UDL) #${idx + 1}</span>
        <button type="button" class="btn-remove" onclick="removeUdl(${idx})">✕ Remove</button>
      </div>
      <div class="form-row-3">
        <div class="form-group">
          <label class="form-label">Start</label>
          <div class="input-with-unit">
            <input type="number" step="0.1" class="form-input has-unit" value="${udl.start_m}" onchange="updateUdl(${idx}, 'start_m', this.value)">
            <span class="input-unit">m</span>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">End</label>
          <div class="input-with-unit">
            <input type="number" step="0.1" class="form-input has-unit" value="${udl.end_m}" onchange="updateUdl(${idx}, 'end_m', this.value)">
            <span class="input-unit">m</span>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Intensity</label>
          <div class="input-with-unit">
            <input type="number" step="0.5" class="form-input has-unit" value="${udl.magnitude_kn_m}" onchange="updateUdl(${idx}, 'magnitude_kn_m', this.value)">
            <span class="input-unit">kN/m</span>
          </div>
        </div>
      </div>
    `;
    container.appendChild(div);
  });
}

window.removePointLoad = function(idx) {
  AppState.pointLoads.splice(idx, 1);
  renderPointLoadsUI();
};

window.updatePointLoad = function(idx, field, val) {
  AppState.pointLoads[idx][field] = parseFloat(val) || 0;
};

window.removeUdl = function(idx) {
  AppState.udlLoads.splice(idx, 1);
  renderUdlUI();
};

window.updateUdl = function(idx, field, val) {
  AppState.udlLoads[idx][field] = parseFloat(val) || 0;
};

function applyBeamPreset(preset) {
  const beamLen = document.getElementById("beam-len");
  const beamType = document.getElementById("beam-type");

  if (preset === "simply_point") {
    beamType.value = "simply_supported";
    beamLen.value = "6.0";
    AppState.pointLoads = [{ position_m: 3.0, magnitude_kn: 20.0 }];
    AppState.udlLoads = [];
  } else if (preset === "simply_udl") {
    beamType.value = "simply_supported";
    beamLen.value = "5.0";
    AppState.pointLoads = [];
    AppState.udlLoads = [{ start_m: 0.0, end_m: 5.0, magnitude_kn_m: 8.0 }];
  } else if (preset === "cantilever_tip") {
    beamType.value = "cantilever";
    beamLen.value = "3.0";
    AppState.pointLoads = [{ position_m: 3.0, magnitude_kn: 12.0 }];
    AppState.udlLoads = [];
  } else if (preset === "combined") {
    beamType.value = "simply_supported";
    beamLen.value = "8.0";
    AppState.pointLoads = [{ position_m: 4.0, magnitude_kn: 15.0 }];
    AppState.udlLoads = [{ start_m: 0.0, end_m: 8.0, magnitude_kn_m: 5.0 }];
  }

  renderPointLoadsUI();
  renderUdlUI();
  solveBeam();
}

async function solveBeam() {
  const beamType = document.getElementById("beam-type").value;
  const length_m = parseFloat(document.getElementById("beam-len").value) || 5.0;
  const material = document.getElementById("beam-mat").value;
  const secType = document.getElementById("sec-type").value;
  const section = { type: secType, ...getSectionDimensions(secType) };

  const payload = {
    beam_type: beamType,
    length_m: length_m,
    material: material,
    section: section,
    point_loads: AppState.pointLoads,
    udl_loads: AppState.udlLoads
  };

  try {
    const res = await fetch("/api/beam/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (result.success) {
      AppState.lastBeamResult = result;
      displayBeamResults(result);
      renderBeamDiagrams(result);
    } else {
      alert("Beam Analysis Error: " + (result.error || "Unknown error"));
    }
  } catch (err) {
    console.error("Beam solve error:", err);
  }
}

function displayBeamResults(res) {
  const crit = res.critical_values;
  const reactions = res.reactions;

  document.getElementById("kpi-moment").textContent = crit.max_bending_moment_kn_m;
  document.getElementById("kpi-shear").textContent = crit.max_shear_force_kn;
  document.getElementById("kpi-stress").textContent = crit.max_stress_mpa;
  document.getElementById("kpi-deflection").textContent = crit.max_deflection_mm;

  // Factor of Safety Card
  const fosCard = document.getElementById("kpi-fos-card");
  const fosPill = document.getElementById("kpi-fos-pill");
  const fosVal = document.getElementById("kpi-fos");
  fosVal.textContent = crit.factor_of_safety;

  fosPill.textContent = crit.safety_status;
  fosPill.className = "status-pill";
  fosCard.className = "kpi-card";

  if (crit.safety_status === "Safe") {
    fosPill.classList.add("safe");
    fosCard.classList.add("success");
  } else if (crit.safety_status === "Marginal") {
    fosPill.classList.add("warning");
    fosCard.classList.add("warning");
  } else {
    fosPill.classList.add("danger");
    fosCard.classList.add("danger");
  }

  // Reactions text
  const rxnText = res.beam_type === "cantilever"
    ? `Reaction Force RA: ${reactions.ra_kn} kN | Fixed Wall Moment MA: ${reactions.moment_a_kn_m} kN·m`
    : `Left Support RA: ${reactions.ra_kn} kN | Right Support RB: ${reactions.rb_kn} kN`;
  document.getElementById("beam-reactions-info").textContent = rxnText;

  // Deflection limit subtitle
  document.getElementById("deflection-limit-text").textContent = `Allowable (L/250): ${crit.allowable_deflection_mm} mm (${crit.deflection_acceptable ? "Within Limit" : "Excessive"})`;
}

function renderBeamDiagrams(res) {
  if (!window.MechVisualizer) return;

  const schematicCanvas = document.getElementById("canvas-schematic");
  const sfdCanvas = document.getElementById("canvas-sfd");
  const bmdCanvas = document.getElementById("canvas-bmd");
  const deflCanvas = document.getElementById("canvas-deflection");

  // 1. Schematic
  MechVisualizer.drawBeamSchematic(schematicCanvas, res.beam_type, res.length_m, res.point_loads, res.udl_loads);

  // 2. SFD
  MechVisualizer.drawDiagram(sfdCanvas, res.diagrams.x_m, res.diagrams.shear_force_kn, "Shear Force Diagram (SFD)", "kN", "#38bdf8");

  // 3. BMD
  MechVisualizer.drawDiagram(bmdCanvas, res.diagrams.x_m, res.diagrams.bending_moment_kn_m, "Bending Moment Diagram (BMD)", "kN·m", "#a855f7");

  // 4. Deflection
  MechVisualizer.drawDiagram(deflCanvas, res.diagrams.x_m, res.diagrams.deflection_mm, "Deflection Profile y(x)", "mm", "#10b981", true);
}

// ---------------- Fluid Mechanics Module ----------------
function initFluidsListeners() {
  document.getElementById("btn-solve-fluids").addEventListener("click", solveFluids);
  document.getElementById("fluid-select").addEventListener("change", (e) => {
    const customDiv = document.getElementById("custom-fluid-fields");
    customDiv.style.display = e.target.value === "custom" ? "grid" : "none";
  });
}

async function solveFluids() {
  const d_mm = parseFloat(document.getElementById("pipe-dia").value) || 50;
  const l_m = parseFloat(document.getElementById("pipe-len").value) || 100;
  const q_m3_h = parseFloat(document.getElementById("pipe-flow-rate").value) || 18;
  const fluid = document.getElementById("fluid-select").value;
  const pipe_mat = document.getElementById("pipe-mat").value;
  const minor_k = parseFloat(document.getElementById("pipe-k").value) || 2.0;
  const pump_eff = (parseFloat(document.getElementById("pump-eff").value) || 75) / 100.0;

  const payload = {
    diameter_mm: d_mm,
    length_m: l_m,
    flow_rate_m3_h: q_m3_h,
    fluid: fluid,
    pipe_material: pipe_mat,
    minor_loss_k: minor_k,
    pump_efficiency: pump_eff
  };

  if (fluid === "custom") {
    payload.fluid = {
      name: "Custom Fluid",
      density_kg_m3: parseFloat(document.getElementById("cust-density").value) || 1000,
      viscosity_pa_s: parseFloat(document.getElementById("cust-visc").value) || 0.001
    };
  }

  try {
    const res = await fetch("/api/fluids/pipe-flow", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (result.success) {
      displayFluidsResults(result);
    }
  } catch (err) {
    console.error("Fluids calculation error:", err);
  }
}

function displayFluidsResults(res) {
  const flow = res.flow_results;
  const loss = res.head_losses;
  const press = res.pressure_drop;
  const pwr = res.power_requirements;

  document.getElementById("kpi-fluid-velocity").textContent = flow.flow_velocity_m_s;
  document.getElementById("kpi-reynolds").textContent = flow.reynolds_number.toLocaleString();

  const regPill = document.getElementById("kpi-regime-pill");
  regPill.textContent = flow.flow_regime;
  regPill.className = "status-pill";
  if (flow.flow_regime === "Laminar") regPill.classList.add("safe");
  else if (flow.flow_regime === "Transition") regPill.classList.add("warning");
  else regPill.classList.add("safe");

  document.getElementById("kpi-darcy-f").textContent = flow.darcy_friction_factor;
  document.getElementById("kpi-headloss").textContent = loss.total_head_loss_m;
  document.getElementById("headloss-breakdown").textContent = `Friction: ${loss.major_friction_loss_m} m | Fittings: ${loss.minor_fitting_loss_m} m`;

  document.getElementById("kpi-pressuredrop").textContent = press.pressure_drop_kpa;
  document.getElementById("pressuredrop-bar").textContent = `${press.pressure_drop_bar} bar`;

  document.getElementById("kpi-pumppower").textContent = pwr.pump_shaft_power_kw;
  document.getElementById("power-hyd").textContent = `Hydraulic: ${pwr.hydraulic_power_kw} kW (${pwr.pump_efficiency_percent}% eff)`;
}

// ---------------- Thermodynamics Module ----------------
function initThermoListeners() {
  document.getElementById("btn-solve-carnot").addEventListener("click", solveCarnot);
  document.getElementById("btn-solve-rankine").addEventListener("click", solveRankine);
  document.getElementById("btn-solve-hx").addEventListener("click", solveHeatExchanger);
}

async function solveCarnot() {
  const th = parseFloat(document.getElementById("carnot-th").value) || 500;
  const tl = parseFloat(document.getElementById("carnot-tl").value) || 30;
  const qin = parseFloat(document.getElementById("carnot-qin").value) || 1000;

  try {
    const res = await fetch("/api/thermo/carnot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ th_celsius: th, tl_celsius: tl, heat_input_kw: qin })
    });
    const result = await res.json();
    if (result.success) {
      const p = result.performance;
      document.getElementById("carnot-eff").textContent = `${p.carnot_efficiency_percent}%`;
      document.getElementById("carnot-wnet").textContent = `${p.net_power_output_kw} kW`;
      document.getElementById("carnot-qout").textContent = `${p.heat_rejected_kw} kW`;
      document.getElementById("carnot-cop").textContent = `Ref: ${p.cop_refrigerator} | HP: ${p.cop_heat_pump}`;
    }
  } catch (err) {
    console.error("Carnot solve error:", err);
  }
}

async function solveRankine() {
  const p1 = parseFloat(document.getElementById("rankine-p1").value) || 60;
  const t1 = parseFloat(document.getElementById("rankine-t1").value) || 500;
  const p2 = parseFloat(document.getElementById("rankine-p2").value) || 10;
  const mdot = parseFloat(document.getElementById("rankine-mdot").value) || 15;
  const etaT = (parseFloat(document.getElementById("rankine-etat").value) || 88) / 100;
  const etaP = (parseFloat(document.getElementById("rankine-etap").value) || 85) / 100;

  const payload = {
    boiler_pressure_bar: p1,
    turbine_inlet_temp_c: t1,
    condenser_pressure_kpa: p2,
    mass_flow_rate_kg_s: mdot,
    turbine_isentropic_eff: etaT,
    pump_isentropic_eff: etaP
  };

  try {
    const res = await fetch("/api/thermo/rankine", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (result.success) {
      const m = result.performance_metrics;
      const t = result.power_plant_totals;
      document.getElementById("rankine-eff").textContent = `${m.thermal_efficiency_percent}%`;
      document.getElementById("rankine-carnot-eff").textContent = `Carnot Limit: ${m.equivalent_carnot_eff_percent}%`;
      document.getElementById("rankine-pwr").textContent = `${t.net_power_output_mw} MW`;
      document.getElementById("rankine-heat").textContent = `Boiler Q: ${t.boiler_heat_input_mw} MW`;
      document.getElementById("rankine-ssc").textContent = `${m.specific_steam_consumption_kg_kwh} kg/kWh`;
      document.getElementById("rankine-quality").textContent = `Steam Quality x2: ${m.steam_exhaust_quality}`;
    }
  } catch (err) {
    console.error("Rankine solve error:", err);
  }
}

async function solveHeatExchanger() {
  const flow = document.getElementById("hx-flow").value;
  const thin = parseFloat(document.getElementById("hx-thin").value) || 95;
  const thout = parseFloat(document.getElementById("hx-thout").value) || 65;
  const tcin = parseFloat(document.getElementById("hx-tcin").value) || 20;
  const tcout = parseFloat(document.getElementById("hx-tcout").value) || 45;
  const u = parseFloat(document.getElementById("hx-u").value) || 800;
  const area = parseFloat(document.getElementById("hx-area").value) || 12;

  const payload = {
    flow_arrangement: flow,
    t_hot_in: thin,
    t_hot_out: thout,
    t_cold_in: tcin,
    t_cold_out: tcout,
    overall_u_w_m2k: u,
    area_m2: area
  };

  try {
    const res = await fetch("/api/thermo/heat-exchanger", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (result.success) {
      document.getElementById("hx-lmtd").textContent = `${result.lmtd_c} °C`;
      document.getElementById("hx-duty").textContent = `${result.heat_duty_kw} kW`;
      document.getElementById("hx-dts").textContent = `ΔT1: ${result.delta_t1_c} °C | ΔT2: ${result.delta_t2_c} °C`;
    }
  } catch (err) {
    console.error("Heat exchanger error:", err);
  }
}

