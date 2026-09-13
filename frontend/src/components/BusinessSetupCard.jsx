import React, { useState, useEffect } from 'react';
import { 
  Wrench, 
  Search, 
  MapPin, 
  ShieldCheck, 
  ShieldAlert, 
  CheckCircle2, 
  ExternalLink, 
  ChevronRight, 
  ChevronDown, 
  ChevronUp, 
  Info, 
  AlertTriangle,
  Sparkles,
  Building2,
  Factory,
  Layers,
  ArrowRight,
  Clock,
  Coins,
  FileText,
  Users,
  Package,
  CalendarCheck
} from 'lucide-react';
import { fetchBusinessSetup, searchSuppliers } from '../services/api';
import { getTranslation } from '../services/translations';

export default function BusinessSetupCard({ 
  businessId,
  businessName, 
  businessScale = 'small', 
  userLocation, 
  userBudget, 
  userProfile,
  feasibilityResult,
  onFeedEquipmentCostToFinance,
  language = 'en'
}) {
  const t = getTranslation(language);
  const [showSetup, setShowSetup] = useState(true);
  const [setupData, setSetupData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // Setup Mode Toggle: 'starter' | 'standard'
  const [setupMode, setSetupMode] = useState('starter');
  
  // Selected machine for dedicated supplier filtering
  const [selectedMachine, setSelectedMachine] = useState(null);
  const [filteredSuppliers, setFilteredSuppliers] = useState([]);
  const [isFilteringSuppliers, setIsFilteringSuppliers] = useState(false);
  const [filterLoc, setFilterLoc] = useState(userLocation || '');
  const [filterBud, setFilterBud] = useState(userBudget || '');
  
  // Active Tab: 'requirements' | 'machinery' | 'suppliers' | 'roadmap'
  const [activeTab, setActiveTab] = useState('requirements');

  // Load Setup Plan whenever businessId or businessName changes
  useEffect(() => {
    if (!businessName && !businessId) return;
    
    const loadSetupPlan = async () => {
      setIsLoading(true);
      try {
        const data = await fetchBusinessSetup({
          business_id: businessId || 'business_default',
          business_name: businessName,
          available_investment: userBudget ? Number(userBudget) : undefined,
          user_profile: userProfile,
          feasibility_result: feasibilityResult
        });
        setSetupData(data);
        if (data.machinery && data.machinery.length > 0) {
          setSelectedMachine(data.machinery[0]);
          setFilteredSuppliers(data.suppliers || []);
        }
      } catch (err) {
        console.error('Error fetching business setup plan:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadSetupPlan();
  }, [businessId, businessName, userBudget, feasibilityResult]);

  // Handle supplier search when user clicks a specific machine
  const handleSelectMachine = async (machine) => {
    setSelectedMachine(machine);
    setIsFilteringSuppliers(true);
    try {
      const res = await searchSuppliers({
        machine_id: machine.machine_id,
        location: filterLoc || undefined,
        budget: filterBud ? Number(filterBud) : undefined
      });
      setFilteredSuppliers(res.suppliers || []);
    } catch (err) {
      console.error('Error filtering suppliers for machine:', err);
    } finally {
      setIsFilteringSuppliers(false);
    }
  };

  if (!businessName && !businessId) return null;

  const currentCost = setupMode === 'starter' ? setupData?.starter_setup : setupData?.standard_setup;
  const currentFundingGap = setupMode === 'starter' ? setupData?.funding_gap : setupData?.funding_gap_standard;
  const userInv = setupData?.user_investment || Number(userBudget) || 0;

  return (
    <div className="bg-white rounded-2xl shadow-card border border-gv-border overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-950 px-5 py-4 text-white flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-xl bg-amber-400/20 text-amber-300 border border-amber-300/30 flex items-center justify-center text-xs font-bold shadow-xs">
            <Wrench className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold font-display flex items-center space-x-1.5">
                <span>{language === 'mr' ? 'व्यवसाय सेटअप व साधन सामग्री प्लॅनर' : language === 'hi' ? 'व्यवसाय सेटअप और मशीनरी प्लानर' : 'Business Setup & Machinery Plan'}</span>
              </h3>
              {setupData?.recommended_scale && (
                <span className="text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 px-2 py-0.5 rounded-full font-bold">
                  {setupData.recommended_scale}
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-300 mt-0.5">
              {language === 'mr' ? 'व्यवसाय: ' : language === 'hi' ? 'व्यवसाय: ' : 'Target Business: '}
              <strong className="text-amber-300">{setupData?.business_name || businessName}</strong>
            </p>
          </div>
        </div>

        {/* Setup Mode Toggle: Starter vs Standard */}
        <div className="flex items-center bg-slate-800/90 p-1 rounded-xl border border-slate-700">
          <button
            onClick={() => setSetupMode('starter')}
            className={`text-xs px-3 py-1 rounded-lg font-bold transition-all ${
              setupMode === 'starter'
                ? 'bg-amber-400 text-slate-950 shadow-xs'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            {language === 'mr' ? 'स्टार्टर सेटअप' : language === 'hi' ? 'स्टार्टर सेटअप' : 'Starter Setup'}
          </button>
          <button
            onClick={() => setSetupMode('standard')}
            className={`text-xs px-3 py-1 rounded-lg font-bold transition-all ${
              setupMode === 'standard'
                ? 'bg-amber-400 text-slate-950 shadow-xs'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            {language === 'mr' ? 'प्रमाणित सेटअप' : language === 'hi' ? 'स्टैंडर्ड सेटअप' : 'Standard Setup'}
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-xs text-slate-400">Loading business setup plan...</div>
      ) : setupData ? (
        <div className="p-4 sm:p-5 space-y-4">
          
          {/* Investment & Funding Gap Summary Card */}
          <div className="bg-gradient-to-br from-slate-50 to-emerald-50/40 p-4 rounded-xl border border-slate-200 shadow-2xs">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-center sm:text-left">
              
              {/* Estimated Investment */}
              <div className="bg-white p-3 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">
                  {setupMode === 'starter' ? 'Starter Total Setup Cost' : 'Standard Growth Setup Cost'}
                </span>
                <p className="text-base font-extrabold text-slate-900 mt-0.5">
                  ₹{currentCost?.total_cost?.toLocaleString('en-IN')}
                </p>
                <div className="text-[10px] text-slate-500 mt-1 flex flex-wrap gap-x-2">
                  <span>Equip: ₹{currentCost?.equipment_cost?.toLocaleString('en-IN')}</span>
                  <span>•</span>
                  <span>Infra: ₹{currentCost?.infrastructure_cost?.toLocaleString('en-IN')}</span>
                </div>
              </div>

              {/* Your Investment */}
              <div className="bg-white p-3 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">
                  Your Available Capital
                </span>
                <p className="text-base font-extrabold text-emerald-800 mt-0.5">
                  ₹{userInv.toLocaleString('en-IN')}
                </p>
                <span className="text-[10px] text-emerald-600 font-semibold">
                  {userInv >= (currentCost?.total_cost || 0) ? '✓ 100% Self-Funded' : `${Math.round((userInv / (currentCost?.total_cost || 1)) * 100)}% Margin Contribution`}
                </span>
              </div>

              {/* Funding Gap */}
              <div className={`p-3 rounded-lg border ${currentFundingGap > 0 ? 'bg-amber-50/80 border-amber-200 text-amber-900' : 'bg-emerald-50 border-emerald-200 text-emerald-900'}`}>
                <span className="text-[10px] font-bold uppercase tracking-wider block">
                  {currentFundingGap > 0 ? 'Funding Gap to Finance' : 'Capital Surplus'}
                </span>
                <p className="text-base font-extrabold mt-0.5">
                  ₹{currentFundingGap?.toLocaleString('en-IN')}
                </p>
                <span className="text-[10px] font-medium block">
                  {currentFundingGap > 0 ? 'Eligible for PMMY / PMEGP micro-credit' : 'Ready for immediate self-launch'}
                </span>
              </div>
            </div>

            {/* Scale Rationale Notice */}
            <div className="mt-3 text-xs text-slate-600 bg-white/80 p-2.5 rounded-lg border border-slate-200 flex items-start space-x-2">
              <Sparkles className="w-4 h-4 text-teal-600 flex-shrink-0 mt-0.5" />
              <span>
                <strong>Scale Recommendation: </strong>{setupData.scale_reason}
              </span>
            </div>
          </div>

          {/* Low-Capital Mode Banner (if user has funding gap) */}
          {setupData.low_capital_advice?.is_low_capital && (
            <div className="bg-amber-50/90 rounded-xl p-3.5 border border-amber-200 text-xs text-amber-950 space-y-2">
              <div className="flex items-center space-x-1.5 font-bold text-amber-900">
                <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                <span>Low-Capital Phased Advisory (Start Lean)</span>
              </div>
              <p className="text-[11px] leading-relaxed">
                {setupData.low_capital_advice.advice}
              </p>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                <div className="bg-white/90 p-2.5 rounded-lg border border-amber-200/80 text-[11px]">
                  <strong className="text-emerald-900 block mb-1">✓ Immediate Launch Actions:</strong>
                  <ul className="list-disc pl-4 space-y-0.5 text-emerald-950">
                    {setupData.low_capital_advice.immediate_actions.map((act, i) => (
                      <li key={i}>{act}</li>
                    ))}
                  </ul>
                </div>

                <div className="bg-white/90 p-2.5 rounded-lg border border-amber-200/80 text-[11px]">
                  <strong className="text-amber-900 block mb-1">⏳ Defer Until Cashflow Positive:</strong>
                  <ul className="list-disc pl-4 space-y-0.5 text-amber-950">
                    {setupData.low_capital_advice.deferred_items.map((defItem, i) => (
                      <li key={i}>{defItem}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Tab Navigation */}
          <div className="flex items-center space-x-1 border-b border-slate-200 pb-1 text-xs overflow-x-auto">
            <button
              onClick={() => setActiveTab('requirements')}
              className={`px-3.5 py-2 font-bold rounded-lg transition-all flex items-center space-x-1.5 whitespace-nowrap ${
                activeTab === 'requirements'
                  ? 'bg-teal-800 text-white shadow-2xs'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              <Building2 className="w-3.5 h-3.5" />
              <span>What You Need ({setupData.infrastructure_requirements?.length + setupData.raw_materials?.length})</span>
            </button>

            <button
              onClick={() => setActiveTab('machinery')}
              className={`px-3.5 py-2 font-bold rounded-lg transition-all flex items-center space-x-1.5 whitespace-nowrap ${
                activeTab === 'machinery'
                  ? 'bg-teal-800 text-white shadow-2xs'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              <Factory className="w-3.5 h-3.5" />
              <span>Required Machinery ({setupData.machinery?.length})</span>
            </button>

            <button
              onClick={() => setActiveTab('suppliers')}
              className={`px-3.5 py-2 font-bold rounded-lg transition-all flex items-center space-x-1.5 whitespace-nowrap ${
                activeTab === 'suppliers'
                  ? 'bg-teal-800 text-white shadow-2xs'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              <span>Ranked Suppliers ({filteredSuppliers?.length})</span>
            </button>

            <button
              onClick={() => setActiveTab('roadmap')}
              className={`px-3.5 py-2 font-bold rounded-lg transition-all flex items-center space-x-1.5 whitespace-nowrap ${
                activeTab === 'roadmap'
                  ? 'bg-teal-800 text-white shadow-2xs'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              <CalendarCheck className="w-3.5 h-3.5" />
              <span>Setup Roadmap (3 Phases)</span>
            </button>
          </div>

          {/* TAB 1: WHAT YOU NEED (Infrastructure, Raw Materials, Labour, Compliance) */}
          {activeTab === 'requirements' && (
            <div className="space-y-3.5">
              {/* Infrastructure */}
              <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
                <h4 className="text-xs font-bold text-slate-800 flex items-center space-x-1.5 mb-2.5">
                  <Building2 className="w-4 h-4 text-teal-700" />
                  <span>Infrastructure & Space Prerequisites</span>
                </h4>
                <div className="space-y-2">
                  {setupData.infrastructure_requirements?.map((req, idx) => (
                    <div key={idx} className="flex items-start justify-between bg-white p-2.5 rounded-lg border border-slate-200/80 text-xs">
                      <div>
                        <div className="flex items-center space-x-2 font-bold text-slate-800">
                          <span>{req.item}</span>
                          <span className={`text-[9px] px-1.5 py-0.2 rounded font-semibold ${
                            req.status.includes('Gap') ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
                          }`}>
                            {req.status}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 mt-0.5">{req.detail}</p>
                      </div>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full flex-shrink-0 ${
                        req.priority === 'Essential' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-slate-100 text-slate-600'
                      }`}>
                        {req.priority}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Raw Materials & Labour in 2 cols */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                {/* Raw Materials */}
                <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
                  <h4 className="text-xs font-bold text-slate-800 flex items-center space-x-1.5 mb-2">
                    <Package className="w-4 h-4 text-blue-700" />
                    <span>Raw Materials & Consumables</span>
                  </h4>
                  <div className="space-y-2">
                    {setupData.raw_materials?.map((mat, idx) => (
                      <div key={idx} className="bg-white p-2.5 rounded-lg border border-slate-200 text-xs">
                        <div className="flex justify-between font-bold text-slate-800">
                          <span>{mat.item}</span>
                          <span className="text-teal-800 font-extrabold text-[11px]">~₹{mat.estimated_monthly_cost?.toLocaleString('en-IN')}/mo</span>
                        </div>
                        <p className="text-[10px] text-slate-500 mt-0.5">Source: {mat.source}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Labour & Compliance */}
                <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-3">
                  <div>
                    <h4 className="text-xs font-bold text-slate-800 flex items-center space-x-1.5 mb-2">
                      <Users className="w-4 h-4 text-purple-700" />
                      <span>Labour Requirements</span>
                    </h4>
                    <div className="space-y-1.5">
                      {setupData.labour_requirements?.map((lab, idx) => (
                        <div key={idx} className="bg-white p-2 rounded-lg border border-slate-200 text-xs flex justify-between">
                          <span className="font-semibold text-slate-800">{lab.role} ({lab.count})</span>
                          <span className="text-[10px] text-slate-500">{lab.skill_level}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-xs font-bold text-slate-800 flex items-center space-x-1.5 mb-1.5">
                      <FileText className="w-3.5 h-3.5 text-slate-600" />
                      <span>Compliance & Licenses</span>
                    </h4>
                    <ul className="space-y-1 pl-4 list-disc text-[11px] text-slate-600">
                      {setupData.compliance_requirements?.map((comp, idx) => (
                        <li key={idx}>{comp}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: MACHINERY (Essential vs Recommended vs Optional) */}
          {activeTab === 'machinery' && (
            <div className="space-y-3">
              <div className="flex justify-between items-center text-xs">
                <span className="font-bold text-slate-800">Catalogue Machinery for {setupData.business_name}</span>
                <span className="text-slate-500 text-[11px]">Click a machine to view verified suppliers</span>
              </div>

              <div className="space-y-2.5">
                {setupData.machinery?.map((m) => {
                  const isSelected = selectedMachine?.machine_id === m.machine_id;
                  return (
                    <div
                      key={m.machine_id}
                      onClick={() => handleSelectMachine(m)}
                      className={`p-3.5 rounded-xl border transition-all cursor-pointer select-none ${
                        isSelected
                          ? 'border-teal-600 bg-teal-50/40 shadow-xs ring-1 ring-teal-500'
                          : 'border-slate-200 hover:border-slate-300 bg-white'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="flex items-center space-x-2">
                            <h5 className="text-xs font-bold text-slate-900 font-display">
                              {m.machine_name}
                            </h5>
                            <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${
                              m.priority === 'Essential'
                                ? 'bg-red-100 text-red-800 border border-red-200'
                                : 'bg-blue-100 text-blue-800 border border-blue-200'
                            }`}>
                              {m.priority}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-600 mt-1">{m.purpose}</p>
                          <div className="mt-1.5 flex flex-wrap gap-x-3 text-[10px] text-slate-500">
                            <span>Capacity: <strong>{m.capacity}</strong></span>
                            <span>•</span>
                            <span>Power: <strong>{m.power_requirement}</strong></span>
                            <span>•</span>
                            <span>Suppliers: <strong>{m.supplier_count} available</strong></span>
                          </div>
                        </div>

                        <div className="text-right flex-shrink-0">
                          <span className="text-xs font-extrabold text-slate-900 block bg-slate-100 px-2 py-1 rounded">
                            {m.price_range}
                          </span>
                          <span className="text-[9px] text-slate-400 mt-0.5 block">Indicative</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 3: RANKED SUPPLIERS */}
          {activeTab === 'suppliers' && (
            <div className="space-y-3.5">
              {/* Filter controls */}
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-2 text-xs">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-bold text-slate-800">
                    Showing Ranked Suppliers for: <span className="text-teal-800">{selectedMachine ? selectedMachine.machine_name : 'All Equipment'}</span>
                  </span>
                  <span className="text-[11px] text-slate-500">Ranked by Proximity, Verification & Price Fit</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-12 gap-2 pt-1">
                  <div className="sm:col-span-6 relative">
                    <MapPin className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
                    <input
                      type="text"
                      placeholder="Filter by district/state (e.g. Pune, Maharashtra)"
                      value={filterLoc}
                      onChange={(e) => setFilterLoc(e.target.value)}
                      className="w-full text-xs pl-8 pr-3 py-1.5 border border-slate-200 rounded-lg bg-white focus:outline-none focus:border-teal-600"
                    />
                  </div>
                  <div className="sm:col-span-4">
                    <input
                      type="number"
                      placeholder="Budget cap (₹)"
                      value={filterBud}
                      onChange={(e) => setFilterBud(e.target.value)}
                      className="w-full text-xs px-3 py-1.5 border border-slate-200 rounded-lg bg-white focus:outline-none focus:border-teal-600"
                    />
                  </div>
                  <div className="sm:col-span-2">
                    <button
                      onClick={() => selectedMachine && handleSelectMachine(selectedMachine)}
                      className="w-full h-full py-1.5 bg-teal-800 hover:bg-teal-900 text-white font-bold rounded-lg text-xs transition"
                    >
                      Filter
                    </button>
                  </div>
                </div>
              </div>

              {/* Suppliers List */}
              {isFilteringSuppliers ? (
                <div className="p-8 text-center text-xs text-slate-400">Searching supplier directory...</div>
              ) : filteredSuppliers.length === 0 ? (
                <div className="p-6 text-center bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-500">
                  No verified supplier found in the current database for this filter. Try clearing location or budget filter.
                </div>
              ) : (
                <div className="space-y-2.5 max-h-[450px] overflow-y-auto pr-1">
                  {filteredSuppliers.map((s, idx) => (
                    <div key={idx} className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs space-y-2 text-xs">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="flex items-center space-x-2">
                            <Building2 className="w-4 h-4 text-teal-700 flex-shrink-0" />
                            <h5 className="font-bold text-slate-900 text-xs">{s.supplier_name}</h5>
                            {s.verified ? (
                              <span className="text-[9px] bg-emerald-100 text-emerald-800 font-bold px-1.5 py-0.2 rounded flex items-center">
                                <ShieldCheck className="w-3 h-3 mr-0.5 text-emerald-700" /> Verified
                              </span>
                            ) : (
                              <span className="text-[9px] bg-slate-100 text-slate-600 font-medium px-1.5 py-0.2 rounded">
                                Demo Listing
                              </span>
                            )}
                          </div>
                          <div className="flex items-center space-x-2 text-[11px] text-slate-500 mt-1">
                            <span>📍 {s.location}, {s.state}</span>
                            <span>•</span>
                            <span className="font-semibold text-emerald-800">{s.location_match_label || 'State Cluster'}</span>
                          </div>
                        </div>

                        <div className="text-right flex-shrink-0">
                          <span className="inline-block text-[11px] font-extrabold bg-emerald-100 text-emerald-900 px-2 py-0.5 rounded-full border border-emerald-300/60">
                            {s.match_score || 85}/100 Match
                          </span>
                        </div>
                      </div>

                      <div className="bg-slate-50 p-2 rounded-lg border border-slate-100 flex justify-between items-center text-[11px]">
                        <div>
                          <span className="text-slate-500">Equipment: </span>
                          <strong className="text-slate-800">{s.machine_name}</strong>
                        </div>
                        <div>
                          <span className="text-slate-500">Price: </span>
                          <strong className="text-slate-900 font-bold">{s.price_range}</strong>
                        </div>
                      </div>

                      {/* Highlights */}
                      {s.match_highlights && s.match_highlights.length > 0 && (
                        <div className="space-y-0.5 text-[11px]">
                          {s.match_highlights.map((h, hIdx) => (
                            <div key={hIdx} className={h.startsWith('✓') ? 'text-emerald-800' : 'text-amber-700 font-medium'}>
                              {h}
                            </div>
                          ))}
                        </div>
                      )}

                      <div className="pt-1.5 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
                        <span>Source: {s.source}</span>
                        {s.contact && <span>Contact: {s.contact}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 4: SETUP ROADMAP (3 Phases) */}
          {activeTab === 'roadmap' && (
            <div className="space-y-3">
              {setupData.setup_phases?.map((phase) => (
                <div key={phase.phase_number} className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2 text-xs">
                  <div className="flex items-center space-x-2">
                    <span className="w-6 h-6 rounded-full bg-teal-800 text-white font-extrabold text-[11px] flex items-center justify-center">
                      0{phase.phase_number}
                    </span>
                    <h5 className="font-bold text-slate-900 text-xs">{phase.phase_name}</h5>
                  </div>
                  <p className="text-[11px] text-teal-900 font-medium bg-teal-50/70 p-2 rounded-lg border border-teal-100">
                    Focus: {phase.focus}
                  </p>
                  <ul className="space-y-1 pl-5 list-disc text-slate-700 text-[11px]">
                    {phase.items.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}

          {/* Statutory Notice */}
          <div className="flex items-start space-x-2 bg-slate-100/80 p-2.5 rounded-lg border border-slate-200 text-[10px] text-slate-500">
            <Info className="w-3.5 h-3.5 text-slate-400 flex-shrink-0 mt-0.5" />
            <span>
              <strong>Transparency Notice: </strong>{setupData.disclaimer}
            </span>
          </div>

        </div>
      ) : null}
    </div>
  );
}
