import React, { useState } from 'react';
import {
  UserCheck,
  MapPin,
  Briefcase,
  Wrench,
  IndianRupee,
  Layers,
  Target,
  Edit3,
  Check,
  X,
  GraduationCap,
  Calendar,
  Compass,
  Building2,
  HelpCircle
} from 'lucide-react';
import { getTranslation } from '../services/translations';

export default function ProfileCard({ profile, onUpdateProfile, language = 'en' }) {
  const t = getTranslation(language);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({ ...profile });

  const handleStartEdit = () => {
    setFormData({
      name: profile.name || '',
      intent: profile.intent || 'Start a new business',
      age: profile.age || '',
      gender: profile.gender || '',
      village: profile.village || '',
      district: profile.district || '',
      state: profile.state || '',
      education: profile.education || '',
      occupation: profile.occupation || '',
      skills: (profile.skills || []).join(', '),
      experience: profile.experience || '',
      capital: profile.available_investment !== null && profile.available_investment !== undefined
        ? profile.available_investment
        : profile.capital || '',
      resources: (profile.resources || []).join(', '),
      business_interest: profile.business_interest || '',
      existing_business: profile.existing_business || '',
      goal: profile.goal || '',
      scale: profile.scale || ''
    });
    setIsEditing(true);
  };

  const handleSave = (e) => {
    e.preventDefault();
    const invAmount = formData.capital ? parseFloat(formData.capital) : null;
    const locParts = [formData.village, formData.district, formData.state].filter(Boolean);
    
    const updated = {
      ...profile,
      name: formData.name ? formData.name.trim() : null,
      intent: formData.intent || null,
      age: formData.age ? parseInt(formData.age, 10) : null,
      gender: formData.gender || null,
      village: formData.village ? formData.village.trim() : null,
      district: formData.district ? formData.district.trim() : null,
      state: formData.state ? formData.state.trim() : null,
      location: locParts.length > 0 ? locParts.join(', ') : null,
      education: formData.education || null,
      occupation: formData.occupation || null,
      skills: formData.skills ? formData.skills.split(',').map((s) => s.trim()).filter(Boolean) : [],
      experience: formData.experience || null,
      available_investment: invAmount,
      capital: invAmount,
      resources: formData.resources ? formData.resources.split(',').map((r) => r.trim()).filter(Boolean) : [],
      business_interest: formData.business_interest || null,
      existing_business: formData.existing_business || null,
      goal: formData.goal || null,
      scale: formData.scale || null
    };
    onUpdateProfile(updated);
    setIsEditing(false);
  };

  const completedFieldsList = [
    profile.name,
    profile.intent,
    profile.age,
    profile.gender,
    profile.village || profile.district || profile.location,
    profile.education,
    profile.skills?.length > 0,
    profile.experience,
    profile.resources?.length > 0,
    profile.available_investment !== null && profile.available_investment !== undefined || profile.capital !== null && profile.capital !== undefined,
    profile.business_interest
  ].filter(Boolean);

  const totalFields = 11;
  const progressPercent = Math.min(100, Math.round((completedFieldsList.length / totalFields) * 100));

  const investmentValue = profile.available_investment !== null && profile.available_investment !== undefined
    ? profile.available_investment
    : profile.capital;

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
              {t.userProfile || 'User Profile'}
            </h3>
            <p className="text-[10px] text-slate-500 font-medium">Aarambh Saathi Profile</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <div className="text-right">
            <span className="text-[11px] font-bold text-gv-primary">{progressPercent}%</span>
            <span className="text-[10px] text-slate-400 block -mt-1">{t.completed || 'Completed'}</span>
          </div>
          {!isEditing ? (
            <button
              onClick={handleStartEdit}
              className="p-1.5 rounded-lg text-slate-600 hover:text-gv-primary hover:bg-white border border-slate-200 transition text-xs flex items-center space-x-1"
              title="Edit Profile"
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline text-[11px]">
                {language === 'mr' ? 'माहिती बदला' : language === 'hi' ? 'विवरण बदलें' : 'Edit Details'}
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
                <label className="block text-slate-600 font-medium mb-0.5">Name / नाव / नाम</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Ramesh Patil"
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
                />
              </div>
              <div>
                <label className="block text-slate-600 font-medium mb-0.5">Intent / उद्देश / उद्देश्य</label>
                <select
                  value={formData.intent}
                  onChange={(e) => setFormData({ ...formData, intent: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary bg-white"
                >
                  <option value="Start a new business">Start a new business / नवीन व्यवसाय</option>
                  <option value="Expand an existing business">Expand an existing business / व्यवसाय वाढवणे</option>
                  <option value="I don't know what business to start">I don't know what business to start / सल्ला हवा</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <div>
                <label className="block text-slate-600 font-medium mb-0.5">Age / वय</label>
                <input
                  type="number"
                  value={formData.age}
                  onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                  placeholder="e.g. 28"
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
                />
              </div>
              <div>
                <label className="block text-slate-600 font-medium mb-0.5">Gender / लिंग</label>
                <select
                  value={formData.gender}
                  onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary bg-white"
                >
                  <option value="">Select / निवडा</option>
                  <option value="Male">Male / पुरुष</option>
                  <option value="Female">Female / महिला</option>
                  <option value="Other">Other / इतर</option>
                </select>
              </div>
              <div className="col-span-2">
                <label className="block text-slate-600 font-medium mb-0.5">Education / शिक्षण</label>
                <select
                  value={formData.education}
                  onChange={(e) => setFormData({ ...formData, education: e.target.value })}
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary bg-white"
                >
                  <option value="">Select / निवडा</option>
                  <option value="10th Pass">10th Pass / १०वी</option>
                  <option value="12th Pass">12th Pass / १२वी</option>
                  <option value="Graduate">Graduate / पदवीधर</option>
                  <option value="Diploma / Vocational">Diploma / ITI</option>
                  <option value="No Formal Schooling">No Formal Schooling</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <div>
                <label className="block text-slate-600 font-medium mb-0.5">Village / City / गाव</label>
                <input
                  type="text"
                  value={formData.village}
                  onChange={(e) => setFormData({ ...formData, village: e.target.value })}
                  placeholder="e.g. Shirwal"
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
                />
              </div>
              <div>
                <label className="block text-slate-600 font-medium mb-0.5">District / जिल्हा</label>
                <input
                  type="text"
                  value={formData.district}
                  onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                  placeholder="e.g. Satara"
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
                />
              </div>
              <div>
                <label className="block text-slate-600 font-medium mb-0.5">State / राज्य</label>
                <input
                  type="text"
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  placeholder="e.g. Maharashtra"
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div>
                <label className="block text-slate-600 font-medium mb-0.5">Available Investment (₹) / गुंतवणूक</label>
                <input
                  type="number"
                  value={formData.capital}
                  onChange={(e) => setFormData({ ...formData, capital: e.target.value })}
                  placeholder="e.g. 100000"
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
                />
              </div>
              <div>
                <label className="block text-slate-600 font-medium mb-0.5">Experience / कामाचा अनुभव</label>
                <input
                  type="text"
                  value={formData.experience}
                  onChange={(e) => setFormData({ ...formData, experience: e.target.value })}
                  placeholder="e.g. 1-3 Years Experience"
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-600 font-medium mb-0.5">Business Interest / इच्छित व्यवसाय</label>
              <input
                type="text"
                value={formData.business_interest}
                onChange={(e) => setFormData({ ...formData, business_interest: e.target.value })}
                placeholder="e.g. Dairy Farming, Mushroom, Tailoring"
                className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
              />
            </div>

            <div>
              <label className="block text-slate-600 font-medium mb-0.5">Skills / कौशल्ये (comma separated)</label>
              <input
                type="text"
                value={formData.skills}
                onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                placeholder="cattle rearing, milking, animal husbandry"
                className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
              />
            </div>

            <div>
              <label className="block text-slate-600 font-medium mb-0.5">Available Resources / साधने (comma separated)</label>
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
                <span>{t.saveProfileBtn || 'Save Details'}</span>
              </button>
            </div>
          </form>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs">
            {/* Name */}
            <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
              <span className="text-[10px] text-slate-400 font-medium block">Entrepreneur</span>
              <p className="font-semibold text-slate-800 truncate">
                {profile.name || <span className="text-slate-400 italic">Not specified</span>}
              </p>
            </div>

            {/* Investment */}
            <div className="bg-emerald-50/60 p-2.5 rounded-xl border border-emerald-100">
              <span className="text-[10px] text-emerald-800 font-medium block flex items-center">
                <IndianRupee className="w-2.5 h-2.5 mr-0.5" /> {t.profileInvestment || 'Available Investment'}
              </span>
              <p className="font-bold text-emerald-900 text-sm">
                {investmentValue !== null && investmentValue !== undefined ? (
                  `₹${Number(investmentValue).toLocaleString('en-IN')}`
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
                {[profile.village, profile.district, profile.state].filter(Boolean).join(', ') || profile.location || (
                  <span className="text-slate-400 italic">Location pending</span>
                )}
              </p>
            </div>

            {/* Age & Gender */}
            <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
              <span className="text-[10px] text-slate-400 font-medium block flex items-center">
                <Calendar className="w-2.5 h-2.5 mr-0.5 text-blue-500" /> Age & Gender
              </span>
              <p className="font-semibold text-slate-800 truncate">
                {profile.age ? `${profile.age} Yrs` : '—'}{profile.gender ? ` · ${profile.gender}` : ''}
              </p>
            </div>

            {/* Education */}
            <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
              <span className="text-[10px] text-slate-400 font-medium block flex items-center">
                <GraduationCap className="w-2.5 h-2.5 mr-0.5 text-purple-600" /> Education
              </span>
              <p className="font-semibold text-slate-800 truncate">
                {profile.education || <span className="text-slate-400 italic font-normal">Pending</span>}
              </p>
            </div>

            {/* Intent / Goal */}
            <div className="bg-amber-50/50 p-2.5 rounded-xl border border-amber-100">
              <span className="text-[10px] text-amber-800 font-medium block flex items-center">
                <Compass className="w-2.5 h-2.5 mr-0.5 text-amber-600" /> Intent
              </span>
              <p className="font-semibold text-amber-950 truncate">
                {profile.intent || <span className="text-slate-400 italic font-normal">Start new business</span>}
              </p>
            </div>

            {/* Business Interest / Existing Business */}
            <div className="col-span-2 sm:col-span-3 bg-amber-50/50 p-2.5 rounded-xl border border-amber-100">
              <span className="text-[10px] text-amber-800 font-medium block flex items-center">
                <Target className="w-2.5 h-2.5 mr-0.5 text-amber-600" /> Business Interest & Focus
              </span>
              <p className="font-semibold text-amber-950">
                {profile.business_interest || <span className="text-slate-400 italic font-normal">Open to AI advice</span>}
                {profile.existing_business && (
                  <span className="ml-2 text-[11px] font-normal text-slate-600">
                    (Expanding: {profile.existing_business})
                  </span>
                )}
              </p>
            </div>

            {/* Skills */}
            <div className="col-span-2 sm:col-span-3 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
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
                  <span className="bg-emerald-100/70 text-emerald-800 px-1.5 py-0.5 rounded text-[10px] font-medium">
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
