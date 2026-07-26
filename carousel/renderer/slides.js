/* Carousel renderer — builds the fixed deck shape from window.BRIEF.
   Deck: Hook · optional Context · 1–5 Beats (chart beats = setup + chart) ·
         Synthesis · So What · CTA · Appendix (source/method, Alabaster, last)
   (08-carousel-application.md). generate.py validates; this file only renders.

   Deck chrome, on every slide with no exceptions:
   - eyebrow top-left: SERIES · SECTOR (cover) / SERIES · SECTOR · TAKEAWAY (rest)
   - slide index top-right: n/N
   - full wordmark lower-right on cover + final slide; monogram on interior slides */

const BRIEF = window.BRIEF

// Backward compat: scalar hook string → object with just headline.
if (typeof BRIEF.hook === 'string') BRIEF.hook = { headline: BRIEF.hook }

const HAS_CONTEXT = false // Boolean(BRIEF.context)
const HAS_PUZZLE  = Boolean(BRIEF.puzzle)
// Each chart beat renders as a pair: a setup slide (what the data is) then the
// chart slide (chart + takeaway on top), so the reader is primed before the plot.
const CHART_BEATS = BRIEF.beats.filter(b => (b.type || b.kind) === 'chart').length
// +5: hook, synthesis, so-what, CTA, appendix (source/method, always last).
const DECK_LEN    = BRIEF.beats.length + CHART_BEATS + 5 + (HAS_CONTEXT ? 1 : 0) + (HAS_PUZZLE ? 1 : 0)

// Reduced monogram, inlined so the renderer has no asset dependencies.
// Paths from dj-brand-kit/assets/monogram/; tight viewBox around the bars.
const MONOGRAM_D = [
  'M148.561 158H134.566L124 211.974H137.971L148.561 158Z',
  'M165.937 211.974L176.527 158H162.532L151.966 211.974H165.937Z',
  'M137.996 211.974L127.405 265.922H141.401L151.966 211.974H137.996Z',
  'M193.902 211.974L204.468 158H190.497L179.932 211.974H193.902Z',
  'M165.962 211.974L155.371 265.922H169.367L179.932 211.974H165.962Z',
  'M221.869 211.974L232.434 158H218.464L207.873 211.974H221.869Z',
  'M193.902 211.974L183.337 265.922H197.307L207.898 211.974H193.902Z',
  'M211.303 265.922H225.273L235.864 211.974H221.868L211.303 265.922Z',
  'M239.269 265.922H253.239L263.805 211.974H249.834L239.269 265.922Z',
  'M267.21 265.922H281.205L291.771 211.974H277.8L267.21 265.922Z',
]

function monogram(color) {
  const paths = MONOGRAM_D.map(d => `<path d="${d}" fill="${color}"/>`).join('')
  return `<svg viewBox="124 158 168 108" xmlns="http://www.w3.org/2000/svg">${paths}</svg>`
}

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

// Honey Bronze pop — the deck's single emphasis accent. Wrap one phrase in
// *asterisks* in hook / so-what copy to lift it; the rest escapes as usual.
function pop(text) {
  return String(text).split('*')
    .map((part, i) => i % 2 ? `<span class="pop">${esc(part)}</span>` : esc(part))
    .join('')
}

// ── Field themes — 02-color-system.md surface pairings ────────────────────────

const THEME_CLASS = { parchment: '', navy: 'dj-theme-navy', carbon: 'dj-theme-carbon', alabaster: 'dj-theme-alabaster' }
// Corner monogram per field: Navy mark on light surfaces; subdued Alabaster
// mark on dark surfaces (04-components.md)
const THEME_MONOGRAM = {
  parchment: 'var(--dj-navy)', alabaster: 'var(--dj-navy)',
  navy: 'var(--dj-alabaster)', carbon: 'var(--dj-alabaster)',
}
const THEME_WORDMARK = {
  parchment: 'wordmark-navy.svg', alabaster: 'wordmark-navy.svg',
  navy: 'wordmark-parchment.svg', carbon: 'wordmark-parchment.svg',
}

