// Measure rendered text in the browser for render_check.py (TASK 108, R7.5, R7.6, R7.8).
//
// Usage: node measure_text.mjs <puppeteer.json> <figure.svg> [--png <out.png>] [--scale <n>]
//                              [--background <css colour>]
// Loads the SVG in the pinned chrome-headless-shell through the puppeteer bundled with the
// mermaid-cli install (the directory that holds <puppeteer.json>), and prints JSON on stdout:
//   {"labels": [{"text", "kind", "id", "owner", "el", "n", "cls", "bbox": [x, y, w, h],
//                "box": [x, y, w, h] | null, "clipped_px": n, "outside_px": n, "font_px": n,
//                "fg": "#rrggbb" | null, "bg": "#rrggbb" | null, "under": [layer, ...],
//                "blend": mode (only when not normal), "uncertain": true (only when set),
//                "rotated": true (only when set), "font": family | null}],
//    "titles": [{"text", "id", "bbox": [...], "box": [...]}], "font_px": n,
//    "kind": aria-roledescription, "browser": version, "png": path | null,
//    "page": "#rrggbb", "fonts": [{"family", "glyphs"}], "font_family": family | null}
//
// Geometry. `bbox` is where the glyphs end; `box` the space mermaid reserved for them: the
// foreignObject of an HTML label, the rectangle of a note, an actor or a gantt bar.
// svg_geometry.py uses `bbox` for title crossings and `bbox` beyond `box` (`clipped_px`, the
// largest overrun on any side) for clipped labels. A rectangle drawn at an angle (a gantt
// milestone: CSS `rotate(45deg) scale(0.8)`) has as `box` the axis-aligned box of its corners,
// which holds the empty corners around the diamond: its `clipped_px` is measured in the
// rectangle's own frame and scaled back to root units. `outside_px` is how far `bbox` runs past
// the viewBox, where every viewer cuts the text. `rotated` marks text drawn at an angle, whose
// `bbox` is larger than its glyphs. Coordinates are SVG user units of the root, the frame
// svg_geometry.py works in. `kind` is one of node, edge, title, note, actor, message, task,
// section, other; `id` is the raw element id that svg_geometry.py matches (the node group of a
// node label, the cluster group of a title, the text element of a gantt label); `owner` is the
// `data-id` of the node or edge the label belongs to, when the SVG carries one. `el` is
// `foreignObject` for an HTML label and `text` for SVG text; `n` is the index of the label's
// element among the root's elements of that name, in document order; `cls` holds the classes of
// the element that holds the text and of its nearest ancestors.
//
// Colour (TASK R7.5, R7.6). `fg` is the colour the glyphs are drawn in: the text's own colour,
// blended with its `mix-blend-mode` and composited with its opacity over `bg`. `bg` is the
// colour under the centre of the painted text: the page background (`page`, set by
// --background), then every filled shape and every HTML background that precedes the text in
// paint order and covers that point, composited in order. `under` lists those layers, bottom to
// top, as {"role", "id", "fill": "rgba(r,g,b,a)"}; role is one of node, cluster, edgeLabel,
// note, actor, activation, task, section, band (a sequence `rect` or `box` block), labelBox,
// marker (a shape a marker draws at a line end, such as the circle under a sequence number),
// label (another HTML label background) or other. `fg` is null for text that is not drawn (no
// fill, hidden, fully transparent). `uncertain` marks a backdrop with a gradient or pattern
// fill, whose colour is not known.
//
// Fonts (TASK R7.8). `font` is the platform font that drew most glyphs of the label, read from
// the browser (CSS.getPlatformFontsForNode); `fonts` sums the glyphs per family over all labels,
// most first; `font_family` is the first of them.
//
// With --png the SVG is also screenshotted at its natural size times --scale (default 2) on
// --background (default white), so render_check.py needs one browser start per render.
//
// Safety: page scripts are disabled, and every request except data: URLs is aborted, on top
// of the network block in puppeteer.json. The SVG is only parsed, laid out and measured. The
// script works in the directory of <puppeteer.json>, the install directory, before it loads
// puppeteer: puppeteer runs a JavaScript configuration it finds in its working directory or a
// parent, and the empty .puppeteerrc.json of the install ends that search (TASK R7.9).
//
// Exit 0 on success, 2 when the browser or the SVG cannot be loaded, 3 on a usage error.
import { createRequire } from "module";
import fs from "fs";
import path from "path";

