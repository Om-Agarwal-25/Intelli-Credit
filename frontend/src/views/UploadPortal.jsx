import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText, X, ArrowRight, Loader2, Zap, CheckCircle2 } from 'lucide-react'

const DOC_TYPE_META = {
  GST_RETURN: { label: 'GST Return', color: 'text-emerald-700', bg: 'bg-emerald-50 border-emerald-200' },
  BANK_STATEMENT: { label: 'Bank Statement', color: 'text-blue-700', bg: 'bg-blue-50 border-blue-200' },
  ANNUAL_REPORT: { label: 'Annual Report', color: 'text-violet-700', bg: 'bg-violet-50 border-violet-200' },
  LEGAL_DOC: { label: 'Legal Doc', color: 'text-rose-700', bg: 'bg-rose-50 border-rose-200' },
  ITR: { label: 'ITR', color: 'text-amber-700', bg: 'bg-amber-50 border-amber-200' },
  RATING_REPORT: { label: 'Rating Report', color: 'text-indigo-700', bg: 'bg-indigo-50 border-indigo-200' },
  OTHER: { label: 'Other', color: 'text-gray-600', bg: 'bg-gray-50 border-gray-200' },
}

const FEATURES = [
  { icon: '🔍', text: 'GST Cross-reference' },
  { icon: '⚖️', text: 'AI Jury Deliberation' },
  { icon: '📋', text: 'Full Audit Trail' },
  { icon: '🔐', text: 'Encrypted Scoring' },
]