// ── Deck chrome ───────────────────────────────────────────────────────────────

function chrome(n, theme, { wordmark = false, monogram: withMono = false, takeaway = false } = {}) {
  // Takeaway only on data slides — they travel out of context; statement
  // slides carry their own words.
  const eyebrow = takeaway
    ? `${BRIEF.series} · ${BRIEF.sector} · ${BRIEF.takeaway}`
    : `${BRIEF.series} · ${BRIEF.sector}`
  const mark = wordmark
    ? `<img class="wordmark-corner" src="../../assets/logo/${THEME_WORDMARK[theme]}" alt="DataJockey">`
    : (withMono ? `<div class="corner-monogram">${monogram(THEME_MONOGRAM[theme])}</div>` : '')
  return `
    <div class="deck-eyebrow">${esc(eyebrow)}</div>
    <div class="slide-index">${n}/${DECK_LEN}</div>
    ${mark}`
}

function judgment(text) {
  // One sentence of interpretation, adjacent to the data it interprets
  return `<div class="judgment">${esc(text)}</div>`
}

// ── Charts — directional colour: one accented element, the rest muted ─────────

function accentColor(d) {
  if (d.protagonist) return 'var(--protagonist)'
  if (d.highlight)   return 'var(--accent-highlight)'
  return d.value < 0 ? 'var(--delta-neg)' : 'var(--delta-pos)'
}

const isAccented = d => d.protagonist || d.highlight || d.accent

// Axis tick helpers — round "nice" ticks from a data domain, so axes label
// themselves instead of relying on hard-coded values per chart.
function niceTicks(lo, hi, target = 5) {
  const span = (hi - lo) || 1
  const mag = Math.pow(10, Math.floor(Math.log10(span / target)))
  const norm = span / target / mag
  const step = (norm < 1.5 ? 1 : norm < 3 ? 2 : norm < 7 ? 5 : 10) * mag
  const out = []
  for (let t = Math.ceil(lo / step) * step; t <= hi + 1e-9; t += step)
    out.push(Math.round(t * 1e6) / 1e6)
  return out
}
const fmtNum = v => Math.abs(v) >= 1000 ? v.toLocaleString('en-US') : String(v)
const fmtTick = (v, suf) => (v > 0 && suf === '%' ? '+' : '') + fmtNum(v) + (suf || '')
const axisTitle = s => esc(String(s).toUpperCase())

function barChart(spec) {
  const W = 952, rowH = 130, gap = 44, labelH = 42
  const rows = spec.data
  const single = rows.length === 1
  const H = rows.length * (rowH + gap) - gap
  const maxAbs = Math.max(...rows.map(d => Math.abs(d.value)))
  const barMax = W - 200
  let y = 0
  const parts = rows.map(d => {
    const on = single || isAccented(d)
    const fill = on ? accentColor(d) : 'var(--chart-faint)'
    const valueInk = on ? 'var(--text-1)' : 'var(--text-3)'
    const w = Math.max(6, Math.abs(d.value) / maxAbs * barMax)
    const signed = spec.signed !== false
    const valStr = signed
      ? `${d.value > 0 ? '+' : '−'}${Math.abs(d.value)}${esc(spec.unit || '')}`
      : `${d.value}${esc(spec.unit || '')}`
    const out = `
      <text x="0" y="${y + labelH - 12}" font-size="30" fill="var(--text-2)" font-family="DM Sans">${esc(d.label)}</text>
      <rect x="0" y="${y + labelH}" width="${w}" height="${rowH - labelH}" fill="${fill}"/>
      <text x="${w + 20}" y="${y + labelH + (rowH - labelH) / 2 + 12}" font-size="40" font-weight="500"
            fill="${valueInk}" font-family="DM Sans">${valStr}</text>`
    y += rowH + gap
    return out
  })
  // Optional axis caption — names exactly what the values are (e.g. an index),
  // so a reader isn't left decoding a bare number.
  const capH = spec.x_label ? 74 : 0
  const caption = spec.x_label
    ? `<line x1="0" y1="${H + 26}" x2="${W}" y2="${H + 26}" stroke="var(--chart-faint)" stroke-width="1"/>
       <text x="0" y="${H + 60}" font-size="24" fill="var(--text-3)" font-family="DM Mono"
             letter-spacing="1">${axisTitle(spec.x_label)}</text>`
    : ''
  return `<svg viewBox="0 0 ${W} ${H + capH}" xmlns="http://www.w3.org/2000/svg">${parts.join('')}${caption}</svg>`
}

