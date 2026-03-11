import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import JuryDeliberationLog from '../components/JuryDeliberationLog'
import ScoreJourney from '../components/ScoreJourney'
import { Download, RefreshCw, Loader2, TrendingDown } from 'lucide-react'

const DEMO_JURY = {
  base_score: 78.0, jury_score: 51.0, net_delta: -27, prosecution_delta: -35, defence_delta: 12, qualitative_delta: 0, jury_decision: 'CONDITIONAL',
  five_cs: { C1: 35, C2: 68, C3: 70, C4: 70, C5: 72 },
  prosecution: {
    prosecution_findings: [
      { finding_id: 'P1', finding_text: 'Director K. Mehta (DIN 07284531) disqualified under Section 164(2) — company running under nominee director.', five_c_pillar: 'C1', score_delta: -15, evidence_source: 'MCA21 · DIN 07284531', severity: 'HIGH' },
      { finding_id: 'P2', finding_text: 'Active NCLT petition and undisclosed e-Courts litigation contradicts self-declaration of no pending litigation.', five_c_pillar: 'C1', score_delta: -12, evidence_source: 'e-Courts Pune · NCLT Mumbai', severity: 'HIGH' },
      { finding_id: 'P3', finding_text: 'Going-concern qualification on page 34 combined with ₹8.4 Cr contingent liability creates sustainability doubt.', five_c_pillar: 'C2', score_delta: -8, evidence_source: 'Annual Report FY24 · Note 31', severity: 'MEDIUM' },
    ], total_prosecution_delta: -35,
  },
  defence: {
    defence_findings: [
      { finding_id: 'D1', finding_text: 'Revenue verified genuine — GST-to-bank match 94% over 24 months confirms ₹340 Cr turnover.', five_c_pillar: 'C2', score_delta: 5, evidence_source: 'GST Returns / Bank Statement FY24', confidence: 'HIGH' },
      { finding_id: 'D2', finding_text: 'DSCR of 1.6x comfortably above RBI minimum 1.25x threshold.', five_c_pillar: 'C2', score_delta: 4, evidence_source: 'Annual Report FY24 — Cash Flow', confidence: 'HIGH' },
      { finding_id: 'D3', finding_text: '18% YoY revenue growth outperforms sector average of 11%.', five_c_pillar: 'C2', score_delta: 3, evidence_source: 'Annual Report / CRISIL Sector', confidence: 'MEDIUM' },
    ], total_defence_delta: 12,
  },
  verdict: {
    accepted_prosecution_findings: ['P1', 'P2', 'P3'], accepted_defence_findings: ['D1', 'D2', 'D3'],
    decisive_factors: ['DIN disqualification of Director K. Mehta is a categorical RBI regulatory violation.', 'Undisclosed NCLT + e-Courts litigation damages borrower credibility fundamentally.', 'Genuine revenue and healthy DSCR support reduced conditional exposure rather than outright rejection.'],
    final_recommendation: 'CONDITIONAL', recommended_loan_amount_cr: 35, recommended_interest_rate_pct: 12.5, loan_tenor_months: 60,
    conditions: ['DIN regularisation for Director K. Mehta within 90 days of sanction', 'Resolution of NCLT Case IB/1234/MB/2024 before first disbursement', 'NOC from NHAI regarding project delay penalty', 'Additional collateral cover ≥1.5x maintained throughout tenure'],
    confidence_band_low_cr: 30, confidence_band_high_cr: 40,
    primary_reason: 'C1 Character failure (disqualified director, undisclosed litigation) decisive per RBI guidelines.',
    verdict_rationale: 'Vardhaman Infra demonstrates genuine business activity with verified revenues and healthy DSCR. However, the disqualified director and deliberate non-disclosure of active litigation constitute fundamental character concerns. A conditional approval at ₹35 Cr with mandatory regularisation conditions balances the commercial opportunity against fiduciary risk.',
  },
}

