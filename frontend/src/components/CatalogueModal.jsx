import React, { useState, useEffect } from 'react';
import {
  X,
  Database,
  Upload,
  RefreshCw,
  Search,
  CheckCircle2,
  Filter,
  Sparkles,
  Layers,
  ArrowRight,
  TrendingUp,
  FileSpreadsheet,
  AlertCircle
} from 'lucide-react';
import {
  fetchTrainStatus,
  fetchBusinesses,
  triggerModelTraining,
  uploadAndTrainFile
} from '../services/api';

export default function CatalogueModal({ isOpen, onClose, onSelectBusinessForAnalysis }) {
  const [trainStatus, setTrainStatus] = useState(null);
  const [businesses, setBusinesses] = useState([]);
  const [selectedDomain, setSelectedDomain] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [isTraining, setIsTraining] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    try {
      const [statusRes, bizRes] = await Promise.all([
        fetchTrainStatus(),
        fetchBusinesses()
      ]);
      setTrainStatus(statusRes);
      setBusinesses(bizRes);
    } catch (err) {
      console.error('Failed to load catalogue data:', err);
    }
  };

  const handleRetrain = async () => {
    setIsTraining(true);
    setUploadStatus(null);
    try {
      const res = await triggerModelTraining();
      setUploadStatus({ type: 'success', message: res.message });
      await loadData();
    } catch (err) {
      setUploadStatus({ type: 'error', message: err.message });
    } finally {
      setIsTraining(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setIsTraining(true);
    setUploadStatus(null);

    try {
      const res = await uploadAndTrainFile(file);
      setUploadStatus({ type: 'success', message: res.message });
      await loadData();
    } catch (err) {
      setUploadStatus({ type: 'error', message: err.message });
    } finally {
      setIsTraining(false);
    }
  };

  if (!isOpen) return null;

  // Extract unique domains
  const uniqueDomains = ['All', ...new Set(businesses.map((b) => b.category).filter(Boolean))];

  // Filter businesses
  const filtered = businesses.filter((b) => {
    const matchesDomain = selectedDomain === 'All' || b.category === selectedDomain;
    const matchesSearch =
      !searchQuery ||
      b.business_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      b.category?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      b.required_skills?.some((s) => s.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesDomain && matchesSearch;
  });

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[92vh] flex flex-col border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="bg-gradient-to-r from-gv-dark via-gv-primary to-gv-secondary text-white px-6 py-4 flex items-center justify-between border-b border-gv-secondary">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-amber-400/20 flex items-center justify-center text-amber-300 border border-amber-300/40">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base font-bold font-display">Business Catalogue & Model Training</h2>
                <span className="text-[10px] bg-emerald-400/20 text-emerald-300 font-semibold px-2 py-0.5 rounded-full border border-emerald-400/30">
                  {businesses.length} Verified Ideas Ingested
                </span>
              </div>
              <p className="text-xs text-slate-300">
                Imported from catalogue with 20 industrial domains for hyper-local matchmaking
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-300 hover:text-white hover:bg-white/10 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Training Status & Import Banner */}
        <div className="bg-slate-50 border-b border-slate-200 px-6 py-3.5 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center space-x-1.5 text-slate-700 font-semibold">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Model Status: <strong>Trained & Active</strong></span>
            </div>
            <div className="text-slate-500">
              Domains: <strong>{trainStatus?.domains_count || 20}</strong>
            </div>
            <div className="text-slate-500">
              Investment Spectrum: <strong>₹50k – ₹25 Lakh</strong>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <label className="flex items-center space-x-1.5 px-3 py-1.5 bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 rounded-lg cursor-pointer transition font-medium">
              <Upload className="w-3.5 h-3.5 text-amber-600" />
              <span>Upload Custom CSV/Excel</span>
              <input
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={handleFileUpload}
                className="hidden"
                disabled={isTraining}
              />
            </label>

            <button
              onClick={handleRetrain}
              disabled={isTraining}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-gv-primary hover:bg-gv-secondary text-white rounded-lg shadow font-medium transition disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isTraining ? 'animate-spin' : ''}`} />
              <span>{isTraining ? 'Training Model...' : 'Re-Train on Catalogue'}</span>
            </button>
          </div>
        </div>

        {/* Upload feedback alert */}
        {uploadStatus && (
          <div
            className={`px-6 py-2.5 text-xs flex items-center space-x-2 ${
              uploadStatus.type === 'success'
                ? 'bg-emerald-50 text-emerald-900 border-b border-emerald-200'
                : 'bg-rose-50 text-rose-900 border-b border-rose-200'
            }`}
          >
            {uploadStatus.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
            )}
            <span>{uploadStatus.message}</span>
          </div>
        )}

        {/* Filter & Search Bar */}
        <div className="p-4 sm:px-6 bg-white border-b border-slate-200 flex flex-col sm:flex-row gap-3 items-center justify-between">
          {/* Search */}
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by name, skill, domain..."
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-lg outline-none focus:border-gv-primary"
            />
          </div>

          {/* Domain Pills */}
          <div className="flex items-center space-x-1 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0 text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-400 mr-1 flex-shrink-0" />
            {uniqueDomains.slice(0, 7).map((dom) => (
              <button
                key={dom}
                onClick={() => setSelectedDomain(dom)}
                className={`px-2.5 py-1 rounded-full whitespace-nowrap text-xs transition ${
                  selectedDomain === dom
                    ? 'bg-gv-primary text-white font-semibold'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {dom}
              </button>
            ))}
          </div>
        </div>

        {/* Businesses Grid */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 bg-slate-50/50">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {filtered.map((b) => (
              <div
                key={b.id}
                className="bg-white rounded-xl p-3.5 border border-slate-200 hover:border-gv-primary/60 hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
                      {b.catalogue_id || b.id.slice(0, 4).toUpperCase()}
                    </span>
                    <span className="text-[10px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded-full">
                      {b.category}
                    </span>
                  </div>

                  <h4 className="font-bold text-slate-900 text-xs sm:text-sm font-display leading-tight mb-1">
                    {b.business_name}
                  </h4>

                  <div className="text-[11px] text-slate-600 mb-2">
                    Min Fund: <strong className="text-gv-primary">₹{Number(b.minimum_investment).toLocaleString('en-IN')}</strong>
                  </div>

                  {/* Skills */}
                  <div className="flex flex-wrap gap-1 mb-2">
                    {b.required_skills?.map((sk, i) => (
                      <span
                        key={i}
                        className="bg-slate-50 border border-slate-200 text-slate-600 px-1.5 py-0.5 rounded text-[9px]"
                      >
                        {sk}
                      </span>
                    ))}
                  </div>

                  {/* Resources */}
                  <div className="text-[10px] text-slate-500 space-y-0.5 mb-3">
                    <p>• Space: <strong>{b.space_requirement || 'Small space'}</strong></p>
                    <p>
                      • Utilities: {b.water_needed ? 'Water ✓ ' : ''}
                      {b.electricity_needed ? 'Electricity ✓' : 'Low Power'}
                    </p>
                    <p>• Risk: <strong className="text-slate-700">{b.risk_level || 'Medium'}</strong> • Scalability: <strong>{b.scalability || 'High'}</strong></p>
                  </div>
                </div>

                <button
                  onClick={() => {
                    if (onSelectBusinessForAnalysis) {
                      onSelectBusinessForAnalysis(b);
                      onClose();
                    }
                  }}
                  className="w-full py-1.5 bg-emerald-50 hover:bg-gv-primary hover:text-white text-gv-primary border border-emerald-200 hover:border-gv-primary text-xs font-semibold rounded-lg transition flex items-center justify-center space-x-1"
                >
                  <span>Select for Advisory</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>

          {filtered.length === 0 && (
            <div className="text-center py-12 text-slate-400 text-xs">
              No businesses found matching your filter. Try searching for something else.
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-slate-100 px-6 py-3 border-t border-slate-200 flex justify-between items-center text-xs">
          <span className="text-slate-500">
            Showing {filtered.length} of {businesses.length} total catalogue items
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-900 text-white font-semibold rounded-lg"
          >
            Close Catalogue
          </button>
        </div>
      </div>
    </div>
  );
}