function slopeChart(spec) {
  const W = 952, H = 640, pad = 70
  const vals = spec.data.flatMap(d => [d.from, d.to])
  // x0/x1 are symmetric margins sized to the longest value+unit label.
  // text-anchor="end" labels sit at (x0-28); text-anchor="start" labels at (x1+28).
  // At font-size 34, DM Sans runs ~20px/char. Fixed labels need ≥210px; long
  // unit strings (e.g. " AED/sqm") need more — compute and take the max.
  const unit = spec.unit || ''
  const longestValChars = Math.max(...vals.map(v => (String(v) + unit).length))
  const x0 = Math.max(210, longestValChars * 20 + 28)
  const x1 = W - x0
  const lo = Math.min(...vals), hi = Math.max(...vals)
  const yOf = v => pad + (hi - v) / (hi - lo || 1) * (H - 2 * pad - 60)
  const single = spec.data.length === 1
  const lines = spec.data.map(d => {
    const on = single || isAccented(d)
    const c = on ? (d.highlight ? 'var(--accent-highlight-mark)' : 'var(--protagonist)') : 'var(--chart-faint)'
    const wgt = on ? 500 : 400
    return `
      <line x1="${x0}" y1="${yOf(d.from)}" x2="${x1}" y2="${yOf(d.to)}" stroke="${c}" stroke-width="5"/>
      <circle cx="${x0}" cy="${yOf(d.from)}" r="10" fill="${c}"/>
      <circle cx="${x1}" cy="${yOf(d.to)}" r="10" fill="${c}"/>
      <text x="${x0 - 28}" y="${yOf(d.from) + 11}" text-anchor="end" font-size="34" font-weight="${wgt}"
            fill="${on ? 'var(--text-1)' : 'var(--text-3)'}" font-family="DM Sans">${d.from}${esc(unit)}</text>
      <text x="${x1 + 28}" y="${yOf(d.to) + 11}" font-size="34" font-weight="${wgt}"
            fill="${on ? 'var(--text-1)' : 'var(--text-3)'}" font-family="DM Sans">${d.to}${esc(unit)}</text>
      <text x="${x1 + 28}" y="${yOf(d.to) + 52}" font-size="24"
            fill="var(--text-3)" font-family="DM Sans">${esc(d.label)}</text>`
  })
  const axis = `
    <text x="${x0}" y="${H - 8}" text-anchor="middle" font-size="24" fill="var(--text-3)"
          font-family="DM Mono" letter-spacing="1">${esc(spec.from_label || 'BEFORE').toUpperCase()}</text>
    <text x="${x1}" y="${H - 8}" text-anchor="middle" font-size="24" fill="var(--text-3)"
          font-family="DM Mono" letter-spacing="1">${esc(spec.to_label || 'AFTER').toUpperCase()}</text>`
  return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">${lines.join('')}${axis}</svg>`
}

