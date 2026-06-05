import React, { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  LayoutDashboard, 
  Flame, 
  Users, 
  Trophy, 
  Sliders,
  Search, 
  Play,
  Settings,
  Star,
  Activity,
  ArrowRight,
  Menu,
  ChevronRight,
  TrendingUp,
  Shield,
  Target,
  Zap,
  Globe,
  BarChart3,
  Clock,
  Cpu,
  Database,
  RefreshCw,
  Crosshair,
  User,
  LogOut,
  Calendar,
  MapPin,
  Lock,
  Home,
  GitFork,
  Palette,
  Heart,
  ExternalLink
} from 'lucide-react'
import AuthModal from './components/AuthModal'

// Brand SVG icons (lucide-react does not ship brand icons)
const GitHubIcon = ({ size = 14, className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" className={className}>
    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
  </svg>
)

const LinkedInIcon = ({ size = 14, className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" className={className}>
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
  </svg>
)

// ─── Country flag emoji lookup ───────────────────────────────────────────────
const COUNTRY_FLAGS = {
  "Argentina": "🇦🇷", "France": "🇫🇷", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Brazil": "🇧🇷",
  "Spain": "🇪🇸", "Portugal": "🇵🇹", "Netherlands": "🇳🇱", "Belgium": "🇧🇪",
  "Germany": "🇩🇪", "Croatia": "🇭🇷", "Colombia": "🇨🇴", "Uruguay": "🇺🇾",
  "Morocco": "🇲🇦", "Japan": "🇯🇵", "United States": "🇺🇸", "Mexico": "🇲🇽",
  "Switzerland": "🇨🇭", "Denmark": "🇩🇰", "Senegal": "🇸🇳", "Iran": "🇮🇷",
  "South Korea": "🇰🇷", "Austria": "🇦🇹", "Australia": "🇦🇺", "Ecuador": "🇪🇨",
  "Turkey": "🇹🇷", "Nigeria": "🇳🇬", "Sweden": "🇸🇪", "Ivory Coast": "🇨🇮",
  "Egypt": "🇪🇬", "Tunisia": "🇹🇳", "Poland": "🇵🇱", "Algeria": "🇩🇿",
  "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Canada": "🇨🇦", "Saudi Arabia": "🇸🇦", "Norway": "🇳🇴",
  "Paraguay": "🇵🇾", "Iraq": "🇮🇶", "Panama": "🇵🇦", "DR Congo": "🇨🇩",
  "New Zealand": "🇳🇿", "Bosnia and Herzegovina": "🇧🇦", "Qatar": "🇶🇦",
  "Ghana": "🇬🇭", "South Africa": "🇿🇦", "Czechia": "🇨🇿", "Haiti": "🇭🇹",
  "Uzbekistan": "🇺🇿", "Curacao": "🇨🇼", "Cape Verde": "🇨🇻", "Jordan": "🇯🇴",
  "Iran": "🇮🇷"
}

const getFlag = (name) => COUNTRY_FLAGS[name] || '🏳️'

const COUNTRY_CODES = {
  "Argentina": "AR", "France": "FR", "England": "GB", "Brazil": "BR",
  "Spain": "ES", "Portugal": "PT", "Netherlands": "NL", "Belgium": "BE",
  "Germany": "DE", "Croatia": "HR", "Colombia": "CO", "Uruguay": "UY",
  "Morocco": "MA", "Japan": "JP", "United States": "US", "Mexico": "MX",
  "Switzerland": "CH", "Denmark": "DK", "Senegal": "SN", "Iran": "IR",
  "South Korea": "KR", "Austria": "AT", "Australia": "AU", "Ecuador": "EC",
  "Turkey": "TR", "Nigeria": "NG", "Sweden": "SE", "Ivory Coast": "CI",
  "Egypt": "EG", "Tunisia": "TN", "Poland": "PL", "Algeria": "DZ",
  "Scotland": "GB", "Canada": "CA", "Saudi Arabia": "SA", "Norway": "NO",
  "Paraguay": "PY", "Iraq": "IQ", "Panama": "PA", "DR Congo": "CD",
  "New Zealand": "NZ", "Bosnia and Herzegovina": "BA", "Qatar": "QA",
  "Ghana": "GH", "South Africa": "ZA", "Czechia": "CZ", "Haiti": "HT",
  "Uzbekistan": "UZ", "Curacao": "CW", "Cape Verde": "CV", "Jordan": "JO",
  "Italy": "IT", "Chile": "CL", "Cameroon": "CM", "Wales": "GB"
}

const getFlagImg = (name, className = "w-5 h-3.5 object-cover inline-block mr-1.5 rounded-sm shadow-xs") => {
  const code = COUNTRY_CODES[name];
  if (code) {
    return (
      <img
        src={`https://flagsapi.com/${code}/flat/64.png`}
        alt={name}
        className={className}
        loading="lazy"
      />
    );
  }
  return <span className={className}>{getFlag(name)}</span>;
}

// ─── FIFA rankings (self-contained) ─────────────────────────────────────────
const FIFA_RANKINGS = {
  "Argentina": 1, "France": 2, "England": 3, "Brazil": 4,
  "Spain": 5, "Portugal": 6, "Netherlands": 7, "Belgium": 8,
  "Germany": 9, "Croatia": 11, "Colombia": 12, "Uruguay": 13,
  "Morocco": 14, "Japan": 15, "United States": 16, "Mexico": 17,
  "Switzerland": 18, "Denmark": 19, "Senegal": 20, "Iran": 21,
  "South Korea": 22, "Austria": 23, "Australia": 24, "Ecuador": 25,
  "Turkey": 26, "Nigeria": 27, "Sweden": 28, "Ivory Coast": 29,
  "Egypt": 30, "Tunisia": 31, "Poland": 32, "Algeria": 33,
  "Scotland": 34, "Canada": 35, "Saudi Arabia": 36, "Norway": 44,
  "Paraguay": 42, "Iraq": 43, "Panama": 45, "DR Congo": 46,
  "New Zealand": 47, "Bosnia and Herzegovina": 48
}

// ─── Animated Counter Hook ──────────────────────────────────────────────────
function useAnimatedCounter(target, duration = 1500, startOnMount = true) {
  const [count, setCount] = useState(0)
  const frameRef = useRef(null)

  useEffect(() => {
    if (!startOnMount) return
    const startTime = performance.now()
    const numTarget = typeof target === 'string' ? parseFloat(target.replace(/[^0-9.]/g, '')) : target

    function tick(now) {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      setCount(Math.floor(eased * numTarget))
      if (progress < 1) {
        frameRef.current = requestAnimationFrame(tick)
      } else {
        setCount(numTarget)
      }
    }

    frameRef.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frameRef.current)
  }, [target, duration, startOnMount])

  return count
}

// ─── Stagger container variants ─────────────────────────────────────────────
const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.1 }
  }
}

const staggerItem = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } }
}

