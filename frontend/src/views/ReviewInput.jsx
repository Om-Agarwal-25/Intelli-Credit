import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import FiveCsGauges from '../components/FiveCsGauges'
import RiskFlagsTable from '../components/RiskFlagsTable'
import { Loader2, SlidersHorizontal } from 'lucide-react'

const DEMO_FIVE_CS = { C1: 35, C2: 68, C3: 70, C4: 70, C5: 72, composite: 56.4 }
const DEMO_FLAGS = [
  { flag_type: 'DIN_DISQUALIFIED', severity: 'HIGH', source_document: 'MCA21', evidence_snippet: 'Director Kavita Mehta (DIN 07284531) disqualified under Section 164(2) since September 2023.', five_c_pillar: 'C1' },
  { flag_type: 'NCLT_PROCEEDINGS', severity: 'HIGH', source_document: 'NCLT Mumbai', evidence_snippet: 'IB/1234/MB/2024 — Section 9 petition admitted. Notice issued.', five_c_pillar: 'C1' },
  { flag_type: 'LITIGATION_UNDISCLOSED', severity: 'HIGH', source_document: 'e-Courts Pune', evidence_snippet: 'Case 1842/2024 — Fraud complaint ₹4.2 Cr. Not disclosed in self-declaration.', five_c_pillar: 'C1' },
  { flag_type: 'REVENUE_INFLATION', severity: 'HIGH', source_document: 'GSTR-1 / Bank Statement', evidence_snippet: 'GST-bank discrepancy >60% in April and May 2023.', five_c_pillar: 'C2' },
  { flag_type: 'GOING_CONCERN', severity: 'HIGH', source_document: 'Annual Report p.34', evidence_snippet: "The Company's ability to continue as a going concern is subject to resolution of Note 31.", five_c_pillar: 'C2' },
  { flag_type: 'PROMOTER_NETWORK_RISK', severity: 'MEDIUM', source_document: 'MCA21', evidence_snippet: '2 associated companies struck off: Vardhaman Buildcon, Vardhaman Holdings LLP.', five_c_pillar: 'C1' },
  { flag_type: 'NEWS_HIGH', severity: 'MEDIUM', source_document: 'Economic Times', evidence_snippet: 'Vardhaman delays NHAI project by 14 months. Penalty notice issued.', five_c_pillar: 'C5' },
  { flag_type: 'CONTINGENT_LIABILITY', severity: 'MEDIUM', source_document: 'Annual Report', evidence_snippet: 'Contingent liabilities ₹8.4 Cr not provided for in accounts.', five_c_pillar: 'C3' },
]

function SegmentedControl({ value, options, onChange }) {
  return (
    <div className="flex rounded-xl overflow-hidden border border-green-100 bg-green-50">
      {options.map(opt => (
        <button key={opt} onClick={() => onChange(opt)}
          className={`flex-1 py-2 text-xs font-semibold transition-all duration-200 ${value === opt ? 'bg-green-600 text-white shadow-sm' : 'text-gray-500 hover:text-green-700'
            }`}>
          {opt}
        </button>
      ))}
    </div>
  )
}

