/**
 * FiveCsGauges — Animated SVG circular gauges for each credit dimension
 */
const C_CONFIG = {
  C1: { label: 'Character', description: 'Integrity & Governance', color: '#DC2626' },
  C2: { label: 'Capacity', description: 'Revenue & Cash Flow', color: '#16A34A' },
  C3: { label: 'Capital', description: 'Net Worth & Leverage', color: '#7C3AED' },
  C4: { label: 'Collateral', description: 'Asset Coverage', color: '#EA580C' },
  C5: { label: 'Conditions', description: 'Sector & Macro', color: '#0891B2' },
}

function getScoreColor(v) {
  if (v < 40) return '#DC2626'
  if (v < 60) return '#D97706'
  return null
}

function Gauge({ value, color, label, description }) {
  const r = 38
  const circ = 2 * Math.PI * r
  const fill = getScoreColor(value) || color
  const offset = circ - (value / 100) * circ

  return (
    <div className="tooltip-root flex flex-col items-center py-3 px-2 rounded-xl transition-all duration-200 hover:bg-slate-50 cursor-default">
      <div className="relative">
        <svg width="88" height="88" className="-rotate-90">
          <circle cx="44" cy="44" r={r} fill="none" stroke="#EEF2F7" strokeWidth="7" />
          <circle cx="44" cy="44" r={r} fill="none" stroke={fill} strokeWidth="7"
            strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round"
            className="gauge-arc"
            style={{ '--target-offset': offset, filter: `drop-shadow(0 2px 6px ${fill}66)` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-lg font-black leading-none text-gray-800">{value.toFixed(0)}</span>
          <span className="text-[9px] text-gray-400 font-medium">/100</span>
        </div>
      </div>
      <p className="text-xs font-bold text-gray-700 mt-2">{label}</p>
      <p className="text-[10px] text-gray-400 text-center">{description}</p>
      <div className="tooltip-box">{label}: {value}/100 — {description}</div>
    </div>
  )
}

export default function FiveCsGauges({ five_cs }) {
  const composite = five_cs?.composite || 65
  return (
    <div className="card p-4">
      <h3 className="text-xs font-black text-gray-400 uppercase tracking-widest mb-4">📊 Five Cs Score Card</h3>
      <div className="grid grid-cols-1 gap-1">
        {Object.entries(C_CONFIG).map(([key, cfg]) => (
          <Gauge key={key} value={five_cs?.[key] || 70} color={cfg.color} label={cfg.label} description={cfg.description} />
        ))}
      </div>
      <div className="mt-4 p-4 rounded-xl text-center bg-slate-50 border border-slate-200">
        <p className="text-xs text-gray-400 font-semibold mb-1">Composite Score</p>
        <p className="text-3xl font-black" style={{ color: composite < 50 ? '#DC2626' : composite < 65 ? '#D97706' : '#16A34A' }}>
          {composite.toFixed(1)}<span className="text-base font-medium text-gray-400">/100</span>
        </p>
      </div>
    </div>
  )
}
