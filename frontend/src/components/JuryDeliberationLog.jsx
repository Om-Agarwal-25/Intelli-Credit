/**
 * JuryDeliberationLog — Styled adversarial debate timeline
 */
export default function JuryDeliberationLog({ prosecution = {}, defence = {}, verdict = {} }) {
  const pf = prosecution?.prosecution_findings || []
  const df = defence?.defence_findings || []
  const acceptedP = new Set(verdict?.accepted_prosecution_findings || [])
  const acceptedD = new Set(verdict?.accepted_defence_findings || [])

  const rows = [
    ...pf.map(f => ({ type: 'prosecution', finding: f })),
    ...df.map(f => ({ type: 'defence', finding: f })),
  ]

  return (
    <div className="card overflow-hidden mt-6">
      <div className="px-5 py-4 flex items-center justify-between border-b" style={{ background: '#F8FAFC', borderColor: '#E2E8F0' }}>
        <span className="font-black text-sm text-gray-800 tracking-wide">⚖️ JURY DELIBERATION LOG</span>
        <div className="flex gap-3 text-xs">
          <span className="flex items-center gap-1.5 text-red-500"><span className="w-1.5 h-1.5 rounded-full bg-red-400" /> Risk Scrutiny</span>
          <span className="flex items-center gap-1.5 text-green-600"><span className="w-1.5 h-1.5 rounded-full bg-green-400" /> Credit Advocacy</span>
        </div>
      </div>

      <div className="overflow-x-auto bg-white">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b" style={{ background: '#F8FAFC', borderColor: '#E2E8F0' }}>
              <th className="px-4 py-2.5 text-left text-gray-400 font-bold uppercase tracking-wider w-32">Agent</th>
              <th className="px-4 py-2.5 text-left text-gray-400 font-bold uppercase tracking-wider">Finding</th>
              <th className="px-4 py-2.5 text-left text-gray-400 font-bold uppercase tracking-wider w-24">Pillar / Δ</th>
              <th className="px-4 py-2.5 text-left text-gray-400 font-bold uppercase tracking-wider w-24">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(({ type, finding }, i) => {
              const isPros = type === 'prosecution'
              const accepted = isPros ? acceptedP.has(finding.finding_id) : acceptedD.has(finding.finding_id)
              return (
                <tr key={i} className="animate-row border-b border-gray-50 transition-colors hover:bg-gray-50/60"
                  style={{ background: isPros ? 'rgba(254,242,242,0.5)' : 'rgba(240,253,244,0.5)', animationDelay: `${i * 60}ms` }}>
                  <td className="px-4 py-3">
                    <div className={`flex items-center gap-1.5 font-semibold ${isPros ? 'text-red-500' : 'text-green-600'}`}>
                      <span>{isPros ? '🔴' : '🟢'}</span>
                      <span>{isPros ? 'Risk Scrutiny' : 'Credit Advocacy'}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-600 leading-5 max-w-xs">
                    <span className="font-bold text-gray-800">[{finding.finding_id}]</span>{' '}{finding.finding_text}
                    {finding.evidence_source && <p className="text-gray-400 text-[10px] mt-1">📎 {finding.evidence_source}</p>}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`font-black text-sm ${isPros ? 'text-red-500' : 'text-green-600'}`}>
                      {isPros ? '' : '+'}{finding.score_delta} pts
                    </span>
                    <p className="text-gray-400 mt-0.5">{finding.five_c_pillar}</p>
                  </td>
                  <td className="px-4 py-3">
                    {accepted ? (
                      <span className={`px-2 py-1 rounded-full font-bold text-[10px] border ${isPros ? 'bg-red-50 text-red-600 border-red-200' : 'bg-green-50 text-green-700 border-green-200'
                        }`}>✓ Accepted</span>
                    ) : (
                      <span className="px-2 py-1 rounded-full font-bold text-[10px] bg-gray-100 text-gray-400 border border-gray-200">Overruled</span>
                    )}
                  </td>
                </tr>
              )
            })}

            {verdict.primary_reason && (
              <tr className="animate-row border-t-2 border-green-100" style={{ background: 'rgba(240,253,244,0.8)' }}>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5 font-semibold text-green-700">
                    <span>⚖️</span><span>Adjudication</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-gray-600 italic leading-5" colSpan={2}>{verdict.primary_reason}</td>
                <td className="px-4 py-3">
                  <span className="px-2.5 py-1.5 rounded-full font-black text-[10px] uppercase text-white" style={{ background: '#16A34A' }}>
                    VERDICT
                  </span>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="px-5 py-3 flex items-center gap-3 flex-wrap text-xs border-t" style={{ background: '#F8FAFC', borderColor: '#E2E8F0' }}>
        <span className="text-gray-500 font-medium">Final Verdict → CAM Section 6</span>
        <span className="px-3 py-1 rounded-full font-bold text-white" style={{ background: '#16A34A' }}>
          {verdict.final_recommendation === 'CONDITIONAL'
            ? `✓ Conditional — ₹${verdict.recommended_loan_amount_cr} Cr @ ${verdict.recommended_interest_rate_pct}%`
            : verdict.final_recommendation === 'APPROVE'
              ? `✅ Approved — ₹${verdict.recommended_loan_amount_cr} Cr @ ${verdict.recommended_interest_rate_pct}%`
              : `❌ Rejected`}
        </span>
      </div>
    </div>
  )
}
