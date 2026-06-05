import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { User, Loader2, Sparkles, X } from 'lucide-react'

export default function AuthModal({ isOpen, onClose, onLoginSuccess }) {
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  const handleLogin = async (e) => {
    e.preventDefault()
    const trimmedUsername = username.trim()
    if (!trimmedUsername) return
    
    setLoading(true)
    setError('')
    
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: trimmedUsername })
      })
      const data = await res.json()
      if (res.ok && data.status === 'success') {
        onLoginSuccess(data.user)
        onClose()
      } else {
        setError(data.detail || 'Failed to enter the Arena.')
      }
    } catch (err) {
      setError('Connection failed. Verify your server is running.')
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

        <h3 className="text-xl font-bold text-white mb-1">Enter the Arena</h3>
        <p className="text-[#7b93a8] text-[12px] text-center mb-6">
          Choose a username to predict matchups, compete on the Leaderboard, and unlock metrics.
        </p>

        {error && (
          <div className="w-full bg-red-500/10 border border-red-500/20 text-red-400 text-[11px] p-2.5 rounded-lg mb-4 text-center">
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="w-full space-y-4">
          <div className="space-y-1.5">
            <label className="text-[10px] font-semibold text-[#7b93a8] uppercase tracking-wider">Username</label>
            <div className="relative">
              <input 
                type="text" 
                required
                minLength={3}
                maxLength={20}
                placeholder="Choose your handle..."
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="auth-input pr-10"
              />
              <User size={15} className="absolute left-3.5 top-3.5 text-[#3f5669]" />
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
              'Enter Arena'
            )}
          </button>
        </form>
      </motion.div>
    </div>
  )
}
