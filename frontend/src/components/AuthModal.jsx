import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Mail, ShieldCheck, ArrowRight, Loader2, Sparkles, X } from 'lucide-react'

export default function AuthModal({ isOpen, onClose, onLoginSuccess }) {
  const [step, setStep] = useState('email') // 'email' or 'otp'
  const [email, setEmail] = useState('')
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  /*
  const handleGoogleLogin = () => {
    setLoading(true)
    setError('')
    
    // Open centered popup window to simulate Google OAuth consent screen
    const width = 500
    const height = 600
    const left = window.screenX + (window.outerWidth - width) / 2
    const top = window.screenY + (window.outerHeight - height) / 2
    
    const popup = window.open("", "google_login", `width=${width},height=${height},left=${left},top=${top}`)
    
    if (popup) {
      popup.document.write(`
        <html>
          <head>
            <title>Sign in with Google</title>
            <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap" rel="stylesheet">
            <style>
              body {
                background: #050a0e;
                color: #edf2f7;
                font-family: 'Outfit', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                text-align: center;
                overflow: hidden;
              }
              .card {
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: 16px;
                padding: 2.5rem;
                width: 80%;
                box-shadow: 0 12px 40px rgba(0,0,0,0.5);
              }
              .logo {
                font-weight: 600;
                font-size: 20px;
                margin-bottom: 2rem;
                display: flex;
                align-items: center;
                gap: 8px;
                justify-content: center;
              }
              .btn {
                background: #00e87b;
                color: #050a0e;
                border: none;
                padding: 0.8rem 2rem;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s;
                font-size: 14px;
              }
              .btn:hover {
                transform: scale(1.03);
              }
              .status {
                color: #7b93a8;
                font-size: 13px;
                margin-top: 1rem;
              }
            </style>
          </head>
          <body>
            <div class="card">
              <div class="logo">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l3.66-2.85z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.85c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                Google Account
              </div>
              <p style="margin-bottom: 1.5rem; font-size: 14px; line-height: 1.6;">
                Choose account to continue to <br/><strong>FIFA World Cup ML Predictor</strong>
              </p>
              <button class="btn" onclick="login()">Continue as Guest User</button>
              <div class="status" id="status"></div>
            </div>
            <script>
              function login() {
                document.getElementById('status').innerText = 'Signing in...';
                setTimeout(() => {
                  window.opener.postMessage({ type: 'GOOGLE_AUTH_SUCCESS', email: 'worldcup.fan@gmail.com', name: 'WC Fan' }, '*');
                  window.close();
                }, 1000);
              }
            </script>
          </body>
        </html>
      `)
      
      const handleMessage = async (event) => {
        if (event.data && event.data.type === 'GOOGLE_AUTH_SUCCESS') {
          window.removeEventListener('message', handleMessage)
          try {
            const res = await fetch('/api/auth/google', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email: event.data.email, name: event.data.name })
            })
            const data = await res.json()
            if (res.ok && data.status === 'success') {
              onLoginSuccess(data.user)
              onClose()
            } else {
              setError(data.detail || 'Google sign-in backend verification failed.')
            }
          } catch (err) {
            setError('Connection failed. Verify your server is running.')
          } finally {
            setLoading(false)
          }
        }
      }
      window.addEventListener('message', handleMessage)
    } else {
      setError('OAuth popup blocked by browser. Please allow popups.')
      setLoading(false)
    }
  }
  */

  const handleSendOtp = async (e) => {
    e.preventDefault()
    if (!email) return
    setLoading(true)
    setError('')
    
    try {
      const res = await fetch('/api/auth/otp/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      })
      const data = await res.json()
      if (res.ok) {
        setStep('otp')
      } else {
        setError(data.detail || 'Failed to send verification code.')
      }
    } catch (err) {
      setError('Connection failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOtp = async (e) => {
    e.preventDefault()
    if (!otp) return
    setLoading(true)
    setError('')
    
    try {
      const res = await fetch('/api/auth/otp/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, code: otp })
      })
      const data = await res.json()
      if (res.ok) {
        onLoginSuccess(data.user)
        onClose()
      } else {
        setError(data.detail || 'Incorrect verification code.')
      }
    } catch (err) {
      setError('Connection failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* Backdrop */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 auth-backdrop bg-black/70"
      />

      {/* Modal Container */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.9, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 15 }}
        transition={{ type: "spring", damping: 25, stiffness: 350 }}
        className="w-full max-w-[400px] overflow-hidden p-6 relative z-10 flex flex-col items-center bg-[#0a1118] border border-white/[0.08] rounded-2xl shadow-[0_32px_64px_rgba(0,0,0,0.9)]"
      >
        {/* Close Button */}
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 text-[#7b93a8] hover:text-white transition-colors"
        >
          <X size={18} />
        </button>

        {/* Header Logo */}
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#00e87b]/10 border border-[#00e87b]/20 text-[#00e87b] mb-4">
          <Sparkles size={20} />
        </div>

        <h3 className="text-xl font-bold text-white mb-1">Join the Arena</h3>
        <p className="text-[#7b93a8] text-[12px] text-center mb-6">
          Sign in to predict matchups, compete on the Leaderboard, and unlock metrics.
        </p>

        {error && (
          <div className="w-full bg-red-500/10 border border-red-500/20 text-red-400 text-[11px] p-2.5 rounded-lg mb-4 text-center">
            ⚠️ {error}
          </div>
        )}

        {step === 'email' ? (
          <form onSubmit={handleSendOtp} className="w-full space-y-4">
            <div className="space-y-1.5">
              <label className="text-[10px] font-semibold text-[#7b93a8] uppercase tracking-wider">Email Address</label>
              <div className="relative">
                <input 
                  type="email" 
                  required
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="auth-input"
                />
                <Mail size={15} className="absolute left-3.5 top-3.5 text-[#3f5669]" />
              </div>
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="w-full h-11 rounded-lg bg-[#00e87b] text-[#050a0e] font-semibold text-[13px] flex items-center justify-center gap-1.5 hover:bg-[#00c464] disabled:opacity-50 transition cursor-pointer"
            >
              {loading ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <>
                  Send Magic Code <ArrowRight size={14} />
                </>
              )}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp} className="w-full space-y-4">
            {/* Inline warning to look at terminal OTP */}
            <div className="bg-[#00e87b]/10 border border-[#00e87b]/20 text-[#00e87b] text-[11px] p-3 rounded-lg text-left leading-relaxed">
              <strong>Local Mock Mode:</strong> Check your <strong>Python backend terminal console</strong> to find the 6-digit OTP code printed for <em>{email}</em>.
            </div>

            <div className="space-y-1.5">
              <label className="text-[10px] font-semibold text-[#7b93a8] uppercase tracking-wider">6-Digit Code</label>
              <div className="relative">
                <input 
                  type="text" 
                  required
                  maxLength={6}
                  placeholder="123456"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  className="auth-input pr-[2.75rem] tracking-[0.2em] font-semibold text-center text-base"
                />
                <ShieldCheck size={16} className="absolute left-3.5 top-3.5 text-[#3f5669]" />
              </div>
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="w-full h-11 rounded-lg bg-[#00e87b] text-[#050a0e] font-semibold text-[13px] flex items-center justify-center gap-1.5 hover:bg-[#00c464] disabled:opacity-50 transition cursor-pointer"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : 'Verify & Enter Arena'}
            </button>

            <button 
              type="button"
              onClick={() => setStep('email')}
              className="w-full text-center text-[11px] text-[#7b93a8] hover:text-white transition-colors"
            >
              Back to email
            </button>
          </form>
        )}
      </motion.div>
    </div>
  )
}
