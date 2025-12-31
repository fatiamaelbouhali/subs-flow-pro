
import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Gestion from './components/Gestion';
import { Language, NavItem, ClientData } from './types';
import { MOCK_CLIENTS, TRANSLATIONS } from './constants';
import { ShieldAlert, LogIn, Loader2 } from 'lucide-react';

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [lang, setLang] = useState<Language>('FR');
  const [nav, setNav] = useState<NavItem>('DASHBOARD');
  const [clients, setClients] = useState<ClientData[]>(MOCK_CLIENTS);
  const [loginData, setLoginData] = useState({ user: '', pass: '' });
  const [isLoading, setIsLoading] = useState(false);

  // Business info mockup
  const bizName = "THE EMPIRE ELITE";

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate API delay
    setTimeout(() => {
      if (loginData.user && loginData.pass) {
        setIsAuthenticated(true);
      }
      setIsLoading(false);
    }, 1000);
  };

  const handleAddClient = (newClient: Omit<ClientData, 'id'>) => {
    const id = (clients.length + 1).toString();
    setClients([{ id, ...newClient }, ...clients]);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setLoginData({ user: '', pass: '' });
  };

  // Auth Screen
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-slate-950">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-teal-500/10 rounded-full blur-[100px]"></div>
          <div className="absolute bottom-1/4 left-1/4 w-64 h-64 bg-purple-500/10 rounded-full blur-[100px]"></div>
        </div>

        <div className="w-full max-w-md bg-slate-900/50 backdrop-blur-2xl border border-white/10 p-10 rounded-[2.5rem] shadow-2xl relative z-10 animate-in zoom-in-95 duration-500">
          <div className="flex flex-col items-center mb-10">
            <div className="bg-teal-500 p-4 rounded-3xl shadow-xl shadow-teal-500/20 mb-6">
              <ShieldAlert size={48} className="text-white" />
            </div>
            <h1 className="text-3xl font-black text-white tracking-tighter text-center">EMPIRE <span className="text-teal-500">GATEWAY</span></h1>
            <p className="text-slate-500 text-sm mt-2 font-bold uppercase tracking-widest">Secured Enterprise V86</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-6">
            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] ml-2">Commander Identity</label>
              <input 
                type="text" 
                value={loginData.user}
                onChange={(e) => setLoginData({...loginData, user: e.target.value})}
                className="w-full bg-slate-950/50 border-2 border-slate-800 rounded-2xl px-6 py-4 text-white focus:border-teal-500 focus:outline-none transition-all placeholder:text-slate-700" 
                placeholder="Username" 
              />
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] ml-2">Access Key</label>
              <input 
                type="password" 
                value={loginData.pass}
                onChange={(e) => setLoginData({...loginData, pass: e.target.value})}
                className="w-full bg-slate-950/50 border-2 border-slate-800 rounded-2xl px-6 py-4 text-white focus:border-teal-500 focus:outline-none transition-all placeholder:text-slate-700" 
                placeholder="••••••••" 
              />
            </div>
            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full bg-teal-500 hover:bg-teal-400 text-slate-900 font-black py-4 rounded-2xl transition-all shadow-lg shadow-teal-500/20 active:scale-95 flex items-center justify-center gap-2 mt-4"
            >
              {isLoading ? <Loader2 className="animate-spin" /> : <LogIn size={20} />}
              {isLoading ? 'INITIATING...' : 'AUTHORIZE ACCESS'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex h-screen bg-slate-950 text-slate-100 selection:bg-teal-500 selection:text-white ${lang === 'AR' ? 'flex-row-reverse' : 'flex-row'}`} dir={lang === 'AR' ? 'rtl' : 'ltr'}>
      <Sidebar 
        currentNav={nav} 
        setNav={setNav} 
        lang={lang} 
        setLang={setLang} 
        onLogout={handleLogout} 
      />
      
      <main className="flex-1 overflow-y-auto relative">
        {/* Top Header Section */}
        <header className="sticky top-0 z-40 bg-slate-950/80 backdrop-blur-md border-b border-white/5 p-8 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="w-1.5 h-10 bg-teal-500 rounded-full"></div>
            <div>
              <h2 className="text-2xl font-black text-white tracking-tight uppercase">{bizName}</h2>
              <p className="text-slate-500 text-[10px] font-bold tracking-[0.3em]">{TRANSLATIONS[lang].nav[nav.toLowerCase() as keyof typeof TRANSLATIONS.FR.nav]}</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
             <div className="flex flex-col items-end">
               <span className="text-xs font-black text-white">ADMIN_COMMANDER</span>
               <span className="text-[10px] font-bold text-teal-500 uppercase tracking-widest">Online / Cloud Sync</span>
             </div>
             <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-slate-700 to-slate-800 border border-white/10 p-0.5 shadow-lg">
                <img src="https://picsum.photos/seed/admin/48/48" className="w-full h-full rounded-[0.8rem] object-cover" alt="User" />
             </div>
          </div>
        </header>

        {/* Content Section */}
        <div className="p-8 max-w-7xl mx-auto">
          {nav === 'DASHBOARD' && <Dashboard lang={lang} data={clients} />}
          {nav === 'GESTION' && <Gestion lang={lang} data={clients} onAddClient={handleAddClient} />}
          
          {(nav === 'RAPPELS' || nav === 'RECEIPTS') && (
            <div className="flex flex-col items-center justify-center py-32 text-slate-500 space-y-4">
              <div className="p-6 bg-slate-900 rounded-full border border-slate-800">
                <Loader2 size={48} className="animate-pulse opacity-20" />
              </div>
              <p className="font-bold tracking-[0.2em] text-xs uppercase opacity-50">Feature Protocol Pending Initialization</p>
            </div>
          )}
        </div>

        {/* Floating Sync Indicator */}
        <div className="fixed bottom-8 right-8 flex items-center gap-2 bg-slate-900/90 border border-teal-500/20 px-4 py-2 rounded-full backdrop-blur-lg shadow-xl shadow-black/50">
          <div className="w-2 h-2 rounded-full bg-teal-500 animate-ping"></div>
          <span className="text-[10px] font-black text-teal-500 uppercase tracking-widest">Live Cloud Connection</span>
        </div>
      </main>
    </div>
  );
};

export default App;