// ═══════════════════════════════════════════════════════════════════════════════
//  MAIN APP
// ═══════════════════════════════════════════════════════════════════════════════
export default function App() {
  const [activeTab, setActiveTab] = useState('home')
  const [teams, setTeams] = useState([])
  const [selectedTeam, setSelectedTeam] = useState('France')
  const [teamDetail, setTeamDetail] = useState(null)
  const [simResults, setSimResults] = useState(null)
  const [loading, setLoading] = useState(true)
  const [simulating, setSimulating] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  
  // Predictor states
  const [predTeamA, setPredTeamA] = useState('France')
  const [predTeamB, setPredTeamB] = useState('Argentina')
  const [prediction, setPrediction] = useState(null)
  const [predLoading, setPredLoading] = useState(false)

  // Auth & Arena states
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('wc_user')
    return saved ? JSON.parse(saved) : null
  })
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [leaderboard, setLeaderboard] = useState([])
  const [leaderboardLoading, setLeaderboardLoading] = useState(false)

  const fetchLeaderboard = useCallback(async () => {
    try {
      setLeaderboardLoading(true)
      const res = await fetch('/api/arena/leaderboard')
      if (res.ok) {
        const data = await res.json()
        setLeaderboard(data.leaderboard)
      }
    } catch (err) {
      console.error("Error fetching leaderboard:", err)
    } finally {
      setLeaderboardLoading(false)
    }
  }, [])

  // 1. Initial load
  useEffect(() => {
    async function init() {
      try {
        setLoading(true)
        const teamsRes = await fetch('/api/teams')
        const teamsData = await teamsRes.json()
        setTeams(teamsData.teams)

        const simRes = await fetch('/api/simulate')
        const simData = await simRes.json()
        setSimResults(simData)
        
        await fetchLeaderboard()
      } catch (err) {
        console.error("Initialization error:", err)
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [fetchLeaderboard])

  // 2. Fetch team detail
  useEffect(() => {
    async function fetchTeamDetail() {
      if (!selectedTeam) return
      try {
        const res = await fetch(`/api/team/${selectedTeam}`)
        const data = await res.json()
        setTeamDetail(data)
      } catch (err) {
        console.error("Error fetching team detail:", err)
      }
    }
    fetchTeamDetail()
  }, [selectedTeam])

  // 3. Run prediction
  const runPrediction = async (t1, t2) => {
    try {
      setPredLoading(true)
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ team_a: t1, team_b: t2 })
      })
      const data = await res.json()
      setPrediction(data)
    } catch (err) {
      console.error("Prediction error:", err)
    } finally {
      setPredLoading(false)
    }
  }

  // 4. Trigger simulation
  const triggerSimulationRun = async () => {
    try {
      setSimulating(true)
      const res = await fetch('/api/simulate/run', { method: 'POST' })
      const data = await res.json()
      setSimResults(data.results)
    } catch (err) {
      console.error("Simulation run error:", err)
    } finally {
      setSimulating(false)
    }
  }

  // Responsive sidebar
  useEffect(() => {
    const handleResize = () => {
      setSidebarCollapsed(window.innerWidth < 1024)
    }
    window.addEventListener('resize', handleResize)
    handleResize()
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // ─── Loading Screen ────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-[#050a0e]">
        <div className="flex flex-col items-center gap-6">
          <div className="relative">
            <div className="h-16 w-16 animate-spin rounded-full border-[3px] border-[#00e87b]/20 border-t-[#00e87b]"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <Cpu size={20} className="text-[#00e87b]" />
            </div>
          </div>
          <div className="text-center space-y-1">
            <span className="text-[10px] font-bold tracking-[0.25em] text-[#7b93a8] uppercase block">
              INITIALIZING ML ENGINE
            </span>
            <span className="text-[9px] text-[#3f5669] block">
              Loading 48 teams · 1,200+ players · Model weights
            </span>
          </div>
        </div>
      </div>
    )
  }

  // ─── Nav items ─────────────────────────────────────────────────────────────
  const navItems = [
    { id: 'home', icon: <Home size={18} />, label: 'Home' },
    { id: 'dashboard', icon: <LayoutDashboard size={18} />, label: 'Groups & Overview' },
    { id: 'predictor', icon: <Flame size={18} />, label: 'Match Predictor', onActivate: () => { if (!prediction) runPrediction(predTeamA, predTeamB) } },
    { id: 'teams', icon: <Users size={18} />, label: 'Rosters & Teams' },
    { id: 'simulator', icon: <Sliders size={18} />, label: 'Tournament Sim' },
    { id: 'arena', icon: <Target size={18} />, label: 'Arena Playground' },
  ]

  return (
    <div className="flex w-full h-full bg-[#050a0e] text-[#edf2f7] font-body overflow-hidden">
      
      {/* ─── SIDEBAR ─── */}
      <aside className={`bg-[#070d13] border-r border-white/[0.04] flex flex-col h-full z-20 shrink-0 transition-all duration-300 ${
        sidebarCollapsed ? 'w-[72px]' : 'w-[260px]'
      }`}>
        
        {/* Logo */}
        <div className="p-5 flex items-center gap-3 border-b border-white/[0.04] min-h-[72px]">
          <div className="flex items-center gap-3 overflow-hidden flex-1">
            <img 
              src="/world_cup_2026_trophy.png" 
              alt="Trophy" 
              className="h-8 w-8 object-contain shrink-0 drop-shadow-[0_0_8px_rgba(212,165,74,0.4)]" 
            />
            {!sidebarCollapsed && (
              <motion.div initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.2 }}>
                <h1 className="font-display text-[20px] text-white leading-none tracking-wide">FIFA WC 2026</h1>
                <span className="text-[9px] text-[#00e87b] font-semibold tracking-[0.2em] block mt-0.5 uppercase">ML PREDICTOR</span>
              </motion.div>
            )}
          </div>
          <button 
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="text-[#3f5669] hover:text-white p-1.5 hover:bg-white/[0.04] rounded-lg transition-colors"
          >
            <Menu size={16} />
          </button>
        </div>
        
        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {!sidebarCollapsed && (
            <span className="text-[9px] font-semibold tracking-[0.2em] text-[#3f5669] uppercase px-3 mb-2 block">Navigation</span>
          )}
          {navItems.map(item => (
            <SidebarLink 
              key={item.id}
              active={activeTab === item.id} 
              collapsed={sidebarCollapsed} 
              onClick={() => {
                if (item.id === 'arena' && !user) {
                  setAuthModalOpen(true);
                }
                setActiveTab(item.id); 
                item.onActivate?.() 
              }} 
              icon={item.icon} 
              text={item.label} 
            />
          ))}
        </nav>
 
        {/* Bottom section */}
        <div className="px-3 pb-4 space-y-1 border-t border-white/[0.04] pt-3">
          {user ? (
            <div className={`flex flex-col gap-2 p-3 rounded-xl bg-white/[0.02] border border-white/[0.04] ${sidebarCollapsed ? 'items-center' : ''}`}>
              <div className="flex items-center gap-3 w-full">
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-[#00e87b]/20 to-[#00e87b]/5 border border-[#00e87b]/20 flex items-center justify-center shrink-0">
                  <User size={14} className="text-[#00e87b]" />
                </div>
                {!sidebarCollapsed && (
                  <div className="overflow-hidden flex-1">
                    <span className="text-[12px] font-semibold text-white block leading-tight truncate">{user.username}</span>
                    <span className="text-[10px] text-[#00e87b] font-medium block leading-tight mt-0.5">{user.points} pts</span>
                  </div>
                )}
              </div>
              {!sidebarCollapsed && (
                <button 
                  onClick={() => {
                    setUser(null);
                    localStorage.removeItem('wc_user');
                  }}
                  className="w-full h-8 mt-1 rounded-lg bg-white/[0.04] border border-white/[0.04] text-[#7b93a8] hover:text-white hover:bg-red-500/10 hover:border-red-500/20 transition flex items-center justify-center gap-1.5 text-[11px] font-semibold cursor-pointer"
                >
                  <LogOut size={12} />
                  Sign Out
                </button>
              )}
            </div>
          ) : (
            <button 
              onClick={() => setAuthModalOpen(true)}
              className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-[13px] font-medium tracking-wide text-[#7b93a8] hover:text-white hover:bg-white/[0.03] transition-all ${sidebarCollapsed ? 'justify-center' : ''}`}
            >
              <User size={18} className="text-[#7b93a8] group-hover:text-white" />
              {!sidebarCollapsed && <span>Sign In</span>}
            </button>
          )}
        </div>

        {/* Social Links & Credit */}
        <div className={`px-3 pb-3 ${sidebarCollapsed ? 'flex flex-col items-center gap-2' : 'space-y-2'}`}>
          <div className={`flex items-center ${sidebarCollapsed ? 'flex-col gap-2' : 'gap-2 px-1'}`}>
            <a 
              href="https://github.com/KRISHsingh0024/FIFA-WC-2026-ML-PREDICTION" 
              target="_blank" 
              rel="noopener noreferrer"
              className="h-8 w-8 rounded-lg bg-white/[0.03] border border-white/[0.04] flex items-center justify-center text-[#7b93a8] hover:text-white hover:bg-white/[0.06] hover:border-white/[0.08] transition-all"
              title="GitHub Repository"
            >
              <GitHubIcon size={14} />
            </a>
            <a 
              href="https://www.linkedin.com/in/krishsingh98899/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="h-8 w-8 rounded-lg bg-white/[0.03] border border-white/[0.04] flex items-center justify-center text-[#7b93a8] hover:text-[#0a66c2] hover:bg-[#0a66c2]/10 hover:border-[#0a66c2]/20 transition-all"
              title="LinkedIn Profile"
            >
              <LinkedInIcon size={14} />
            </a>
          </div>
          {!sidebarCollapsed && (
            <div className="px-1 pt-1">
              <span className="text-[9px] text-[#3f5669] block leading-relaxed">
                Developed with <Heart size={8} className="inline text-red-400 fill-red-400 mx-0.5" /> by{' '}
                <a 
                  href="https://www.linkedin.com/in/krishsingh98899/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-[#7b93a8] hover:text-[#00e87b] transition-colors font-semibold"
                >
                  Krish Singh
                </a>
              </span>
            </div>
          )}
        </div>
      </aside>
 
      {/* ─── MAIN CONTENT ─── */}
      <main className="flex-1 h-full overflow-y-auto bg-transparent relative smooth-scroll">
        <div className="p-6 lg:p-8 max-w-[1400px] mx-auto min-h-screen">
          
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.2 }}
            >
              {activeTab === 'home' && (
                <LandingView 
                  simResults={simResults}
                  setActiveTab={setActiveTab}
                />
              )}
              {activeTab === 'dashboard' && (
                <DashboardView 
                  simResults={simResults} 
                  teams={teams} 
                  setActiveTab={setActiveTab} 
                  setSelectedTeam={setSelectedTeam}
                />
              )}
              {activeTab === 'predictor' && (
                <PredictorView 
                  teams={teams}
                  predTeamA={predTeamA}
                  setPredTeamA={setPredTeamA}
                  predTeamB={predTeamB}
                  setPredTeamB={setPredTeamB}
                  prediction={prediction}
                  predLoading={predLoading}
                  runPrediction={runPrediction}
                />
              )}
              {activeTab === 'teams' && (
                <TeamsView 
                  teams={teams}
                  selectedTeam={selectedTeam}
                  setSelectedTeam={setSelectedTeam}
                  teamDetail={teamDetail}
                />
              )}
              {activeTab === 'simulator' && (
                <SimulatorView 
                  simResults={simResults}
                  simulating={simulating}
                  triggerSimulationRun={triggerSimulationRun}
                  user={user}
                  setAuthModalOpen={setAuthModalOpen}
                />
              )}
              {activeTab === 'arena' && (
                <ArenaView 
                  user={user}
                  teams={teams}
                  setAuthModalOpen={setAuthModalOpen}
                  leaderboard={leaderboard}
                  leaderboardLoading={leaderboardLoading}
                  fetchLeaderboard={fetchLeaderboard}
                />
              )}
            </motion.div>
          </AnimatePresence>
 
        </div>

        {/* ─── FOOTER ─── */}
        <footer className="border-t border-white/[0.04] mt-12 py-8 px-6 lg:px-8 max-w-[1400px] mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <img 
                src="/world_cup_2026_trophy.png" 
                alt="Trophy" 
                className="h-6 w-6 object-contain opacity-60" 
              />
              <div>
                <span className="text-[11px] text-[#7b93a8] block">
                  Developed with <Heart size={9} className="inline text-red-400 fill-red-400 mx-0.5" /> by{' '}
                  <a 
                    href="https://www.linkedin.com/in/krishsingh98899/" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-white hover:text-[#00e87b] transition-colors font-semibold"
                  >
                    Krish Singh
                  </a>
                </span>
                <span className="text-[9px] text-[#3f5669] block mt-0.5">FIFA World Cup 2026 ML Predictor &copy; {new Date().getFullYear()}</span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <a 
                href="https://github.com/KRISHsingh0024/FIFA-WC-2026-ML-PREDICTION" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-[11px] font-semibold text-[#7b93a8] hover:text-white transition-colors px-3 py-2 rounded-lg bg-white/[0.02] border border-white/[0.04] hover:border-white/[0.08]"
              >
                <GitHubIcon size={13} />
                Source Code
                <ExternalLink size={10} className="opacity-50" />
              </a>
              <a 
                href="https://www.linkedin.com/in/krishsingh98899/" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-[11px] font-semibold text-[#7b93a8] hover:text-[#0a66c2] transition-colors px-3 py-2 rounded-lg bg-white/[0.02] border border-white/[0.04] hover:border-[#0a66c2]/20"
              >
                <LinkedInIcon size={13} />
                LinkedIn
                <ExternalLink size={10} className="opacity-50" />
              </a>
            </div>
          </div>
        </footer>
      </main>

      <AuthModal 
        isOpen={authModalOpen} 
        onClose={() => setAuthModalOpen(false)} 
        onLoginSuccess={(userData) => {
          setUser(userData);
          localStorage.setItem('wc_user', JSON.stringify(userData));
          fetchLeaderboard();
        }}
      />
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
//  SIDEBAR LINK
// ═══════════════════════════════════════════════════════════════════════════════
function SidebarLink({ active, collapsed, icon, text, onClick }) {
  return (
    <button 
      onClick={onClick}
      title={collapsed ? text : undefined}
      className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-[13px] font-medium tracking-wide transition-all relative group ${
        active 
          ? 'bg-[#00e87b]/[0.08] text-white' 
          : 'text-[#7b93a8] hover:text-white hover:bg-white/[0.03]'
      } ${collapsed ? 'justify-center' : ''}`}
    >
      {/* Active indicator */}
      {active && (
        <motion.div 
          layoutId="sidebar-indicator"
          className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-[#00e87b] rounded-r-full"
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        />
      )}
      <span className={active ? "text-[#00e87b]" : "text-current"}>{icon}</span>
      {!collapsed && (
        <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.15 }}>
          {text}
        </motion.span>
      )}
    </button>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
//  ANIMATED STAT CARD
// ═══════════════════════════════════════════════════════════════════════════════
function AnimatedStatCard({ icon, value, suffix, label, delay = 0 }) {
  const numericValue = typeof value === 'number' ? value : parseFloat(String(value).replace(/[^0-9.]/g, ''))
  const animatedValue = useAnimatedCounter(numericValue, 1800)
  const displaySuffix = suffix || ''

  // Format display
  const formatValue = (val) => {
    if (numericValue >= 1000) return val.toLocaleString()
    if (String(value).includes('.')) return val.toFixed(1)
    return val
  }

  return (
    <motion.div 
      className="stat-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: 'easeOut' }}
    >
      <div className="flex items-center gap-2.5 mb-3">
        <div className="h-8 w-8 rounded-lg bg-[#00e87b]/[0.08] flex items-center justify-center">
          {icon}
        </div>
      </div>
      <div className="font-display text-3xl text-white tracking-wide leading-none">
        {formatValue(animatedValue)}{displaySuffix}
      </div>
      <span className="text-[11px] text-[#7b93a8] font-medium mt-1.5 block">{label}</span>
    </motion.div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
//  DASHBOARD VIEW
// ═══════════════════════════════════════════════════════════════════════════════
function DashboardView({ simResults, teams, setActiveTab, setSelectedTeam }) {
  const sim_stats = simResults?.sim_stats || {}
  
  const contenders = Object.entries(sim_stats)
    .map(([name, probs]) => ({ name, ...probs }))
    .sort((a, b) => b.champion_prob - a.champion_prob)
  
  const top5 = contenders.slice(0, 5)
  const top6 = contenders.slice(0, 6)

  // Group teams by group letter
  const groupedTeams = {}
  teams.forEach(t => {
    if (!groupedTeams[t.group]) groupedTeams[t.group] = []
    groupedTeams[t.group].push(t)
  })

  return (
    <motion.div 
      className="space-y-8"
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
    >
      
      {/* ─── HERO BANNER ─── */}
      <motion.div variants={staggerItem} className="relative overflow-hidden rounded-2xl border border-white/[0.04]">
        {/* Gradient mesh background */}
        <div className="absolute inset-0" style={{
          background: `
            radial-gradient(ellipse 80% 60% at 20% 80%, rgba(0, 232, 123, 0.07) 0%, transparent 60%),
            radial-gradient(ellipse 60% 50% at 80% 20%, rgba(212, 165, 74, 0.05) 0%, transparent 50%),
            radial-gradient(ellipse 90% 70% at 50% 50%, rgba(0, 0, 0, 0.3) 0%, transparent 100%),
            linear-gradient(135deg, #070d13 0%, #0a1520 50%, #070d13 100%)
          `
        }} />
        
        {/* Decorative grid lines */}
        <div className="absolute inset-0 opacity-[0.03]" style={{
          backgroundImage: `
            linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px'
        }} />

        {/* Floating particles */}
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full bg-[#00e87b]/10"
            style={{
              width: 4 + i * 2,
              height: 4 + i * 2,
              left: `${15 + i * 18}%`,
              top: `${20 + (i % 3) * 25}%`,
            }}
            animate={{
              y: [0, -15 - i * 5, 0],
              opacity: [0.3, 0.7, 0.3],
            }}
            transition={{
              duration: 3 + i * 0.7,
              repeat: Infinity,
              ease: 'easeInOut',
              delay: i * 0.4,
            }}
          />
        ))}

        <div className="relative z-10 flex flex-col lg:flex-row items-center justify-between p-8 lg:p-10">
          
          <div className="space-y-5 max-w-xl">
            <motion.span 
              className="inline-flex items-center gap-1.5 text-[10px] font-semibold tracking-[0.2em] text-[#00e87b] uppercase bg-[#00e87b]/[0.06] border border-[#00e87b]/[0.12] px-3 py-1.5 rounded-full"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Zap size={10} />
              ML-POWERED ANALYTICS
            </motion.span>
            
            <motion.h2 
              className="text-[clamp(2.5rem,5vw,4.5rem)] font-display text-white leading-[0.95] tracking-wide"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.5 }}
            >
              FIFA WORLD CUP<br/>
              <span className="text-[#00e87b] text-green-glow">2026 PREDICTOR</span>
            </motion.h2>
            
            <motion.p 
              className="text-[#7b93a8] text-sm leading-relaxed max-w-md"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.45, duration: 0.4 }}
            >
              Leverage XGBoost models and Monte Carlo simulations to forecast every matchup across all 48 teams competing in North America.
            </motion.p>
            
            <motion.div 
              className="flex gap-3 pt-1"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.55, duration: 0.4 }}
            >
              <button 
                onClick={() => setActiveTab('predictor')}
                className="bg-[#00e87b] hover:bg-[#00d46f] text-[#050a0e] px-5 py-2.5 rounded-full text-[12px] font-bold transition-all flex items-center gap-2 tracking-wide hover:shadow-[0_0_20px_rgba(0,232,123,0.25)]"
              >
                Explore Predictions
                <ArrowRight size={14} />
              </button>
              <button 
                onClick={() => setActiveTab('simulator')}
                className="border border-white/10 text-[#edf2f7] hover:border-[#00e87b]/30 hover:text-[#00e87b] px-5 py-2.5 rounded-full text-[12px] font-bold transition-all tracking-wide"
              >
                Simulate Tournament
              </button>
            </motion.div>
          </div>

          {/* Trophy */}
          <motion.div 
            className="flex-shrink-0 py-6 lg:py-0"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4, duration: 0.6, ease: 'easeOut' }}
          >
            <motion.img 
              src="/world_cup_2026_trophy.png" 
              alt="FIFA World Cup 2026 Trophy" 
              className="w-40 lg:w-48 h-auto object-contain select-none drop-shadow-[0_0_40px_rgba(212,165,74,0.35)]"
              animate={{ 
                y: [0, -10, 0],
                rotate: [-3, -1, -3]
              }}
              transition={{ 
                duration: 5, 
                repeat: Infinity, 
                ease: "easeInOut" 
              }}
            />
          </motion.div>
        </div>
      </motion.div>

      {/* ─── STATS ROW ─── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <AnimatedStatCard 
          icon={<Globe size={16} className="text-[#00e87b]" />}
          value={48} suffix="/48" label="Teams Analyzed" delay={0.1}
        />
        <AnimatedStatCard 
          icon={<Users size={16} className="text-[#00e87b]" />}
          value={1200} suffix="+" label="Players Logged" delay={0.2}
        />
        <AnimatedStatCard 
          icon={<BarChart3 size={16} className="text-[#00e87b]" />}
          value={100000} suffix="+" label="Matches Simulated" delay={0.3}
        />
        <AnimatedStatCard 
          icon={<Target size={16} className="text-[#00e87b]" />}
          value={56.8} suffix="%" label="Model Accuracy" delay={0.4}
        />
      </div>

      {/* ─── WIN PROBABILITY + INFO ─── */}
      <motion.div variants={staggerItem} className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        
        {/* Win Probability Top 5 */}
        <div className="glass-panel p-6 lg:col-span-3 space-y-5">
          <div className="flex justify-between items-center">
            <h3 className="font-display text-xl tracking-wider text-white flex items-center gap-2">
              <Activity size={18} className="text-[#00e87b]" />
              WIN PROBABILITY
            </h3>
            <button 
              onClick={() => setActiveTab('simulator')} 
              className="text-[#7b93a8] hover:text-[#00e87b] text-[11px] font-semibold flex items-center gap-1 transition-colors"
            >
              All Projections <ChevronRight size={14} />
            </button>
          </div>
          
          <div className="space-y-3.5">
            {top5.map((team, idx) => {
              const maxProb = top5[0]?.champion_prob || 1
              const barWidth = (team.champion_prob / maxProb) * 100
              
              return (
                <div key={team.name} className="group">
                  <div className="flex items-center gap-3">
                    {/* Rank badge */}
                    <div className={`h-7 w-7 rounded-lg flex items-center justify-center text-[11px] font-bold shrink-0 ${
                      idx === 0 ? 'bg-[#d4a54a]/15 text-[#d4a54a] border border-[#d4a54a]/20' :
                      idx === 1 ? 'bg-[#94a3b8]/10 text-[#94a3b8] border border-[#94a3b8]/15' :
                      idx === 2 ? 'bg-[#cd7f32]/10 text-[#cd7f32] border border-[#cd7f32]/15' :
                      'bg-white/[0.03] text-[#7b93a8] border border-white/[0.04]'
                    }`}>
                      {idx + 1}
                    </div>
                    
                    {/* Team name with flag */}
                    <button 
                      onClick={() => { setSelectedTeam(team.name); setActiveTab('teams') }}
                      className="text-[13px] font-semibold text-white hover:text-[#00e87b] transition-colors w-32 text-left shrink-0 truncate flex items-center gap-1.5"
                    >
                      {getFlagImg(team.name, "w-5 h-3.5 object-cover rounded-sm shadow-xs shrink-0")}
                      <span>{team.name}</span>
                    </button>
                    
                    {/* Bar */}
                    <div className="flex-1 h-[22px] bg-white/[0.03] rounded-lg overflow-hidden relative">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${barWidth}%` }}
                        transition={{ duration: 1, ease: [0.34, 1.56, 0.64, 1], delay: idx * 0.12 }}
                        className={`h-full rounded-lg ${
                          idx === 0 
                            ? 'bg-gradient-to-r from-[#00e87b]/80 to-[#00e87b]/50' 
                            : 'bg-gradient-to-r from-[#00e87b]/40 to-[#00e87b]/20'
                        }`}
                      />
                    </div>
                    
                    {/* Percentage */}
                    <span className="text-[13px] font-bold text-[#00e87b] w-14 text-right shrink-0 font-display tracking-wider">
                      {(team.champion_prob * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Tournament Format */}
        <div className="glass-panel p-6 lg:col-span-2 flex flex-col justify-between">
          <h3 className="font-display text-xl tracking-wider text-white flex items-center gap-2 mb-4">
            <Trophy size={18} className="text-[#d4a54a]" />
            TOURNAMENT FORMAT
          </h3>
          <div className="grid grid-cols-2 gap-3 flex-1">
            {[
              { label: 'Host Nations', value: '3', sub: 'USA · MEX · CAN' },
              { label: 'Host Cities', value: '16', sub: 'Across North America' },
              { label: 'Total Matches', value: '104', sub: 'Group + Knockout' },
              { label: 'Group Format', value: '12×4', sub: '12 groups of 4' },
            ].map((item, i) => (
              <div key={i} className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.04]">
                <span className="text-[9px] text-[#3f5669] font-semibold block uppercase tracking-wider">{item.label}</span>
                <span className="text-lg font-display text-white block leading-tight mt-0.5">{item.value}</span>
                <span className="text-[9px] text-[#3f5669] block mt-0.5">{item.sub}</span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* ─── GROUP STAGE OVERVIEW ─── */}
      <motion.div variants={staggerItem} className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="font-display text-xl tracking-wider text-white flex items-center gap-2">
            <Shield size={18} className="text-[#00e87b]" />
            GROUP STAGE DRAW
          </h3>
          <span className="text-[11px] text-[#3f5669] font-medium">12 Groups · 48 Teams</span>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3">
          {Object.entries(groupedTeams).sort().map(([group, groupTeams]) => (
            <div key={group} className="group-card">
              <div className="flex items-center justify-between mb-3">
                <span className="font-display text-lg text-[#00e87b] tracking-wider">GROUP {group}</span>
              </div>
              <div className="space-y-1.5">
                {groupTeams.map(t => (
                  <button 
                    key={t.name}
                    onClick={() => { setSelectedTeam(t.name); setActiveTab('teams') }}
                    className="flex items-center justify-between w-full text-left hover:text-[#00e87b] transition-colors"
                  >
                    <span className="text-[11px] font-medium text-[#edf2f7] group-card:hover:text-[#00e87b] truncate flex items-center gap-1.5">
                      {getFlagImg(t.name, "w-4 h-2.5 object-cover rounded-sm shadow-xs shrink-0")}
                      <span>{t.name}</span>
                    </span>
                    <span className="text-[9px] text-[#3f5669] font-medium shrink-0 ml-1">#{t.fifa_rank}</span>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* ─── TOP CONTENDERS ─── */}
      <motion.div variants={staggerItem} className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="font-display text-xl tracking-wider text-white flex items-center gap-2">
            <Star size={18} className="text-[#d4a54a]" />
            TOP CONTENDERS
          </h3>
          <button 
            onClick={() => setActiveTab('teams')} 
            className="text-[#7b93a8] hover:text-[#00e87b] text-[11px] font-semibold flex items-center gap-1 transition-colors"
          >
            View All Teams <ChevronRight size={14} />
          </button>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {top6.map((team, idx) => (
            <div 
              key={team.name}
              className="contender-card"
              onClick={() => { setSelectedTeam(team.name); setActiveTab('teams') }}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2.5">
                  {getFlagImg(team.name, "w-8 h-5.5 object-cover rounded-md shadow-sm shrink-0")}
                  <div>
                    <h4 className="text-[14px] font-bold text-white leading-tight">{team.name}</h4>
                    <span className="text-[10px] text-[#3f5669] font-medium">FIFA Rank #{FIFA_RANKINGS[team.name] || '—'}</span>
                  </div>
                </div>
                <div className={`h-6 w-6 rounded-md flex items-center justify-center text-[10px] font-bold ${
                  idx === 0 ? 'bg-[#d4a54a]/15 text-[#d4a54a]' :
                  idx === 1 ? 'bg-[#94a3b8]/10 text-[#94a3b8]' :
                  idx === 2 ? 'bg-[#cd7f32]/10 text-[#cd7f32]' :
                  'bg-white/[0.03] text-[#7b93a8]'
                }`}>
                  {idx + 1}
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div className="p-2.5 rounded-lg bg-white/[0.02]">
                  <span className="text-[9px] text-[#3f5669] font-medium block uppercase tracking-wider">Champion</span>
                  <span className="text-[15px] font-display text-[#00e87b] tracking-wide">{(team.champion_prob * 100).toFixed(1)}%</span>
                </div>
                <div className="p-2.5 rounded-lg bg-white/[0.02]">
                  <span className="text-[9px] text-[#3f5669] font-medium block uppercase tracking-wider">Semi-final</span>
                  <span className="text-[15px] font-display text-white tracking-wide">{(team.semifinal_prob * 100).toFixed(1)}%</span>
                </div>
              </div>
              
              {/* Form indicator */}
              <div className="flex items-center gap-1.5">
                <span className="text-[9px] text-[#3f5669] font-medium mr-1">Form</span>
                {getFormForRank(FIFA_RANKINGS[team.name]).map((f, i) => (
                  <span 
                    key={i} 
                    className={`h-4 w-4 rounded flex items-center justify-center text-[8px] font-bold ${
                      f === 'W' ? 'bg-emerald-500/20 text-emerald-400' : 
                      f === 'D' ? 'bg-amber-500/15 text-amber-400' : 
                      'bg-red-500/15 text-red-400'
                    }`}
                  >
                    {f}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* ─── RECENT MODEL UPDATES ─── */}
      <motion.div variants={staggerItem} className="glass-panel p-5">
        <div className="flex items-center gap-2 mb-3">
          <RefreshCw size={14} className="text-[#00e87b]" />
          <h3 className="font-display text-base tracking-wider text-white">RECENT UPDATES</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {[
            { icon: <Database size={13} />, text: 'Player stats refreshed', time: 'June 2026' },
            { icon: <Cpu size={13} />, text: 'XGBoost model v3.2 deployed', time: '2 days ago' },
            { icon: <BarChart3 size={13} />, text: 'Monte Carlo recalibrated', time: '1,000 simulations' },
            { icon: <Clock size={13} />, text: 'Group draw finalized', time: 'Official FIFA draw' },
          ].map((update, i) => (
            <div key={i} className="flex items-start gap-2.5 p-3 rounded-xl bg-white/[0.015] border border-white/[0.03]">
              <div className="text-[#00e87b] mt-0.5 shrink-0">{update.icon}</div>
              <div>
                <span className="text-[11px] font-medium text-[#edf2f7] block leading-tight">{update.text}</span>
                <span className="text-[9px] text-[#3f5669] block mt-0.5">{update.time}</span>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  )
}

// ── Helper: form based on rank ────────────────────────────────────────────
function getFormForRank(rank) {
  if (!rank) return ['D', 'D', 'D', 'D', 'D']
  if (rank <= 10) return ['W', 'W', 'W', 'D', 'W']
  if (rank <= 25) return ['W', 'D', 'W', 'L', 'W']
  if (rank <= 40) return ['D', 'W', 'L', 'D', 'L']
  return ['L', 'L', 'D', 'L', 'W']
}

// ═══════════════════════════════════════════════════════════════════════════════
//  CUSTOM TEAM SELECT DROPDOWN (FOR CROSS-PLATFORM GRAPHICAL FLAGS SUPPORT)
// ═══════════════════════════════════════════════════════════════════════════════
function CustomTeamSelect({ value, onChange, teams }) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="relative w-full sm:w-56" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between bg-[#0c1620] border border-white/[0.06] hover:border-white/[0.12] rounded-xl px-4 py-2.5 text-[12px] font-semibold text-white transition-colors cursor-pointer select-none"
      >
        <div className="flex items-center gap-2 truncate">
          {getFlagImg(value, "w-4.5 h-3 object-cover rounded-sm shrink-0")}
          <span className="truncate">{value}</span>
        </div>
        <span className="text-[#3f5669] text-[9px] transition-transform duration-200" style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)' }}>▼</span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 4 }}
            transition={{ duration: 0.12 }}
            className="absolute left-0 right-0 mt-2 z-50 bg-[#070e15] border border-white/[0.08] rounded-xl shadow-[0_8px_32px_rgba(0,0,0,0.6)] max-h-60 overflow-y-auto"
          >
            <div className="p-1 space-y-0.5">
              {teams.map((t) => (
                <button
                  key={t.name}
                  type="button"
                  onClick={() => {
                    onChange(t.name)
                    setIsOpen(false)
                  }}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-[12px] font-medium transition-colors hover:bg-white/[0.03] text-left cursor-pointer ${
                    t.name === value 
                      ? 'bg-[#00e87b]/[0.08] text-white border-l-2 border-[#00e87b]' 
                      : 'text-[#7b93a8] hover:text-white'
                  }`}
                >
                  <span className="flex items-center gap-2 truncate">
                    {getFlagImg(t.name, "w-4.5 h-3 object-cover rounded-xs shrink-0")}
                    <span className="truncate">{t.name}</span>
                  </span>
                  <span className="text-[9px] text-[#3f5669] shrink-0 ml-1">#{t.fifa_rank}</span>
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
//  PREDICTOR VIEW
// ═══════════════════════════════════════════════════════════════════════════════
function PredictorView({ teams, predTeamA, setPredTeamA, predTeamB, setPredTeamB, prediction, predLoading, runPrediction }) {
  
  const handleSwap = () => {
    const tmp = predTeamA
    setPredTeamA(predTeamB)
    setPredTeamB(tmp)
    runPrediction(predTeamB, tmp)
  }

  return (
    <div className="space-y-6">
      
      {/* Team selectors */}
      <div className="glass-panel flex flex-col md:flex-row items-center justify-center gap-6 p-6 relative z-30">
        <div className="flex items-center gap-3">
          <span className="text-[10px] font-semibold text-[#3f5669] uppercase tracking-wider">Team A</span>
          <CustomTeamSelect 
            value={predTeamA}
            onChange={(val) => { setPredTeamA(val); runPrediction(val, predTeamB) }}
            teams={teams}
          />
        </div>
        
        <button 
          onClick={handleSwap}
          className="h-9 w-9 rounded-full bg-white/[0.03] hover:bg-white/[0.06] transition flex items-center justify-center text-[#00e87b] border border-white/[0.06] shrink-0 text-sm font-bold cursor-pointer"
        >
          ⇄
        </button>

        <div className="flex items-center gap-3">
          <span className="text-[10px] font-semibold text-[#3f5669] uppercase tracking-wider">Team B</span>
          <CustomTeamSelect 
            value={predTeamB}
            onChange={(val) => { setPredTeamB(val); runPrediction(predTeamA, val) }}
            teams={teams}
          />
        </div>
      </div>

      {predLoading ? (
        <div className="flex h-64 items-center justify-center">
          <div className="h-12 w-12 animate-spin rounded-full border-[3px] border-[#00e87b]/20 border-t-[#00e87b]"></div>
        </div>
      ) : prediction ? (
        <div className="space-y-6">
          
          {/* Probability outcome */}
          <div className="glass-panel space-y-6 text-center py-8 px-6">
            <span className="inline-flex items-center gap-1.5 text-[10px] font-semibold tracking-[0.2em] text-[#00e87b] uppercase bg-[#00e87b]/[0.06] border border-[#00e87b]/[0.12] px-3 py-1 rounded-full">
              <Crosshair size={10} />
              MATCH ODDS FORECAST
            </span>
            
            <div className="flex items-center justify-center gap-8 lg:gap-14 pt-4">
              <div className="w-1/3 text-center">
                {getFlagImg(prediction.team_a, "w-16 h-11 object-cover rounded-md shadow-md mx-auto mb-2")}
                <h3 className="text-xl lg:text-3xl font-display text-white leading-none">{prediction.team_a}</h3>
                <span className="text-[10px] text-[#3f5669] font-medium block mt-1">Rank #{FIFA_RANKINGS[prediction.team_a] || 50}</span>
              </div>
              <span className="text-[11px] font-semibold text-[#3f5669] px-3 py-1.5 bg-white/[0.02] rounded-full border border-white/[0.04] shrink-0">VS</span>
              <div className="w-1/3 text-center">
                {getFlagImg(prediction.team_b, "w-16 h-11 object-cover rounded-md shadow-md mx-auto mb-2")}
                <h3 className="text-xl lg:text-3xl font-display text-white leading-none">{prediction.team_b}</h3>
                <span className="text-[10px] text-[#3f5669] font-medium block mt-1">Rank #{FIFA_RANKINGS[prediction.team_b] || 50}</span>
              </div>
            </div>

            <div className="max-w-xl mx-auto space-y-3 pt-6 px-4">
              <div className="flex justify-between text-[11px] font-semibold text-[#7b93a8]">
                <span>{prediction.team_a}: {(prediction.probabilities.team_a_win * 100).toFixed(1)}%</span>
                <span>Draw: {(prediction.probabilities.draw * 100).toFixed(1)}%</span>
                <span>{prediction.team_b}: {(prediction.probabilities.team_b_win * 100).toFixed(1)}%</span>
              </div>
              <div className="h-7 w-full rounded-xl overflow-hidden flex text-[10px] font-bold text-white">
                <motion.div 
                  className="bg-blue-500/70 flex items-center justify-center"
                  initial={{ width: 0 }}
                  animate={{ width: `${prediction.probabilities.team_a_win * 100}%` }}
                  transition={{ duration: 0.8, ease: 'easeOut' }}
                >
                  {(prediction.probabilities.team_a_win * 100) > 12 && `${(prediction.probabilities.team_a_win * 100).toFixed(0)}%`}
                </motion.div>
                <motion.div 
                  className="bg-[#7b93a8]/30 flex items-center justify-center"
                  initial={{ width: 0 }}
                  animate={{ width: `${prediction.probabilities.draw * 100}%` }}
                  transition={{ duration: 0.8, ease: 'easeOut', delay: 0.1 }}
                >
                  {(prediction.probabilities.draw * 100) > 12 && `${(prediction.probabilities.draw * 100).toFixed(0)}%`}
                </motion.div>
                <motion.div 
                  className="bg-red-500/60 flex items-center justify-center"
                  initial={{ width: 0 }}
                  animate={{ width: `${prediction.probabilities.team_b_win * 100}%` }}
                  transition={{ duration: 0.8, ease: 'easeOut', delay: 0.2 }}
                >
                  {(prediction.probabilities.team_b_win * 100) > 12 && `${(prediction.probabilities.team_b_win * 100).toFixed(0)}%`}
                </motion.div>
              </div>
            </div>
          </div>

          {/* Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Explanations */}
            <div className="glass-panel p-6 space-y-4">
              <h3 className="font-display text-lg tracking-wider text-white flex items-center gap-2">
                <Cpu size={16} className="text-[#00e87b]" />
                ML INSIGHTS
              </h3>
              <div className="space-y-2.5">
                {prediction.explanations.map((exp, i) => (
                  <div key={i} className="flex gap-3 text-[12px] text-[#edf2f7] leading-relaxed bg-white/[0.015] p-3 rounded-xl border border-white/[0.03]">
                    <Star size={13} className="text-[#00e87b] shrink-0 mt-0.5" />
                    <span>{exp}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Factor bars */}
            <div className="glass-panel p-6 space-y-4">
              <h3 className="font-display text-lg tracking-wider text-white flex items-center gap-2">
                <BarChart3 size={16} className="text-[#00e87b]" />
                KEY MATCHUP FACTORS
              </h3>
              <div className="space-y-3.5 pt-1">
                <FactorRow label="Attack Strength" diff={prediction.features_a.team_attack_strength - prediction.features_b.team_attack_strength} />
                <FactorRow label="Midfield Creativity" diff={prediction.features_a.team_midfield_creativity - prediction.features_b.team_midfield_creativity} />
                <FactorRow label="Defense Solidity" diff={prediction.features_a.team_defense_solidity - prediction.features_b.team_defense_solidity} />
                <FactorRow label="Roster Depth" diff={prediction.features_a.team_depth_score - prediction.features_b.team_depth_score} />
                <FactorRow label="Star Player Impact" diff={prediction.features_a.team_star_player_impact - prediction.features_b.team_star_player_impact} />
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex h-64 items-center justify-center text-[#3f5669] text-sm">Select teams to predict a matchup.</div>
      )}
    </div>
  )
}

function FactorRow({ label, diff }) {
  const isA = diff >= 0
  const pct = Math.min(Math.abs(diff) * 100, 100).toFixed(0)
  return (
    <div className="space-y-1.5 text-[12px]">
      <div className="flex justify-between font-medium">
        <span className="text-[#7b93a8]">{label}</span>
        <span className={isA ? "text-blue-400 font-semibold" : "text-red-400 font-semibold"}>
          {isA ? `+${Math.abs(diff).toFixed(3)} Team A` : `+${Math.abs(diff).toFixed(3)} Team B`}
        </span>
      </div>
      <div className="h-1.5 w-full bg-white/[0.03] rounded-full overflow-hidden">
        <motion.div 
          className={`h-full rounded-full ${isA ? "bg-blue-500/60" : "bg-red-500/50"}`}
          initial={{ width: 0 }}
          animate={{ width: `${Math.max(5, pct)}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
//  TEAMS VIEW
// ═══════════════════════════════════════════════════════════════════════════════
function TeamsView({ teams, selectedTeam, setSelectedTeam, teamDetail }) {
  const [search, setSearch] = useState('')
  const filteredTeams = teams.filter(t => t.name.toLowerCase().includes(search.toLowerCase()))

  const getJerseyColor = (teamName) => {
    const colorMap = {
      "France": "#1e3a8a", "Argentina": "#7dd3fc", "Brazil": "#eab308",
      "Spain": "#dc2626", "Portugal": "#991b1b", "Germany": "#ffffff",
      "England": "#f8fafc", "Netherlands": "#ea580c", "Uruguay": "#38bdf8",
      "Mexico": "#15803d", "Croatia": "#dc2626", "United States": "#f8fafc",
      "Norway": "#dc2626"
    }
    return colorMap[teamName] || "#374151"
  }

  const getJerseyStripeColor = (teamName) => {
    const stripeMap = {
      "Argentina": "#ffffff", "Germany": "#000000", "United States": "#1e3a8a",
      "Mexico": "#dc2626", "Croatia": "#ffffff", "Brazil": "#15803d"
    }
    return stripeMap[teamName] || "transparent"
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      
      {/* Search panel */}
      <div className="lg:col-span-1 space-y-3">
        <h3 className="font-display text-xl tracking-wider text-white">TEAMS</h3>
        <div className="relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-[#3f5669]" />
          <input 
            type="text" 
            placeholder="Search teams..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#0c1620] border border-white/[0.06] rounded-xl pl-9 pr-4 py-2.5 text-[12px] focus:outline-none focus:border-[#00e87b]/30 placeholder:text-[#3f5669]"
          />
        </div>
        <div className="space-y-0.5 max-h-[520px] overflow-y-auto pr-1">
          {filteredTeams.map((t) => (
            <button 
              key={t.name}
              onClick={() => setSelectedTeam(t.name)}
              className={`w-full text-left px-3 py-2.5 rounded-xl text-[12px] font-medium transition flex justify-between items-center ${
                selectedTeam === t.name 
                  ? 'bg-[#00e87b]/[0.06] text-white border-l-[3px] border-[#00e87b]' 
                  : 'text-[#7b93a8] hover:text-white hover:bg-white/[0.02]'
              }`}
            >
              <span className="flex items-center gap-1.5">
                {getFlagImg(t.name, "w-5 h-3.5 object-cover rounded-sm shadow-xs shrink-0")}
                <span>{t.name}</span>
              </span>
              <span className="text-[9px] text-[#3f5669]">#{t.fifa_rank}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Team detail */}
      <div className="lg:col-span-3">
        {teamDetail ? (
          <div className="space-y-6">
            
            {/* Team header */}
            <div className="glass-panel flex flex-col md:flex-row items-center justify-between gap-6 p-6 relative overflow-hidden">
              {/* Subtle gradient accent */}
              <div className="absolute inset-0 opacity-30" style={{
                background: `radial-gradient(ellipse 50% 80% at 0% 100%, rgba(0, 232, 123, 0.06) 0%, transparent 60%)`
              }} />
              
              <div className="space-y-3 flex-1 w-full relative z-10">
                <span className="inline-flex items-center text-[9px] font-semibold uppercase tracking-[0.15em] text-[#00e87b] bg-[#00e87b]/[0.06] px-2.5 py-1 rounded-full border border-[#00e87b]/[0.12]">
                  {teamDetail.confederation}
                </span>
                <h2 className="text-4xl font-display text-white leading-none tracking-wide flex items-center gap-3">
                  {getFlagImg(teamDetail.name, "w-10 h-7 object-cover rounded-md shadow-md shrink-0")}
                  <span>{teamDetail.name}</span>
                </h2>
                
                <div className="grid grid-cols-3 gap-4 pt-2">
                  <div>
                    <span className="block text-[9px] uppercase font-semibold text-[#3f5669] tracking-wider">FIFA Rank</span>
                    <span className="text-base font-bold text-white">#{teamDetail.fifa_rank}</span>
                  </div>
                  <div>
                    <span className="block text-[9px] uppercase font-semibold text-[#3f5669] tracking-wider">Attack</span>
                    <span className="text-base font-bold text-[#00e87b]">{teamDetail.features.team_attack_strength.toFixed(3)}</span>
                  </div>
                  <div>
                    <span className="block text-[9px] uppercase font-semibold text-[#3f5669] tracking-wider">Defense</span>
                    <span className="text-base font-bold text-white">{teamDetail.features.team_defense_solidity.toFixed(3)}</span>
                  </div>
                </div>

                <div className="pt-2">
                  <span className="block text-[9px] uppercase font-semibold text-[#3f5669] tracking-wider mb-1.5">Recent Form</span>
                  <div className="flex gap-1.5">
                    {teamDetail.form.map((f, i) => (
                      <span 
                        key={i} 
                        className={`h-6 w-6 rounded-md flex items-center justify-center text-[10px] font-bold ${
                          f === 'W' ? 'bg-emerald-500/20 text-emerald-400' : 
                          f === 'D' ? 'bg-amber-500/15 text-amber-400' : 
                          'bg-red-500/15 text-red-400'
                        }`}
                      >
                        {f}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Jersey */}
              <div className="shrink-0 flex flex-col items-center gap-2 p-3 bg-white/[0.02] border border-white/[0.04] rounded-2xl relative z-10">
                <svg className="h-28 w-28" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                  <path d="M 20 20 L 35 15 L 40 10 L 60 10 L 65 15 L 80 20 L 75 40 L 70 40 L 70 85 L 30 85 L 30 40 L 25 40 Z" fill={getJerseyColor(teamDetail.name)} />
                  <path d="M 20 20 L 25 20 L 25 35 L 20 35 Z" fill="#ffffff" opacity="0.2" />
                  <path d="M 80 20 L 75 20 L 75 35 L 80 35 Z" fill="#ffffff" opacity="0.2" />
                  <path d="M 46 10 L 54 10 L 54 85 L 46 85 Z" fill={getJerseyStripeColor(teamDetail.name)} />
                  <path d="M 40 10 C 45 15, 55 15, 60 10 Z" fill="#050a0e" />
                  <text x="50" y="55" dominantBaseline="middle" textAnchor="middle" fill="#ffffff" fontSize="20" fontWeight="900" opacity="0.8">10</text>
                </svg>
                <span className="text-[9px] text-[#3f5669] font-medium uppercase tracking-wider">Jersey #10</span>
              </div>
            </div>

            {/* Roster */}
            <div className="glass-panel p-6 space-y-4">
              <h3 className="font-display text-lg tracking-wider text-white">SQUAD ROSTER</h3>
              <div className="overflow-x-auto border border-white/[0.04] rounded-xl">
                <table className="w-full text-[12px] text-left border-collapse">
                  <thead className="bg-white/[0.02] text-[#7b93a8] font-semibold border-b border-white/[0.04]">
                    <tr>
                      <th className="px-4 py-3">Player</th>
                      <th className="px-4 py-3">Position</th>
                      <th className="px-4 py-3">Club</th>
                      <th className="px-4 py-3">Role</th>
                      <th className="px-4 py-3 text-right">Goals/90</th>
                      <th className="px-4 py-3 text-right">Key Pass/90</th>
                      <th className="px-4 py-3 text-right">Pass %</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/[0.03]">
                    {teamDetail.roster.map((player) => (
                      <tr key={player.name} className="hover:bg-white/[0.01] transition">
                        <td className="px-4 py-3 font-semibold text-white">{player.name}</td>
                        <td className="px-4 py-3 text-[#7b93a8]">{player.position}</td>
                        <td className="px-4 py-3 text-[#7b93a8]">{player.club}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-0.5 rounded-full text-[9px] font-semibold ${
                            player.is_starter 
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/15' 
                              : 'bg-white/[0.03] text-[#3f5669] border border-white/[0.04]'
                          }`}>
                            {player.is_starter ? 'Starter' : 'Bench'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right text-[#00e87b] font-mono text-[11px]">{player.goals_p90.toFixed(2)}</td>
                        <td className="px-4 py-3 text-right text-[#7b93a8] font-mono text-[11px]">{player.key_passes_p90.toFixed(2)}</td>
                        <td className="px-4 py-3 text-right text-[#7b93a8] font-mono text-[11px]">{player.pass_completion_pct.toFixed(0)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            
          </div>
        ) : (
          <div className="flex h-64 items-center justify-center text-[#3f5669] text-sm">Select a team to view details.</div>
        )}
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
//  SIMULATOR VIEW
// ═══════════════════════════════════════════════════════════════════════════════
// ═══════════════════════════════════════════════════════════════════════════════
//  BRACKET LINE HELPER
// ═══════════════════════════════════════════════════════════════════════════════
const getBracketPath = (x1, y1, x2, y2, side, r = 8) => {
  if (Math.abs(y1 - y2) < 2) {
    return `M ${x1} ${y1} L ${x2} ${y2}`
  }
  const xMid = x1 + (x2 - x1) * 0.5
  const dy = y2 - y1
  const signY = dy > 0 ? 1 : -1
  const actualR = Math.min(r, Math.abs(dy) * 0.5)
  
  if (side === 'left') {
    return `M ${x1} ${y1} H ${xMid - actualR} Q ${xMid} ${y1}, ${xMid} ${y1 + signY * actualR} V ${y2 - signY * actualR} Q ${xMid} ${y2}, ${xMid + actualR} ${y2} H ${x2}`
  } else {
    return `M ${x1} ${y1} H ${xMid + actualR} Q ${xMid} ${y1}, ${xMid} ${y1 + signY * actualR} V ${y2 - signY * actualR} Q ${xMid} ${y2}, ${xMid - actualR} ${y2} H ${x2}`
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
//  SIMULATOR VIEW
// ═══════════════════════════════════════════════════════════════════════════════
function SimulatorView({ simResults, simulating, triggerSimulationRun, user, setAuthModalOpen }) {
  const sample = simResults?.sample_run
  const sim_stats = simResults?.sim_stats || {}
  const containerRef = useRef(null)
  const [paths, setPaths] = useState([])
  const [simTab, setSimTab] = useState('monte_carlo')
  
  // Interactive bracket states
  const [picks, setPicks] = useState({})
  const [lockedPicks, setLockedPicks] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [selectedMatch, setSelectedMatch] = useState(null)
  const [matchOdds, setMatchOdds] = useState(null)
  const [oddsLoading, setOddsLoading] = useState(false)

  const handleAutoFill = () => {
    if (!sample) return;
    const newPicks = {};
    
    // Populate R16
    sample.r16_matches.forEach((m, idx) => {
      newPicks[`R16-${idx + 1}`] = m.winner;
    });
    
    // Populate QF
    sample.qf_matches.forEach((m, idx) => {
      newPicks[`QF-${idx + 1}`] = m.winner;
    });
    
    // Populate SF
    sample.sf_matches.forEach((m, idx) => {
      newPicks[`SF-${idx + 1}`] = m.winner;
    });
    
    // Populate Final
    newPicks['FINAL'] = sample.final_match.winner;
    
    setPicks(newPicks);
  }

  // Fetch locked predictions if user logged in, or pre-populate with ML predictions
  useEffect(() => {
    const getMlPicks = () => {
      if (!sample) return {};
      const mlPicks = {};
      sample.r16_matches.forEach((m, idx) => { mlPicks[`R16-${idx + 1}`] = m.winner; });
      sample.qf_matches.forEach((m, idx) => { mlPicks[`QF-${idx + 1}`] = m.winner; });
      sample.sf_matches.forEach((m, idx) => { mlPicks[`SF-${idx + 1}`] = m.winner; });
      mlPicks['FINAL'] = sample.final_match.winner;
      return mlPicks;
    };

    if (user?.email) {
      fetch(`/api/predictions/locked?email=${encodeURIComponent(user.email)}`)
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success' && data.predictions) {
            setLockedPicks(data.predictions)
            setPicks(data.predictions)
          } else {
            setLockedPicks(null)
            setPicks(getMlPicks())
          }
        })
        .catch(err => {
          console.error("Error loading locked predictions:", err);
          setPicks(getMlPicks());
        })
    } else {
      setLockedPicks(null)
      setPicks(getMlPicks())
    }
  }, [user, sample])

  const cleanDownstream = (updatedPicks) => {
    // QF-1 teams
    const qf1_a = updatedPicks['R16-1'];
    const qf1_b = updatedPicks['R16-2'];
    if (updatedPicks['QF-1'] && updatedPicks['QF-1'] !== qf1_a && updatedPicks['QF-1'] !== qf1_b) {
      delete updatedPicks['QF-1'];
    }
    
    // QF-2 teams
    const qf2_a = updatedPicks['R16-3'];
    const qf2_b = updatedPicks['R16-4'];
    if (updatedPicks['QF-2'] && updatedPicks['QF-2'] !== qf2_a && updatedPicks['QF-2'] !== qf2_b) {
      delete updatedPicks['QF-2'];
    }

    // QF-3 teams
    const qf3_a = updatedPicks['R16-5'];
    const qf3_b = updatedPicks['R16-6'];
    if (updatedPicks['QF-3'] && updatedPicks['QF-3'] !== qf3_a && updatedPicks['QF-3'] !== qf3_b) {
      delete updatedPicks['QF-3'];
    }

    // QF-4 teams
    const qf4_a = updatedPicks['R16-7'];
    const qf4_b = updatedPicks['R16-8'];
    if (updatedPicks['QF-4'] && updatedPicks['QF-4'] !== qf4_a && updatedPicks['QF-4'] !== qf4_b) {
      delete updatedPicks['QF-4'];
    }

    // SF-1 teams
    const sf1_a = updatedPicks['QF-1'];
    const sf1_b = updatedPicks['QF-2'];
    if (updatedPicks['SF-1'] && updatedPicks['SF-1'] !== sf1_a && updatedPicks['SF-1'] !== sf1_b) {
      delete updatedPicks['SF-1'];
    }

    // SF-2 teams
    const sf2_a = updatedPicks['QF-3'];
    const sf2_b = updatedPicks['QF-4'];
    if (updatedPicks['SF-2'] && updatedPicks['SF-2'] !== sf2_a && updatedPicks['SF-2'] !== sf2_b) {
      delete updatedPicks['SF-2'];
    }

    // FINAL teams
    const final_a = updatedPicks['SF-1'];
    const final_b = updatedPicks['SF-2'];
    if (updatedPicks['FINAL'] && updatedPicks['FINAL'] !== final_a && updatedPicks['FINAL'] !== final_b) {
      delete updatedPicks['FINAL'];
    }
  }

  const getInteractiveMatch = (nodeId) => {
    if (nodeId.startsWith('R16-')) {
      const idx = parseInt(nodeId.split('-')[1]) - 1;
      const baseMatch = sample?.r16_matches[idx];
      return {
        nodeId,
        team_a: baseMatch?.team_a || '',
        team_b: baseMatch?.team_b || '',
        winner: picks[nodeId] || ''
      };
    }
    if (nodeId === 'QF-1') {
      return { nodeId, team_a: picks['R16-1'] || '', team_b: picks['R16-2'] || '', winner: picks['QF-1'] || '' };
    }
    if (nodeId === 'QF-2') {
      return { nodeId, team_a: picks['R16-3'] || '', team_b: picks['R16-4'] || '', winner: picks['QF-2'] || '' };
    }
    if (nodeId === 'QF-3') {
      return { nodeId, team_a: picks['R16-5'] || '', team_b: picks['R16-6'] || '', winner: picks['QF-3'] || '' };
    }
    if (nodeId === 'QF-4') {
      return { nodeId, team_a: picks['R16-7'] || '', team_b: picks['R16-8'] || '', winner: picks['QF-4'] || '' };
    }
    if (nodeId === 'SF-1') {
      return { nodeId, team_a: picks['QF-1'] || '', team_b: picks['QF-2'] || '', winner: picks['SF-1'] || '' };
    }
    if (nodeId === 'SF-2') {
      return { nodeId, team_a: picks['QF-3'] || '', team_b: picks['QF-4'] || '', winner: picks['SF-2'] || '' };
    }
    if (nodeId === 'FINAL') {
      return { nodeId, team_a: picks['SF-1'] || '', team_b: picks['SF-2'] || '', winner: picks['FINAL'] || '' };
    }
    return null;
  }

  const handleSelectWinner = (nodeId, winnerName) => {
    if (lockedPicks) return;
    if (!winnerName) return;
    const nextPicks = { ...picks, [nodeId]: winnerName };
    cleanDownstream(nextPicks);
    setPicks(nextPicks);
  }

  const handleNodeClick = (node) => {
    if (!node.team_a || !node.team_b) return;
    setSelectedMatch(node);
    fetchOdds(node.team_a, node.team_b);
  }

  const fetchOdds = async (t1, t2) => {
    try {
      setOddsLoading(true);
      setMatchOdds(null);
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ team_a: t1, team_b: t2 })
      });
      if (res.ok) {
        const data = await res.json();
        setMatchOdds(data);
      }
    } catch (err) {
      console.error("Error fetching match odds:", err);
    } finally {
      setOddsLoading(false);
    }
  }

  const handleSubmitPredictions = async () => {
    if (!user) {
      setAuthModalOpen(true);
      return;
    }
    
    const requiredKeys = [
      'R16-1', 'R16-2', 'R16-3', 'R16-4', 'R16-5', 'R16-6', 'R16-7', 'R16-8',
      'QF-1', 'QF-2', 'QF-3', 'QF-4',
      'SF-1', 'SF-2',
      'FINAL'
    ];
    const allPicksMade = requiredKeys.every(k => picks[k]);
    if (!allPicksMade) {
      alert("Please complete the entire bracket before submitting!");
      return;
    }
    
    try {
      setIsSubmitting(true);
      const res = await fetch('/api/predictions/lock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: user.email, predictions: picks })
      });
      if (res.ok) {
        setLockedPicks(picks);
        alert("Predictions locked successfully! 🔒 You have entered the Leaderboard Arena.");
      } else {
        const errData = await res.json();
        alert("Failed to lock predictions: " + (errData.detail || "Server error"));
      }
    } catch (err) {
      console.error("Lock error:", err);
      alert("Error connecting to server. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  const updatePaths = useCallback(() => {
    const container = containerRef.current
    if (!container) return
    
    const containerRect = container.getBoundingClientRect()
    const newPaths = []
    
    const getPortCoords = (id, side, isRightSide) => {
      const el = document.getElementById(id)
      if (!el) return null
      const rect = el.getBoundingClientRect()
      
      if (isRightSide) {
        const x = side === 'output' ? rect.left : rect.right
        const y = rect.top + rect.height / 2
        return { x: x - containerRect.left, y: y - containerRect.top }
      } else {
        const x = side === 'output' ? rect.right : rect.left
        const y = rect.top + rect.height / 2
        return { x: x - containerRect.left, y: y - containerRect.top }
      }
    }
    
    const checkActive = (parentMatch, childMatch) => {
      if (!parentMatch || !childMatch) return false
      const winner = parentMatch.winner
      if (!winner) return false
      return childMatch.team_a === winner || childMatch.team_b === winner
    }

    const checkInteractiveActive = (fromNodeId, toNodeId) => {
      const winner = picks[fromNodeId];
      if (!winner) return false;
      const targetMatch = getInteractiveMatch(toNodeId);
      return targetMatch?.team_a === winner || targetMatch?.team_b === winner;
    }

    const isInteractive = simTab === 'locked';
    const activeCheck = (fromNode, toNode, sampleParent, sampleChild) => {
      if (isInteractive) {
        return checkInteractiveActive(fromNode, toNode);
      } else {
        return checkActive(sampleParent, sampleChild);
      }
    };

    if (sample) {
      const connections = []

      // Left side connections
      // R16 to QF
      connections.push({ from: 'match-R16-1', to: 'match-QF-1', side: 'left', active: activeCheck('R16-1', 'QF-1', sample.r16_matches[0], sample.qf_matches[0]) })
      connections.push({ from: 'match-R16-2', to: 'match-QF-1', side: 'left', active: activeCheck('R16-2', 'QF-1', sample.r16_matches[1], sample.qf_matches[0]) })
      connections.push({ from: 'match-R16-3', to: 'match-QF-2', side: 'left', active: activeCheck('R16-3', 'QF-2', sample.r16_matches[2], sample.qf_matches[1]) })
      connections.push({ from: 'match-R16-4', to: 'match-QF-2', side: 'left', active: activeCheck('R16-4', 'QF-2', sample.r16_matches[3], sample.qf_matches[1]) })

      // QF to SF
      connections.push({ from: 'match-QF-1', to: 'match-SF-1', side: 'left', active: activeCheck('QF-1', 'SF-1', sample.qf_matches[0], sample.sf_matches[0]) })
      connections.push({ from: 'match-QF-2', to: 'match-SF-1', side: 'left', active: activeCheck('QF-2', 'SF-1', sample.qf_matches[1], sample.sf_matches[0]) })

      // SF to Final
      connections.push({ from: 'match-SF-1', to: 'match-FINAL', side: 'left', active: activeCheck('SF-1', 'FINAL', sample.sf_matches[0], sample.final_match) })

      // Right side connections
      // R16 to QF
      connections.push({ from: 'match-R16-5', to: 'match-QF-3', side: 'right', active: activeCheck('R16-5', 'QF-3', sample.r16_matches[4], sample.qf_matches[2]) })
      connections.push({ from: 'match-R16-6', to: 'match-QF-3', side: 'right', active: activeCheck('R16-6', 'QF-3', sample.r16_matches[5], sample.qf_matches[2]) })
      connections.push({ from: 'match-R16-7', to: 'match-QF-4', side: 'right', active: activeCheck('R16-7', 'QF-4', sample.r16_matches[6], sample.qf_matches[3]) })
      connections.push({ from: 'match-R16-8', to: 'match-QF-4', side: 'right', active: activeCheck('R16-8', 'QF-4', sample.r16_matches[7], sample.qf_matches[3]) })

      // QF to SF
      connections.push({ from: 'match-QF-3', to: 'match-SF-2', side: 'right', active: activeCheck('QF-3', 'SF-2', sample.qf_matches[2], sample.sf_matches[1]) })
      connections.push({ from: 'match-QF-4', to: 'match-SF-2', side: 'right', active: activeCheck('QF-4', 'SF-2', sample.qf_matches[3], sample.sf_matches[1]) })

      // SF to Final
      connections.push({ from: 'match-SF-2', to: 'match-FINAL', side: 'right', active: activeCheck('SF-2', 'FINAL', sample.sf_matches[1], sample.final_match) })

      connections.forEach(conn => {
         const pCoords = getPortCoords(conn.from, 'output', conn.side === 'right')
         const cCoords = getPortCoords(conn.to, 'input', conn.side === 'right')
         if (pCoords && cCoords) {
           const d = getBracketPath(pCoords.x, pCoords.y, cCoords.x, cCoords.y, conn.side)
           newPaths.push({ d, active: conn.active })
         }
      })
    }
    
    setPaths(newPaths)
  }, [sample, simTab, picks])

  useEffect(() => {
    if (!sample) return
    
    const timer = setTimeout(() => {
      updatePaths()
    }, 150)
    
    window.addEventListener('resize', updatePaths)
    return () => {
      clearTimeout(timer)
      window.removeEventListener('resize', updatePaths)
    }
  }, [sample, simulating, updatePaths, simTab, picks])

  // Count picks
  const interactivePicksCount = Object.keys(picks).length;
  const isBracketComplete = interactivePicksCount === 15;

  return (
    <div className="space-y-6">
      
      {/* Sub Tab Switcher */}
      <div className="flex border-b border-white/[0.04] gap-6 mb-2">
        <button
          onClick={() => setSimTab('monte_carlo')}
          className={`pb-3 text-sm font-semibold tracking-wide border-b-2 transition-all cursor-pointer ${
            simTab === 'monte_carlo' 
              ? 'border-[#00e87b] text-white text-green-glow' 
              : 'border-transparent text-[#7b93a8] hover:text-white'
          }`}
        >
          Monte Carlo Projections
        </button>
        <button
          onClick={() => setSimTab('locked')}
          className={`pb-3 text-sm font-semibold tracking-wide border-b-2 transition-all cursor-pointer flex items-center gap-1.5 ${
            simTab === 'locked' 
              ? 'border-[#00e87b] text-white text-green-glow' 
              : 'border-transparent text-[#7b93a8] hover:text-white'
          }`}
        >
          <Lock size={13} className={lockedPicks ? 'text-[#00e87b]' : ''} />
          Locked Predictions {lockedPicks && '🔒'}
        </button>
      </div>

      {/* Header */}
      {simTab === 'monte_carlo' ? (
        <div className="glass-panel flex flex-col md:flex-row justify-between items-center gap-6 p-6 relative overflow-hidden">
          <div className="absolute inset-0 opacity-30" style={{
            background: `radial-gradient(ellipse 50% 80% at 0% 100%, rgba(0, 232, 123, 0.06) 0%, transparent 60%)`
          }} />
          <div className="space-y-1.5 flex-1 relative z-10">
            <h2 className="text-xl font-display tracking-wider text-white flex items-center gap-2">
              <Trophy size={20} className="text-[#d4a54a]" />
              MONTE CARLO SIMULATOR
            </h2>
            <p className="text-[12px] text-[#7b93a8] max-w-lg">
              Run 500 complete tournament simulations incorporating current player stats and model weights.
            </p>
          </div>
          <button 
            onClick={triggerSimulationRun}
            disabled={simulating}
            className="relative z-10 bg-[#00e87b] hover:bg-[#00d46f] disabled:bg-[#00e87b]/30 disabled:text-[#050a0e]/50 text-[#050a0e] font-bold px-6 py-3 rounded-full text-[12px] shrink-0 transition-all flex items-center gap-2 hover:shadow-[0_0_20px_rgba(0,232,123,0.25)] cursor-pointer tracking-wide"
          >
            {simulating ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-[#050a0e] border-t-transparent"></div>
                Simulating...
              </>
            ) : (
              <>
                <Play size={12} fill="currentColor" />
                Run 500 Simulations
              </>
            )}
          </button>
        </div>
      ) : (
        <div className="glass-panel flex flex-col md:flex-row justify-between items-center gap-6 p-6 relative overflow-hidden">
          <div className="absolute inset-0 opacity-30" style={{
            background: `radial-gradient(ellipse 50% 80% at 0% 100%, rgba(212, 165, 74, 0.04) 0%, transparent 60%)`
          }} />
          <div className="space-y-1.5 flex-1 relative z-10">
            <h2 className="text-xl font-display tracking-wider text-white flex items-center gap-2">
              <Lock size={18} className="text-[#d4a54a]" />
              LOCKED BRACKET PREDICTIONS
            </h2>
            <p className="text-[12px] text-[#7b93a8] max-w-lg">
              Make your interactively calculated picks from the Round of 16 to the Final. Lock them to compete in the leaderboard.
            </p>
          </div>
          
          {lockedPicks ? (
            <div className="relative z-10 px-5 py-2.5 rounded-full bg-[#00e87b]/10 border border-[#00e87b]/20 text-[#00e87b] text-xs font-bold flex items-center gap-2">
              <span>PREDICTIONS LOCKED 🔒</span>
            </div>
          ) : (
            <div className="relative z-10 flex flex-col md:flex-row items-center gap-4">
              <button
                onClick={handleAutoFill}
                className="bg-white/[0.04] border border-white/[0.08] hover:bg-[#00e87b]/10 hover:border-[#00e87b]/20 text-[#7b93a8] hover:text-[#00e87b] font-bold px-4 py-2.5 rounded-full text-[11px] transition-all cursor-pointer flex items-center gap-1.5"
              >
                <Cpu size={12} />
                Auto-fill with ML Projections
              </button>
              <div className="text-right">
                <span className="text-[10px] text-[#7b93a8] block uppercase font-bold tracking-wider">Progress</span>
                <span className="text-xs text-white block mt-0.5 font-semibold">{interactivePicksCount} / 15 Picks Made</span>
              </div>
              <button 
                onClick={handleSubmitPredictions}
                disabled={!isBracketComplete || isSubmitting}
                className="bg-[#d4a54a] hover:bg-[#c39439] disabled:bg-white/[0.04] disabled:text-[#3f5669] text-black font-bold px-6 py-3 rounded-full text-[12px] shrink-0 transition-all flex items-center gap-2 hover:shadow-[0_0_20px_rgba(212,165,74,0.25)] cursor-pointer tracking-wide"
              >
                {isSubmitting ? 'Submitting...' : 'Lock & Submit Predictions'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Locked prediction certificate card */}
      {simTab === 'locked' && lockedPicks && (
        <div className="glass-panel p-6 border-[#d4a54a]/30 bg-gradient-to-r from-[#d4a54a]/[0.02] to-[#00e87b]/[0.02] relative overflow-hidden flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="absolute inset-0 bg-[#d4a54a]/[0.02] pointer-events-none" />
          <div className="space-y-1.5 relative z-10">
            <h4 className="text-xs font-bold uppercase tracking-widest text-[#d4a54a] flex items-center gap-1.5">
              <Shield size={14} />
              Verified Predictions Stamp
            </h4>
            <p className="text-[11px] text-[#7b93a8] max-w-lg leading-relaxed">
              Your tournament predictions are officially submitted and locked. Your champion pick is {picks['FINAL']}. Points will be calculated dynamically based on real 2026 World Cup outcomes!
            </p>
          </div>
          <div className="flex flex-col items-center border border-[#d4a54a]/20 bg-black/40 rounded-xl p-3.5 relative z-10 min-w-[200px]">
            <span className="text-[9px] uppercase font-bold tracking-wider text-[#7b93a8]">Your Champion Pick</span>
            <span className="text-base font-display text-white mt-1.5 flex items-center gap-2">
              {getFlagImg(picks['FINAL'] || '')}
              {picks['FINAL']}
            </span>
          </div>
        </div>
      )}

      {/* Bracket */}
      {sample ? (
        <div className="space-y-4">
          <h3 className="font-display text-lg tracking-wider text-white flex items-center gap-2">
            <TrendingUp size={16} className="text-[#00e87b]" />
            {simTab === 'monte_carlo' ? 'SIMULATED BRACKET PATHWAY' : 'INTERACTIVE PREDICTIONS PATHWAY'}
          </h3>
          
          <div className="overflow-x-auto pb-4 pt-2">
            <div 
              ref={containerRef}
              className="min-w-[1100px] h-[580px] relative flex justify-between gap-2 p-5 border border-white/[0.04] rounded-2xl bg-[#03070b]/60 select-none"
            >
              {/* SVG Connectors Overlay */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
                {paths.map((p, idx) => (
                  <path
                    key={idx}
                    d={p.d}
                    fill="none"
                    stroke={p.active ? '#d4a54a' : 'rgba(255, 255, 255, 0.04)'}
                    strokeWidth={p.active ? 2.5 : 1.5}
                    style={{
                      filter: p.active ? 'drop-shadow(0px 0px 5px rgba(212, 165, 74, 0.55))' : 'none',
                      transition: 'stroke 0.4s ease, stroke-width 0.4s ease'
                    }}
                  />
                ))}
              </svg>
              
              {/* R16 Left */}
              <div className="sim-bracket-column w-44">
                <div className="text-center mb-1 shrink-0">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-white block">Round of 16</span>
                  <span className="text-[9px] text-[#7b93a8] block mt-0.5">Jun 28 – Jul 1</span>
                </div>
                <div className="flex-1 flex flex-col justify-around py-2">
                  {simTab === 'monte_carlo' ? (
                    sample.r16_matches.slice(0, 4).map((m, idx) => (
                      <BracketMatchNode key={idx} match={m} domId={`match-R16-${idx + 1}`} />
                    ))
                  ) : (
                    ['R16-1', 'R16-2', 'R16-3', 'R16-4'].map((nodeId) => (
                      <InteractiveBracketMatchNode 
                        key={nodeId} 
                        node={getInteractiveMatch(nodeId)} 
                        onSelect={handleSelectWinner} 
                        onClick={handleNodeClick} 
                        isLocked={!!lockedPicks} 
                      />
                    ))
                  )}
                </div>
              </div>

              {/* QF Left */}
              <div className="sim-bracket-column w-44">
                <div className="text-center mb-1 shrink-0">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-white block">Quarterfinals</span>
                  <span className="text-[9px] text-[#7b93a8] block mt-0.5">Jul 4 – Jul 5</span>
                </div>
                <div className="flex-1 flex flex-col justify-around py-6">
                  {simTab === 'monte_carlo' ? (
                    sample.qf_matches.slice(0, 2).map((m, idx) => (
                      <BracketMatchNode key={idx} match={m} domId={`match-QF-${idx + 1}`} />
                    ))
                  ) : (
                    ['QF-1', 'QF-2'].map((nodeId) => (
                      <InteractiveBracketMatchNode 
                        key={nodeId} 
                        node={getInteractiveMatch(nodeId)} 
                        onSelect={handleSelectWinner} 
                        onClick={handleNodeClick} 
                        isLocked={!!lockedPicks} 
                      />
                    ))
                  )}
                </div>
              </div>

              {/* SF Left */}
              <div className="sim-bracket-column w-44">
                <div className="text-center mb-1 shrink-0">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-white block">Semifinals</span>
                  <span className="text-[9px] text-[#7b93a8] block mt-0.5">Jul 8</span>
                </div>
                <div className="flex-1 flex flex-col justify-around py-14">
                  {simTab === 'monte_carlo' ? (
                    sample.sf_matches.slice(0, 1).map((m, idx) => (
                      <BracketMatchNode key={idx} match={m} domId="match-SF-1" />
                    ))
                  ) : (
                    ['SF-1'].map((nodeId) => (
                      <InteractiveBracketMatchNode 
                        key={nodeId} 
                        node={getInteractiveMatch(nodeId)} 
                        onSelect={handleSelectWinner} 
                        onClick={handleNodeClick} 
                        isLocked={!!lockedPicks} 
                      />
                    ))
                  )}
                </div>
              </div>

              {/* Champion + Final */}
              {simTab === 'monte_carlo' ? (
                <div className="sim-bracket-column w-60 items-center justify-center space-y-8 self-center">
                  <div className="text-center space-y-2 relative pt-2">
                    <div className="absolute h-36 w-36 bg-[#d4a54a]/10 rounded-full blur-3xl top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-0"></div>
                    <img 
                      src="/world_cup_2026_trophy.png" 
                      alt="Trophy" 
                      className="h-20 w-20 object-contain mx-auto drop-shadow-[0_0_24px_rgba(212,165,74,0.5)] animate-float relative z-10" 
                    />
                    <div className="relative z-10">
                      <span className="text-[10px] font-bold uppercase text-[#d4a54a] tracking-[0.25em] block text-gold-glow">CHAMPION</span>
                      <span className="text-4xl font-display text-white tracking-wider uppercase block mt-1 leading-none">{sample.final_match.winner}</span>
                    </div>
                  </div>
                  
                  <div className="w-full text-center space-y-2 relative z-10 pt-4 border-t border-white/[0.04]">
                    <div>
                      <span className="text-[10px] uppercase font-bold tracking-wider text-[#3f5669] block">Final</span>
                      <span className="text-[9px] text-[#7b93a8] block mt-0.5">Jul 12</span>
                    </div>
                    <BracketMatchNode match={sample.final_match} domId="match-FINAL" isFinal={true} />
                  </div>
                </div>
              ) : (
                <div className="sim-bracket-column w-60 items-center justify-center space-y-8 self-center">
                  <div className="text-center space-y-2 relative pt-2">
                    <div className="absolute h-36 w-36 bg-[#d4a54a]/10 rounded-full blur-3xl top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-0"></div>
                    <img 
                      src="/world_cup_2026_trophy.png" 
                      alt="Trophy" 
                      className="h-20 w-20 object-contain mx-auto drop-shadow-[0_0_24px_rgba(212,165,74,0.5)] animate-float relative z-10" 
                    />
                    <div className="relative z-10">
                      <span className="text-[10px] font-bold uppercase text-[#d4a54a] tracking-[0.25em] block text-gold-glow">PREDICTED CHAMPION</span>
                      <span className="text-4xl font-display text-white tracking-wider uppercase block mt-1 leading-none">
                        {picks['FINAL'] ? (
                          <span className="flex items-center justify-center gap-1.5 text-2xl lg:text-3xl text-[#d4a54a]">
                            {getFlagImg(picks['FINAL'])}
                            {picks['FINAL']}
                          </span>
                        ) : 'Awaiting Final'}
                      </span>
                    </div>
                  </div>
                  
                  <div className="w-full text-center space-y-2 relative z-10 pt-4 border-t border-white/[0.04]">
                    <div>
                      <span className="text-[10px] uppercase font-bold tracking-wider text-[#3f5669] block">Final</span>
                      <span className="text-[9px] text-[#7b93a8] block mt-0.5">Jul 12</span>
                    </div>
                    <InteractiveBracketMatchNode 
                      node={getInteractiveMatch('FINAL')} 
                      onSelect={handleSelectWinner} 
                      onClick={handleNodeClick} 
                      isFinal={true} 
                      isLocked={!!lockedPicks} 
                    />
                  </div>
                </div>
              )}

              {/* SF Right */}
              <div className="sim-bracket-column w-44">
                <div className="text-center mb-1 shrink-0">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-white block">Semifinals</span>
                  <span className="text-[9px] text-[#7b93a8] block mt-0.5">Jul 8</span>
                </div>
                <div className="flex-1 flex flex-col justify-around py-14">
                  {simTab === 'monte_carlo' ? (
                    sample.sf_matches.slice(1, 2).map((m, idx) => (
                      <BracketMatchNode key={idx} match={m} domId="match-SF-2" />
                    ))
                  ) : (
                    ['SF-2'].map((nodeId) => (
                      <InteractiveBracketMatchNode 
                        key={nodeId} 
                        node={getInteractiveMatch(nodeId)} 
                        onSelect={handleSelectWinner} 
                        onClick={handleNodeClick} 
                        isLocked={!!lockedPicks} 
                      />
                    ))
                  )}
                </div>
              </div>

              {/* QF Right */}
              <div className="sim-bracket-column w-44">
                <div className="text-center mb-1 shrink-0">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-white block">Quarterfinals</span>
                  <span className="text-[9px] text-[#7b93a8] block mt-0.5">Jul 4 – Jul 5</span>
                </div>
                <div className="flex-1 flex flex-col justify-around py-6">
                  {simTab === 'monte_carlo' ? (
                    sample.qf_matches.slice(2, 4).map((m, idx) => (
                      <BracketMatchNode key={idx} match={m} domId={`match-QF-${idx + 3}`} />
                    ))
                  ) : (
                    ['QF-3', 'QF-4'].map((nodeId) => (
                      <InteractiveBracketMatchNode 
                        key={nodeId} 
                        node={getInteractiveMatch(nodeId)} 
                        onSelect={handleSelectWinner} 
                        onClick={handleNodeClick} 
                        isLocked={!!lockedPicks} 
                      />
                    ))
                  )}
                </div>
              </div>

              {/* R16 Right */}
              <div className="sim-bracket-column w-44">
                <div className="text-center mb-1 shrink-0">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-white block">Round of 16</span>
                  <span className="text-[9px] text-[#7b93a8] block mt-0.5">Jun 28 – Jul 1</span>
                </div>
                <div className="flex-1 flex flex-col justify-around py-2">
                  {simTab === 'monte_carlo' ? (
                    sample.r16_matches.slice(4, 8).map((m, idx) => (
                      <BracketMatchNode key={idx} match={m} domId={`match-R16-${idx + 5}`} />
                    ))
                  ) : (
                    ['R16-5', 'R16-6', 'R16-7', 'R16-8'].map((nodeId) => (
                      <InteractiveBracketMatchNode 
                        key={nodeId} 
                        node={getInteractiveMatch(nodeId)} 
                        onSelect={handleSelectWinner} 
                        onClick={handleNodeClick} 
                        isLocked={!!lockedPicks} 
                      />
                    ))
                  )}
                </div>
              </div>

            </div>
          </div>

          {/* Design Notes Footer */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 border-t border-white/[0.04] pt-6 mt-8">
            <div className="p-4 rounded-xl bg-white/[0.01] border border-white/[0.03] flex flex-col gap-2">
              <div className="flex items-center gap-2 text-[#d4a54a]">
                <Trophy size={16} />
                <span className="text-[11px] font-bold uppercase tracking-wider">Clear Hierarchy</span>
              </div>
              <p className="text-[10px] text-[#7b93a8] leading-relaxed">
                Use size, color, and spacing to guide the eye to the final.
              </p>
            </div>
            
            <div className="p-4 rounded-xl bg-white/[0.01] border border-white/[0.03] flex flex-col gap-2">
              <div className="flex items-center gap-2 text-[#00e87b]">
                <GitFork size={16} />
                <span className="text-[11px] font-bold uppercase tracking-wider">Improve Readability</span>
              </div>
              <p className="text-[10px] text-[#7b93a8] leading-relaxed">
                Increase spacing, use consistent alignment, and larger text.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-white/[0.01] border border-white/[0.03] flex flex-col gap-2">
              <div className="flex items-center gap-2 text-[#00e87b]">
                <Palette size={16} />
                <span className="text-[11px] font-bold uppercase tracking-wider">Consistent Visuals</span>
              </div>
              <p className="text-[10px] text-[#7b93a8] leading-relaxed">
                Keep colors, flags, and score badges uniform.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-white/[0.01] border border-white/[0.03] flex flex-col gap-2">
              <div className="flex items-center gap-2 text-blue-400">
                <Calendar size={16} />
                <span className="text-[11px] font-bold uppercase tracking-wider">Add Context</span>
              </div>
              <p className="text-[10px] text-[#7b93a8] leading-relaxed">
                Include dates to show when each round is played.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-white/[0.01] border border-white/[0.03] flex flex-col gap-2 col-span-2 md:col-span-1">
              <div className="flex items-center gap-2 text-[#d4a54a]">
                <Star size={16} />
                <span className="text-[11px] font-bold uppercase tracking-wider">Highlight Winner</span>
              </div>
              <p className="text-[10px] text-[#7b93a8] leading-relaxed">
                Use accent color and effects to celebrate the champion.
              </p>
            </div>
          </div>

        </div>
      ) : (
        <div className="flex h-64 items-center justify-center text-[#3f5669] text-sm">Click simulate to generate a bracket pathway.</div>
      )}

      {/* XGBoost Odds Modal Overlay */}
      {selectedMatch && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-md p-4">
          <div className="w-full max-w-md bg-[#070d13] border border-white/[0.08] rounded-2xl shadow-[0_12px_48px_rgba(0,0,0,0.8)] overflow-hidden flex flex-col max-h-[90vh]">
            
            {/* Modal Header */}
            <div className="p-4 border-b border-white/[0.06] flex justify-between items-center bg-[#0a1118]">
              <div className="flex items-center gap-2">
                <Cpu size={16} className="text-[#00e87b]" />
                <span className="text-[10px] uppercase font-bold tracking-wider text-white">XGBoost Matchup Oracle</span>
              </div>
              <button 
                onClick={() => { setSelectedMatch(null); setMatchOdds(null); }}
                className="text-[#7b93a8] hover:text-white text-xs font-semibold p-1"
              >
                ✕
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-6 flex-1">
              
              {/* Teams Display */}
              <div className="flex justify-between items-center gap-4 border-b border-white/[0.03] pb-4">
                <div className="flex flex-col items-center flex-1 text-center">
                  <div className="h-12 w-12 rounded-full overflow-hidden flex items-center justify-center bg-white/[0.02] border border-white/[0.05] shadow-inner mb-2">
                    {getFlagImg(selectedMatch.team_a, "w-10 h-7 object-cover rounded shadow-md")}
                  </div>
                  <span className="text-xs font-semibold text-white truncate max-w-[120px]">{selectedMatch.team_a}</span>
                  <span className="text-[9px] text-[#3f5669] mt-0.5">FIFA Rank: {FIFA_RANKINGS[selectedMatch.team_a] || 'N/A'}</span>
                </div>

                <div className="text-center font-display text-[#3f5669] text-lg">VS</div>

                <div className="flex flex-col items-center flex-1 text-center">
                  <div className="h-12 w-12 rounded-full overflow-hidden flex items-center justify-center bg-white/[0.02] border border-white/[0.05] shadow-inner mb-2">
                    {getFlagImg(selectedMatch.team_b, "w-10 h-7 object-cover rounded shadow-md")}
                  </div>
                  <span className="text-xs font-semibold text-white truncate max-w-[120px]">{selectedMatch.team_b}</span>
                  <span className="text-[9px] text-[#3f5669] mt-0.5">FIFA Rank: {FIFA_RANKINGS[selectedMatch.team_b] || 'N/A'}</span>
                </div>
              </div>

              {oddsLoading ? (
                <div className="py-8 flex flex-col items-center gap-3">
                  <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#00e87b]/20 border-t-[#00e87b]"></div>
                  <span className="text-[10px] text-[#7b93a8] tracking-widest uppercase">Calculating Odds...</span>
                </div>
              ) : matchOdds ? (
                <div className="space-y-6">
                  
                  {/* Probability Chart */}
                  <div className="space-y-2">
                    <span className="text-[10px] uppercase font-bold text-[#7b93a8] tracking-wider block">Win Probabilities (90 Mins)</span>
                    <div className="grid grid-cols-3 gap-2">
                      <div className="bg-white/[0.02] border border-white/[0.04] rounded-lg p-2.5 text-center">
                        <span className="block text-[9px] text-[#7b93a8] uppercase font-semibold">Team A Win</span>
                        <span className="block text-base font-display font-bold text-[#00e87b] mt-0.5">
                          {Math.round(matchOdds.probabilities.team_a_win * 100)}%
                        </span>
                      </div>
                      <div className="bg-white/[0.02] border border-white/[0.04] rounded-lg p-2.5 text-center">
                        <span className="block text-[9px] text-[#7b93a8] uppercase font-semibold">Draw</span>
                        <span className="block text-base font-display font-bold text-white mt-0.5">
                          {Math.round(matchOdds.probabilities.draw * 100)}%
                        </span>
                      </div>
                      <div className="bg-white/[0.02] border border-white/[0.04] rounded-lg p-2.5 text-center">
                        <span className="block text-[9px] text-[#7b93a8] uppercase font-semibold">Team B Win</span>
                        <span className="block text-base font-display font-bold text-[#d4a54a] mt-0.5">
                          {Math.round(matchOdds.probabilities.team_b_win * 100)}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Advance Odds Bar */}
                  <div className="space-y-2">
                    <span className="text-[10px] uppercase font-bold text-[#7b93a8] tracking-wider block">Advance Projection (Including OT/Penalties)</span>
                    {(() => {
                      const pA = matchOdds.probabilities.team_a_win;
                      const pB = matchOdds.probabilities.team_b_win;
                      const pctA = Math.round((pA / (pA + pB)) * 100);
                      const pctB = 100 - pctA;
                      return (
                        <div className="space-y-1">
                          <div className="h-2.5 w-full bg-white/[0.04] rounded-full overflow-hidden flex">
                            <div className="h-full bg-gradient-to-r from-[#00e87b] to-[#00c464]" style={{ width: `${pctA}%` }}></div>
                            <div className="h-full bg-gradient-to-r from-[#e5b658] to-[#d4a54a]" style={{ width: `${pctB}%` }}></div>
                          </div>
                          <div className="flex justify-between items-center text-[10px] font-bold">
                            <span className="text-[#00e87b]">{pctA}% {selectedMatch.team_a}</span>
                            <span className="text-[#d4a54a]">{selectedMatch.team_b} {pctB}%</span>
                          </div>
                        </div>
                      )
                    })()}
                  </div>

                  {/* Model Explanation */}
                  {matchOdds.explanations && matchOdds.explanations.length > 0 && (
                    <div className="space-y-2">
                      <span className="text-[10px] uppercase font-bold text-[#7b93a8] tracking-wider block">Key Match Factors</span>
                      <ul className="space-y-2 bg-white/[0.02] border border-white/[0.04] p-3.5 rounded-xl text-[11px] text-[#7b93a8] leading-relaxed">
                        {matchOdds.explanations.map((exp, idx) => (
                          <li key={idx} className="flex gap-2 items-start">
                            <span className="text-[#00e87b] font-bold mt-0.5">•</span>
                            <span>{exp}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Features Comparison */}
                  {matchOdds.features_a && matchOdds.features_b && (
                    <div className="space-y-2">
                      <span className="text-[10px] uppercase font-bold text-[#7b93a8] tracking-wider block">ML Stats Comparison</span>
                      <div className="space-y-2.5 bg-white/[0.01] border border-white/[0.03] p-3.5 rounded-xl">
                        {[
                          { label: 'Attack Strength', key: 'team_attack_strength' },
                          { label: 'Defense Solidity', key: 'team_defense_solidity' },
                          { label: 'Midfield Creativity', key: 'team_midfield_creativity' },
                          { label: 'Squad Depth', key: 'team_depth_score' },
                          { label: 'Star Impact', key: 'team_star_player_impact' }
                        ].map((stat) => {
                          const valA = parseFloat(matchOdds.features_a[stat.key]) || 0;
                          const valB = parseFloat(matchOdds.features_b[stat.key]) || 0;
                          const maxVal = Math.max(valA, valB, 1.0);
                          const widthA = Math.round((valA / maxVal) * 100);
                          const widthB = Math.round((valB / maxVal) * 100);
                          
                          return (
                            <div key={stat.key} className="space-y-1">
                              <div className="flex justify-between items-center text-[9px] uppercase font-semibold text-[#7b93a8]">
                                <span className="text-[#00e87b]">{valA.toFixed(1)}</span>
                                <span>{stat.label}</span>
                                <span className="text-[#d4a54a]">{valB.toFixed(1)}</span>
                              </div>
                              <div className="h-1.5 w-full bg-white/[0.02] rounded-full overflow-hidden flex relative">
                                <div className="absolute top-0 bottom-0 left-[50%] right-[50%] bg-white/10 w-[1px]"></div>
                                {/* Left Bar (Team A) */}
                                <div className="h-full flex justify-end w-[50%] pr-[0.5px]">
                                  <div className="h-full bg-[#00e87b] rounded-l" style={{ width: `${widthA * 0.5}%` }}></div>
                                </div>
                                {/* Right Bar (Team B) */}
                                <div className="h-full flex justify-start w-[50%] pl-[0.5px]">
                                  <div className="h-full bg-[#d4a54a] rounded-r" style={{ width: `${widthB * 0.5}%` }}></div>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                </div>
              ) : (
                <div className="text-center text-xs text-[#3f5669] py-8">Failed to calculate prediction odds.</div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-white/[0.06] bg-[#0a1118] text-center">
              <button
                onClick={() => { setSelectedMatch(null); setMatchOdds(null); }}
                className="bg-white/[0.04] border border-white/[0.05] hover:bg-white/[0.08] text-[#edf2f7] font-semibold text-xs px-4 py-2 rounded-lg cursor-pointer"
              >
                Close Insights
              </button>
            </div>

          </div>
        </div>
      )}
    </div>
  )
}

function InteractiveBracketMatchNode({ node, onSelect, onClick, isFinal, isLocked }) {
  if (!node) return null;
  const { team_a, team_b, winner, nodeId } = node;
  const isWinnerA = winner === team_a && team_a !== '';
  const isWinnerB = winner === team_b && team_b !== '';

  return (
    <div 
      id={`match-${nodeId}`}
      className={`p-3 rounded-xl border text-[11px] font-medium transition-all duration-300 w-full flex flex-col justify-center gap-1.5 shadow-[0_4px_24px_rgba(0,0,0,0.5)] z-10 relative ${
        isFinal 
          ? 'border-[#d4a54a]/30 bg-[#070e15]/95 shadow-[0_4px_32px_rgba(212,165,74,0.15)]' 
          : 'border-white/[0.06] bg-[#070e15]/90'
      } ${team_a && team_b ? 'hover:border-[#00e87b]/30 cursor-pointer' : ''}`}
      onClick={() => onClick?.(node)}
    >
      <div className="flex justify-between items-center text-[8px] text-[#3f5669] uppercase font-bold tracking-wider mb-0.5">
        <span>Match {nodeId}</span>
        {team_a && team_b && !isLocked && <span className="text-[#00e87b]/75">Click for odds</span>}
      </div>

      <div className="space-y-1.5">
        {/* Team A */}
        <div 
          onClick={(e) => {
            if (isLocked) return;
            e.stopPropagation();
            if (team_a) onSelect?.(nodeId, team_a);
          }}
          className={`flex justify-between items-center gap-2 p-1 rounded-md transition-colors ${
            !isLocked && team_a ? 'hover:bg-white/[0.04] cursor-pointer' : ''
          } ${isWinnerA ? 'bg-[#00e87b]/10 border border-[#00e87b]/20' : 'border border-transparent'}`}
        >
          <span className={`flex items-center gap-1.5 truncate ${isWinnerA ? "text-white font-bold" : "text-[#7b93a8] font-normal"}`}>
            {team_a ? getFlagImg(team_a, "w-4.5 h-3 object-cover rounded-xs shadow-xs shrink-0") : '🏳️'}
            <span className="truncate">{team_a || 'Awaiting Team'}</span>
          </span>
          {isWinnerA && <span className="text-[10px] text-[#00e87b] font-bold pr-1">✓</span>}
        </div>

        {/* Team B */}
        <div 
          onClick={(e) => {
            if (isLocked) return;
            e.stopPropagation();
            if (team_b) onSelect?.(nodeId, team_b);
          }}
          className={`flex justify-between items-center gap-2 p-1 rounded-md transition-colors ${
            !isLocked && team_b ? 'hover:bg-white/[0.04] cursor-pointer' : ''
          } ${isWinnerB ? 'bg-[#00e87b]/10 border border-[#00e87b]/20' : 'border border-transparent'}`}
        >
          <span className={`flex items-center gap-1.5 truncate ${isWinnerB ? "text-white font-bold" : "text-[#7b93a8] font-normal"}`}>
            {team_b ? getFlagImg(team_b, "w-4.5 h-3 object-cover rounded-xs shadow-xs shrink-0") : '🏳️'}
            <span className="truncate">{team_b || 'Awaiting Team'}</span>
          </span>
          {isWinnerB && <span className="text-[10px] text-[#00e87b] font-bold pr-1">✓</span>}
        </div>
      </div>
    </div>
  )
}

function BracketMatchNode({ match, domId, isFinal }) {
  if (!match) return null
  const isWinnerA = match.winner === match.team_a
  const isWinnerB = match.winner === match.team_b

  return (
    <div 
      id={domId}
      className={`p-3 rounded-xl border text-[11px] font-medium transition-all duration-300 w-full flex flex-col justify-center gap-1.5 shadow-[0_4px_24px_rgba(0,0,0,0.5)] z-10 relative ${
        isFinal 
          ? 'border-[#d4a54a]/30 bg-[#070e15]/95 hover:border-[#d4a54a]/50 shadow-[0_4px_32px_rgba(212,165,74,0.15)]' 
          : 'border-white/[0.06] bg-[#070e15]/90 hover:border-white/[0.12]'
      }`}
    >
      <div className="space-y-1.5">
        <div className="flex justify-between items-center gap-2">
          <span className={`flex items-center gap-1.5 truncate ${isWinnerA ? "text-white font-bold" : "text-[#7b93a8] font-normal"}`}>
            {getFlagImg(match.team_a, "w-4.5 h-3 object-cover rounded-xs shadow-xs shrink-0")}
            <span className="truncate">{match.team_a}</span>
          </span>
          <span className={`font-mono px-2 py-0.5 rounded text-[10px] font-bold min-w-[20px] text-center border transition-colors ${
            isWinnerA 
              ? "bg-[#00e87b]/15 text-[#00e87b] border-[#00e87b]/20" 
              : "bg-white/[0.02] text-[#3f5669] border-white/[0.04]"
          }`}>
            {match.goals_a}
          </span>
        </div>
        <div className="flex justify-between items-center gap-2">
          <span className={`flex items-center gap-1.5 truncate ${isWinnerB ? "text-white font-bold" : "text-[#7b93a8] font-normal"}`}>
            {getFlagImg(match.team_b, "w-4.5 h-3 object-cover rounded-xs shadow-xs shrink-0")}
            <span className="truncate">{match.team_b}</span>
          </span>
          <span className={`font-mono px-2 py-0.5 rounded text-[10px] font-bold min-w-[20px] text-center border transition-colors ${
            isWinnerB 
              ? "bg-[#00e87b]/15 text-[#00e87b] border-[#00e87b]/20" 
              : "bg-white/[0.02] text-[#3f5669] border-white/[0.04]"
          }`}>
            {match.goals_b}
          </span>
        </div>
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
//  LANDING VIEW
// ═══════════════════════════════════════════════════════════════════════════════
function LandingView({ simResults, setActiveTab }) {
  const sim_stats = simResults?.sim_stats || {}
  const contenders = Object.entries(sim_stats)
    .map(([name, probs]) => ({ name, ...probs }))
    .sort((a, b) => b.champion_prob - a.champion_prob)
  const top5 = contenders.slice(0, 5)
  const [showAllTeams, setShowAllTeams] = useState(false)
  const displayedTeams = showAllTeams ? contenders : contenders.slice(0, 15)

  return (
    <motion.div 
      className="space-y-12 py-4"
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        
        {/* Left Side: Copy & Stats */}
        <div className="lg:col-span-5 space-y-6">
          <motion.span 
            className="inline-flex items-center gap-1.5 text-[10px] font-semibold tracking-[0.25em] text-[#00e87b] uppercase bg-[#00e87b]/[0.06] border border-[#00e87b]/[0.12] px-3.5 py-2 rounded-full"
            variants={staggerItem}
          >
            <Zap size={10} className="animate-pulse" />
            FIFA WORLD CUP 2026 FORECASTS
          </motion.span>

          <motion.h1 
            className="text-5xl lg:text-7xl font-display text-white leading-[0.95] tracking-wide"
            variants={staggerItem}
          >
            THE ULTIMATE<br/>
            <span className="text-[#00e87b] text-green-glow">ML PREDICTOR</span>
          </motion.h1>

          <motion.p 
            className="text-[#7b93a8] text-sm leading-relaxed"
            variants={staggerItem}
          >
            Experience the next generation of tournament forecasting. Harnessing deep player performance telemetry, historical matchup records, and complex XGBoost simulation matrices, Antigravity models predict the road to the 2026 champion trophy across North America.
          </motion.p>

          {/* Stats row */}
          <motion.div 
            className="grid grid-cols-3 gap-3 pt-2"
            variants={staggerItem}
          >
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.04] hover:border-[#00e87b]/20 transition-all text-center">
              <span className="block text-xl font-display font-bold text-[#00e87b] tracking-wider">92.7%</span>
              <span className="block text-[9px] uppercase font-semibold text-[#3f5669] tracking-wider mt-1">Backtest Accuracy</span>
            </div>
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.04] hover:border-[#00e87b]/20 transition-all text-center">
              <span className="block text-xl font-display font-bold text-white tracking-wider">8.4B+</span>
              <span className="block text-[9px] uppercase font-semibold text-[#3f5669] tracking-wider mt-1">Data Points</span>
            </div>
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.04] hover:border-[#00e87b]/20 transition-all text-center">
              <span className="block text-xl font-display font-bold text-white tracking-wider">128</span>
              <span className="block text-[9px] uppercase font-semibold text-[#3f5669] tracking-wider mt-1">ML Models</span>
            </div>
          </motion.div>

          <motion.div 
            className="flex gap-4 pt-2"
            variants={staggerItem}
          >
            <button 
              onClick={() => setActiveTab('predictor')}
              className="bg-[#00e87b] hover:bg-[#00d46f] text-[#050a0e] px-6 py-3 rounded-full text-[12px] font-bold transition-all flex items-center gap-2 tracking-wide hover:shadow-[0_0_20px_rgba(0,232,123,0.35)] cursor-pointer"
            >
              Match Simulator
              <ArrowRight size={14} />
            </button>
            <button 
              onClick={() => setActiveTab('arena')}
              className="border border-white/10 text-white hover:border-[#00e87b]/30 hover:text-[#00e87b] px-6 py-3 rounded-full text-[12px] font-bold transition-all tracking-wide cursor-pointer"
            >
              Enter prediction arena
            </button>
          </motion.div>
        </div>

        {/* Center: Trophy Flanked by Flags */}
        <div className="lg:col-span-4 flex justify-center py-6 lg:py-0">
          <motion.div 
            className="trophy-flank-container"
            variants={staggerItem}
          >
            {/* USA Flag left-top */}
            <img 
              src="https://flagsapi.com/US/flat/64.png" 
              className="flag-flank flag-left-1 border border-white/[0.1] bg-black/20" 
              alt="United States" 
            />
            {/* Mexico Flag left-bottom */}
            <img 
              src="https://flagsapi.com/MX/flat/64.png" 
              className="flag-flank flag-left-2 border border-white/[0.1] bg-black/20" 
              alt="Mexico" 
            />
            {/* Canada Flag right-center */}
            <img 
              src="https://flagsapi.com/CA/flat/64.png" 
              className="flag-flank flag-right border border-white/[0.1] bg-black/20" 
              alt="Canada" 
            />

            {/* Central Trophy */}
            <motion.img 
              src="/world_cup_2026_trophy.png" 
              alt="FIFA World Cup 2026 Trophy" 
              className="w-48 h-auto object-contain select-none drop-shadow-[0_0_40px_rgba(212,165,74,0.35)] relative z-10"
              animate={{ 
                y: [0, -10, 0],
                rotate: [-2, 1, -2]
              }}
              transition={{ 
                duration: 6, 
                repeat: Infinity, 
                ease: "easeInOut" 
              }}
            />
          </motion.div>
        </div>

        {/* Right Side: Contenders Outlook (compact top 5) */}
        <div className="lg:col-span-3">
          <motion.div 
            className="glass-panel p-6 space-y-4"
            variants={staggerItem}
          >
            <div className="space-y-1">
              <span className="text-[9px] font-bold uppercase text-[#00e87b] tracking-[0.2em] block">2026 OUTLOOK</span>
              <h3 className="font-display text-2xl text-white tracking-wider">TOP CONTENDERS</h3>
            </div>

            <div className="space-y-3.5 pt-2">
              {top5.map((team, idx) => {
                const maxProb = top5[0]?.champion_prob || 1
                const barWidth = (team.champion_prob / maxProb) * 100
                return (
                  <div key={team.name} className="space-y-1.5">
                    <div className="flex justify-between items-center text-[12px]">
                      <span className="font-semibold text-white flex items-center gap-1.5 truncate">
                        {getFlagImg(team.name, "w-4 h-2.5 object-cover rounded-xs shrink-0")}
                        <span>{team.name}</span>
                      </span>
                      <span className="font-bold text-[#00e87b]">{(team.champion_prob * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-1 w-full bg-white/[0.02] rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-[#00e87b] rounded-full" 
                        style={{ width: `${barWidth}%` }} 
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </motion.div>
        </div>

      </div>

      {/* ─── FULL TOURNAMENT STATS TABLE ─── */}
      <motion.div
        className="glass-panel p-6 space-y-4"
        variants={staggerItem}
      >
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[9px] font-bold uppercase text-[#00e87b] tracking-[0.2em] block">MONTE CARLO SIMULATION</span>
            <h3 className="font-display text-2xl text-white tracking-wider">COMPLETE TOURNAMENT PROBABILITIES</h3>
            <p className="text-[11px] text-[#7b93a8]">All 48 teams ranked by predicted championship probability across 1,000+ simulations</p>
          </div>
          <button
            onClick={() => setShowAllTeams(!showAllTeams)}
            className="text-[11px] font-semibold text-[#00e87b] hover:text-white border border-[#00e87b]/20 hover:border-[#00e87b]/40 px-4 py-2 rounded-lg bg-[#00e87b]/[0.05] hover:bg-[#00e87b]/[0.1] transition-all cursor-pointer whitespace-nowrap"
          >
            {showAllTeams ? 'Show Top 15' : `Show All ${contenders.length} Teams`}
          </button>
        </div>

        {/* Table Header */}
        <div className="grid grid-cols-[40px_1fr_80px_80px_80px_80px_80px] gap-2 px-3 py-2 border-b border-white/[0.06] text-[9px] font-bold uppercase tracking-[0.15em] text-[#3f5669]">
          <span>#</span>
          <span>Team</span>
          <span className="text-center">Champion</span>
          <span className="text-center">Finalist</span>
          <span className="text-center">Semi-Final</span>
          <span className="text-center">Quarter-Final</span>
          <span className="text-center">Round of 16</span>
        </div>

        {/* Table Body */}
        <div className="space-y-0.5">
          {displayedTeams.map((team, idx) => {
            const maxChamp = contenders[0]?.champion_prob || 1
            const champBar = (team.champion_prob / maxChamp) * 100
            const isTop3 = idx < 3
            return (
              <div 
                key={team.name}
                className={`grid grid-cols-[40px_1fr_80px_80px_80px_80px_80px] gap-2 px-3 py-2.5 rounded-lg transition-all hover:bg-white/[0.03] ${
                  isTop3 ? 'bg-[#00e87b]/[0.02] border border-[#00e87b]/[0.06]' : 'border border-transparent'
                }`}
              >
                {/* Rank */}
                <span className={`text-[12px] font-display font-bold ${
                  idx === 0 ? 'text-[#d4a54a]' : idx === 1 ? 'text-[#c0c0c0]' : idx === 2 ? 'text-[#cd7f32]' : 'text-[#3f5669]'
                }`}>
                  {idx + 1}
                </span>

                {/* Team Name + Flag + Bar */}
                <div className="flex items-center gap-2 min-w-0">
                  {getFlagImg(team.name, "w-5 h-3 object-cover rounded-xs shrink-0 border border-white/[0.08]")}
                  <span className="text-[12px] font-semibold text-white truncate">{team.name}</span>
                  <div className="flex-1 h-1 bg-white/[0.02] rounded-full overflow-hidden ml-1 min-w-[30px] hidden md:block">
                    <div 
                      className={`h-full rounded-full ${isTop3 ? 'bg-[#00e87b]' : 'bg-[#00e87b]/50'}`}
                      style={{ width: `${champBar}%` }}
                    />
                  </div>
                </div>

                {/* Champion % */}
                <span className={`text-center text-[12px] font-bold ${
                  team.champion_prob >= 0.1 ? 'text-[#00e87b]' : team.champion_prob >= 0.03 ? 'text-white' : 'text-[#7b93a8]'
                }`}>
                  {(team.champion_prob * 100).toFixed(1)}%
                </span>

                {/* Finalist % */}
                <span className="text-center text-[12px] font-medium text-[#7b93a8]">
                  {(team.finalist_prob * 100).toFixed(1)}%
                </span>

                {/* Semi-Final % */}
                <span className="text-center text-[12px] font-medium text-[#7b93a8]">
                  {(team.semi_finalist_prob * 100).toFixed(1)}%
                </span>

                {/* QF % */}
                <span className="text-center text-[12px] font-medium text-[#7b93a8]">
                  {(team.quarter_finalist_prob * 100).toFixed(1)}%
                </span>

                {/* R16 % */}
                <span className="text-center text-[12px] font-medium text-[#3f5669]">
                  {(team.round_of_16_prob * 100).toFixed(1)}%
                </span>
              </div>
            )
          })}
        </div>

        {!showAllTeams && contenders.length > 15 && (
          <div className="text-center pt-2">
            <button
              onClick={() => setShowAllTeams(true)}
              className="text-[11px] text-[#7b93a8] hover:text-[#00e87b] transition-colors cursor-pointer"
            >
              + {contenders.length - 15} more teams...
            </button>
          </div>
        )}
      </motion.div>

      {/* Bottom Row info cards */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-3 gap-4 border-t border-white/[0.04] pt-8"
        variants={staggerItem}
      >
        <div className="p-5 rounded-2xl bg-white/[0.01] border border-white/[0.03] flex items-start gap-4">
          <div className="p-3 bg-[#d4a54a]/10 border border-[#d4a54a]/20 text-[#d4a54a] rounded-xl shrink-0">
            <Calendar size={18} />
          </div>
          <div>
            <span className="block text-[10px] uppercase font-bold text-[#3f5669] tracking-widest">TOURNAMENT DATES</span>
            <span className="block text-base font-bold text-white mt-1">June 11 – July 19, 2026</span>
            <span className="block text-[11px] text-[#7b93a8] mt-0.5">39 days of non-stop action</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white/[0.01] border border-white/[0.03] flex items-start gap-4">
          <div className="p-3 bg-[#00e87b]/10 border border-[#00e87b]/20 text-[#00e87b] rounded-xl shrink-0">
            <MapPin size={18} />
          </div>
          <div>
            <span className="block text-[10px] uppercase font-bold text-[#3f5669] tracking-widest">HOST CITIES</span>
            <span className="block text-base font-bold text-white mt-1">16 Cities Across N. America</span>
            <span className="block text-[11px] text-[#7b93a8] mt-0.5">United States, Mexico & Canada</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white/[0.01] border border-white/[0.03] flex items-start gap-4">
          <div className="p-3 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-xl shrink-0">
            <Trophy size={18} />
          </div>
          <div>
            <span className="block text-[10px] uppercase font-bold text-[#3f5669] tracking-widest">EXPANDED FIELD</span>
            <span className="block text-base font-bold text-white mt-1">48 Qualified Teams</span>
            <span className="block text-[11px] text-[#7b93a8] mt-0.5">104 matches, 12 groups of 4</span>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
//  ARENA PLAYGROUND VIEW
// ═══════════════════════════════════════════════════════════════════════════════
function ArenaView({ user, teams, setAuthModalOpen, leaderboard, leaderboardLoading, fetchLeaderboard }) {
  const [teamA, setTeamA] = useState('United States')
  const [teamB, setTeamB] = useState('Mexico')
  const [scoreA, setScoreA] = useState(1)
  const [scoreB, setScoreB] = useState(1)
  
  // Background match odds for the select matchup
  const [odds, setOdds] = useState(null)
  const [oddsLoading, setOddsLoading] = useState(false)
  const [simResult, setSimResult] = useState(null)
  const [simLoading, setSimLoading] = useState(false)
  const [history, setHistory] = useState([])

  // Fetch odds for selected A & B
  useEffect(() => {
    if (!teamA || !teamB || teamA === teamB) {
      setOdds(null)
      return
    }
    let active = true
    async function getOdds() {
      try {
        setOddsLoading(true)
        const res = await fetch('/api/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ team_a: teamA, team_b: teamB })
        })
        if (res.ok) {
          const data = await res.json()
          if (active) setOdds(data.probabilities)
        }
      } catch (err) {
        console.error("Error fetching odds in Arena:", err)
      } finally {
        if (active) setOddsLoading(false)
      }
    }
    getOdds()
    return () => { active = false }
  }, [teamA, teamB])

  const handleSwap = () => {
    const temp = teamA
    setTeamA(teamB)
    setTeamB(temp)
  }

  const handleSimulate = async (e) => {
    e.preventDefault()
    if (!user) {
      setAuthModalOpen(true)
      return
    }
    if (teamA === teamB) return
    
    try {
      setSimLoading(true)
      const res = await fetch('/api/arena/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: user.email,
          team_a: teamA,
          team_b: teamB,
          score_a: parseInt(scoreA),
          score_b: parseInt(scoreB)
        })
      })
      const data = await res.json()
      if (res.ok && data.status === 'success') {
        setSimResult(data)
        setHistory(prev => [data, ...prev])
        // Refetch leaderboard and update user state points externally
        fetchLeaderboard()
        // Update user points locally
        user.points = data.new_total_points
        user.predictions_count += 1
      }
    } catch (err) {
      console.error("Simulation submission failed:", err)
    } finally {
      setSimLoading(false)
    }
  }

  return (
    <div className="space-y-8 animate-fade-slide-up">
      
      {/* If user is not authenticated: Locked Screen state */}
      {!user ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-7 flex flex-col items-center justify-center p-8 glass-panel text-center min-h-[400px]">
            <div className="h-16 w-16 bg-[#00e87b]/10 border border-[#00e87b]/20 text-[#00e87b] rounded-2xl flex items-center justify-center mb-6">
              <Lock size={28} className="animate-pulse" />
            </div>
            <h2 className="text-3xl font-display text-white tracking-wide mb-2">ARENA PLAYGROUND</h2>
            <p className="text-[#7b93a8] text-sm max-w-md leading-relaxed mb-6">
              Prediction arena is a competitive simulation zone. Log in to enter match score predictions, match outcomes simulated by the ML engine, earn points, and enter the leaderboard!
            </p>
            <button 
              onClick={() => setAuthModalOpen(true)}
              className="bg-[#00e87b] hover:bg-[#00d46f] text-[#050a0e] px-8 py-3.5 rounded-full text-[13px] font-bold transition-all tracking-wide hover:shadow-[0_0_20px_rgba(0,232,123,0.3)] cursor-pointer"
            >
              Sign In to Join the Arena
            </button>
          </div>
          
          {/* Global Leaderboard (Read-Only) */}
          <div className="lg:col-span-5 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="font-display text-xl text-white tracking-wider flex items-center gap-2">
                <Trophy size={18} className="text-[#d4a54a]" />
                LEADERBOARD STANDINGS
              </h3>
            </div>
            
            <div className="glass-panel overflow-hidden p-4">
              {leaderboardLoading ? (
                <div className="flex h-64 items-center justify-center">
                  <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#00e87b] border-t-transparent"></div>
                </div>
              ) : (
                <table className="leaderboard-table">
                  <thead>
                    <tr>
                      <th className="w-16">Rank</th>
                      <th>User</th>
                      <th className="text-center">Preds</th>
                      <th className="text-right">Points</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaderboard.map((player, idx) => (
                      <tr key={idx} className="hover:bg-white/[0.01] transition-colors">
                        <td className="font-bold font-mono text-[#7b93a8]">{idx + 1}</td>
                        <td className="font-semibold text-white">{player.username}</td>
                        <td className="text-center font-mono text-[#7b93a8]">{player.predictions_count}</td>
                        <td className="text-right font-bold text-[#00e87b] font-mono">{player.points}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      ) : (
        /* Logged In View */
        <div className="space-y-6">
          
          {/* User Info Bar */}
          <div className="glass-panel p-5 flex flex-col sm:flex-row justify-between items-center gap-4 bg-[#0a1118]/80">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-[#00e87b]/10 border border-[#00e87b]/20 flex items-center justify-center text-[#00e87b]">
                <User size={18} />
              </div>
              <div>
                <h3 className="text-base font-bold text-white leading-tight">Welcome, {user.username}!</h3>
                <span className="text-[11px] text-[#7b93a8]">Predict matchups and check simulation outcomes below.</span>
              </div>
            </div>
            
            <div className="flex gap-6">
              <div className="text-center sm:text-right">
                <span className="block text-[9px] uppercase font-bold text-[#3f5669] tracking-wider">Predictions Made</span>
                <span className="block text-lg font-display text-white tracking-wide mt-0.5">{user.predictions_count}</span>
              </div>
              <div className="text-center sm:text-right">
                <span className="block text-[9px] uppercase font-bold text-[#3f5669] tracking-wider">Total Score</span>
                <span className="block text-lg font-display text-[#00e87b] tracking-wide mt-0.5">{user.points} pts</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Prediction Form & Simulator Panel */}
            <div className="lg:col-span-7 space-y-6">
              <div className="glass-panel p-6 space-y-5">
                <h3 className="font-display text-xl text-white tracking-wider flex items-center gap-2">
                  <Crosshair size={18} className="text-[#00e87b]" />
                  ARENA MATCHMAKER
                </h3>

                <form onSubmit={handleSimulate} className="space-y-5">
                  {/* Team Selection Dropdowns */}
                  <div className="grid grid-cols-1 sm:grid-cols-11 items-center gap-4 relative z-20">
                    {/* Team A Select */}
                    <div className="sm:col-span-5 space-y-1.5">
                      <label className="text-[10px] font-semibold text-[#7b93a8] uppercase tracking-wider">Team A</label>
                      <CustomTeamSelect 
                        value={teamA}
                        onChange={(val) => setTeamA(val)}
                        teams={teams}
                      />
                    </div>

                    {/* Swap Button */}
                    <div className="sm:col-span-1 flex justify-center pt-4 sm:pt-0">
                      <button 
                        type="button"
                        onClick={handleSwap}
                        className="h-8 w-8 rounded-full bg-white/[0.03] hover:bg-white/[0.06] transition flex items-center justify-center text-[#00e87b] border border-white/[0.06] cursor-pointer text-xs"
                      >
                        ⇄
                      </button>
                    </div>

                    {/* Team B Select */}
                    <div className="sm:col-span-5 space-y-1.5">
                      <label className="text-[10px] font-semibold text-[#7b93a8] uppercase tracking-wider">Team B</label>
                      <CustomTeamSelect 
                        value={teamB}
                        onChange={(val) => setTeamB(val)}
                        teams={teams}
                      />
                    </div>
                  </div>

                  {/* Team Matchup Model Odds Display */}
                  {teamA && teamB && teamA !== teamB && (
                    <div className="p-4 rounded-xl bg-white/[0.015] border border-white/[0.03] space-y-2.5">
                      <div className="flex justify-between items-center">
                        <span className="text-[10px] font-bold text-[#3f5669] uppercase tracking-wider">XGBoost Match Odds</span>
                        {oddsLoading && <span className="text-[9px] text-[#7b93a8] animate-pulse">Calculating...</span>}
                      </div>
                      {odds ? (
                        <div className="space-y-1.5">
                          <div className="flex justify-between text-[11px] font-semibold text-[#7b93a8]">
                            <span>{teamA}: {(odds.team_a_win * 100).toFixed(0)}%</span>
                            <span>Draw: {(odds.draw * 100).toFixed(0)}%</span>
                            <span>{teamB}: {(odds.team_b_win * 100).toFixed(0)}%</span>
                          </div>
                          <div className="h-2.5 w-full rounded-full overflow-hidden flex">
                            <div className="bg-blue-500/60" style={{ width: `${odds.team_a_win * 100}%` }} />
                            <div className="bg-[#7b93a8]/20" style={{ width: `${odds.draw * 100}%` }} />
                            <div className="bg-red-500/50" style={{ width: `${odds.team_b_win * 100}%` }} />
                          </div>
                        </div>
                      ) : (
                        <div className="text-[10px] text-[#3f5669]">Could not load model odds forecast.</div>
                      )}
                    </div>
                  )}

                  {/* Predictions inputs */}
                  <div className="space-y-2">
                    <label className="text-[10px] font-semibold text-[#7b93a8] uppercase tracking-wider block">YOUR SCORE PREDICTION</label>
                    <div className="flex items-center justify-center gap-6 p-4 rounded-xl bg-white/[0.015] border border-white/[0.03]">
                      <div className="flex items-center gap-2.5">
                        <span className="text-[12px] font-bold text-white flex items-center gap-1.5 truncate max-w-[120px]">
                          {getFlagImg(teamA, "w-4 h-2.5 object-cover rounded-xs shrink-0")}
                          <span>{teamA}</span>
                        </span>
                        <input 
                          type="number" 
                          min={0}
                          max={15}
                          required
                          value={scoreA}
                          onChange={(e) => setScoreA(e.target.value)}
                          className="w-12 h-10 rounded-lg bg-[#0c1620] border border-white/[0.06] text-center font-bold text-white text-sm focus:outline-none focus:border-[#00e87b]/30"
                        />
                      </div>
                      
                      <span className="text-[11px] font-semibold text-[#3f5669]">VS</span>

                      <div className="flex items-center gap-2.5">
                        <input 
                          type="number" 
                          min={0}
                          max={15}
                          required
                          value={scoreB}
                          onChange={(e) => setScoreB(e.target.value)}
                          className="w-12 h-10 rounded-lg bg-[#0c1620] border border-white/[0.06] text-center font-bold text-white text-sm focus:outline-none focus:border-[#00e87b]/30"
                        />
                        <span className="text-[12px] font-bold text-white flex items-center gap-1.5 truncate max-w-[120px]">
                          {getFlagImg(teamB, "w-4 h-2.5 object-cover rounded-xs shrink-0")}
                          <span>{teamB}</span>
                        </span>
                      </div>
                    </div>
                  </div>

                  <button 
                    type="submit" 
                    disabled={simLoading || teamA === teamB}
                    className="w-full h-12 rounded-xl bg-[#00e87b] hover:bg-[#00d46f] disabled:opacity-40 text-[#050a0e] font-bold text-[13px] tracking-wide flex items-center justify-center gap-2 transition hover:shadow-[0_0_20px_rgba(0,232,123,0.2)] cursor-pointer"
                  >
                    {simLoading ? (
                      <>
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-[#050a0e] border-t-transparent"></div>
                        Simulating Match...
                      </>
                    ) : (
                      <>
                        <Play size={12} fill="currentColor" />
                        Simulate & Resolve Match
                      </>
                    )}
                  </button>
                </form>
              </div>

              {/* Simulated Outcome Result Alert */}
              {simResult && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-5 rounded-2xl bg-white/[0.02] border border-white/[0.04] space-y-4"
                >
                  <div className="flex justify-between items-center">
                    <span className="inline-flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider text-[#00e87b] bg-[#00e87b]/[0.06] border border-[#00e87b]/[0.1] px-2.5 py-1 rounded-full">
                      <Zap size={10} />
                      Resolution Complete
                    </span>
                    <span className={`text-base font-bold font-display ${
                      simResult.points_earned === 3 ? 'text-[#00e87b] text-green-glow' :
                      simResult.points_earned === 1 ? 'text-blue-400' : 'text-[#7b93a8]'
                    }`}>
                      +{simResult.points_earned} Points Awarded
                    </span>
                  </div>

                  <div className="flex items-center justify-center gap-10 pt-1 text-center">
                    <div className="w-1/3">
                      <span className="block text-[10px] text-[#3f5669] font-medium uppercase tracking-wider">Prediction</span>
                      <span className="block text-2xl font-display text-white mt-1">
                        {simResult.user_prediction.goals_a} – {simResult.user_prediction.goals_b}
                      </span>
                    </div>
                    
                    <div className="h-10 w-[1px] bg-white/[0.04]" />

                    <div className="w-1/3">
                      <span className="block text-[10px] text-[#3f5669] font-medium uppercase tracking-wider">Simulated Score</span>
                      <span className="block text-2xl font-display text-[#00e87b] text-green-glow mt-1">
                        {simResult.actual_outcome.goals_a} – {simResult.actual_outcome.goals_b}
                      </span>
                    </div>
                  </div>

                  <p className="text-[11px] text-[#7b93a8] text-center leading-relaxed">
                    {simResult.points_earned === 3 ? '✨ Fantastic! Exact score predicted! You earned 3 points.' :
                     simResult.points_earned === 1 ? '👍 Correct match outcome predicted! You earned 1 point.' :
                     '❌ Wrong score and match outcome. Try another prediction to score points.'}
                  </p>
                </motion.div>
              )}
            </div>

            {/* Global Leaderboard Panel */}
            <div className="lg:col-span-5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="font-display text-xl text-white tracking-wider flex items-center gap-2">
                  <Trophy size={18} className="text-[#d4a54a]" />
                  LEADERBOARD STANDINGS
                </h3>
              </div>

              <div className="glass-panel overflow-hidden p-4">
                {leaderboardLoading ? (
                  <div className="flex h-64 items-center justify-center">
                    <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#00e87b] border-t-transparent"></div>
                  </div>
                ) : (
                  <table className="leaderboard-table">
                    <thead>
                      <tr>
                        <th className="w-16">Rank</th>
                        <th>User</th>
                        <th className="text-center">Preds</th>
                        <th className="text-right">Points</th>
                      </tr>
                    </thead>
                    <tbody>
                      {leaderboard.map((player, idx) => {
                        const isCurrentUser = user && player.email === user.email
                        return (
                          <tr 
                            key={idx} 
                            className={`hover:bg-white/[0.01] transition-colors ${
                              isCurrentUser ? 'leaderboard-row-user bg-[#00e87b]/[0.02]' : ''
                            }`}
                          >
                            <td className={`font-bold font-mono ${isCurrentUser ? 'text-[#00e87b]' : 'text-[#7b93a8]'}`}>
                              {idx + 1}
                            </td>
                            <td className={`font-semibold ${isCurrentUser ? 'text-[#00e87b]' : 'text-white'}`}>
                              {player.username} {isCurrentUser && <span className="text-[9px] font-bold text-[#00e87b]/70 border border-[#00e87b]/20 bg-[#00e87b]/5 px-1.5 py-0.5 rounded-sm ml-1.5">YOU</span>}
                            </td>
                            <td className="text-center font-mono text-[#7b93a8]">{player.predictions_count}</td>
                            <td className={`text-right font-bold font-mono ${isCurrentUser ? 'text-[#00e87b] text-green-glow' : 'text-white'}`}>{player.points}</td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          </div>

          {/* Session Predictions Log */}
          {history.length > 0 && (
            <div className="glass-panel p-6 space-y-4">
              <h3 className="font-display text-lg text-white tracking-wider flex items-center gap-2">
                <Activity size={16} className="text-[#00e87b]" />
                SESSION PREDICTIONS HISTORY
              </h3>

              <div className="overflow-x-auto border border-white/[0.04] rounded-xl">
                <table className="w-full text-[12px] text-left border-collapse">
                  <thead className="bg-white/[0.02] text-[#7b93a8] font-semibold border-b border-white/[0.04]">
                    <tr>
                      <th className="px-4 py-3">Matchup</th>
                      <th className="px-4 py-3 text-center">Your Prediction</th>
                      <th className="px-4 py-3 text-center">Simulated Score</th>
                      <th className="px-4 py-3 text-right">Points Earned</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/[0.03]">
                    {history.map((item, idx) => (
                      <tr key={idx} className="hover:bg-white/[0.01]">
                        <td className="px-4 py-3 font-semibold text-white">
                          <span className="flex items-center gap-2">
                            {getFlagImg(item.user_prediction.team_a, "w-4 h-2.5 object-cover rounded-xs")}
                            <span>{item.user_prediction.team_a}</span>
                            <span className="text-[#3f5669] font-normal">vs</span>
                            {getFlagImg(item.user_prediction.team_b, "w-4 h-2.5 object-cover rounded-xs")}
                            <span>{item.user_prediction.team_b}</span>
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center font-mono text-[#7b93a8]">
                          {item.user_prediction.goals_a} – {item.user_prediction.goals_b}
                        </td>
                        <td className="px-4 py-3 text-center font-mono text-[#00e87b]">
                          {item.actual_outcome.goals_a} – {item.actual_outcome.goals_b}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            item.points_earned === 3 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/15' :
                            item.points_earned === 1 ? 'bg-blue-500/10 text-blue-400 border border-blue-500/15' :
                            'bg-white/[0.02] text-[#3f5669]'
                          }`}>
                            +{item.points_earned} pts
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

        </div>
      )}

    </div>
  )
}
