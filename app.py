
import React, { useState } from 'react';
import { Plus, ChevronDown, CheckCircle2 } from 'lucide-react';

const GestionView: React.FC = () => {
  const [formData, setFormData] = useState({
    nom: '',
    email: '',
    prix: 0,
    whatsapp: '',
    service: 'Netflix',
    startDate: new Date().toISOString().split('T')[0],
    months: 1
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'prix' || name === 'months' ? Number(value) : value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert('Enregistré avec succès !');
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-700">
      <div className="space-y-2">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center">
            <Plus className="text-indigo-600 w-6 h-6" />
          </div>
          <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Gestion des Clients</h1>
        </div>
        <p className="text-slate-500 text-sm font-medium ml-13">Ajoutez un nouvel abonné à votre base de données.</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white p-10 rounded-[2.5rem] border border-slate-100 shadow-sm space-y-10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-10 gap-y-8">
          {/* Nom */}
          <div className="space-y-3">
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-widest">Nom & Prénom</label>
            <input
              type="text"
              name="nom"
              value={formData.nom}
              onChange={handleInputChange}
              className="w-full p-4 border border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none text-slate-700 font-medium"
              placeholder="Nom du client"
            />
          </div>

          {/* Email */}
          <div className="space-y-3">
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-widest">Email (Facultatif)</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className="w-full p-4 border border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none text-slate-700 font-medium"
              placeholder="client@domaine.com"
            />
          </div>

          {/* WhatsApp */}
          <div className="space-y-3">
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-widest">WhatsApp</label>
            <input
              type="text"
              name="whatsapp"
              value={formData.whatsapp}
              onChange={handleInputChange}
              className="w-full p-4 border border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none text-slate-700 font-medium"
              placeholder="+212 ..."
            />
          </div>

          {/* Service */}
          <div className="space-y-3">
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-widest">Service</label>
            <div className="relative">
              <select
                name="service"
                value={formData.service}
                onChange={handleInputChange}
                className="w-full p-4 border border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none appearance-none text-slate-700 font-bold"
              >
                <option>Netflix</option>
                <option>IPTV</option>
                <option>ChatGPT</option>
                <option>Udemy</option>
                <option>Spotify</option>
              </select>
              <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none w-4 h-4" />
            </div>
          </div>

          {/* Prix */}
          <div className="space-y-3">
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-widest">Tarif (DH)</label>
            <div className="flex items-center group">
              <button 
                type="button" 
                onClick={() => setFormData(p => ({...p, prix: Math.max(0, p.prix - 10)}))}
                className="w-14 h-14 flex items-center justify-center border border-r-0 border-slate-200 rounded-l-xl hover:bg-white hover:text-indigo-600 transition-colors font-bold text-xl bg-slate-50 text-slate-500"
              >-</button>
              <input
                type="number"
                name="prix"
                value={formData.prix}
                onChange={handleInputChange}
                className="flex-1 h-14 border border-slate-200 text-center font-bold text-xl outline-none text-slate-800 bg-white"
              />
              <button 
                type="button" 
                onClick={() => setFormData(p => ({...p, prix: p.prix + 10}))}
                className="w-14 h-14 flex items-center justify-center border border-l-0 border-slate-200 rounded-r-xl hover:bg-white hover:text-indigo-600 transition-colors font-bold text-xl bg-slate-50 text-slate-500"
              >+</button>
            </div>
          </div>

          {/* Start Date */}
          <div className="space-y-3">
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-widest">Date de début</label>
            <input
              type="date"
              name="startDate"
              value={formData.startDate}
              onChange={handleInputChange}
              className="w-full p-4 border border-slate-200 rounded-xl bg-slate-50 focus:bg-white focus:border-indigo-400 outline-none font-semibold text-slate-700"
            />
          </div>

          {/* Months */}
          <div className="space-y-3 md:col-start-1">
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-widest">Durée (Mois)</label>
            <div className="flex items-center">
              <button 
                type="button" 
                onClick={() => setFormData(p => ({...p, months: Math.max(1, p.months - 1)}))}
                className="w-14 h-14 flex items-center justify-center border border-r-0 border-slate-200 rounded-l-xl hover:bg-white hover:text-indigo-600 transition-colors font-bold text-xl bg-slate-50 text-slate-500"
              >-</button>
              <input
                type="number"
                name="months"
                value={formData.months}
                onChange={handleInputChange}
                className="flex-1 h-14 border border-slate-200 text-center font-bold text-xl outline-none text-slate-800 bg-white"
              />
              <button 
                type="button" 
                onClick={() => setFormData(p => ({...p, months: p.months + 1}))}
                className="w-14 h-14 flex items-center justify-center border border-l-0 border-slate-200 rounded-r-xl hover:bg-white hover:text-indigo-600 transition-colors font-bold text-xl bg-slate-50 text-slate-500"
              >+</button>
            </div>
          </div>
        </div>

        <button
          type="submit"
          className="w-full py-5 bg-indigo-600 text-white rounded-[1.5rem] font-bold text-lg shadow-xl shadow-indigo-100 hover:bg-indigo-700 hover:-translate-y-0.5 transition-all flex items-center justify-center gap-3 active:scale-95"
        >
          <CheckCircle2 className="w-6 h-6" />
          Sauvegarder les données
        </button>
      </form>
    </div>
  );
};

export default GestionView;
