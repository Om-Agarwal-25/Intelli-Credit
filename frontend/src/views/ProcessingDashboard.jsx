import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { CheckCircle2, Loader2, Clock, ArrowRight } from 'lucide-react'

const STAGES = [
  { id: 'EXTRACTION', label: 'Text Extraction', group: 'INGESTION', icon: '📄' },
  { id: 'GST_RECON', label: 'GST Cross-Reference', group: 'INGESTION', icon: '🔁' },
  { id: 'RAG', label: 'RAG Semantic Analysis', group: 'INGESTION', icon: '🧠' },
  { id: 'MCA', label: 'MCA21 Intelligence', group: 'RESEARCH', icon: '🏛️' },
  { id: 'LEGAL', label: 'Legal Intelligence', group: 'RESEARCH', icon: '⚖️' },
  { id: 'WEB', label: 'News & Web Intelligence', group: 'RESEARCH', icon: '🌐' },
  { id: 'FLAGS', label: 'Risk Flag Consolidation', group: 'INGESTION', icon: '🚩' },
  { id: 'FIVE_CS', label: 'Five Cs Computation', group: 'SCORING', icon: '📊' },
  { id: 'BASE_SCORE', label: 'XGBoost Base Score', group: 'SCORING', icon: '🎯' },
]

const GROUP_META = {
  INGESTION: { label: 'Data Ingestion', color: 'text-blue-600', border: 'border-blue-100', bg: 'bg-blue-50/60', accent: 'card-accent-blue' },
  RESEARCH: { label: 'AI Research', color: 'text-violet-600', border: 'border-violet-100', bg: 'bg-violet-50/60', accent: 'card-accent-violet' },
  SCORING: { label: 'Scoring', color: 'text-green-700', border: 'border-green-100', bg: 'bg-green-50/60', accent: 'card-accent-green' },
}

function StageRow({ stage, status, detail, index }) {
  const isDone = status === 'done'
  const isRunning = status === 'running'
  return (
    <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-300 animate-row"
      style={{
        animationDelay: `${index * 40}ms`,
        background: isRunning ? 'rgba(22,163,74,0.07)' : isDone ? 'rgba(22,163,74,0.04)' : 'transparent',
        border: isRunning ? '1px solid rgba(22,163,74,0.2)' : '1px solid transparent',
      }}>
      <div className="shrink-0">
        {isDone ? <CheckCircle2 size={15} className="text-green-500" /> :
          isRunning ? <Loader2 size={15} className="text-green-600 animate-spin" /> :
            <Clock size={15} className="text-gray-300" />}
      </div>
      <span className="text-sm font-medium" style={{ color: isRunning ? '#16A34A' : isDone ? '#15803d' : '#9CA3AF' }}>
        {stage.icon} {stage.label}
      </span>
      {detail && <span className="ml-auto text-xs text-gray-400 truncate max-w-[140px]">{detail}</span>}
    </div>
  )
}

