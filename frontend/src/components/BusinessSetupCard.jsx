import React, { useState, useEffect } from 'react';
import { 
  Wrench, 
  Search, 
  MapPin, 
  ShieldCheck, 
  ShieldAlert, 
  CheckCircle2, 
  ExternalLink, 
  SlidersHorizontal, 
  ChevronRight, 
  ChevronDown, 
  ChevronUp, 
  Info, 
  AlertTriangle,
  Sparkles,
  RefreshCw,
  Building2
} from 'lucide-react';
import { fetchEquipment, searchSuppliers } from '../services/api';

export default function BusinessSetupCard({ 
  businessName, 
  businessScale = 'small', 
  userLocation, 
  userBudget, 
  onFeedEquipmentCostToFinance 
}) {
  const [showSetup, setShowSetup] = useState(false);
  const [equipmentList, setEquipmentList] = useState([]);
  const [isLoadingEquipment, setIsLoadingEquipment] = useState(false);
  const [selectedMachine, setSelectedMachine] = useState(null);

  // Supplier search state
  const [suppliers, setSuppliers] = useState([]);
  const [isLoadingSuppliers, setIsLoadingSuppliers] = useState(false);
  const [searchWarning, setSearchWarning] = useState(null);
  const [budgetStatus, setBudgetStatus] = useState(null);

  // Filters & sorting
  const [filterLocation, setFilterLocation] = useState(userLocation || '');
  const [filterBudget, setFilterBudget] = useState(userBudget || '');
  const [sortBy, setSortBy] = useState('best_match'); // 'best_match' | 'lowest_price' | 'location'

  // Fetch equipment whenever businessName changes
  useEffect(() => {
    if (!businessName) return;
    const loadEquipment = async () => {
      setIsLoadingEquipment(true);
      try {
        const data = await fetchEquipment(businessName, businessScale);
        setEquipmentList(data);
        if (data.length > 0) {
          // Auto-select first essential machine
          handleFindSuppliers(data[0], filterLocation, filterBudget);
        }
      } catch (err) {
        console.error('Error fetching equipment:', err);
      } finally {
        setIsLoadingEquipment(false);
      }
    };

    if (showSetup) {
      loadEquipment();
    }
  }, [businessName, businessScale, showSetup]);

  // Handle finding suppliers for a chosen machine
  const handleFindSuppliers = async (machine, loc = filterLocation, bud = filterBudget) => {
    setSelectedMachine(machine);
    setIsLoadingSuppliers(true);
    setSearchWarning(null);
    try {
      const budgetNum = bud ? Number(bud) : null;
      const res = await searchSuppliers({
        machine_id: machine.machine_id,
        location: loc || undefined,
        budget: budgetNum || undefined
      });
      setSuppliers(res.suppliers || []);
      setSearchWarning(res.warning);
      setBudgetStatus(res.budget_status);
    } catch (err) {
      console.error('Error searching suppliers:', err);
    } finally {
      setIsLoadingSuppliers(false);
    }
  };

  // Sort suppliers deterministically
  const sortedSuppliers = [...suppliers].sort((a, b) => {
    if (sortBy === 'lowest_price') {
      return (a.estimated_price_min || 0) - (b.estimated_price_min || 0);
    }
    if (sortBy === 'location') {
      // Prioritize local match
      const getLocWeight = (s) => (s.location_match_label?.includes('Same') ? 3 : s.location_match_label?.includes('State') ? 2 : 1);
      return getLocWeight(b) - getLocWeight(a);
    }
    return (b.match_score || 0) - (a.match_score || 0);
  });

  // Calculate total essential equipment cost
  const totalEssentialMin = equipmentList
    .filter((m) => m.priority === 'Essential')
    .reduce((sum, m) => sum + (m.estimated_price_min || 0), 0);
  const totalEssentialMax = equipmentList
    .filter((m) => m.priority === 'Essential')
    .reduce((sum, m) => sum + (m.estimated_price_max || 0), 0);

  if (!businessName) return null;

  // Prompter Banner when user hasn't expanded setup yet
  if (!showSetup) {
    return (
      <div className="bg-gradient-to-r from-amber-50 via-emerald-50 to-white rounded-2xl p-5 shadow-card border border-amber-200/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500 text-white flex items-center justify-center font-bold shadow-xs flex-shrink-0">
            <Wrench className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-900 font-display flex items-center space-x-1.5">
              <span>Business Setup & Machinery Planner</span>
              <span className="text-[10px] bg-amber-100 text-amber-800 font-semibold px-2 py-0.5 rounded-full">
                New Module
              </span>
            </h4>
            <p className="text-xs text-slate-600 mt-0.5">
              Would you like to see the machines and equipment required to start <strong>{businessName}</strong>?
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <button
            onClick={() => setShowSetup(true)}
            className="flex-1 sm:flex-none px-4 py-2 bg-gv-primary hover:bg-gv-secondary text-white text-xs font-bold rounded-xl shadow-xs transition flex items-center justify-center space-x-1"
          >
            <span>Yes, Show Equipment</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-card border border-gv-border overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-950 px-5 py-4 text-white flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-xl bg-amber-400/20 text-amber-300 border border-amber-300/30 flex items-center justify-center text-xs font-bold shadow-xs">
            <Wrench className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold font-display flex items-center space-x-2">
              <span>🏭 Business Setup & Machinery Planner</span>
              <span className="text-[10px] bg-amber-400 text-slate-950 font-extrabold px-2 py-0.5 rounded">
                Machinery Search & Ranking
              </span>
            </h3>
            <p className="text-[11px] text-slate-300">
              Required machinery, indicative capital outlays & ranked potential suppliers
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowSetup(false)}
          className="text-xs text-slate-400 hover:text-white px-2.5 py-1 rounded-lg border border-slate-700 bg-slate-800/60"
        >
          Hide Setup
        </button>
      </div>

      {/* Cost Summary & Financial Engine Feedback Bar */}
      {totalEssentialMin > 0 && (
        <div className="bg-emerald-50/70 border-b border-emerald-100 px-5 py-3 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div>
            <span className="text-slate-600 font-medium">Estimated Essential Machinery Investment: </span>
            <strong className="text-emerald-900 font-bold">
              ₹{totalEssentialMin.toLocaleString('en-IN')} – ₹{totalEssentialMax.toLocaleString('en-IN')}
            </strong>
            <span className="text-[11px] text-slate-500 ml-1.5">(Indicative bounds)</span>
          </div>

          {onFeedEquipmentCostToFinance && (
            <button
              onClick={() => onFeedEquipmentCostToFinance(totalEssentialMin)}
              className="text-[11px] bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-3 py-1.5 rounded-lg shadow-2xs transition flex items-center space-x-1"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span>Use Equipment Cost in Financial Plan</span>
            </button>
          )}
        </div>
      )}

      {/* Main Content Layout: Left = Required Machines, Right = Suppliers */}
      <div className="p-4 sm:p-5 grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Left Column: Required Equipment List (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Required Machinery ({equipmentList.length})
            </h4>
            <span className="text-[11px] text-slate-500">
              {businessName}
            </span>
          </div>

          {isLoadingEquipment ? (
            <div className="p-6 text-center text-xs text-slate-400">Loading equipment requirements...</div>
          ) : equipmentList.length === 0 ? (
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-500">
              Standard commercial tools required. Contact DIC for specialized lists.
            </div>
          ) : (
            <div className="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
              {equipmentList.map((m) => {
                const isSelected = selectedMachine?.machine_id === m.machine_id;
                return (
                  <div
                    key={m.machine_id}
                    onClick={() => handleFindSuppliers(m)}
                    className={`p-3.5 rounded-xl border transition-all cursor-pointer select-none ${
                      isSelected
                        ? 'border-amber-400 bg-amber-50/40 shadow-xs ring-1 ring-amber-300'
                        : 'border-slate-200 hover:border-slate-300 bg-white'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h5 className="text-xs font-bold text-slate-900 leading-snug">
                          {m.machine_name}
                        </h5>
                        <p className="text-[11px] text-slate-500 mt-1 line-clamp-2">
                          {m.purpose}
                        </p>
                      </div>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full flex-shrink-0 ${
                          m.priority === 'Essential'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {m.priority}
                      </span>
                    </div>

                    <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
                      <div>
                        <span className="text-slate-400">Indicative: </span>
                        <strong className="text-slate-800">
                          ₹{m.estimated_price_min?.toLocaleString('en-IN')} – ₹{m.estimated_price_max?.toLocaleString('en-IN')}
                        </strong>
                      </div>
                      <span className="text-gv-primary font-bold hover:underline flex items-center">
                        Find Suppliers <ChevronRight className="w-3 h-3 ml-0.5" />
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Column: Suppliers Search & Ranking (7 cols) */}
        <div className="lg:col-span-7 bg-slate-50/70 p-4 rounded-xl border border-slate-200 space-y-3.5">
          {selectedMachine ? (
            <>
              {/* Header & Filter Bar */}
              <div className="space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <h4 className="text-xs font-bold text-slate-900">
                      Potential Suppliers for: <span className="text-amber-800">{selectedMachine.machine_name}</span>
                    </h4>
                    <p className="text-[11px] text-slate-500">
                      Capacity: {selectedMachine.capacity} | Indicative Cost: ₹{selectedMachine.estimated_price_min?.toLocaleString('en-IN')} – ₹{selectedMachine.estimated_price_max?.toLocaleString('en-IN')}
                    </p>
                  </div>

                  {/* Sort dropdown */}
                  <div className="flex items-center space-x-1.5 text-xs">
                    <span className="text-slate-400 text-[11px]">Sort:</span>
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      className="text-xs py-1 px-2 border border-slate-200 rounded-lg bg-white font-medium text-slate-700"
                    >
                      <option value="best_match">Best Match Score</option>
                      <option value="lowest_price">Lowest Base Price</option>
                      <option value="location">Nearest / Location</option>
                    </select>
                  </div>
                </div>

                {/* Search Inputs (Location & Budget) */}
                <div className="grid grid-cols-1 sm:grid-cols-12 gap-2 pt-1">
                  <div className="sm:col-span-6 relative">
                    <MapPin className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
                    <input
                      type="text"
                      placeholder="Filter location (e.g. Pune, Maharashtra)"
                      value={filterLocation}
                      onChange={(e) => setFilterLocation(e.target.value)}
                      className="w-full text-xs pl-8 pr-3 py-1.5 border border-slate-200 rounded-lg bg-white placeholder:text-slate-400 focus:outline-none focus:border-gv-primary"
                    />
                  </div>

                  <div className="sm:col-span-4 relative">
                    <input
                      type="number"
                      placeholder="Budget (e.g. 50000)"
                      value={filterBudget}
                      onChange={(e) => setFilterBudget(e.target.value)}
                      className="w-full text-xs px-3 py-1.5 border border-slate-200 rounded-lg bg-white placeholder:text-slate-400 focus:outline-none focus:border-gv-primary"
                    />
                  </div>

                  <div className="sm:col-span-2">
                    <button
                      onClick={() => handleFindSuppliers(selectedMachine, filterLocation, filterBudget)}
                      className="w-full h-full py-1.5 bg-slate-800 hover:bg-slate-900 text-white text-xs font-bold rounded-lg transition"
                    >
                      Filter
                    </button>
                  </div>
                </div>
              </div>

              {/* Warning / Budget Status Notice */}
              {searchWarning && (
                <div className="p-2.5 bg-amber-50 rounded-lg border border-amber-200 text-xs text-amber-800 flex items-start space-x-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                  <span>{searchWarning}</span>
                </div>
              )}

              {/* Suppliers List */}
              {isLoadingSuppliers ? (
                <div className="p-8 text-center text-xs text-slate-400">Searching and ranking suppliers...</div>
              ) : sortedSuppliers.length === 0 ? (
                <div className="p-5 text-center bg-white rounded-xl border border-slate-200 text-xs text-slate-500">
                  No suppliers found matching the criteria. Try clearing the location/budget filters.
                </div>
              ) : (
                <div className="space-y-2.5 max-h-[380px] overflow-y-auto pr-1">
                  {sortedSuppliers.map((s) => (
                    <div
                      key={s.supplier_id}
                      className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs space-y-2"
                    >
                      {/* Top Bar */}
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <h5 className="text-xs font-bold text-slate-900 font-display flex items-center space-x-1.5">
                            <Building2 className="w-3.5 h-3.5 text-slate-400" />
                            <span>{s.supplier_name}</span>
                          </h5>
                          <div className="flex items-center space-x-2 text-[11px] text-slate-500 mt-0.5">
                            <span className="flex items-center">
                              <MapPin className="w-3 h-3 text-slate-400 mr-0.5" />
                              {s.location}, {s.state}
                            </span>
                            <span className="text-slate-300">•</span>
                            <span className="font-semibold text-emerald-800">{s.location_match_label}</span>
                          </div>
                        </div>

                        {/* Match Score Badge */}
                        <div className="text-right">
                          <span className="inline-block text-[11px] font-extrabold bg-emerald-100 text-emerald-900 px-2.5 py-0.5 rounded-full border border-emerald-300/60">
                            {s.match_score}/100 Match
                          </span>
                        </div>
                      </div>

                      {/* Pricing & Capacity Row */}
                      <div className="bg-slate-50 p-2 rounded-lg border border-slate-100 flex flex-wrap items-center justify-between text-xs">
                        <div>
                          <span className="text-slate-500 text-[11px]">Indicative Price: </span>
                          <strong className="text-slate-800 font-bold">{s.price_range}</strong>
                        </div>
                        <div>
                          <span className="text-slate-500 text-[11px]">Rated Capacity: </span>
                          <strong className="text-slate-700">{s.capacity}</strong>
                        </div>
                      </div>

                      {/* Highlights */}
                      <div className="space-y-0.5 text-[11px]">
                        {s.match_highlights?.map((h, hIdx) => (
                          <div key={hIdx} className={h.startsWith('✓') ? 'text-emerald-800' : 'text-amber-700 font-medium'}>
                            {h}
                          </div>
                        ))}
                      </div>

                      {/* Footer & Source Link */}
                      <div className="pt-1.5 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
                        <span className="flex items-center space-x-1">
                          {s.verified ? (
                            <span className="text-emerald-700 font-bold flex items-center">
                              <ShieldCheck className="w-3 h-3 mr-0.5 text-emerald-600" /> Verified Supplier
                            </span>
                          ) : (
                            <span className="text-amber-700 font-medium flex items-center">
                              <ShieldAlert className="w-3 h-3 mr-0.5 text-amber-600" /> Demo Listing (Verification Required)
                            </span>
                          )}
                          <span className="text-slate-300">|</span>
                          <span>Source: {s.source}</span>
                        </span>

                        {s.website && (
                          <a
                            href={s.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gv-primary hover:underline font-bold flex items-center"
                          >
                            <span>View Profile</span>
                            <ExternalLink className="w-2.5 h-2.5 ml-0.5" />
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="p-8 text-center text-xs text-slate-400">
              Select a machine on the left to view ranked suppliers.
            </div>
          )}

          {/* Statutory Trust & Verification Disclaimer */}
          <div className="p-2.5 bg-slate-100 rounded-lg text-[10px] text-slate-500 flex items-start space-x-1.5 border border-slate-200">
            <Info className="w-3.5 h-3.5 text-slate-400 flex-shrink-0 mt-0.5" />
            <span>
              <strong>Consumer Notice:</strong> GramVantage AI is an advisory and search platform, not a machinery dealer or marketplace. Prices are indicative and must be confirmed directly with suppliers before purchase.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