function fail(code, message) {
  process.stderr.write(`measure_text.mjs: ${message}\n`);
  process.exit(code);
}

const argv = process.argv.slice(2);
const positional = [];
const options = { png: null, scale: 2, background: "white" };
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === "--png" || a === "--scale" || a === "--background") {
    if (i + 1 >= argv.length) fail(3, `${a} needs a value`);
    options[a.slice(2)] = argv[++i];
  } else if (a.startsWith("--")) {
    fail(3, `unknown option ${a}`);
  } else {
    positional.push(a);
  }
}
if (positional.length !== 2) {
  fail(3, "usage: node measure_text.mjs <puppeteer.json> <figure.svg> [--png out.png] [--scale n] [--background colour]");
}
const scale = Number(options.scale);
if (!(scale > 0 && scale <= 4)) fail(3, "--scale must be a number in (0, 4]");
if (!/^(#[0-9A-Fa-f]{3,8}|[A-Za-z]{3,20})$/.test(options.background)) {
  fail(3, "--background must be a hex colour or a colour name");
}

// Every path is resolved before the script leaves the caller's directory.
const [ppPath, svgPath] = positional.map((p) => path.resolve(p));
const pngPath = options.png === null ? null : path.resolve(options.png);
let config, svgText;
try {
  config = JSON.parse(fs.readFileSync(ppPath, "utf8"));
} catch (e) {
  fail(2, `cannot read the puppeteer config ${ppPath}: ${e.message}`);
}
try {
  svgText = fs.readFileSync(svgPath, "utf8");
} catch (e) {
  fail(2, `cannot read the SVG ${svgPath}: ${e.message}`);
}
if (!/<svg[\s>]/.test(svgText)) fail(2, `${svgPath} holds no <svg> element`);

try {
  process.chdir(path.dirname(ppPath));
} catch (e) {
  fail(2, `cannot work in the install directory ${path.dirname(ppPath)}: ${e.message}`);
}
const require = createRequire(path.join(path.dirname(ppPath), "package.json"));
let puppeteer;
try {
  puppeteer = require("puppeteer");
} catch (e) {
  fail(2, `puppeteer is not installed next to ${ppPath}: ${e.message}`);
}

const viewBox = (svgText.match(/viewBox="([^"]+)"/) || [])[1];
const vb = viewBox ? viewBox.trim().split(/[\s,]+/).map(Number) : [0, 0, 800, 600];
const width = Math.max(1, Math.ceil(vb[2] || 800));
const height = Math.max(1, Math.ceil(vb[3] || 600));

// Runs in the page. Returns the measurement JSON described above, without the font fields.
// Every element whose text is measured gets the attribute data-mt="<label index>", which the
// font lookup below reads.
function measureInPage() {
  const SVG_NS = "http://www.w3.org/2000/svg";
  const svg = document.querySelector("svg");
  const figureKind = svg.getAttribute("aria-roledescription") || "";
  const inv = svg.getScreenCTM().inverse();
  const toRoot = (el) => inv.multiply(el.getScreenCTM());
  const corners = (m, x, y, w, h) => {
    const ps = [[x, y], [x + w, y], [x, y + h], [x + w, y + h]].map(([px, py]) => {
      const p = new DOMPoint(px, py).matrixTransform(m);
      return [p.x, p.y];
    });
    const xs = ps.map((p) => p[0]);
    const ys = ps.map((p) => p[1]);
    return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
  };
  const boxOf = (el) => {
    const b = el.getBBox();
    if (!(b.width > 0 && b.height > 0)) return null;
    return corners(toRoot(el), b.x, b.y, b.width, b.height);
  };
  // The text nodes below el that hold text, and the union of their line boxes in client px.
  const textNodes = (el) => {
    const out = [];
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      if (n.textContent.trim() && n.parentElement) out.push(n);
    }
    return out;
  };
  const clientTextBox = (nodes) => {
    const range = document.createRange();
    let L = Infinity, T = Infinity, R = -Infinity, B = -Infinity;
    for (const n of nodes) {
      range.selectNodeContents(n);
      for (const r of range.getClientRects()) {
        if (r.width === 0 || r.height === 0) continue;
        L = Math.min(L, r.left); T = Math.min(T, r.top);
        R = Math.max(R, r.right); B = Math.max(B, r.bottom);
      }
    }
    return R > L ? [L, T, R, B] : null;
  };
  const xywh = (b) => (b ? [b[0], b[1], b[2] - b[0], b[3] - b[1]].map((v) => Math.round(v * 100) / 100) : null);
  // The largest overrun of the painted text past a box, on any side: a label that loses its
  // last line under a short box is clipped as surely as one cut at its right end.
  const overflow = (paint, box) => (paint && box
    ? Math.max(0, box[0] - paint[0], paint[2] - box[2], box[1] - paint[1], paint[3] - box[3]) : 0);
  // The overrun of the painted text past the shape that holds it, whose root-frame box is box.
  // A shape drawn at an angle is measured in its own frame: the corners of the painted box are
  // mapped through the inverse of its transform and compared with its own box, and each side's
  // overrun is scaled back by the length of that axis in the root frame.
  const overflowPast = (paint, shape, box) => {
    if (!paint || !box) return 0;
    const m = toRoot(shape);
    if (!(Math.abs(m.b) > 1e-6 || Math.abs(m.c) > 1e-6)) return overflow(paint, box);
    const b = shape.getBBox();
    const own = corners(m.inverse(), paint[0], paint[1], paint[2] - paint[0], paint[3] - paint[1]);
    const sx = Math.hypot(m.a, m.b), sy = Math.hypot(m.c, m.d);
    return Math.max(0, (b.x - own[0]) * sx, (own[2] - b.x - b.width) * sx,
                    (b.y - own[1]) * sy, (own[3] - b.y - b.height) * sy);
  };
  const vb = svg.viewBox && svg.viewBox.baseVal;
  const canvas = vb && vb.width > 0 && vb.height > 0 ? [vb.x, vb.y, vb.x + vb.width, vb.y + vb.height] : null;
  const round2 = (v) => Math.round(v * 100) / 100;
  // Text drawn at an angle: its box in the root frame holds more than its glyphs.
  const rotatedFlag = (el) => {
    const m = toRoot(el);
    return Math.abs(m.b) > 1e-6 || Math.abs(m.c) > 1e-6 ? { rotated: true } : {};
  };
  const text = (el) => el.textContent.replace(/\s+/g, " ").trim().slice(0, 120);
  const classesNear = (el) => {
    const out = [];
    for (let e = el, k = 0; e && e !== svg && k < 4; e = e.parentElement, k++) {
      for (const c of (e.getAttribute && e.getAttribute("class") || "").split(/\s+/)) {
        if (c && !out.includes(c)) out.push(c);
      }
    }
    return out.join(" ");
  };

  // ----- colours
  const parseColour = (s) => {
    if (!s) return null;
    s = String(s).trim();
    if (s === "transparent") return [0, 0, 0, 0];
    let m = s.match(/^rgba?\(\s*([-\d.]+)[\s,]+([-\d.]+)[\s,]+([-\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)$/i);
    if (m) {
      const a = m[4] === undefined ? 1 : (m[4].endsWith("%") ? parseFloat(m[4]) / 100 : parseFloat(m[4]));
      return [Number(m[1]), Number(m[2]), Number(m[3]), a];
    }
    m = s.match(/^color\(srgb\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)(?:\s*\/\s*([\d.]+%?))?\s*\)$/i);
    if (m) {
      const a = m[4] === undefined ? 1 : (m[4].endsWith("%") ? parseFloat(m[4]) / 100 : parseFloat(m[4]));
      return [Number(m[1]) * 255, Number(m[2]) * 255, Number(m[3]) * 255, a];
    }
    return null; // none, url(#gradient), and colour spaces this page does not use
  };
  const clamp = (v) => Math.max(0, Math.min(255, v));
  const over = (rgb, alpha, base) => rgb.map((c, k) => clamp(c) * alpha + base[k] * (1 - alpha));
  const hex = (rgb) => "#" + rgb.map((c) => Math.round(clamp(c)).toString(16).padStart(2, "0")).join("");
  const rgbaText = (rgb, a) => `rgba(${rgb.map((c) => Math.round(clamp(c))).join(",")},${Math.round(a * 1000) / 1000})`;
  const blend = (mode, s, b) => s.map((cs, k) => {
    const cb = b[k];
    switch (mode) {
      case "difference": return Math.abs(cb - cs);
      case "exclusion": return cb + cs - (2 * cb * cs) / 255;
      case "multiply": return (cb * cs) / 255;
      case "screen": return cb + cs - (cb * cs) / 255;
      default: return cs;
    }
  });
  const opacityCache = new Map();
  const opacityOf = (el) => {
    if (!el || el.nodeType !== 1 || el === document.body || el === document.documentElement) return 1;
    if (opacityCache.has(el)) return opacityCache.get(el);
    const own = parseFloat(getComputedStyle(el).opacity);
    const o = (isNaN(own) ? 1 : own) * (el === svg ? 1 : opacityOf(el.parentElement));
    opacityCache.set(el, o);
    return o;
  };
  const visible = (el) => (typeof el.checkVisibility === "function"
    ? el.checkVisibility({ visibilityProperty: true }) : true);

  // ----- what a layer is: the figure element whose fill it draws
  const roleOf = (el) => {
    const node = el.closest("g.node");
    if (node) return { role: "node", id: node.getAttribute("data-id") || node.id || "" };
    const cluster = el.closest("g.cluster, g.statediagram-cluster");
    if (cluster) return { role: "cluster", id: cluster.getAttribute("data-id") || cluster.id || "" };
    if (el.closest("g.edgeLabel, .edgeLabel, .labelBkg")) return { role: "edgeLabel", id: "" };
    const cls = (el.getAttribute("class") || "").split(/\s+/);
    if (cls.includes("note")) return { role: "note", id: "" };
    if (cls.includes("actor")) return { role: "actor", id: el.getAttribute("name") || "" };
    if (cls.some((c) => /^activation\d*$/.test(c))) return { role: "activation", id: "" };
    if (cls.includes("task") || cls.some((c) => /^(task|done|active|crit|activeCrit|doneCrit)\d+$/.test(c))) {
      return { role: "task", id: el.id || "" };
    }
    if (cls.includes("section") || cls.some((c) => /^section\d+$/.test(c))) return { role: "section", id: "" };
    if (cls.includes("rect") && figureKind === "sequence") return { role: "band", id: "" };
    if (cls.includes("labelBox")) return { role: "labelBox", id: "" };
    if (el.namespaceURI !== SVG_NS) return { role: "label", id: "" };
    return { role: "other", id: el.id || "" };
  };

  // ----- markers: the shapes a marker draws at the ends of a line or path (the circle under a
  // sequence number, an arrowhead), placed as SVG 1.1 section 11.6.2 places them.
  const markerUrl = /url\(\s*["']?#([^"')]+)["']?\s*\)/;
  const ends = (el) => {
    if (el.localName === "line") {
      const p = [el.x1.baseVal.value, el.y1.baseVal.value];
      const q = [el.x2.baseVal.value, el.y2.baseVal.value];
      const a = Math.atan2(q[1] - p[1], q[0] - p[0]);
      return { start: [p, a], end: [q, a] };
    }
    if (typeof el.getTotalLength !== "function") return null;
    const total = el.getTotalLength();
    if (!(total > 0)) return null;
    const at = (s) => el.getPointAtLength(Math.max(0, Math.min(total, s)));
    const d = Math.min(0.5, total / 2);
    const s0 = at(0), s1 = at(d), e0 = at(total - d), e1 = at(total);
    return { start: [[s0.x, s0.y], Math.atan2(s1.y - s0.y, s1.x - s0.x)],
             end: [[e1.x, e1.y], Math.atan2(e1.y - e0.y, e1.x - e0.x)] };
  };
  const markerLayers = (el, cs, i) => {
    const out = [];
    let geometry = null;
    for (const [which, value] of [["start", cs.markerStart], ["end", cs.markerEnd]]) {
      const m = markerUrl.exec(value || "");
      if (!m) continue;
      const marker = document.getElementById(m[1]);
      if (!marker || marker.localName !== "marker") continue;
      geometry = geometry || ends(el);
      if (!geometry) return out;
      const [[vx, vy], direction] = geometry[which];
      const orient = marker.getAttribute("orient") || "0";
      let angle = /^auto/.test(orient) ? direction * 180 / Math.PI : (parseFloat(orient) || 0);
      if (orient === "auto-start-reverse" && which === "start") angle += 180;
      const units = marker.getAttribute("markerUnits") === "userSpaceOnUse" ? 1 : (parseFloat(cs.strokeWidth) || 1);
      const mw = marker.markerWidth.baseVal.value, mh = marker.markerHeight.baseVal.value;
      const vbox = marker.viewBox && marker.viewBox.baseVal;
      let s = 1, tx = 0, ty = 0;
      if (vbox && vbox.width > 0 && vbox.height > 0) {
        s = Math.min(mw / vbox.width, mh / vbox.height);
        tx = (mw - vbox.width * s) / 2 - vbox.x * s;
        ty = (mh - vbox.height * s) / 2 - vbox.y * s;
      }
      const rx = marker.refX.baseVal.value * s + tx, ry = marker.refY.baseVal.value * s + ty;
      const place = new DOMMatrix().translateSelf(vx, vy).rotateSelf(angle).scaleSelf(units, units)
        .translateSelf(-rx, -ry).translateSelf(tx, ty).scaleSelf(s, s);
      const screen = DOMMatrix.fromMatrix(el.getScreenCTM()).multiply(place);
      for (const child of marker.querySelectorAll("rect, circle, ellipse, path, polygon, polyline")) {
        const ccs = getComputedStyle(child);
        const c = parseColour(ccs.fill);
        if (!c) continue;
        let alpha = c[3] * opacityOf(el);
        const fo = parseFloat(ccs.fillOpacity);
        if (!isNaN(fo)) alpha *= fo;
        if (!(alpha > 0.004)) continue;
        let b;
        try { b = child.getBBox(); } catch (e) { continue; }
        const pts = [[b.x, b.y], [b.x + b.width, b.y], [b.x, b.y + b.height], [b.x + b.width, b.y + b.height]]
          .map(([x, y]) => new DOMPoint(x, y).matrixTransform(screen));
        const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y);
        const rect = { left: Math.min(...xs), right: Math.max(...xs), top: Math.min(...ys), bottom: Math.max(...ys) };
        out.push({ el: child, i, isSvg: true, rgb: c.slice(0, 3), alpha, rect, screen,
                   role: { role: "marker", id: m[1] } });
      }
    }
    return out;
  };

  // ----- every element that paints a fill or a background, in paint (document) order
  const all = Array.from(svg.querySelectorAll("*"));
  const order = new Map(all.map((el, i) => [el, i]));
  const SHAPES = new Set(["rect", "circle", "ellipse", "path", "polygon", "polyline"]);
  const MARKED = new Set(["line", "path", "polyline", "polygon"]);
  const layers = [];
  for (const el of all) {
    const isSvg = el.namespaceURI === SVG_NS;
    if (isSvg) {
      if (!SHAPES.has(el.localName) && !MARKED.has(el.localName)) continue;
      if (el.closest("defs, marker, clipPath, mask, pattern, symbol")) continue;
    } else if (!el.closest("foreignObject")) {
      continue;
    }
    if (!visible(el)) continue;
    const cs = getComputedStyle(el);
    if (isSvg && MARKED.has(el.localName)) {
      // A marker is painted after the fill and the stroke of its element.
      const marks = markerLayers(el, cs, order.get(el));
      if (SHAPES.has(el.localName)) {
        const own = shapeLayer(el, cs, isSvg);
        if (own) layers.push(own);
      }
      layers.push(...marks);
      continue;
    }
    const own = shapeLayer(el, cs, isSvg);
    if (own) layers.push(own);
  }
  // The layer of one filled shape or HTML background, or null when it paints nothing.
  function shapeLayer(el, cs, isSvg) {
    const paint = isSvg ? cs.fill : cs.backgroundColor;
    const c = parseColour(paint);
    if (!c) {
      if (isSvg && /^url\(/.test(paint || "")) {
        const r = el.getBoundingClientRect();
        return { el, i: order.get(el), isSvg, rgb: null, alpha: 1, rect: r, role: roleOf(el) };
      }
      return null;
    }
    let alpha = c[3] * opacityOf(el);
    if (isSvg) {
      const fo = parseFloat(cs.fillOpacity);
      if (!isNaN(fo)) alpha *= fo;
    }
    if (!(alpha > 0.004)) return null;
    const r = el.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0)) return null;
    return { el, i: order.get(el), isSvg, rgb: c.slice(0, 3), alpha, rect: r, role: roleOf(el) };
  }
  const covers = (layer, cx, cy) => {
    const r = layer.rect;
    if (cx < r.left || cx > r.right || cy < r.top || cy > r.bottom) return false;
    if (layer.isSvg) {
      try {
        const m = layer.screen || layer.el.getScreenCTM();
        const p = new DOMPoint(cx, cy).matrixTransform(m.inverse());
        return layer.el.isPointInFill(p);
      } catch (e) {
        return true; // no hit test: the bounding box decides
      }
    }
    for (const q of layer.el.getClientRects()) {
      if (cx >= q.left && cx <= q.right && cy >= q.top && cy <= q.bottom) return true;
    }
    return false;
  };
  const pageColour = parseColour(getComputedStyle(document.body).backgroundColor) || [255, 255, 255, 1];
  let base = over(pageColour.slice(0, 3), pageColour[3], [255, 255, 255]);
  const svgBackground = parseColour(getComputedStyle(svg).backgroundColor);
  if (svgBackground && svgBackground[3] > 0) base = over(svgBackground.slice(0, 3), svgBackground[3], base);

  // The colour under (cx, cy) below the element holder, and the colour holder draws its text in.
  const colours = (holder, isSvgText, cx, cy) => {
    const idx = order.get(holder);
    let bg = base.slice();
    let uncertain = false;
    const under = [];
    for (const L of layers) {
      if (L.i > idx) break;
      if (!covers(L, cx, cy)) continue;
      if (L.rgb === null) {
        uncertain = true;
        under.push({ role: L.role.role, id: L.role.id, fill: "unknown" });
        continue;
      }
      bg = over(L.rgb, L.alpha, bg);
      under.push({ role: L.role.role, id: L.role.id, fill: rgbaText(L.rgb, L.alpha) });
    }
    const out = { fg: null, bg: hex(bg), under };
    if (uncertain) out.uncertain = true;
    if (!visible(holder)) return out;
    const cs = getComputedStyle(holder);
    const c = parseColour(isSvgText ? cs.fill : cs.color);
    if (!c) return out;
    let alpha = c[3] * opacityOf(holder);
    if (isSvgText) {
      const fo = parseFloat(cs.fillOpacity);
      if (!isNaN(fo)) alpha *= fo;
    }
    if (!(alpha > 0.004)) return out;
    const mode = cs.mixBlendMode || "normal";
    if (mode !== "normal") out.blend = mode;
    out.fg = hex(over(blend(mode, c.slice(0, 3), bg), alpha, bg));
    return out;
  };

  const labels = [];
  const titles = [];
  const fos = Array.from(svg.querySelectorAll("foreignObject"));
  fos.forEach((fo, n) => {
    const t = text(fo);
    if (!t) return;
    const nodes = textNodes(fo);
    const client = clientTextBox(nodes);
    if (!client) return;
    const paint = corners(inv, client[0], client[1], client[2] - client[0], client[3] - client[1]);
    const box = boxOf(fo);
    let kind = "other", id = "", owner = "";
    const clusterLabel = fo.closest("g.cluster-label");
    if (clusterLabel) {
      kind = "title";
      const cluster = clusterLabel.closest("g.cluster, g.statediagram-cluster");
      id = cluster ? cluster.id : "";
      owner = cluster ? cluster.getAttribute("data-id") || "" : "";
      titles.push({ text: t, id, bbox: xywh(paint), box: xywh(box) });
    } else if (fo.closest("g.edgeLabel")) {
      kind = "edge";
      const holderOfId = fo.closest("[data-id]");
      id = holderOfId ? holderOfId.getAttribute("data-id") : "";
      owner = id;
    } else if (fo.closest("g.node")) {
      kind = "node";
      const node = fo.closest("g.node");
      id = node.id;
      owner = node.getAttribute("data-id") || "";
    }
    const holder = nodes[0].parentElement;
    const k = labels.length;
    holder.setAttribute("data-mt", String(k));
    const c = colours(holder, false, (client[0] + client[2]) / 2, (client[1] + client[3]) / 2);
    labels.push(Object.assign({ text: t, kind, id, owner, el: "foreignObject", n, cls: classesNear(holder),
                                bbox: xywh(paint), box: xywh(box),
                                clipped_px: round2(overflow(paint, box)),
                                outside_px: round2(overflow(paint, canvas)),
                                font_px: parseFloat(getComputedStyle(holder).fontSize) || 0 },
                              rotatedFlag(fo), c));
  });
  const texts = Array.from(svg.querySelectorAll("text"));
  texts.forEach((el, n) => {
    const t = text(el);
    if (!t) return;
    const cls = el.getAttribute("class") || "";
    const paint = boxOf(el);
    if (!paint) return;
    let kind = "other", shape = null;
    const parent = el.parentElement;
    if (/\bmessageText\b/.test(cls)) {
      kind = "message";
    } else if (/\bnoteText\b/.test(cls)) {
      kind = "note";
      shape = parent && parent.querySelector("rect.note");
    } else if (/\bactor\b/.test(cls)) {
      kind = "actor";
      shape = parent && parent.querySelector("rect.actor");
    } else if (/\btaskText/.test(cls)) {
      kind = "task";
      if (/\btaskText\b/.test(cls) && el.id && el.id.endsWith("-text")) {
        shape = document.getElementById(el.id.slice(0, -5));
      }
    } else if (/\bsectionTitle\b/.test(cls)) {
      kind = "section";
    }
    const reserved = shape ? boxOf(shape) : null;
    const nodes = textNodes(el);
    const holder = nodes.length ? nodes[0].parentElement : el;
    const k = labels.length;
    holder.setAttribute("data-mt", String(k));
    const r = el.getBoundingClientRect();
    const c = colours(holder, true, r.left + r.width / 2, r.top + r.height / 2);
    labels.push(Object.assign({ text: t, kind, id: el.id || "", owner: "", el: "text", n,
                                cls: classesNear(holder),
                                bbox: xywh(paint), box: xywh(reserved),
                                clipped_px: round2(overflowPast(paint, shape, reserved)),
                                outside_px: round2(overflow(paint, canvas)),
                                font_px: parseFloat(getComputedStyle(el).fontSize) || 0 },
                              rotatedFlag(el), c));
  });
  // The most common size among node, edge, message and task labels (all text when none of
  // those exist): the size the report line names. Legibility is gated on the smallest drawn
  // text, which svg_geometry.py reads from the labels.
  const counts = new Map();
  const main = labels.filter((l) => ["node", "edge", "message", "task"].includes(l.kind));
  for (const l of (main.length ? main : labels)) {
    if (!(l.font_px > 0)) continue;
    const k = Math.round(l.font_px * 2) / 2;
    counts.set(k, (counts.get(k) || 0) + 1);
  }
  let fontPx = 0, best = -1;
  for (const [k, c] of counts) if (c > best || (c === best && k < fontPx)) { fontPx = k; best = c; }
  return { labels, titles, font_px: fontPx, kind: figureKind, page: hex(base) };
}

