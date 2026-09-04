/**
 * MechSuite Visualizer - HTML5 Canvas Engine for Mechanical Engineering Diagrams
 * Handles rendering of:
 * - Beam Loading Schematics (supports, dimensions, point loads, UDL)
 * - Shear Force Diagrams (SFD)
 * - Bending Moment Diagrams (BMD)
 * - Beam Elastic Deflection Curves
 * - Cross-Section Geometries
 */

const MechVisualizer = {
  // Set up canvas with high-DPI scaling
  initCanvas(canvas) {
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const width = rect.width || canvas.parentElement.clientWidth || 600;
    const height = rect.height || 180;

    canvas.width = width * dpr;
    canvas.height = height * dpr;

    const ctx = canvas.getContext("2d");
    ctx.scale(dpr, dpr);
    return { ctx, width, height };
  },

  // Draw engineering blueprint grid
  drawGrid(ctx, width, height) {
    ctx.fillStyle = "#0d131f";
    ctx.fillRect(0, 0, width, height);

    ctx.strokeStyle = "rgba(36, 50, 71, 0.4)";
    ctx.lineWidth = 1;
    const gridSize = 20;

    ctx.beginPath();
    for (let x = 0; x < width; x += gridSize) {
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
    }
    for (let y = 0; y < height; y += gridSize) {
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
    }
    ctx.stroke();
  },

  // 1. Draw Beam Loading Schematic
  drawBeamSchematic(canvas, beamType, length, pointLoads = [], udlLoads = []) {
    const setup = this.initCanvas(canvas);
    if (!setup) return;
    const { ctx, width, height } = setup;

    this.drawGrid(ctx, width, height);

    const padX = 60;
    const padY = 50;
    const beamY = height / 2 + 10;
    const beamWidth = width - 2 * padX;
    const scaleX = beamWidth / length;

    // Draw Fixed Support or Pin/Roller Supports
    if (beamType === "cantilever") {
      // Fixed Wall at Left End
      ctx.fillStyle = "#334155";
      ctx.fillRect(padX - 12, beamY - 35, 12, 70);
      ctx.strokeStyle = "#64748b";
      ctx.lineWidth = 1.5;
      ctx.strokeRect(padX - 12, beamY - 35, 12, 70);

      // Hatching on wall
      ctx.beginPath();
      for (let y = beamY - 30; y < beamY + 35; y += 8) {
        ctx.moveTo(padX - 12, y);
        ctx.lineTo(padX - 2, y + 8);
      }
      ctx.stroke();
    } else {
      // Simply Supported: Pin at Left, Roller at Right
      // Pin (Triangle) at Left
      ctx.fillStyle = "#475569";
      ctx.beginPath();
      ctx.moveTo(padX, beamY + 8);
      ctx.lineTo(padX - 12, beamY + 28);
      ctx.lineTo(padX + 12, beamY + 28);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = "#94a3b8";
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Pin base hatch
      ctx.strokeStyle = "#64748b";
      ctx.beginPath();
      ctx.moveTo(padX - 16, beamY + 28);
      ctx.lineTo(padX + 16, beamY + 28);
      ctx.stroke();

      // Roller (Circle + Base) at Right
      const rightX = padX + beamWidth;
      ctx.fillStyle = "#475569";
      ctx.beginPath();
      ctx.arc(rightX, beamY + 18, 10, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = "#94a3b8";
      ctx.lineWidth = 1.5;
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(rightX - 16, beamY + 28);
      ctx.lineTo(rightX + 16, beamY + 28);
      ctx.stroke();
    }

    // Draw Beam Member
    ctx.fillStyle = "#1e293b";
    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 3;
    ctx.fillRect(padX, beamY - 8, beamWidth, 16);
    ctx.strokeRect(padX, beamY - 8, beamWidth, 16);

    // Draw UDL Loads
    udlLoads.forEach(udl => {
      const uStartX = padX + udl.start_m * scaleX;
      const uEndX = padX + udl.end_m * scaleX;
      const uWidth = Math.max(2, uEndX - uStartX);
      const uHeight = 24;
      const uTop = beamY - 8 - uHeight;

      // Hatched / shaded box
      ctx.fillStyle = "rgba(245, 158, 11, 0.2)";
      ctx.strokeStyle = "#f59e0b";
      ctx.lineWidth = 1.5;
      ctx.fillRect(uStartX, uTop, uWidth, uHeight);
      ctx.strokeRect(uStartX, uTop, uWidth, uHeight);

      // Small downward arrows inside UDL
      const arrowStep = Math.max(15, uWidth / 5);
      for (let ax = uStartX + 6; ax <= uEndX - 4; ax += arrowStep) {
        this.drawArrow(ctx, ax, uTop, ax, beamY - 8, "#f59e0b", 4);
      }

      // UDL Text
      ctx.fillStyle = "#fbbf24";
      ctx.font = "bold 10px monospace";
      ctx.textAlign = "center";
      ctx.fillText(`${udl.magnitude_kn_m} kN/m`, uStartX + uWidth / 2, uTop - 5);
    });

    // Draw Point Loads
    pointLoads.forEach(p => {
      const px = padX + p.position_m * scaleX;
      const arrowLen = 35;
      const startY = beamY - 8 - arrowLen;
      const endY = beamY - 8;

      this.drawArrow(ctx, px, startY, px, endY, "#ef4444", 7);

      // Value label
      ctx.fillStyle = "#f87171";
      ctx.font = "bold 11px monospace";
      ctx.textAlign = "center";
      ctx.fillText(`${p.magnitude_kn} kN`, px, startY - 5);
    });

    // Dimension Line at Bottom
    const dimY = height - 14;
    ctx.strokeStyle = "#64748b";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padX, dimY);
    ctx.lineTo(padX + beamWidth, dimY);
    // ticks
    ctx.moveTo(padX, dimY - 4);
    ctx.lineTo(padX, dimY + 4);
    ctx.moveTo(padX + beamWidth, dimY - 4);
    ctx.lineTo(padX + beamWidth, dimY + 4);
    ctx.stroke();

    ctx.fillStyle = "#94a3b8";
    ctx.font = "11px monospace";
    ctx.textAlign = "center";
    ctx.fillText(`L = ${length} m`, padX + beamWidth / 2, dimY - 4);
  },

  // Helper: Draw Arrow
  drawArrow(ctx, fromX, fromY, toX, toY, color, headLen = 6) {
    const angle = Math.atan2(toY - fromY, toX - fromX);
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = 2;

    ctx.beginPath();
    ctx.moveTo(fromX, fromY);
    ctx.lineTo(toX, toY);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(toX, toY);
    ctx.lineTo(toX - headLen * Math.cos(angle - Math.PI / 6), toY - headLen * Math.sin(angle - Math.PI / 6));
    ctx.lineTo(toX - headLen * Math.cos(angle + Math.PI / 6), toY - headLen * Math.sin(angle + Math.PI / 6));
    ctx.closePath();
    ctx.fill();
  },

  // 2. Draw SFD / BMD / Deflection Diagram
  drawDiagram(canvas, xPts, yPts, title, unit, primaryColor = "#38bdf8", invertY = false) {
    const setup = this.initCanvas(canvas);
    if (!setup) return;
    const { ctx, width, height } = setup;

    this.drawGrid(ctx, width, height);

    if (!xPts || xPts.length === 0 || !yPts || yPts.length === 0) return;

    const padL = 60;
    const padR = 25;
    const padT = 25;
    const padB = 30;
    const plotW = width - padL - padR;
    const plotH = height - padT - padB;

    const xMin = xPts[0];
    const xMax = xPts[xPts.length - 1];

    let yMin = Math.min(...yPts);
    let yMax = Math.max(...yPts);

    // Symmetric zero axis or safe bounds
    if (Math.abs(yMax - yMin) < 1e-5) {
      yMax = yMax === 0 ? 1 : yMax * 1.2;
      yMin = yMin === 0 ? -1 : yMin * 1.2;
    }

    // Pad range so zero line is clear
    const yAbsMax = Math.max(Math.abs(yMin), Math.abs(yMax)) * 1.15;
    const rangeMin = -yAbsMax;
    const rangeMax = yAbsMax;

    const mapX = x => padL + ((x - xMin) / (xMax - xMin)) * plotW;
    const mapY = y => {
      const normalized = (y - rangeMin) / (rangeMax - rangeMin);
      return invertY ? padT + normalized * plotH : padT + (1 - normalized) * plotH;
    };

    const zeroY = mapY(0);

    // Draw Zero Axis
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(padL, zeroY);
    ctx.lineTo(padL + plotW, zeroY);
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw Area Fill
    ctx.beginPath();
    ctx.moveTo(mapX(xPts[0]), zeroY);
    for (let i = 0; i < xPts.length; i++) {
      ctx.lineTo(mapX(xPts[i]), mapY(yPts[i]));
    }
    ctx.lineTo(mapX(xPts[xPts.length - 1]), zeroY);
    ctx.closePath();

    const gradient = ctx.createLinearGradient(0, padT, 0, height - padB);
    gradient.addColorStop(0, primaryColor + "44");
    gradient.addColorStop(0.5, primaryColor + "11");
    gradient.addColorStop(1, primaryColor + "44");
    ctx.fillStyle = gradient;
    ctx.fill();

    // Draw Curve
    ctx.beginPath();
    ctx.moveTo(mapX(xPts[0]), mapY(yPts[0]));
    for (let i = 1; i < xPts.length; i++) {
      ctx.lineTo(mapX(xPts[i]), mapY(yPts[i]));
    }
    ctx.strokeStyle = primaryColor;
    ctx.lineWidth = 2.5;
    ctx.stroke();

    // Extreme Value Markers
    const maxVal = Math.max(...yPts);
    const minVal = Math.min(...yPts);
    const maxIdx = yPts.indexOf(maxVal);
    const minIdx = yPts.indexOf(minVal);

    ctx.font = "bold 10px monospace";
    ctx.fillStyle = "#f1f5f9";

    // Mark peak
    if (Math.abs(maxVal) > 1e-4) {
      const px = mapX(xPts[maxIdx]);
      const py = mapY(maxVal);
      ctx.beginPath();
      ctx.arc(px, py, 4, 0, Math.PI * 2);
      ctx.fillStyle = primaryColor;
      ctx.fill();
      ctx.fillStyle = "#fff";
      ctx.textAlign = "center";
      ctx.fillText(`${maxVal.toFixed(2)} ${unit}`, px, py - 7);
    }

    // Mark trough if significantly different
    if (Math.abs(minVal) > 1e-4 && minIdx !== maxIdx) {
      const px = mapX(xPts[minIdx]);
      const py = mapY(minVal);
      ctx.beginPath();
      ctx.arc(px, py, 4, 0, Math.PI * 2);
      ctx.fillStyle = "#ef4444";
      ctx.fill();
      ctx.fillStyle = "#fff";
      ctx.textAlign = "center";
      ctx.fillText(`${minVal.toFixed(2)} ${unit}`, px, py + 14);
    }

    // Y Axis Labels
    ctx.fillStyle = "#94a3b8";
    ctx.font = "10px monospace";
    ctx.textAlign = "right";
    ctx.fillText(`${rangeMax.toFixed(1)} ${unit}`, padL - 8, padT + 6);
    ctx.fillText("0.0", padL - 8, zeroY + 3);
    ctx.fillText(`${rangeMin.toFixed(1)} ${unit}`, padL - 8, height - padB);

    // X Axis Labels
    ctx.textAlign = "center";
    ctx.fillText("0 m", padL, height - 10);
    ctx.fillText(`${xMax.toFixed(1)} m`, padL + plotW, height - 10);

    // Title Badge
    ctx.fillStyle = "#38bdf8";
    ctx.font = "bold 11px sans-serif";
    ctx.textAlign = "left";
    ctx.fillText(title, padL, 16);
  },

  // 3. Draw Cross Section Geometry
  drawCrossSection(canvas, sectionType, dims) {
    const setup = this.initCanvas(canvas);
    if (!setup) return;
    const { ctx, width, height } = setup;

    ctx.fillStyle = "#0d131f";
    ctx.fillRect(0, 0, width, height);

    const cx = width / 2;
    const cy = height / 2;
    const maxDim = Math.min(width, height) * 0.72;

    ctx.strokeStyle = "#38bdf8";
    ctx.fillStyle = "rgba(56, 189, 248, 0.25)";
    ctx.lineWidth = 2;

    if (sectionType === "rectangular") {
      const b = dims.width || 50;
      const h = dims.height || 100;
      const aspect = b / h;
      let drawH = maxDim;
      let drawW = drawH * aspect;
      if (drawW > maxDim) {
        drawW = maxDim;
        drawH = drawW / aspect;
      }
      ctx.fillRect(cx - drawW / 2, cy - drawH / 2, drawW, drawH);
      ctx.strokeRect(cx - drawW / 2, cy - drawH / 2, drawW, drawH);
    } else if (sectionType === "circular") {
      const r = maxDim / 2;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    } else if (sectionType === "pipe") {
      const rOuter = maxDim / 2;
      const t = dims.thickness || 5;
      const d = dims.outer_diameter || 80;
      const rInner = Math.max(5, rOuter * (1 - (2 * t) / d));

      ctx.beginPath();
      ctx.arc(cx, cy, rOuter, 0, Math.PI * 2, false);
      ctx.arc(cx, cy, rInner, 0, Math.PI * 2, true);
      ctx.fill();
      ctx.stroke();
    } else if (sectionType === "i_beam") {
      const bf = maxDim * 0.75;
      const h = maxDim;
      const tf = maxDim * 0.15;
      const tw = maxDim * 0.12;

      ctx.beginPath();
      // Top flange
      ctx.rect(cx - bf / 2, cy - h / 2, bf, tf);
      // Web
      ctx.rect(cx - tw / 2, cy - h / 2 + tf, tw, h - 2 * tf);
      // Bottom flange
      ctx.rect(cx - bf / 2, cy + h / 2 - tf, bf, tf);
      ctx.fill();
      ctx.stroke();
    }

    // Draw Neutral Axis (N.A.) line
    ctx.strokeStyle = "#f59e0b";
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 3]);
    ctx.beginPath();
    ctx.moveTo(10, cy);
    ctx.lineTo(width - 10, cy);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = "#f59e0b";
    ctx.font = "9px monospace";
    ctx.textAlign = "left";
    ctx.fillText("N.A.", 10, cy - 4);
  }
};

window.MechVisualizer = MechVisualizer;

