
import React, { useState } from 'react';
import { BusinessStats } from '../types.ts';
import { getSmartInsights } from '../services/geminiService.ts';
import { Sparkles, TrendingUp, Users, AlertCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface AnalyticsViewProps {
  stats: BusinessStats;
}

export default function AnalyticsView({ stats }: AnalyticsViewProps) {
  const [insights, setInsights] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGetInsights = async () => {
    setLoading(true);
    const result = await getSmartInsights(stats);
    setInsights(result || "Erreur de connexion");
    setLoading(false);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <span className="text-slate-400 font-bold text-[10px] tracking-widest uppercase">Chiffre d'Affaire</span>
            <div className="p-2 bg-emerald-50 rounded-lg">
              <TrendingUp className="text-emerald-500 w-4 h-4" />
            </div>
          </div>
          <p className="text-3xl font-black text-slate-800">{stats.revenueTotal} DH</p>
        </div>

        <div className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <span className="text-slate-400 font-bold text-[10px] tracking-widest uppercase">Abonnés Actifs</span>
            <div className="p-2 bg-indigo-50 rounded-lg">
              <Users className="text-indigo-500 w-4 h-4" />
            </div>
          </div>
          <p className="text-3xl font-black text-slate-800">{stats.actifs}</p>
        </div>

        <div className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <span className="text-slate-400 font-bold text-[10px] tracking-widest uppercase">Alertes Fin</span>
            <div className="p-2 bg-rose-50 rounded-lg">
              <AlertCircle className="text-rose-500 w-4 h-4" />
            </div>
          </div>
          <p className="text-3xl font-black text-slate-800">{stats.alertes}</p>
        </div>
      </div>

      <div className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm">
        <div className="flex items-center gap-3 mb-6">
          <Sparkles className="text-amber-500 w-5 h-5" />
          <h2 className="text-lg font-bold text-slate-800 tracking-tight">Analyse Intelligente</h2>
        </div>
        {!insights ? (
          <button
            onClick={handleGetInsights}
            disabled={loading}
            className="px-8 py-3 bg-indigo-600 text-white rounded-xl text-sm font-bold hover:bg-indigo-700 transition-all disabled:opacity-50 shadow-lg shadow-indigo-100"
          >
            {loading ? "Calcul en cours..." : "Générer les insights de Fatima"}
          </button>
        ) : (
          <div className="p-6 bg-slate-50 border border-slate-100 rounded-2xl text-slate-600 text-sm leading-relaxed font-medium italic">
            "{insights}"
          </div>
        )}
      </div>

      <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-50 bg-slate-50/50">
          <h2 className="text-lg font-bold text-slate-800 tracking-tight">Répartition par Service</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-indigo-600 text-white">
                <th className="px-8 py-4 font-bold text-xs uppercase tracking-widest">Service</th>
                <th className="px-8 py-4 font-bold text-xs uppercase tracking-widest text-center">Clients</th>
                <th className="px-8 py-4 font-bold text-xs uppercase tracking-widest text-right">Revenu</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {stats.summaries.map((s, i) => (
                <tr key={i} className="hover:bg-slate-50/80 transition-colors">
                  <td className="px-8 py-5 font-bold text-slate-700">{s.service}</td>
                  <td className="px-8 py-5 font-bold text-indigo-600 text-center">{s.clients}</td>
                  <td className="px-8 py-5 font-bold text-slate-800 text-right">{s.caTotal} DH</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm h-96">
        <h2 className="text-lg font-bold text-slate-800 mb-8 tracking-tight">Performance Mensuelle</h2>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={stats.summaries}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis dataKey="service" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12, fontWeight: 600}} dy={10} />
            <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12, fontWeight: 600}} />
            <Tooltip 
              cursor={{fill: '#f8fafc'}}
              contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)', padding: '12px' }}
            />
            <Bar dataKey="caTotal" fill="#6366f1" radius={[8, 8, 0, 0]} barSize={45} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
