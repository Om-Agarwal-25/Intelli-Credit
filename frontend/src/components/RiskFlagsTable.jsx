/**
 * RiskFlagsTable — Filterable, expandable risk flag list
 */
import { useState } from 'react'
import { AlertTriangle, AlertCircle, Info, ChevronDown, ChevronUp } from 'lucide-react'

const SEVERITY_META = {
  HIGH: { icon: AlertTriangle, border: 'border-l-red-400', bg: 'bg-red-50/50 hover:bg-red-50', dot: '#EF4444' },
  MEDIUM: { icon: AlertCircle, border: 'border-l-amber-400', bg: 'bg-amber-50/50 hover:bg-amber-50', dot: '#F59E0B' },
  LOW: { icon: Info, border: 'border-l-green-400', bg: 'bg-green-50/50 hover:bg-green-50', dot: '#22C55E' },
}

function FlagRow({ flag, index }) {
  const [expanded, setExpanded] = useState(false)
  const meta = SEVERITY_META[flag.severity] || SEVERITY_META.LOW
  const Icon = meta.icon

  return (
    <div className={`border-b border-gray-50 border-l-4 ${meta.border} ${meta.bg} cursor-pointer transition-colors duration-150 animate-row`}
      style={{ animationDelay: `${index * 35}ms` }}
      onClick={() => setExpanded(e => !e)}>
      <div className="flex items-center gap-3 px-4 py-3">
        <Icon size={13} style={{ color: meta.dot }} className="shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-bold text-gray-800">{flag.flag_type?.replace(/_/g, ' ')}</span>
            <span className={`badge-${flag.severity}`}>{flag.severity}</span>
            {flag.five_c_pillar && (
              <span className="text-[10px] px-1.5 py-0.5 rounded font-bold bg-green-100 text-green-700 border border-green-200">
                {flag.five_c_pillar}
              </span>
            )}
          </div>
          {!expanded && <p className="text-xs text-gray-400 truncate mt-0.5">{flag.evidence_snippet}</p>}
        </div>
        {expanded ? <ChevronUp size={13} className="text-gray-300 shrink-0" /> : <ChevronDown size={13} className="text-gray-300 shrink-0" />}
      </div>
      {expanded && (
        <div className="px-4 pb-3 ml-7">
          <p className="text-xs text-gray-500 leading-5 mb-1.5">{flag.evidence_snippet}</p>
          {flag.source_document && <p className="text-xs text-gray-400">📄 {flag.source_document}</p>}
        </div>
      )}
    </div>
  )
}

export default function RiskFlagsTable({ flags = [] }) {
  const [filter, setFilter] = useState('ALL')
  const counts = { HIGH: 0, MEDIUM: 0, LOW: 0 }
  flags.forEach(f => { if (counts[f.severity] !== undefined) counts[f.severity]++ })
  const filtered = filter === 'ALL' ? flags : flags.filter(f => f.severity === filter)

  return (
    <div className="card overflow-hidden flex flex-col" style={{ maxHeight: '580px' }}>
      <div className="px-4 py-3 border-b border-gray-50 flex items-center justify-between flex-wrap gap-2 shrink-0 bg-white">
        <h3 className="text-xs font-black text-gray-400 uppercase tracking-widest">🚩 Risk Flags · {flags.length} total</h3>
        <div className="flex gap-1.5">
          {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map(sev => {
            const count = sev === 'ALL' ? flags.length : counts[sev]
            const dotColor = sev === 'HIGH' ? '#EF4444' : sev === 'MEDIUM' ? '#F59E0B' : sev === 'LOW' ? '#22C55E' : 'transparent'
            return (
              <button key={sev} onClick={() => setFilter(sev)}
                className={`flex items-center gap-1 text-xs px-2.5 py-1 rounded-lg font-semibold transition-all duration-150 ${filter === sev ? 'bg-gray-800 text-white' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                  }`}>
                {sev !== 'ALL' && <span className="w-1.5 h-1.5 rounded-full" style={{ background: dotColor }} />}
                {sev} {count > 0 && <span className="opacity-60">({count})</span>}
              </button>
            )
          })}
        </div>
      </div>
      <div className="overflow-y-auto flex-1 bg-white">
        {filtered.length === 0 && <div className="p-8 text-center text-gray-400 text-sm">No flags for selected filter.</div>}
        {filtered.map((flag, i) => <FlagRow key={i} flag={flag} index={i} />)}
      </div>
    </div>
  )
}