// The platform fonts that drew the text of each marked element (data-mt), through the DevTools
// protocol: no page script runs. Returns {"byLabel": {index: family}, "fonts": [{family, glyphs}]}.
async function platformFonts(page, limit) {
  const client = typeof page.createCDPSession === "function"
    ? await page.createCDPSession() : await page.target().createCDPSession();
  try {
    await client.send("DOM.enable");
    await client.send("CSS.enable");
    const { root } = await client.send("DOM.getDocument", { depth: -1 });
    const { nodeIds } = await client.send("DOM.querySelectorAll", { nodeId: root.nodeId, selector: "[data-mt]" });
    const byLabel = {};
    const totals = new Map();
    for (const nodeId of nodeIds.slice(0, limit)) {
      const { attributes } = await client.send("DOM.getAttributes", { nodeId });
      const at = attributes.indexOf("data-mt");
      const label = at >= 0 ? attributes[at + 1] : null;
      const { fonts } = await client.send("CSS.getPlatformFontsForNode", { nodeId });
      let top = null, topCount = -1;
      for (const f of fonts || []) {
        const family = f.familyName || f.postScriptName || "";
        if (!family) continue;
        totals.set(family, (totals.get(family) || 0) + (f.glyphCount || 0));
        if ((f.glyphCount || 0) > topCount) { top = family; topCount = f.glyphCount || 0; }
      }
      if (label !== null) byLabel[label] = top;
    }
    const list = Array.from(totals, ([family, glyphs]) => ({ family, glyphs }))
      .sort((a, b) => b.glyphs - a.glyphs || (a.family < b.family ? -1 : 1));
    return { byLabel, fonts: list };
  } finally {
    await client.detach().catch(() => {});
  }
}