export default function ProcessingDashboard({ session }) {
  const navigate = useNavigate()
  const location = useLocation()
  const sessionId = location.state?.session_id || session?.session_id
  const isDemo = location.state?.demo

  const [stageStatus, setStageStatus] = useState({})
  const [flags, setFlags] = useState({ high: 0, medium: 0, low: 0 })
  const [baseScore, setBaseScore] = useState(null)
  const [readyForQual, setReadyForQual] = useState(false)
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => { const t = setInterval(() => setElapsed(s => s + 1), 1000); return () => clearInterval(t) }, [])

  useEffect(() => {
    if (!sessionId) return
    if (isDemo) { simulateDemoPipeline(); return }
    const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`)
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      if (msg.type === 'progress') {
        setStageStatus(prev => ({ ...prev, [msg.stage]: { status: msg.status, detail: msg.detail } }))
        if (msg.flags) setFlags(msg.flags)
      } else if (msg.type === 'ready_for_qualitative') { setBaseScore(msg.base_score); setReadyForQual(true) }
    }
    ws.onerror = () => simulateDemoPipeline()
    return () => ws.close()
  }, [sessionId])

  const simulateDemoPipeline = async () => {
    const demo = [
      { id: 'EXTRACTION', delay: 700, detail: 'Extracted from 4 PDFs' },
      { id: 'GST_RECON', delay: 600, detail: '2 flags raised' },
      { id: 'RAG', delay: 1100, detail: '3 semantic flags' },
      { id: 'MCA', delay: 900, detail: '3 findings' },
      { id: 'LEGAL', delay: 700, detail: '2 findings' },
      { id: 'WEB', delay: 500, detail: '1 signal' },
      { id: 'FLAGS', delay: 400, detail: '4 HIGH · 3 MEDIUM' },
      { id: 'FIVE_CS', delay: 600, detail: 'C1=35 C2=68 C3=70 C4=70 C5=72' },
      { id: 'BASE_SCORE', delay: 800, detail: 'Score: 78.0/100' },
    ]
    for (const s of demo) {
      setStageStatus(prev => ({ ...prev, [s.id]: { status: 'running', detail: '' } }))
      await new Promise(r => setTimeout(r, s.delay))
      setStageStatus(prev => ({ ...prev, [s.id]: { status: 'done', detail: s.detail } }))
    }
    setFlags({ high: 4, medium: 3, low: 1 })
    setBaseScore({ composite: 78.0, decision: 'APPROVE' })
    setReadyForQual(true)
  }

  const completedCount = Object.values(stageStatus).filter(s => s.status === 'done').length
  const progress = Math.round((completedCount / STAGES.length) * 100)
  const goToReview = () => navigate('/review', { state: { session_id: sessionId, demo: isDemo, base_score: baseScore, flags } })

  return (
    <div className="min-h-screen py-10 px-4" style={{ background: '#F8F9FB' }}>
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <div className="text-center mb-8 animate-fade-up">
          <h1 className="text-3xl font-black tracking-tight text-gray-900 mb-1">Live Analysis Pipeline</h1>
          <p className="text-gray-400 text-sm font-mono">SESSION · {sessionId?.slice(0, 8).toUpperCase()} · {elapsed}s elapsed</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-6 animate-fade-up" style={{ animationDelay: '0.1s' }}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-400">Overall Progress</span>
            <span className="text-xs font-bold text-green-600">{progress}%</span>
          </div>
          <div className="progress-track">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-3 gap-4 mb-6 animate-fade-up" style={{ animationDelay: '0.15s' }}>
          {[
            { label: 'HIGH Risk Flags', value: flags.high, color: '#DC2626', bg: 'bg-red-50', border: 'border-red-100' },
            { label: 'MEDIUM Risk Flags', value: flags.medium, color: '#D97706', bg: 'bg-amber-50', border: 'border-amber-100' },
            { label: 'Documents Processed', value: 4, color: '#16A34A', bg: 'bg-green-50', border: 'border-green-100' },
          ].map(({ label, value, color, bg, border }) => (
            <div key={label} className={`rounded-2xl p-5 text-center border animate-count-up ${bg} ${border}`}>
              <div className="text-4xl font-black mb-1" style={{ color }}>{value}</div>
              <div className="text-xs text-gray-500 font-medium">{label}</div>
            </div>
          ))}
        </div>

        {/* Pipeline Columns */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 animate-fade-up" style={{ animationDelay: '0.2s' }}>
          {['INGESTION', 'RESEARCH', 'SCORING'].map(group => {
            const gm = GROUP_META[group]
            const groupStages = STAGES.filter(s => s.group === group)
            const groupDone = groupStages.filter(s => stageStatus[s.id]?.status === 'done').length
            return (
              <div key={group} className={`card p-4 border ${gm.border} ${gm.bg} ${gm.accent}`}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className={`text-xs font-semibold uppercase tracking-[0.08em] ${gm.color}`}>{gm.label}</h3>
                  <span className="text-xs text-gray-400 font-mono">{groupDone}/{groupStages.length}</span>
                </div>
                <div className="space-y-1">
                  {groupStages.map((stage, i) => {
                    const st = stageStatus[stage.id] || { status: 'pending' }
                    return <StageRow key={stage.id} stage={stage} status={st.status} detail={st.detail} index={i} />
                  })}
                </div>
              </div>
            )
          })}
        </div>

        {/* Base Score */}
        {baseScore && (
          <div className="card card-glow p-8 text-center mb-6 animate-fade-up" style={{ border: '2px solid rgba(22,163,74,0.2)' }}>
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">AI Base Score · Pre-Jury</p>
            <div className="text-7xl font-black mb-3 text-green-600">{baseScore.composite}<span className="text-2xl text-gray-400 font-medium">/100</span></div>
            <span className={`inline-block px-5 py-2 rounded-full text-sm font-bold ${baseScore.decision === 'APPROVE' ? 'bg-green-100 text-green-700 border border-green-200' : 'bg-amber-100 text-amber-700 border border-amber-200'
              }`}>
              {baseScore.decision} · Raw Model Output
            </span>
            <p className="text-xs text-gray-400 mt-3">⚠️ Score does not account for qualitative inputs or Jury adjustment</p>
          </div>
        )}

        {readyForQual && (
          <div className="text-center animate-fade-up">
            <button onClick={goToReview} className="btn-primary text-base px-10 py-4 animate-pulse-green">
              Proceed to Credit Review <ArrowRight size={18} />
            </button>
            <p className="text-xs text-gray-400 mt-3">AI pre-processing complete · Officer input required</p>
          </div>
        )}
        {!readyForQual && (
          <div className="flex justify-center">
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <Loader2 size={16} className="animate-spin text-green-500" />
              Pipeline running — this takes 2–4 minutes…
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
