
import React from 'react';
import { NavItem, Language } from '../types';
import { TRANSLATIONS } from '../constants';
import { 
  LayoutDashboard, 
  Users, 
  Bell, 
  FileText, 
  LogOut, 
  Download,
  ChevronLeft,
  ChevronRight,
  Menu
} from 'lucide-react';
import { storageService } from '../services/storageService';

interface SidebarProps {
  lang: Language;
  setLang: (lang: Language) => void;
  activeTab: NavItem;
  setActiveTab: (tab: NavItem) => void;
  isOpen: boolean;
  toggleSidebar: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  lang, 
  setLang, 
  activeTab, 
  setActiveTab, 
  isOpen, 
  toggleSidebar 
}) => {
  const L = TRANSLATIONS[lang];

  // Reordered to put GESTION first
  const menuItems: { id: NavItem; icon: React.ReactNode; label: string }[] = [
    { id: 'GESTION', icon: <Users size={22} />, label: L.nav.management },
    { id: 'ANALYTICS', icon: <LayoutDashboard size={22} />, label: L.nav.analytics },
    { id: 'REMINDERS', icon: <Bell size={22} />, label: L.nav.reminders },
    { id: 'RECEIPTS', icon: <FileText size={22} />, label: L.nav.receipts },
  ];

  return (
    <div className={`
      relative h-screen flex flex-col transition-all duration-300 bg-slate-900 shadow-2xl z-50
      ${isOpen ? 'w-80' : 'w-24'}
      ${lang === 'AR' ? 'border-l border-slate-800' : 'border-r border-slate-800'}
    `}>
      {/* Header */}
      <div className="p-8 flex items-center justify-between">
        {isOpen && (
          <div className="flex items-center gap-2">
            <span className="font-black text-2xl text-white italic tracking-tighter">EMPIRE</span>
            <span className="w-1.5 h-1.5 rounded-full bg-[#14B8A6]"></span>
          </div>
        )}
        <button 
          onClick={toggleSidebar}
          className="p-2.5 hover:bg-slate-800 rounded-xl text-slate-400 transition-colors"
        >
          {isOpen ? (lang === 'AR' ? <ChevronRight size={20} /> : <ChevronLeft size={20} />) : <Menu size={20} />}
        </button>
      </div>

      {/* Language Toggle */}
      <div className={`px-6 mb-8 ${isOpen ? '' : 'hidden'}`}>
        <div className="bg-slate-800/50 p-1.5 rounded-[1.25rem] flex items-center border border-slate-800">
          <button 
            onClick={() => setLang('FR')}
            className={`flex-1 py-2 rounded-xl text-xs font-black transition-all ${lang === 'FR' ? 'bg-[#14B8A6] text-white shadow-lg shadow-teal-900/20' : 'text-slate-500 hover:text-slate-300'}`}
          >
            FR
          </button>
          <button 
            onClick={() => setLang('AR')}
            className={`flex-1 py-2 rounded-xl text-xs font-black transition-all ${lang === 'AR' ? 'bg-[#14B8A6] text-white shadow-lg shadow-teal-900/20' : 'text-slate-500 hover:text-slate-300'}`}
          >
            AR
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-6 space-y-3">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`
              w-full flex items-center p-4 rounded-2xl transition-all group relative
              ${activeTab === item.id 
                ? 'bg-gradient-to-r from-slate-800 to-slate-800/50 text-[#14B8A6] border border-slate-700' 
                : 'text-slate-400 hover:bg-slate-800/30 hover:text-white'}
              ${lang === 'AR' ? 'flex-row-reverse gap-4' : 'flex-row gap-4'}
            `}
          >
            {activeTab === item.id && (
              <div className={`absolute w-1.5 h-6 bg-[#14B8A6] rounded-full ${lang === 'AR' ? 'right-0' : 'left-0'}`} />
            )}
            <span className={activeTab === item.id ? 'text-[#14B8A6]' : 'text-slate-500 group-hover:text-slate-300 transition-colors'}>
              {item.icon}
            </span>
            {isOpen && <span className="font-bold text-sm tracking-wide uppercase">{item.label}</span>}
          </button>
        ))}
      </nav>

      {/* Footer Actions */}
      <div className="p-6 border-t border-slate-800 space-y-3">
        <button 
          onClick={() => storageService.exportToJSON()}
          className={`
            w-full flex items-center p-4 rounded-xl hover:bg-slate-800 text-slate-400 transition-all
            ${lang === 'AR' ? 'flex-row-reverse gap-4' : 'flex-row gap-4'}
          `}
        >
          <Download size={20} />
          {isOpen && <span className="font-bold text-sm">{L.common.export}</span>}
        </button>
        <button 
          onClick={() => window.location.reload()}
          className={`
            w-full flex items-center p-4 rounded-xl hover:bg-rose-950/30 text-rose-400 transition-all
            ${lang === 'AR' ? 'flex-row-reverse gap-4' : 'flex-row gap-4'}
          `}
        >
          <LogOut size={20} />
          {isOpen && <span className="font-bold text-sm">{L.common.logout}</span>}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