const WATCHDOG_MS = 60000;
const FONT_LOOKUP_LIMIT = 600;
let browser;
const watchdog = setTimeout(() => {
  try {
    if (browser && browser.process()) browser.process().kill("SIGKILL");
  } catch (e) {
    // the browser is already gone
  }
  fail(2, `the browser did not answer within ${WATCHDOG_MS / 1000} s`);
}, WATCHDOG_MS);
try {
  browser = await puppeteer.launch(config);
} catch (e) {
  fail(2, `the browser did not start: ${String(e.message || e).split("\n")[0]}`);
}
let result;
try {
  const page = await browser.newPage();
  await page.setJavaScriptEnabled(false);
  await page.setRequestInterception(true);
  page.on("request", (r) => {
    const u = r.url();
    if (u.startsWith("data:") || u === "about:blank") r.continue();
    else r.abort();
  });
  await page.setViewport({ width: width + 16, height: height + 16, deviceScaleFactor: scale });
  await page.setContent(
    `<!doctype html><html><head><meta charset="utf-8"></head>` +
    `<body style="margin:0;background:${options.background}">${svgText}</body></html>`,
    { waitUntil: "load" });
  // Synchronous calls only: with page scripts disabled, puppeteer 19 never settles an
  // evaluate that awaits a page promise, so the font wait polls from node.
  await page.evaluate((w, h) => {
    const s = document.querySelector("svg");
    s.style.maxWidth = "none";
    s.setAttribute("width", String(w));
    s.setAttribute("height", String(h));
  }, vb[2] || width, vb[3] || height);
  for (let i = 0; i < 150; i++) {
    const status = await page.evaluate(() => (document.fonts ? document.fonts.status : "loaded"));
    if (status === "loaded") break;
    await new Promise((resolve) => setTimeout(resolve, 20));
  }
  result = await page.evaluate(measureInPage);
  result.browser = await browser.version();
  try {
    const fonts = await platformFonts(page, FONT_LOOKUP_LIMIT);
    result.labels.forEach((l, k) => { l.font = fonts.byLabel[String(k)] || null; });
    result.fonts = fonts.fonts;
    result.font_family = fonts.fonts.length ? fonts.fonts[0].family : null;
  } catch (e) {
    result.fonts = [];
    result.font_family = null;
    result.font_error = String(e.message || e).split("\n")[0];
  }
  result.png = null;
  if (pngPath) {
    // A page screenshot clipped to the SVG: an element screenshot scrolls the element into
    // view with a page promise, which never settles in puppeteer 19 with page scripts off.
    await page.screenshot({ path: pngPath,
                            clip: { x: 0, y: 0, width: vb[2] || width, height: vb[3] || height } });
    result.png = pngPath;
  }
} catch (e) {
  await browser.close().catch(() => {});
  fail(2, `the SVG could not be measured: ${String(e.message || e).split("\n")[0]}`);
}
await browser.close();
clearTimeout(watchdog);
process.stdout.write(JSON.stringify(result));
process.exit(0);