function beeswarmChart(spec) {
  // Distribution chart: one dot per community along x = signed % change.
  // Colour encodes a single group, not a named series — communities that got
  // cheaper carry the Navy protagonist ink; the rest stay muted. The eye reads
  // the mass, not the outliers. Size = transaction weight (sqrt-scaled).
  const W = 952, H = 600
  const padL = 24, padR = 24, cy = 250, yBase = 470
  const pts = spec.data.map(d => Array.isArray(d)
    ? { v: d[0], n: d[1], label: d[2] } : { v: d.value, n: d.weight, label: d.label })
  const vs = pts.map(p => p.v)
  let lo = Math.min(...vs, 0), hi = Math.max(...vs, 0)
  const span = (hi - lo) || 1
  lo -= span * 0.04; hi += span * 0.04
  const xOf = v => padL + (v - lo) / (hi - lo) * (W - padL - padR)
  const maxN = Math.max(...pts.map(p => p.n))
  const rOf = n => 6 + 20 * Math.sqrt(n / maxN)

  // Greedy vertical packing around the centreline — no overlap, symmetric spread.
  const placed = []
  const collide = (x, y, r) => placed.some(q => {
    const dx = x - q.x, dy = y - q.y
    const min = r + q.r + 2
    return dx * dx + dy * dy < min * min
  })
  for (const p of [...pts].sort((a, b) => a.v - b.v)) {
    p.x = xOf(p.v); p.r = rOf(p.n); p.y = cy
    if (collide(p.x, p.y, p.r)) {
      for (let off = 4; off < H; off += 4) {
        if (!collide(p.x, cy - off, p.r)) { p.y = cy - off; break }
        if (!collide(p.x, cy + off, p.r)) { p.y = cy + off; break }
      }
    }
    placed.push(p)
  }

  const dots = placed.map(p => {
    const fill = p.v < 0 ? 'var(--protagonist)' : 'var(--chart-faint)'
    return `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="${p.r.toFixed(1)}"
      fill="${fill}" fill-opacity="0.82" stroke="var(--bg)" stroke-width="1.5"/>`
  }).join('')
  // A few named communities, drawn on top with a leader, to make it concrete.
  const labels = placed.filter(p => p.label).map(p => {
    const above = p.y <= cy
    const ly = above ? Math.max(24, p.y - p.r - 16) : p.y + p.r + 30
    const y1 = above ? p.y - p.r : p.y + p.r
    const y2 = above ? ly + 8 : ly - 18
    return `<line x1="${p.x.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${p.x.toFixed(1)}" y2="${y2.toFixed(1)}"
        stroke="var(--text-3)" stroke-width="1"/>
      <text x="${p.x.toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="middle" font-size="22" font-weight="500"
        fill="var(--text-1)" font-family="DM Sans" stroke="var(--bg)" stroke-width="3" paint-order="stroke">${esc(p.label)}</text>`
  }).join('')

  // Zero line divides cheaper (left) from dearer (right); ticks from the domain,
  // direction cues at the ends, and the axis title centred (what the data is).
  const x0 = xOf(0)
  const suf = spec.x_suffix != null ? spec.x_suffix : '%'
  const tickMarks = niceTicks(lo, hi).filter(t => t >= lo && t <= hi).map(t =>
    `<text x="${xOf(t).toFixed(1)}" y="${yBase + 40}" text-anchor="middle" font-size="24"
      fill="var(--text-3)" font-family="DM Sans">${fmtTick(t, suf)}</text>`).join('')
  const zero = `<line x1="${x0.toFixed(1)}" y1="30" x2="${x0.toFixed(1)}" y2="${yBase}"
      stroke="var(--text-3)" stroke-width="1.5" stroke-dasharray="4,5"/>`
  const dir = spec.left_label === '' ? '' : `
    <text x="${padL}" y="${yBase + 84}" font-size="24" font-family="DM Mono" letter-spacing="1"
      fill="var(--text-3)">← ${axisTitle(spec.left_label || 'Cheaper')}</text>
    <text x="${W - padR}" y="${yBase + 84}" text-anchor="end" font-size="24" font-family="DM Mono"
      letter-spacing="1" fill="var(--text-3)">${axisTitle(spec.right_label || 'Dearer')} →</text>`
  const xTitle = spec.x_label ? `<text x="${W / 2}" y="${yBase + 84}" text-anchor="middle" font-size="22"
      fill="var(--text-3)" font-family="DM Mono" letter-spacing="1">${axisTitle(spec.x_label)}</text>` : ''
  return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
    ${zero}<line x1="${padL}" y1="${yBase}" x2="${W - padR}" y2="${yBase}"
      stroke="var(--chart-faint)" stroke-width="1"/>${dots}${tickMarks}${dir}${xTitle}${labels}</svg>`
}

function scatterChart(spec) {
  // Relationship chart: one dot per item, x vs y, size = weight. A restrained
  // muted field with a small set of labelled points carrying the Navy accent —
  // colour marks the points worth reading, not a series. An OLS trend line is
  // drawn only when the relationship is strong enough to be worth a line.
  const W = 952, H = 620, mL = 108, mR = 44, mT = 24, mB = 104
  const pts = spec.data.map(d => Array.isArray(d)
    ? { x: d[0], y: d[1], w: d[2], label: d[3], anchor: d[4], dy: d[5] }
    : d)
  const xs = pts.map(p => p.x), ys = pts.map(p => p.y), ws = pts.map(p => p.w)
  let xlo = Math.min(...xs), xhi = Math.max(...xs)
  let ylo = Math.min(...ys, 0), yhi = Math.max(...ys, 0)
  xlo -= (xhi - xlo) * 0.06; xhi += (xhi - xlo) * 0.04
  ylo -= (yhi - ylo) * 0.08; yhi += (yhi - ylo) * 0.06
  const PX = W - mL - mR, PY = H - mT - mB
  const xOf = v => mL + (v - xlo) / (xhi - xlo) * PX
  const yOf = v => mT + (yhi - v) / (yhi - ylo) * PY
  const maxW = Math.max(...ws)
  const rOf = w => 5 + 16 * Math.sqrt(w / maxW)

  // OLS fit + correlation; a line only earns its place at |r| ≥ 0.3.
  const n = pts.length
  const mx = xs.reduce((a, b) => a + b, 0) / n, my = ys.reduce((a, b) => a + b, 0) / n
  let sxy = 0, sxx = 0, syy = 0
  for (let i = 0; i < n; i++) { sxy += (xs[i] - mx) * (ys[i] - my); sxx += (xs[i] - mx) ** 2; syy += (ys[i] - my) ** 2 }
  const slope = sxy / sxx, intercept = my - slope * mx, r = sxy / Math.sqrt(sxx * syy)
  const trend = Math.abs(r) >= 0.3
    ? `<line x1="${xOf(xlo).toFixed(1)}" y1="${yOf(intercept + slope * xlo).toFixed(1)}"
        x2="${xOf(xhi).toFixed(1)}" y2="${yOf(intercept + slope * xhi).toFixed(1)}"
        stroke="var(--protagonist)" stroke-width="2.5" stroke-dasharray="2,7" stroke-linecap="round" opacity="0.55"/>`
    : ''

  const yZero = yOf(0)
  const zeroLine = `<line x1="${mL}" y1="${yZero.toFixed(1)}" x2="${W - mR}" y2="${yZero.toFixed(1)}"
      stroke="var(--chart-faint)" stroke-width="1.5"/>`

  // Axes: ticks computed from the data domain, titles supplied by the brief.
  const xSuf = spec.x_suffix || '', ySuf = spec.y_suffix || ''
  const yTicks = niceTicks(Math.min(...ys, 0), Math.max(...ys, 0)).filter(t => t >= ylo && t <= yhi).map(t =>
    `<text x="${mL - 16}" y="${(yOf(t) + 9).toFixed(1)}" text-anchor="end" font-size="24"
      fill="var(--text-3)" font-family="DM Sans">${fmtTick(t, ySuf)}</text>`).join('')
  const xTicks = niceTicks(Math.min(...xs), Math.max(...xs)).filter(t => t >= xlo && t <= xhi).map(t =>
    `<text x="${xOf(t).toFixed(1)}" y="${H - mB + 44}" text-anchor="middle" font-size="24"
      fill="var(--text-3)" font-family="DM Sans">${fmtTick(t, xSuf)}</text>`).join('')
  const xTitle = spec.x_label ? `<text x="${mL + PX / 2}" y="${H - 12}" text-anchor="middle" font-size="22"
      fill="var(--text-3)" font-family="DM Mono" letter-spacing="1">${axisTitle(spec.x_label)}</text>` : ''
  const cyT = mT + PY / 2
  const yTitle = spec.y_label ? `<text x="24" y="${cyT}" text-anchor="middle" font-size="22"
      fill="var(--text-3)" font-family="DM Mono" letter-spacing="1"
      transform="rotate(-90 24 ${cyT})">${axisTitle(spec.y_label)}</text>` : ''

  const dots = pts.map(p => {
    const on = Boolean(p.label)
    const fill = on ? 'var(--protagonist)' : 'var(--chart-faint)'
    const circle = `<circle cx="${xOf(p.x).toFixed(1)}" cy="${yOf(p.y).toFixed(1)}" r="${rOf(p.w).toFixed(1)}"
      fill="${fill}" fill-opacity="${on ? 0.9 : 0.4}" stroke="var(--bg)" stroke-width="1.25"/>`
    if (!on) return circle
    const r0 = rOf(p.w), side = p.anchor === 'end' ? -1 : 1
    const tx = xOf(p.x) + side * (r0 + 10)
    const ty = yOf(p.y) + 8 + (p.dy || 0)
    const label = `<text x="${tx.toFixed(1)}" y="${ty.toFixed(1)}" text-anchor="${p.anchor || 'start'}"
      font-size="24" font-weight="500" fill="var(--text-1)" font-family="DM Sans"
      stroke="var(--bg)" stroke-width="3" paint-order="stroke">${esc(p.label)}</text>`
    return circle + label
  }).join('')

  return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
    ${zeroLine}${trend}${yTicks}${xTicks}${xTitle}${yTitle}${dots}</svg>`
}

