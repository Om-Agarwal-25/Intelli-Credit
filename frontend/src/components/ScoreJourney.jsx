/**
 * ScoreJourney — Animated horizontal bar chart showing score at each jury stage
 */
export default function ScoreJourney({ baseScore, afterProsecution, afterDefence, juryScore }) {
  const stages = [
    { label: 'XGBoost Base Score', score: baseScore, color: '#16A34A', icon: '🎯' },
    { label: 'After Prosecution', score: Math.round(afterProsecution * 10) / 10, color: '#DC2626', icon: '🔴' },
    { label: 'After Defence', score: Math.round(afterDefence * 10) / 10, color: '#22C55E', icon: '🟢' },
    { label: 'Final Jury Score', score: juryScore, color: '#D97706', icon: '⚖️' },
  ]

  return (
    <div className="card p-6 mt-4 bg-white">
      <h3 className="text-xs font-black text-gray-400 uppercase tracking-widest mb-5">📈 Credit Score Journey</h3>
      <div className="space-y-4">
        {stages.map(({ label, score, color, icon }, i) => (
          <div key={i} className="flex items-center gap-4">
            <div className="w-40 text-right shrink-0">
              <span className="text-xs text-gray-500 font-semibold">{icon} {label}</span>
            </div>
            <div className="flex-1 h-7 rounded relative overflow-hidden" style={{ background: '#EDF2F7' }}>
              {/* Approve threshold */}
              <div className="absolute top-0 bottom-0 border-l border-dashed border-green-400/60 z-10" style={{ left: '65%' }} />
              {/* Conditional threshold */}
              <div className="absolute top-0 bottom-0 border-l border-dashed border-amber-400/60 z-10" style={{ left: '50%' }} />
              <div className="h-full rounded animate-bar-fill flex items-center justify-end pr-3"
                style={{ width: `${Math.max(6, score)}%`, background: `linear-gradient(90deg, ${color}99, ${color})`, animationDelay: `${i * 180}ms` }}>
                <span className="text-xs font-black text-white">{score}</span>
              </div>
            </div>
            {i > 0 ? (
              <div className={`w-12 text-xs font-black text-right shrink-0 ${score > stages[i - 1].score ? 'text-green-600' : score < stages[i - 1].score ? 'text-red-500' : 'text-gray-400'
                }`}>
                {score > stages[i - 1].score ? '+' : ''}{Math.round((score - stages[i - 1].score) * 10) / 10}
              </div>
            ) : <div className="w-12" />}
          </div>
        ))}
      </div>
      <div className="flex gap-6 mt-4 text-xs text-gray-400">
        <span className="flex items-center gap-1.5"><span className="w-4 border-t border-dashed border-green-400" /> Approve ≥65</span>
        <span className="flex items-center gap-1.5"><span className="w-4 border-t border-dashed border-amber-400" /> Conditional ≥50</span>
      </div>
    </div>
  )
}