const DECISION_STYLE = {
  APPROVE: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700', pill: 'bg-green-100 text-green-700 border-green-200', label: '✅ APPROVED', dot: '#16A34A' },
  CONDITIONAL: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', pill: 'bg-amber-100 text-amber-700 border-amber-200', label: '⚠️ CONDITIONAL APPROVAL', dot: '#D97706' },
  REJECT: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', pill: 'bg-red-100 text-red-700 border-red-200', label: '❌ REJECTED', dot: '#DC2626' },
}

export default function JuryDecision({ session }) {
  const location = useLocation()
  const navigate = useNavigate()
  const sessionId = location.state?.session_id || session?.session_id
  const isDemo = location.state?.demo

  const [juryResult, setJuryResult] = useState(null)
  const [isDownloading, setIsDownloading] = useState(false)
  const [isLoading, setIsLoading] = useState(!isDemo)

  useEffect(() => {
    if (isDemo) { setTimeout(() => setJuryResult(DEMO_JURY), 600); return }
    const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`)
    ws.onmessage = (e) => { const msg = JSON.parse(e.data); if (msg.type === 'jury_complete') { setJuryResult(msg.jury_result); setIsLoading(false) } }
    ws.onerror = () => { setJuryResult(DEMO_JURY); setIsLoading(false) }
    const poll = setInterval(async () => {
      try { const data = await (await fetch(`/api/sessions/${sessionId}/results`)).json(); if (data.jury_result) { setJuryResult(data.jury_result); setIsLoading(false); clearInterval(poll) } } catch { }
    }, 2000)
    return () => { ws.close(); clearInterval(poll) }
  }, [sessionId, isDemo])

  const downloadCAM = async () => {
    setIsDownloading(true)
    try { await fetch(`/api/sessions/${sessionId}/cam`, { method: 'POST' }); window.open(`/api/sessions/${sessionId}/cam/download`, '_blank') }
    catch { alert('CAM download requires backend. Run: python run.py') }
    setIsDownloading(false)
  }

  if (!juryResult && isLoading) return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-5" style={{ background: '#F8F9FB' }}>
      <div className="w-20 h-20 rounded-full border-4 border-green-100 border-t-green-500 animate-spin" />
      <div className="text-center">
        <p className="font-bold text-lg text-gray-800">AI Jury deliberating…</p>
        <p className="text-sm text-gray-400 mt-1">Prosecutor → Defender → Judge → Verdict</p>
      </div>
    </div>
  )

  if (!juryResult) return null

  const verdict = juryResult.verdict || {}
  const rec = verdict.final_recommendation || juryResult.jury_decision || 'CONDITIONAL'
  const amount = verdict.recommended_loan_amount_cr || 35
  const rate = verdict.recommended_interest_rate_pct || 12.5
  const tenor = verdict.loan_tenor_months || 60
  const ds = DECISION_STYLE[rec] || DECISION_STYLE.CONDITIONAL

  const afterProsecution = juryResult.base_score + (juryResult.prosecution_delta || 0)
  const afterDefence = afterProsecution + (juryResult.defence_delta || 0)

  return (
    <div className="min-h-screen py-10 px-4" style={{ background: '#F8F9FB' }}>
      <div className="max-w-6xl mx-auto">

        <div className="flex items-start justify-between mb-8 animate-fade-up flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-black tracking-tight text-gray-900">Jury Verdict & Final Decision</h1>
            <p className="text-gray-400 text-sm mt-1 font-mono">SESSION · {sessionId?.slice(0, 8).toUpperCase()?.replace('DEMO-', 'DEMO ')}</p>
          </div>
          <div className="flex gap-3">
            <button onClick={downloadCAM} disabled={isDownloading} className="btn-ghost text-sm">
              {isDownloading ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />} Download CAM (.docx)
            </button>
            <button onClick={() => navigate('/')} className="btn-secondary text-sm">
              <RefreshCw size={14} /> New Application
            </button>
          </div>
        </div>

        {/* Before / After */}
        <div className="grid grid-cols-2 gap-4 mb-6 animate-fade-up" style={{ animationDelay: '0.1s' }}>
          <div className="card p-8 text-center" style={{ background: '#FFF8F8', borderLeft: '3px solid #FCA5A5' }}>
            <p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">Before Jury</p>
            <div className="text-6xl font-black mb-3 text-gray-700">{juryResult.base_score}</div>
            <span className="inline-block px-4 py-1.5 rounded-full text-xs font-bold bg-green-100 text-green-700 border border-green-200">APPROVE · Raw Model</span>
            <p className="text-xs text-red-500 mt-3 flex items-center justify-center gap-1">
              <TrendingDown size={11} /> Without Jury: ₹60 Cr disbursed at full risk
            </p>
          </div>
          <div className={`card card-glow p-8 text-center border-2 ${ds.border} ${ds.bg}`} style={{ borderLeft: '3px solid #16A34A' }}>
            <p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">After Jury</p>
            <div className="text-6xl font-black mb-3 text-gray-800">{juryResult.jury_score}</div>
            <span className={`inline-block px-4 py-1.5 rounded-full text-xs font-bold border ${ds.pill}`}>{ds.label}</span>
            <p className="text-xs text-gray-400 mt-3">₹{amount} Cr conditional · DIN regularisation required</p>
          </div>
        </div>

        <div className="animate-fade-up" style={{ animationDelay: '0.15s' }}>
          <ScoreJourney baseScore={juryResult.base_score} afterProsecution={afterProsecution} afterDefence={afterDefence} juryScore={juryResult.jury_score} />
        </div>

        <div className="animate-fade-up" style={{ animationDelay: '0.2s' }}>
          <JuryDeliberationLog prosecution={juryResult.prosecution} defence={juryResult.defence} verdict={verdict} />
        </div>

        {/* Final Decision */}
        <div className="mt-6 rounded-2xl p-8 animate-fade-up border border-green-100"
          style={{ animationDelay: '0.25s', background: 'linear-gradient(135deg, #F0FDF4 0%, #ECFDF5 100%)', boxShadow: '0 4px 16px rgba(0,0,0,0.06)' }}>
          <div className="flex items-center gap-2 mb-6">
            <span className="w-2 h-2 rounded-full" style={{ background: ds.dot }} />
            <h3 className="text-gray-800 font-black text-sm uppercase tracking-widest">⚖️ Final Decision</h3>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center mb-6">
            {[
              { label: 'Decision', value: rec, sub: '' },
              { label: 'Recommended Amount', value: `₹${amount} Cr`, sub: `↓ from ₹60 Cr` },
              { label: 'Interest Rate', value: `${rate}%`, sub: 'per annum' },
              { label: 'Tenor', value: `${tenor}m`, sub: `${Math.round(tenor / 12)} years` },
            ].map(({ label, value, sub }) => (
              <div key={label} className="p-4 rounded-xl bg-white border border-green-100">
                <p className="text-gray-400 text-xs mb-1">{label}</p>
                <p className={`text-xl font-black ${ds.text}`}>{value}</p>
                {sub && <p className="text-gray-400 text-xs mt-0.5">{sub}</p>}
              </div>
            ))}
          </div>

          <div className="border-t border-green-200 pt-5 mb-5">
            <p className="text-gray-500 text-xs font-bold uppercase tracking-widest mb-3">Conditions Precedent</p>
            <div className="space-y-2">
              {(verdict.conditions || []).map((c, i) => (
                <div key={i} className="flex items-start gap-2.5">
                  <span className="mt-0.5 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-black shrink-0 bg-amber-100 text-amber-700">{i + 1}</span>
                  <p className="text-gray-700 text-sm">{c}</p>
                </div>
              ))}
            </div>
          </div>

          {verdict.verdict_rationale && (
            <div className="border-t border-green-200 pt-5">
              <p className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-2">Adjudication Rationale</p>
              <p className="text-gray-600 text-sm italic leading-relaxed">{verdict.verdict_rationale}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