function tableChart(spec) {
  // Ranked table: recognisable rows a reader scans for names they know.
  // First column left (labels), the rest right-aligned (figures, mono).
  const W = 952, headerH = 66
  const cols = spec.columns, rows = spec.data, m = cols.length, n = rows.length
  const rowH = Math.min(104, Math.max(72, 860 / n))
  const H = headerH + n * rowH
  const xOf = j => j === 0 ? 6 : Math.round(W * (0.58 + 0.42 * j / (m - 1)))
  const anchor = j => j === 0 ? 'start' : 'end'
  const head = cols.map((c, j) =>
    `<text x="${xOf(j)}" y="40" text-anchor="${anchor(j)}" font-size="26"
       fill="var(--text-3)" font-family="DM Mono" letter-spacing="1">${esc(String(c).toUpperCase())}</text>`).join('')
  const hrule = `<line x1="0" y1="${headerH}" x2="${W}" y2="${headerH}" stroke="var(--text-3)" stroke-width="1.5"/>`
  const body = rows.map((r, i) => {
    const y = headerH + i * rowH + rowH * 0.62
    const cells = r.map((v, j) => {
      const isName = j === 0
      return `<text x="${xOf(j)}" y="${y}" text-anchor="${anchor(j)}"
        font-size="${isName ? 34 : 32}" font-weight="${isName ? 500 : 400}"
        fill="${isName ? 'var(--text-1)' : 'var(--text-2)'}"
        font-family="${isName ? 'DM Sans' : 'DM Mono'}">${esc(v)}</text>`
    }).join('')
    const rule = i < n - 1 ? `<line x1="0" y1="${headerH + (i + 1) * rowH}" x2="${W}" y2="${headerH + (i + 1) * rowH}" stroke="var(--chart-faint)" stroke-width="1"/>` : ''
    return cells + rule
  }).join('')
  return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">${head}${hrule}${body}</svg>`
}

