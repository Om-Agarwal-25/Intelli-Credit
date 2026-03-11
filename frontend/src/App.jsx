import { useState } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import UploadPortal from './views/UploadPortal'
import ProcessingDashboard from './views/ProcessingDashboard'
import ReviewInput from './views/ReviewInput'
import JuryDecision from './views/JuryDecision'
import { Shield, Lock, Scale } from 'lucide-react'

const NAV_STEPS = [
  { path: '/', label: 'Upload', step: 1 },
  { path: '/processing', label: 'Analysis', step: 2 },
  { path: '/review', label: 'Review', step: 3 },
  { path: '/verdict', label: 'Verdict', step: 4 },
]

function Navbar() {
  const location = useLocation()
  const currentStep = NAV_STEPS.find(s => s.path === location.pathname)?.step || 1

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-slate-200"
      style={{ boxShadow: '0 1px 4px rgba(0,0,0,0.06)' }}>
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center gap-6">
        {/* Logo */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #22C55E, #16A34A)' }}>
            <span className="text-white font-black text-sm tracking-tight">IC</span>
          </div>
          <div>
            <span className="font-bold text-base tracking-tight text-gray-900">IntelliCredit</span>
            <span className="ml-2 text-xs px-2 py-0.5 rounded-full font-semibold"
              style={{ background: 'rgba(22,163,74,0.1)', color: '#16A34A', border: '1px solid rgba(22,163,74,0.25)' }}>
              AI Appraisal
            </span>
          </div>
        </div>

        {/* Step indicator */}
        <div className="hidden md:flex items-center gap-1 mx-auto">
          {NAV_STEPS.map((s, i) => {
            const done = s.step < currentStep
            const active = s.step === currentStep
            return (
              <div key={s.path} className="flex items-center gap-1">
                {i > 0 && (
                  <div className={`w-12 h-0.5 transition-all duration-500 ${done ? 'bg-green-400' : 'bg-slate-200'}`} />
                )}
                <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold transition-all duration-300 ${active ? 'text-white' : done ? 'text-green-600' : 'text-gray-400'
                  }`}
                  style={active ? { background: '#16A34A', boxShadow: '0 0 12px rgba(22,163,74,0.35)' } : {}}>
                  <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold ${active ? 'bg-white text-green-700' : done ? 'bg-green-500 text-white' : 'bg-gray-100 text-gray-400'
                    }`}>{s.step}</span>
                  {s.label}
                </div>
              </div>
            )
          })}
        </div>

        {/* Compliance strip */}
        <div className="hidden lg:flex items-center gap-3 shrink-0 ml-auto">
          {[
            { icon: Shield, label: 'RBI Compliant' },
            { icon: Lock, label: 'Encrypted' },
            { icon: Scale, label: 'AI Jury' },
          ].map(({ icon: Icon, label }) => (
            <div key={label} className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
              <Icon size={11} className="text-green-500" />
              {label}
            </div>
          ))}
        </div>
      </div>
    </nav>
  )
}

function App() {
  const [session, setSession] = useState(null)
  return (
    <>
      <Navbar />
      <div className="pt-16 min-h-screen">
        <Routes>
          <Route path="/" element={<UploadPortal setSession={setSession} />} />
          <Route path="/processing" element={<ProcessingDashboard session={session} />} />
          <Route path="/review" element={<ReviewInput session={session} />} />
          <Route path="/verdict" element={<JuryDecision session={session} />} />
        </Routes>
      </div>
    </>
  )
}

export default App
