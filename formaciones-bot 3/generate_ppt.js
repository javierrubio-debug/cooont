const pptxgen = require("pptxgenjs");
const fs = require("fs");

const [,, dataFile, outputFile] = process.argv;
const evidencias = JSON.parse(fs.readFileSync(dataFile, "utf8"));

const DARK_BG   = "0F172A";
const TEAL      = "0D9488";
const TEAL_L    = "14B8A6";
const PURPLE    = "7C3AED";
const PURPLE_L  = "A78BFA";
const WHITE     = "FFFFFF";
const GRAY      = "94A3B8";
const CARD_BG   = "1E293B";

const COLORS = [TEAL, PURPLE, "B45309", "065F46", "1D4ED8", "9D174D"];

async function build() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.title  = "Informe de Formaciones";

  // ── PORTADA ─────────────────────────────────────────────────────────────────
  const totalPax     = evidencias.reduce((s, e) => s + (parseInt(e.pax) || 0), 0);
  const totalSesiones= evidencias.reduce((s, e) => s + (parseInt(e.sesiones) || 0), 0);
  const totalFotos   = evidencias.filter(e => e.photo_path || e.photo_file_id).length;

  const s1 = pres.addSlide();
  s1.background = { color: DARK_BG };
  s1.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:0.12, h:5.625, fill:{color:TEAL}, line:{color:TEAL} });
  s1.addText("INFORME DE",    { x:0.5, y:1.1, w:9, h:0.9, fontSize:48, bold:true, color:WHITE, fontFace:"Calibri", margin:0 });
  s1.addText("FORMACIONES",   { x:0.5, y:1.9, w:9, h:0.9, fontSize:48, bold:true, color:TEAL_L, fontFace:"Calibri", margin:0 });
  s1.addShape(pres.shapes.RECTANGLE, { x:0.5, y:3.0, w:4.5, h:0.04, fill:{color:TEAL}, line:{color:TEAL} });
  s1.addText(`Evidencias de campo · ${new Date().toLocaleDateString("es-ES", {month:"long", year:"numeric"})}`, {
    x:0.5, y:3.1, w:9, h:0.5, fontSize:16, color:GRAY, fontFace:"Calibri", margin:0
  });

  const stats = [
    { label:"FORMACIONES", value: String(evidencias.length) },
    { label:"PAX FORMADAS", value: totalPax > 0 ? String(totalPax) : "—" },
    { label:"SESIONES",     value: totalSesiones > 0 ? String(totalSesiones) : `${totalFotos} 📸` },
  ];
  stats.forEach((st, i) => {
    const x = 0.5 + i * 3.1;
    s1.addShape(pres.shapes.RECTANGLE, { x, y:4.0, w:2.8, h:1.2, fill:{color:CARD_BG}, line:{color:TEAL, width:1} });
    s1.addText(st.value, { x:x+0.1, y:4.05, w:2.6, h:0.6, fontSize:28, bold:true, color:TEAL_L, fontFace:"Calibri", align:"center", margin:0 });
    s1.addText(st.label,  { x:x+0.1, y:4.65, w:2.6, h:0.4, fontSize:9,  color:GRAY,   fontFace:"Calibri", align:"center", charSpacing:2, margin:0 });
  });

  // ── RESUMEN GENERAL ─────────────────────────────────────────────────────────
  // Agrupar en filas de 2
  for (let idx = 0; idx < evidencias.length; idx += 2) {
    const group = evidencias.slice(idx, idx + 2);
    const sRes = pres.addSlide();
    sRes.background = { color: DARK_BG };
    sRes.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:10, h:0.75, fill:{color:TEAL}, line:{color:TEAL} });
    sRes.addText(`RESUMEN · ${idx+1}–${Math.min(idx+2, evidencias.length)} de ${evidencias.length}`, {
      x:0.4, y:0.1, w:9.2, h:0.55, fontSize:16, bold:true, color:WHITE, fontFace:"Calibri", valign:"middle", margin:0
    });

    group.forEach((e, i) => {
      const color = COLORS[(idx + i) % COLORS.length];
      const colorL = color === TEAL ? TEAL_L : color === PURPLE ? PURPLE_L : WHITE;
      const x = 0.3 + i * 4.9;

      sRes.addShape(pres.shapes.RECTANGLE, {
        x, y:1.0, w:4.5, h:4.2,
        fill:{color:CARD_BG}, line:{color, width:1.5},
        shadow:{type:"outer", color:"000000", blur:10, offset:3, angle:135, opacity:0.3}
      });
      sRes.addShape(pres.shapes.RECTANGLE, { x, y:1.0, w:4.5, h:0.08, fill:{color}, line:{color} });

      const nombre = e.formador || `Evidencia #${idx+i+1}`;
      sRes.addText(nombre.toUpperCase(), { x:x+0.2, y:1.15, w:4.1, h:0.5, fontSize:20, bold:true, color:WHITE, fontFace:"Calibri", margin:0 });

      const details = [
        ["FECHA",    e.fecha    || "—"],
        ["CLIENTE",  e.cliente  || "—"],
        ["PRODUCTO", e.producto || "—"],
        ["PAX",      e.pax ? `${e.pax} pax` : "—"],
        ["SESIONES", e.sesiones || "—"],
      ];
      details.forEach(([label, val], j) => {
        const dy = 1.8 + j * 0.63;
        sRes.addText(label, { x:x+0.2, y:dy,       w:3.8, h:0.25, fontSize:8,  color:GRAY,  fontFace:"Calibri", charSpacing:1.5, bold:true, margin:0 });
        sRes.addText(val,   { x:x+0.2, y:dy+0.25,  w:3.8, h:0.3,  fontSize:12, color:WHITE, fontFace:"Calibri", margin:0 });
      });
    });
  }

  // ── SLIDE POR EVIDENCIA ─────────────────────────────────────────────────────
  for (let idx = 0; idx < evidencias.length; idx++) {
    const e = evidencias[idx];
    const color  = COLORS[idx % COLORS.length];
    const colorL = color === TEAL ? TEAL_L : color === PURPLE ? PURPLE_L : WHITE;

    const sE = pres.addSlide();
    sE.background = { color: DARK_BG };

    // Header bar
    sE.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:10, h:0.75, fill:{color}, line:{color} });
    const headerText = [e.formador, e.cliente].filter(Boolean).join(" · ").toUpperCase() || `EVIDENCIA #${idx+1}`;
    sE.addText(headerText, { x:0.4, y:0.1, w:7, h:0.55, fontSize:15, bold:true, color:WHITE, fontFace:"Calibri", valign:"middle", margin:0 });
    if (e.fecha) sE.addText(e.fecha, { x:7.5, y:0.1, w:2.1, h:0.55, fontSize:13, color:WHITE, fontFace:"Calibri", valign:"middle", align:"right", margin:0 });

    // Foto o placeholder
    const hasPhoto = e.photo_path && fs.existsSync(e.photo_path);
    if (hasPhoto) {
      sE.addImage({ path: e.photo_path, x:0.3, y:0.9, w:5.8, h:4.4, sizing:{type:"cover", w:5.8, h:4.4} });
    } else {
      sE.addShape(pres.shapes.RECTANGLE, { x:0.3, y:0.9, w:5.8, h:4.4, fill:{color:CARD_BG}, line:{color, width:1} });
      sE.addText("Sin foto", { x:0.3, y:2.8, w:5.8, h:0.6, fontSize:16, color:GRAY, align:"center", fontFace:"Calibri", margin:0 });
    }

    // Info panel
    sE.addShape(pres.shapes.RECTANGLE, { x:6.3, y:0.9, w:3.4, h:4.4, fill:{color:CARD_BG}, line:{color, width:1} });
    sE.addText("DETALLES", { x:6.5, y:1.0, w:3.0, h:0.35, fontSize:9, color:colorL, fontFace:"Calibri", charSpacing:2.5, bold:true, margin:0 });

    const fields = [
      ["FECHA",    e.fecha    || "—"],
      ["FORMADOR", e.formador || "—"],
      ["CLIENTE",  e.cliente  || "—"],
      ["PRODUCTO", e.producto || "—"],
      ["PAX",      e.pax      ? `${e.pax} pax` : "—"],
      ["SESIONES", e.sesiones || "—"],
    ];
    fields.forEach(([label, val], j) => {
      if (j > 4) return;
      const dy = 1.5 + j * 0.63;
      sE.addText(label, { x:6.5, y:dy,      w:3.0, h:0.25, fontSize:8,  color:GRAY,  fontFace:"Calibri", charSpacing:1.5, bold:true, margin:0 });
      sE.addText(val,   { x:6.5, y:dy+0.25, w:3.0, h:0.3,  fontSize:12, color:WHITE, fontFace:"Calibri", bold:true, margin:0 });
    });

    // Texto original al pie si existe
    if (e.texto_original) {
      const snippet = e.texto_original.slice(0, 100);
      sE.addText(snippet, { x:0.3, y:5.3, w:5.8, h:0.3, fontSize:8, color:GRAY, fontFace:"Calibri", margin:0 });
    }
  }

  await pres.writeFile({ fileName: outputFile });
  console.log("OK");
}

build().catch(err => { console.error(err); process.exit(1); });
