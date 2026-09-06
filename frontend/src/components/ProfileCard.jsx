import React, { useState } from 'react';
import { UserCheck, MapPin, Briefcase, Wrench, IndianRupee, Layers, Target, Edit3, Check, X, AlertCircle } from 'lucide-react';
import { getTranslation } from '../services/translations';

export default function ProfileCard({ profile, onUpdateProfile, language = 'en' }) {
  const t = getTranslation(language);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({ ...profile });

  const handleStartEdit = () => {
    setFormData({
      name: profile.name || '',
      location: profile.location || '',
      district: profile.district || '',
      state: profile.state || '',
      occupation: profile.occupation || '',
      skills: (profile.skills || []).join(', '),
      experience: profile.experience || '',
      capital: profile.capital || '',
      resources: (profile.resources || []).join(', '),
      business_interest: profile.business_interest || '',
      goal: profile.goal || '',
      scale: profile.scale || ''
    });
    setIsEditing(true);
  };

  const handleSave = (e) => {
    e.preventDefault();
    const updated = {
      ...profile,
      name: formData.name || null,
      location: formData.location || null,
      district: formData.district || null,
      state: formData.state || null,
      occupation: formData.occupation || null,
      skills: formData.skills ? formData.skills.split(',').map((s) => s.trim()).filter(Boolean) : [],
      experience: formData.experience || null,
      capital: formData.capital ? parseFloat(formData.capital) : null,
      resources: formData.resources ? formData.resources.split(',').map((r) => r.trim()).filter(Boolean) : [],
      business_interest: formData.business_interest || null,
      goal: formData.goal || null,
      scale: formData.scale || null
    };
    onUpdateProfile(updated);
    setIsEditing(false);
  };

  const completionCount = [
    profile.name,
    profile.location || profile.district,
    profile.skills?.length > 0,
    profile.capital !== null && profile.capital !== undefined,
    profile.business_interest,
    profile.resources?.length > 0
  ].filter(Boolean).length;

  const totalFields = 6;
  const progressPercent = Math.round((completionCount / totalFields) * 100);

  return (
    <div className="bg-white rounded-2xl shadow-card border border-gv-border overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-gv-surface via-emerald-50 to-amber-50/40 px-4 py-3 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-7 h-7 rounded-lg bg-gv-primary text-white flex items-center justify-center text-xs font-bold shadow-2xs">
            <UserCheck className="w-4 h-4 text-amber-300" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-gv-dark uppercase tracking-wider font-display">
              {t.userProfile}
            </h3>
            <p className="text-[10px] text-slate-500 font-medium">Aarambh Saathi Profile</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <div className="text-right">
            <span className="text-[11px] font-bold text-gv-primary">{progressPercent}%</span>
            <span className="text-[10px] text-slate-400 block -mt-1">{t.completed}</span>
          </div>
          {!isEditing ? (
            <button
              onClick={handleStartEdit}
              className="p-1.5 rounded-lg text-slate-600 hover:text-gv-primary hover:bg-white border border-slate-200 transition text-xs flex items-center space-x-1"
              title="Edit Profile"
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline text-[11px]">
                {language === 'mr' ? 'बदला' : language === 'hi' ? 'संपादित करें' : 'Edit'}
              </span>
            </button>
          ) : (
            <button
              onClick={() => setIsEditing(false)}
              className="p-1.5 rounded-lg text-slate-500 hover:bg-slate-200 text-xs"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-100 h-1.5">
        <div
          className="bg-gradient-to-r from-amber-400 to-gv-secondary h-1.5 transition-all duration-500"
          style={{ width: `${progressPercent}%` }}
        ></div>
      </div>

      {/* Profile Body */}
      <div className="p-4">
        {isEditing ? (
          <form onSubmit={handleSave} className="space-y-3 text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div>
                <label className="block text-slate-600 font-medium mb-0.5">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Ramesh Patil"
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
                />
              </div>
              <div>
                <label className="block text-slate-600 font-medium mb-0.5">Available Capital (₹)</label>
                <input
                  type="number"
                  value={formData.capital}
                  onChange={(e) => setFormData({ ...formData, capital: e.target.value })}
                  placeholder="e.g. 100000"
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <div>
                <label className="block text-slate-600 font-medium mb-0.5">Village / City</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="e.g. Shirwal"
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
                />
              </div>
              <div>
                <label className="block text-slate-600 font-medium mb-0.5">District</label>
                <input
                  type="text"
                  value={formData.district}
                  onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                  placeholder="e.g. Satara"
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
                />
              </div>
              <div>
                <label className="block text-slate-600 font-medium mb-0.5">State</label>
                <input
                  type="text"
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  placeholder="e.g. Maharashtra"
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-600 font-medium mb-0.5">Business Interest</label>
              <input
                type="text"
                value={formData.business_interest}
                onChange={(e) => setFormData({ ...formData, business_interest: e.target.value })}
                placeholder="e.g. Dairy Farming, Mushroom, Tailoring"
                className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
              />
            </div>

            <div>
              <label className="block text-slate-600 font-medium mb-0.5">Skills (comma separated)</label>
              <input
                type="text"
                value={formData.skills}
                onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                placeholder="cattle, milking, animal husbandry"
                className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
              />
            </div>

            <div>
              <label className="block text-slate-600 font-medium mb-0.5">Available Resources (comma separated)</label>
              <input
                type="text"
                value={formData.resources}
                onChange={(e) => setFormData({ ...formData, resources: e.target.value })}
                placeholder="land, shed, water supply, electricity"
                className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
              />
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="px-3 py-1.5 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-3 py-1.5 bg-gv-primary hover:bg-gv-secondary text-white font-medium rounded-lg flex items-center space-x-1"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Save Profile</span>
              </button>
            </div>
          </form>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
            {/* Name */}
            <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
              <span className="text-[10px] text-slate-400 font-medium block">Entrepreneur</span>
              <p className="font-semibold text-slate-800 truncate">
                {profile.name || <span className="text-slate-400 italic">Not specified</span>}
              </p>
            </div>

            {/* Capital */}
            <div className="bg-emerald-50/60 p-2.5 rounded-xl border border-emerald-100">
              <span className="text-[10px] text-emerald-800 font-medium block flex items-center">
                <IndianRupee className="w-2.5 h-2.5 mr-0.5" /> Available Capital
              </span>
              <p className="font-bold text-emerald-900 text-sm">
                {profile.capital !== null && profile.capital !== undefined ? (
                  `₹${Number(profile.capital).toLocaleString('en-IN')}`
                ) : (
                  <span className="text-slate-400 italic text-xs font-normal">Pending</span>
                )}
              </p>
            </div>

            {/* Location */}
            <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
              <span className="text-[10px] text-slate-400 font-medium block flex items-center">
                <MapPin className="w-2.5 h-2.5 mr-0.5 text-amber-600" /> Location
              </span>
              <p className="font-semibold text-slate-800 truncate">
                {[profile.location, profile.district, profile.state].filter(Boolean).join(', ') || (
                  <span className="text-slate-400 italic">Location pending</span>
                )}
              </p>
            </div>

            {/* Business Interest */}
            <div className="bg-amber-50/50 p-2.5 rounded-xl border border-amber-100">
              <span className="text-[10px] text-amber-800 font-medium block flex items-center">
                <Target className="w-2.5 h-2.5 mr-0.5 text-amber-600" /> Interest
              </span>
              <p className="font-semibold text-amber-950 truncate">
                {profile.business_interest || <span className="text-slate-400 italic font-normal">Open to AI advice</span>}
              </p>
            </div>

            {/* Skills */}
            <div className="col-span-2 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
              <span className="text-[10px] text-slate-400 font-medium block flex items-center">
                <Wrench className="w-2.5 h-2.5 mr-0.5 text-gv-secondary" /> Known Skills & Background
              </span>
              <div className="flex flex-wrap gap-1 mt-1">
                {profile.skills && profile.skills.length > 0 ? (
                  profile.skills.map((s, idx) => (
                    <span
                      key={idx}
                      className="bg-white border border-slate-200 text-slate-700 px-2 py-0.5 rounded text-[10px] font-medium"
                    >
                      {s}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-400 italic">None registered yet</span>
                )}
                {profile.experience && (
                  <span className="bg-emerald-100/70 text-emerald-800 px-1.5 py-0.5 rounded text-[10px]">
                    Exp: {profile.experience}
                  </span>
                )}
              </div>
            </div>

            {/* Resources */}
            <div className="col-span-2 sm:col-span-3 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
              <span className="text-[10px] text-slate-400 font-medium block flex items-center">
                <Layers className="w-2.5 h-2.5 mr-0.5 text-blue-600" /> Available Physical Resources
              </span>
              <div className="flex flex-wrap gap-1 mt-1">
                {profile.resources && profile.resources.length > 0 ? (
                  profile.resources.map((r, idx) => (
                    <span
                      key={idx}
                      className="bg-blue-50 border border-blue-200 text-blue-800 px-2 py-0.5 rounded text-[10px] font-medium"
                    >
                      ✓ {r}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-400 italic">Land, shed, water or electricity info not yet shared</span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