export default function ReviewInput({ session }) {
  const navigate = useNavigate()
  const location = useLocation()
  const sessionId = location.state?.session_id || session?.session_id
  const isDemo = location.state?.demo
  const stateData = location.state?.session_data || {}

  const five_cs = stateData.five_cs || DEMO_FIVE_CS
  const risk_flags = stateData.risk_flags || DEMO_FLAGS
  const base_score = (stateData.base_score?.composite || stateData.base_score) || 78.0

  const [form, setForm] = useState({ factory_utilisation: 70, management_impression: 'Confident', promoter_reputation: 'Neutral', site_visit_notes: '', other_observations: '' })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [adjustments, setAdjustments] = useState([])

  const handleSubmit = async () => {
    setIsSubmitting(true)
    try {
      const resp = await fetch(`/api/sessions/${sessionId}/qualitative`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, ...form, officer_id: 'officer_001' }),
      })
      const data = await resp.json()
      setAdjustments(data.parsed_adjustments || [])
      setTimeout(() => navigate('/verdict', { state: { session_id: sessionId, demo: isDemo, base_score, five_cs } }), 1500)
    } catch {
      navigate('/verdict', { state: { session_id: sessionId, demo: true, base_score, five_cs } })
    }
    setIsSubmitting(false)
  }

  const utilColor = form.factory_utilisation >= 75 ? '#16A34A' : form.factory_utilisation >= 50 ? '#D97706' : '#DC2626'

  return (
    <div className="min-h-screen py-10 px-4" style={{ background: '#F8F9FB' }}>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 animate-fade-up">
          <h1 className="text-3xl font-black tracking-tight text-gray-900">Credit Review Panel</h1>
          <p className="text-gray-500 text-sm mt-1">
            AI Base Score: <span className="font-bold text-green-600">{base_score}/100</span>
            <span className="mx-2 text-gray-300">·</span>
            Review findings and provide qualitative officer input
          </p>
        </div>

        <div className="grid grid-cols-12 gap-5">
          <div className="col-span-12 md:col-span-3 animate-fade-up" style={{ animationDelay: '0.1s' }}>
            <FiveCsGauges five_cs={five_cs} />
          </div>
          <div className="col-span-12 md:col-span-5 animate-fade-up" style={{ animationDelay: '0.15s' }}>
            <RiskFlagsTable flags={risk_flags} />
          </div>
          <div className="col-span-12 md:col-span-4 animate-fade-up" style={{ animationDelay: '0.2s' }}>
            <div className="card p-5 sticky top-20" style={{ background: '#FAFBFC', boxShadow: '0 4px 16px rgba(0,0,0,0.07)' }}>
              <h3 className="font-bold text-sm mb-5 flex items-center gap-2 text-gray-800">
                <SlidersHorizontal size={15} className="text-green-600" />
                Credit Officer Input
              </h3>

              <div className="mb-5">
                <label className="flex items-center justify-between text-xs font-semibold text-gray-500 mb-3">
                  Factory Utilisation Observed
                  <span className="font-black text-base" style={{ color: utilColor }}>{form.factory_utilisation}%</span>
                </label>
                <input type="range" min="0" max="100" value={form.factory_utilisation}
                  onChange={e => setForm(f => ({ ...f, factory_utilisation: parseInt(e.target.value) }))}
                  style={{ accentColor: utilColor }} />
                <div className="flex justify-between text-xs text-gray-400 mt-1"><span>0%</span><span>50%</span><span>100%</span></div>
              </div>

              <div className="mb-4">
                <label className="block text-xs font-semibold text-gray-500 mb-2">Management Interview Impression</label>
                <SegmentedControl value={form.management_impression} options={['Confident', 'Mixed', 'Evasive']}
                  onChange={v => setForm(f => ({ ...f, management_impression: v }))} />
              </div>

              <div className="mb-4">
                <label className="block text-xs font-semibold text-gray-500 mb-2">Promoter Reputation Assessment</label>
                <SegmentedControl value={form.promoter_reputation} options={['Strong', 'Neutral', 'Concerning']}
                  onChange={v => setForm(f => ({ ...f, promoter_reputation: v }))} />
              </div>

              <div className="mb-4">
                <label className="block text-xs font-semibold text-gray-500 mb-2">Site Visit Notes</label>
                <textarea rows={3} placeholder="Describe site visit observations…" value={form.site_visit_notes}
                  onChange={e => setForm(f => ({ ...f, site_visit_notes: e.target.value }))}
                  className="input-dark resize-none text-sm leading-relaxed" />
              </div>
              <div className="mb-5">
                <label className="block text-xs font-semibold text-gray-500 mb-2">Other Observations</label>
                <textarea rows={2} placeholder="Any additional notes…" value={form.other_observations}
                  onChange={e => setForm(f => ({ ...f, other_observations: e.target.value }))}
                  className="input-dark resize-none text-sm" />
              </div>

              {adjustments.length > 0 && (
                <div className="mb-4 p-3 rounded-xl border border-amber-200 bg-amber-50">
                  <p className="text-xs font-bold text-amber-700 mb-2">Parsed Score Adjustments</p>
                  {adjustments.map((a, i) => (
                    <p key={i} className="text-xs text-amber-700">{a.five_c_pillar}: <strong>{a.score_delta > 0 ? '+' : ''}{a.score_delta} pts</strong> — {a.reasoning}</p>
                  ))}
                </div>
              )}

              <button onClick={handleSubmit} disabled={isSubmitting} className="btn-primary w-full py-3.5 text-sm">
                {isSubmitting && <Loader2 size={15} className="animate-spin" />}
                {isSubmitting ? 'Launching Jury…' : '⚖️ Submit & Start AI Jury Deliberation'}
              </button>
              <p className="text-xs text-gray-400 mt-2 text-center">Score cap: ±25 pts from qualitative input</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