const CHARTS = { bar: barChart, slope: slopeChart, beeswarm: beeswarmChart, scatter: scatterChart, table: tableChart }

// ── Concept slide — explanatory, not data: a vertical ladder of steps, or two
//    parallel ladders. No judgment; it carries an argument, not a figure. ───────
function ladder(steps) {
  return `<div class="ladder">` + steps.map((s, i) =>
    (i ? '<div class="ladder-link"></div>' : '') + `<div class="ladder-step">${esc(s)}</div>`
  ).join('') + `</div>`
}
function conceptBody(spec) {
  const title = spec.title ? `<div class="concept-title">${esc(spec.title)}</div>` : ''
  if (spec.columns) {
    const cols = spec.columns.map(c =>
      `<div class="concept-col"><div class="concept-col-head">${esc(c.label)}</div>${ladder(c.steps)}</div>`
    ).join('')
    return `<div class="slide-body concept">${title}<div class="concept-cols">${cols}</div></div>`
  }
  if (spec.ladder) return `<div class="slide-body concept">${title}${ladder(spec.ladder)}</div>`
  // Punchline: a headline conclusion + a line of plain-English support, no chart.
  const body = spec.body ? `<div class="concept-body">${esc(spec.body)}</div>` : ''
  return `<div class="slide-body concept concept--statement">${title}${body}</div>`
}