export default function UploadPortal({ setSession }) {
  const navigate = useNavigate()
  const [files, setFiles] = useState([])
  const [isDragging, setIsDragging] = useState(false)
  const [isStarting, setIsStarting] = useState(false)
  const [isLoadingDemo, setIsLoadingDemo] = useState(false)
  const [borrowerName, setBorrowerName] = useState('')
  const [loanAmount, setLoanAmount] = useState('')
  const [error, setError] = useState(null)

  const handleDrop = useCallback((e) => {
    e.preventDefault(); setIsDragging(false)
    addFiles(Array.from(e.dataTransfer.files).filter(f => f.name.endsWith('.pdf')))
  }, [])

  const handleFileInput = (e) => addFiles(Array.from(e.target.files))
  const addFiles = (newFiles) => setFiles(prev => [...prev, ...newFiles.map(f => ({ file: f, name: f.name, doc_type: 'CLASSIFYING', status: 'pending' }))])
  const removeFile = (idx) => setFiles(prev => prev.filter((_, i) => i !== idx))

  const loadVardhamanDemo = async () => {
    setIsLoadingDemo(true); setError(null)
    try {
      const resp = await fetch('/api/demo/load-vardhaman', { method: 'POST' })
      const data = await resp.json()
      const sid = data.session_id
      setFiles(data.uploaded.map(f => ({ file: null, name: f.filename, doc_type: f.doc_type, status: 'uploaded', demo: true })))
      setBorrowerName('Vardhaman Infra & Logistics Pvt. Ltd.')
      setLoanAmount('60')
      setSession({ session_id: sid, borrower_name: 'Vardhaman Infra & Logistics Pvt. Ltd.', loan_amount_cr: 60 })
      await fetch(`/api/sessions/${sid}/analyze`, { method: 'POST' })
      navigate('/processing', { state: { session_id: sid } })
    } catch { setError('Demo load failed — backend not running.') }
    setIsLoadingDemo(false)
  }

  const beginAnalysis = async () => {
    if (files.length === 0) return
    setIsStarting(true); setError(null)
    try {
      const ses = await (await fetch('/api/sessions', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ borrower_name: borrowerName || 'Vardhaman Infra & Logistics Pvt. Ltd.', loan_amount_cr: parseFloat(loanAmount) || 60, loan_type: 'Term Loan' }),
      })).json()
      const sid = ses.session_id
      const formData = new FormData()
      files.forEach(f => formData.append('files', f.file))
      const upData = await (await fetch(`/api/sessions/${sid}/upload`, { method: 'POST', body: formData })).json()
      setFiles(prev => prev.map((f, i) => ({ ...f, doc_type: upData.uploaded[i]?.doc_type || 'OTHER', status: 'uploaded' })))
      setSession({ session_id: sid, borrower_name: borrowerName || 'Vardhaman Infra & Logistics Pvt. Ltd.', loan_amount_cr: parseFloat(loanAmount) || 60 })
      await fetch(`/api/sessions/${sid}/analyze`, { method: 'POST' })
      navigate('/processing', { state: { session_id: sid } })
    } catch {
      const demoSid = 'demo-' + Date.now()
      setSession({ session_id: demoSid, borrower_name: borrowerName || 'Demo Corp', loan_amount_cr: 60 })
      navigate('/processing', { state: { session_id: demoSid, demo: true } })
    }
    setIsStarting(false)
  }

  return (
    <div className="min-h-screen py-12 px-4" style={{ background: 'radial-gradient(ellipse at 60% 40%, #e8f5e9 0%, #f0fdf4 40%, #F8F9FB 100%)' }}>
      <div className="max-w-4xl mx-auto">

        {/* Hero */}
        <div className="text-center mb-12 animate-fade-up relative">
          {/* Geometric grid behind hero */}
          <div className="absolute inset-0 -mx-8 -my-4 pointer-events-none rounded-3xl" style={{
            backgroundImage: 'linear-gradient(rgba(22,163,74,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(22,163,74,0.05) 1px, transparent 1px)',
            backgroundSize: '40px 40px',
          }} />
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold mb-6 relative"
            style={{ background: 'rgba(22,163,74,0.08)', color: '#16A34A', border: '1px solid rgba(22,163,74,0.2)', borderLeft: '3px solid #16A34A' }}>
            AI-Powered Credit Intelligence
          </div>
          <h1 className="text-5xl font-black tracking-tight mb-4 text-gray-900">
            Credit Appraisal,<br />
            <span style={{ background: 'linear-gradient(135deg, #16A34A, #4ADE80)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Reimagined
            </span>
          </h1>
          <p className="text-gray-500 text-lg max-w-xl mx-auto leading-relaxed">
            Upload financial documents and our adversarial AI Jury delivers a decision with full audit trail — in under 5 minutes.
          </p>
          <div className="flex justify-center gap-6 mt-6">
            {FEATURES.map(f => (
              <div key={f.text} className="flex items-center gap-1.5 text-xs text-gray-400 font-medium">
                <span>{f.icon}</span>{f.text}
              </div>
            ))}
          </div>
        </div>

        {/* Borrower Info Card */}
        <div className="card p-6 mb-5 animate-fade-up" style={{ animationDelay: '0.1s' }}>
          <h2 className="text-sm font-bold text-gray-700 mb-4 flex items-center gap-2">
            <span className="w-6 h-6 rounded-md flex items-center justify-center text-[10px] font-black text-white"
              style={{ background: '#16A34A' }}>1</span>
            Borrower Information
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-500 mb-2">Company Name</label>
              <input className="input-dark" placeholder="Vardhaman Infra & Logistics Pvt. Ltd."
                value={borrowerName} onChange={e => setBorrowerName(e.target.value)} />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-500 mb-2">Loan Amount Applied (₹ Crore)</label>
              <input type="number" className="input-dark" placeholder="60"
                value={loanAmount} onChange={e => setLoanAmount(e.target.value)} />
            </div>
          </div>
        </div>

        {/* Demo Quick-Start */}
        <div className="flex items-center gap-3 mb-5 animate-fade-up" style={{ animationDelay: '0.15s' }}>
          <div className="flex-1 h-px bg-slate-200" />
          <button id="load-demo-btn" onClick={loadVardhamanDemo} disabled={isLoadingDemo} className="btn-secondary text-xs gap-2">
            {isLoadingDemo ? <Loader2 size={13} className="animate-spin" /> : <Zap size={13} />}
            {isLoadingDemo ? 'Loading Demo...' : '🎯 Load Vardhaman Demo (4 PDFs)'}
          </button>
          <div className="flex-1 h-px bg-slate-200" />
        </div>

        {/* Drop Zone */}
        <div
          onDrop={handleDrop}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
          onDragLeave={() => setIsDragging(false)}
          onClick={() => document.getElementById('fileInput').click()}
          className="relative rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 mb-5 animate-fade-up"
          style={{
            animationDelay: '0.2s',
            border: `2px dashed ${isDragging ? '#16A34A' : '#D1FAE5'}`,
            background: isDragging ? 'rgba(22,163,74,0.04)' : '#FFFFFF',
            boxShadow: isDragging ? '0 0 32px rgba(22,163,74,0.1)' : 'none',
          }}
        >
          <div className={`w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center transition-all ${isDragging ? 'scale-110' : ''}`}
            style={{ background: isDragging ? 'rgba(22,163,74,0.12)' : '#F0FDF4' }}>
            <Upload size={28} className={isDragging ? 'text-green-600' : 'text-green-400'} />
          </div>
          <p className="font-bold text-gray-700 text-lg mb-1">
            {isDragging ? 'Release to upload' : 'Drop documents here or click to browse'}
          </p>
          <p className="text-sm text-gray-400">PDF files only · GST Returns · Bank Statements · Annual Reports · ITRs</p>
          <input id="fileInput" type="file" multiple accept=".pdf" className="hidden" onChange={handleFileInput} />
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="card p-4 mb-5 animate-fade-up">
            <p className="text-xs font-bold text-gray-400 mb-3 uppercase tracking-wider">
              Uploaded Files · {files.length} document{files.length > 1 ? 's' : ''}
            </p>
            <div className="space-y-2">
              {files.map((f, i) => {
                const meta = DOC_TYPE_META[f.doc_type] || DOC_TYPE_META.OTHER
                return (
                  <div key={i} className="flex items-center gap-3 px-4 py-3 rounded-xl bg-gray-50 border border-gray-100 transition-all">
                    <FileText size={16} className="text-green-500 shrink-0" />
                    <span className="text-sm font-medium text-gray-700 flex-1 truncate">{f.name}</span>
                    {f.doc_type === 'CLASSIFYING' ? (
                      <span className="flex items-center gap-1.5 text-xs text-gray-400">
                        <Loader2 size={11} className="animate-spin" /> Classifying…
                      </span>
                    ) : (
                      <span className={`text-xs px-2.5 py-1 rounded-full border font-semibold ${meta.bg} ${meta.color}`}>
                        {meta.label} {f.status === 'uploaded' && <CheckCircle2 size={10} className="inline ml-1" />}
                      </span>
                    )}
                    <button onClick={(e) => { e.stopPropagation(); removeFile(i) }} className="text-gray-300 hover:text-rose-400 transition-colors ml-1">
                      <X size={15} />
                    </button>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {error && (
          <div className="mb-4 px-4 py-3 rounded-xl text-sm text-rose-700 border border-rose-200 bg-rose-50">{error}</div>
        )}

        {/* CTA */}
        <div className="flex justify-center animate-fade-up" style={{ animationDelay: '0.25s' }}>
          <button onClick={beginAnalysis} disabled={files.length === 0 || isStarting} className="btn-primary text-base px-10 py-4">
            {isStarting ? <Loader2 size={18} className="animate-spin" /> : null}
            {isStarting ? 'Starting Analysis…' : 'Begin AI Analysis'}
            {!isStarting && <ArrowRight size={18} />}
          </button>
        </div>

        {/* Compliance strip */}
        <div className="mt-10 flex justify-center gap-8 text-xs text-gray-400 font-medium animate-fade-up" style={{ animationDelay: '0.3s' }}>
          <span>✓ RBI Data Localisation</span>
          <span>🔐 Homomorphic Encryption</span>
          <span>⚖️ Adversarial Jury System</span>
          <span>📋 Full Audit Trail</span>
        </div>
      </div>
    </div>
  )
}