// ── Slides ────────────────────────────────────────────────────────────────────

function hookSlide(hook, n) {
  // Cover: always Navy, full wordmark lower-right.
  // hook.number (new format) or legacy BRIEF.hook_stat both trigger the stat layout.
  const newStat    = hook.number
  const legacyStat = BRIEF.hook_stat
  const hasStat    = Boolean(newStat || legacyStat)
  const statHtml   = newStat
    ? `<div class="hook-number">${esc(newStat)}</div>
       ${hook.number_label ? `<div class="hook-number-label">${esc(hook.number_label)}</div>` : ''}`
    : legacyStat
      ? `<div class="hook-stat">${esc(legacyStat)}</div>`
      : ''
  return `<section class="slide slide--hook dj-theme-navy${hasStat ? ' has-stat' : ''}">
    ${statHtml}
    <div class="statement">${pop(hook.headline)}</div>
    ${chrome(n, 'navy', { wordmark: true })}
  </section>`
}

function puzzleSlide(puzzle, n) {
  // Parchment interior: the question created by the hook, and the intuitive
  // assumption the beats will overturn.
  return `<section class="slide slide--puzzle">
    <div class="puzzle-question">${esc(puzzle.question)}</div>
    <div class="puzzle-assumption-label">Common assumption</div>
    <div class="puzzle-assumption">${esc(puzzle.misconception)}</div>
    ${chrome(n, 'parchment', { monogram: true })}
  </section>`
}

function contextSlide(text, n) {
  // Always Alabaster: the series premise, expanded from the eyebrow —
  // what the series tracks and its event anchor, before the numbers.
  return `<section class="slide slide--context dj-theme-alabaster">
    <div class="context-kicker">The series</div>
    <div class="statement">${esc(text)}</div>
    ${chrome(n, 'alabaster', { monogram: true })}
  </section>`
}

function numberBody(spec) {
  return `
    <div class="slide-body slide-body--center">
      <div class="metric">${esc(spec.value)}</div>
      <div class="label">${esc(spec.label)}</div>
      ${spec.delta ? `<div class="delta">${esc(spec.delta)}</div>` : ''}
    </div>
    ${judgment(spec.judgment)}`
}

function chartBody(spec) {
  const chart = CHARTS[spec.kind]
  // Hero-chart number — the one honey-bronze figure that carries the finding,
  // set beside the takeaway so it pops without competing with the plot.
  const stat = spec.stat
    ? `<div class="chart-stat"><span class="chart-stat-num">${esc(spec.stat)}</span>${
        spec.stat_label ? `<span class="chart-stat-label">${esc(spec.stat_label)}</span>` : ''}</div>`
    : ''
  // The takeaway sits at the top — the chart below proves it. The reader was
  // already told what the data is on the preceding setup slide, so no title here.
  return `
    <div class="slide-body">
      <div class="chart-head">${judgment(spec.judgment)}${stat}</div>
      <div class="chart-frame">${chart(spec)}</div>
    </div>`
}

function setupSlide(spec, n) {
  // Primer that precedes every chart: what the data is, before the plot. Keeps
  // the chart slide itself to one takeaway. Falls back to the chart title.
  return `<section class="slide slide--setup">
    <div class="setup-kicker">The data</div>
    <div class="statement">${esc(spec.setup || spec.title)}</div>
    ${chrome(n, 'parchment', { monogram: true, takeaway: true })}
  </section>`
}

function dataSlide(spec, n) {
  const theme = spec.theme || 'parchment'
  const kind = spec.type || spec.kind
  const body = kind === 'concept' ? conceptBody(spec)
    : kind === 'big_number' ? numberBody(spec)
    : chartBody(spec)
  const cls = kind === 'concept' ? 'slide--concept'
    : kind === 'big_number' ? 'slide--number' : 'slide--chart'
  return `<section class="slide ${cls} ${THEME_CLASS[theme]}">
    ${body}
    ${chrome(n, theme, { monogram: true, takeaway: kind !== 'concept' })}
  </section>`
}

function soWhatSlide(text, n) {
  // Always Carbon: what decision or action these numbers inform.
  // (The brand never says "actionable insight" — this slide is the plain-
  // English version of that job.)
  return `<section class="slide slide--sowhat dj-theme-carbon">
    <div class="sowhat-kicker">So what?</div>
    <div class="statement">${pop(text)}</div>
    ${chrome(n, 'carbon', { monogram: true })}
  </section>`
}

function ctaSlide(cta, n) {
  // Content-driven: a concrete next piece when known, else directional
  // series-rotation copy — never a bare follow-ask.
  const theme = (cta && cta.theme) || 'navy'
  const line = (cta && cta.next)
    ? cta.next
    : `The ${BRIEF.series} series continues — ${BRIEF.sector.toLowerCase()} is one chapter.`
  // Clean close: the conclusion + where to follow. Source/method live on the
  // appendix that follows, so nothing boring competes with the call to action.
  return `<section class="slide slide--cta ${THEME_CLASS[theme]}">
    <div class="statement">${esc(line)}</div>
    <div class="cta-urls">
      <a class="cta-url" href="https://thedatajockey.substack.com">thedatajockey.substack.com</a>
      <a class="cta-url" href="https://www.thedatajockey.com">www.thedatajockey.com</a>
    </div>
    ${chrome(n, theme, { wordmark: true })}
  </section>`
}

function appendixSlide(n) {
  // Always Alabaster, always last: the deck's source, calculations and metric
  // definitions — the boring-but-necessary trace-back, off the CTA.
  const notes = Array.isArray(BRIEF.notes) ? BRIEF.notes : (BRIEF.notes ? [BRIEF.notes] : [])
  const noteEls = notes.map(x => `<li>${esc(x)}</li>`).join('')
  return `<section class="slide slide--appendix dj-theme-alabaster">
    <div class="appendix-kicker">Sources &amp; method</div>
    <div class="appendix-source">${esc(BRIEF.source)}</div>
    ${noteEls ? `<ul class="appendix-notes">${noteEls}</ul>` : ''}
    ${chrome(n, 'alabaster', { monogram: true })}
  </section>`
}

// Build the deck as a flat list of slide thunks, then number them in order —
// a chart beat expands to [setup, chart], so indices aren't fixed up front.
const seq = [n => hookSlide(BRIEF.hook, n)]
if (HAS_PUZZLE)  seq.push(n => puzzleSlide(BRIEF.puzzle, n))
if (HAS_CONTEXT) seq.push(n => contextSlide(BRIEF.context, n))
for (const b of BRIEF.beats) {
  if ((b.type || b.kind) === 'chart') seq.push(n => setupSlide(b, n))
  seq.push(n => dataSlide(b, n))
}
seq.push(n => dataSlide(BRIEF.synthesis, n))
seq.push(n => soWhatSlide(BRIEF.so_what, n))
seq.push(n => ctaSlide(BRIEF.cta, n))
seq.push(n => appendixSlide(n))
document.body.innerHTML = seq.map((fn, i) => fn(i + 1)).join('\n')
