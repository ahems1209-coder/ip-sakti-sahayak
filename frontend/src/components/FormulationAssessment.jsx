import React, { useState } from 'react';
import { FileCheck, AlertTriangle, CheckCircle2, ShieldAlert, ArrowRight, Info, RefreshCw, Lock } from 'lucide-react';
import { assessFormulation } from '../services/api';

export default function FormulationAssessment({ confidentialMode, onOpenCitationModal }) {
  const [productName, setProductName] = useState('Ashwagandha & Brahmi Synergy Extract');
  const [productType, setProductType] = useState('Polyherbal Extract');
  const [ingredientsText, setIngredientsText] = useState('Ashwagandha (Withania somnifera), Brahmi (Bacopa monnieri)');
  const [purpose, setPurpose] = useState('Cognitive enhancement, stress reduction, and neuroprotection');
  const [isClassical, setIsClassical] = useState('no'); // 'yes', 'no', 'notsure'
  const [classicalRef, setClassicalRef] = useState('Ayurvedic Pharmacopoeia of India (API)');
  const [applicantType, setApplicantType] = useState('Indian entity');
  const [targetJurisdiction, setTargetJurisdiction] = useState('India');
  const [useType, setUseType] = useState('Commercial');

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAssess = async (e) => {
    e.preventDefault();
    if (!productName.trim() || !ingredientsText.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const ingredientsList = ingredientsText.split(',').map((s) => s.trim()).filter(Boolean);
      const payload = {
        product_name: productName,
        ingredients: ingredientsList,
        purpose: purpose,
        is_classical_formulation: isClassical === 'yes',
        classical_reference: isClassical === 'yes' ? classicalRef : null,
        target_jurisdiction: targetJurisdiction,
        confidential_mode: confidentialMode
      };
      const data = await assessFormulation(payload);
      setResult(data);
    } catch (err) {
      console.error('Formulation assessment error:', err);
      setError(err.message || 'Failed to complete formulation assessment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-amber-50 rounded-lg border border-amber-200 text-amber-700">
            <FileCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gov-navy">Polyherbal Formulation IP & Regulatory Assessment</h1>
            <p className="text-sm text-slate-600">
              Evaluate patentability constraints under Section 3(p)/3(e), Drugs & Cosmetics licensing, and NBA Access & Benefit Sharing (ABS) rules.
            </p>
          </div>
        </div>

        {/* Assessment Form */}
        <form onSubmit={handleAssess} className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Product / Formulation Name *
            </label>
            <input
              type="text"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-gov-accent focus:border-gov-accent"
              placeholder="e.g. MemoryEnhance Botanical Extract"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Product Type
            </label>
            <select
              value={productType}
              onChange={(e) => setProductType(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white font-medium text-slate-700"
            >
              <option value="Polyherbal Extract">Polyherbal Extract / Hydro-alcoholic</option>
              <option value="Classical Churna / Kwath">Classical Churna / Kwath / Vati</option>
              <option value="Proprietary ASU Medicine">Proprietary ASU Medicine</option>
              <option value="Nutraceutical / Dietary Supplement">Nutraceutical / Dietary Supplement</option>
              <option value="Cosmeceutical">Cosmeceutical / Topical Herbal</option>
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Botanical Ingredients & Bio-Resources (Comma Separated) *
            </label>
            <input
              type="text"
              value={ingredientsText}
              onChange={(e) => setIngredientsText(e.target.value)}
              required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-gov-accent focus:border-gov-accent"
              placeholder="e.g. Ashwagandha (Withania somnifera), Brahmi (Bacopa monnieri), Curcumin"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Purpose / Intended Therapeutic or Health Use
            </label>
            <input
              type="text"
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-gov-accent focus:border-gov-accent"
              placeholder="e.g. Adaptogenic relief, memory retention support"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Classical Formulation Status
            </label>
            <select
              value={isClassical}
              onChange={(e) => setIsClassical(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white font-medium text-slate-700"
            >
              <option value="no">No - Novel / Proprietary Combination</option>
              <option value="yes">Yes - Classical Ayurvedic Recipe</option>
              <option value="notsure">Not Sure / Partial Classical Origin</option>
            </select>
          </div>

          {isClassical === 'yes' && (
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Classical Text Reference
              </label>
              <input
                type="text"
                value={classicalRef}
                onChange={(e) => setClassicalRef(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                placeholder="e.g. Charaka Samhita, Ayurvedic Pharmacopoeia"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Applicant Category
            </label>
            <select
              value={applicantType}
              onChange={(e) => setApplicantType(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white font-medium text-slate-700"
            >
              <option value="Indian entity">Indian Entity / Citizen / MSME</option>
              <option value="Foreign entity">Foreign Entity / NRIs / Non-Indian Org</option>
              <option value="Other / Joint Venture">Other / Joint Venture</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Target Jurisdiction
            </label>
            <select
              value={targetJurisdiction}
              onChange={(e) => setTargetJurisdiction(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white font-medium text-slate-700"
            >
              <option value="India">India</option>
              <option value="International">International / PCT</option>
            </select>
          </div>

          <div className="md:col-span-2 pt-2 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="bg-gov-accent hover:bg-amber-600 disabled:opacity-50 text-white px-6 py-2.5 rounded-lg font-bold text-sm shadow transition-all flex items-center gap-2"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Running Regulatory Assessment...
                </>
              ) : (
                <>
                  <FileCheck className="w-4 h-4" />
                  Submit Formulation Assessment
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Assessment Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Assessment Result Output */}
      {result && (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden divide-y divide-slate-200">
          <div className="p-6 bg-slate-50 flex justify-between items-center">
            <div>
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Assessment Target</span>
              <h2 className="text-xl font-bold text-gov-navy">{result.formulation_name}</h2>
            </div>

            <div className="flex items-center gap-2">
              <span className="gov-badge-verified">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Evidence Status: {result.confidence === 'evidence_supported' ? 'Verified Legal Framework' : 'Insufficient Evidence'}
              </span>
            </div>
          </div>

          {/* Risk Matrix Section */}
          <div className="p-6 space-y-4">
            <h3 className="text-sm font-bold text-gov-navy uppercase tracking-wider flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-gov-blue" />
              IP & Regulatory Risk Breakdown
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Patentability Risk */}
              <div className="p-4 border border-amber-200 bg-amber-50/50 rounded-lg space-y-1">
                <div className="text-xs font-bold text-amber-900 uppercase">Potentially Relevant IP Consideration</div>
                <p className="text-sm text-slate-800">{result.risk_matrix.patentability}</p>
                <div className="text-xs text-amber-800 font-mono pt-1">Statutory Authority: Patents Act 1970 § 3(p) / 3(e)</div>
              </div>

              {/* Regulatory Compliance */}
              <div className="p-4 border border-blue-200 bg-blue-50/50 rounded-lg space-y-1">
                <div className="text-xs font-bold text-blue-900 uppercase">Regulatory Licensing Requirement</div>
                <p className="text-sm text-slate-800">{result.risk_matrix.regulatory_compliance}</p>
                <div className="text-xs text-blue-800 font-mono pt-1">Authority: CDSCO & State Licensing Authority</div>
              </div>

              {/* Traditional Knowledge */}
              <div className="p-4 border border-purple-200 bg-purple-50/50 rounded-lg space-y-1">
                <div className="text-xs font-bold text-purple-900 uppercase">Traditional Knowledge & Prior Art</div>
                <p className="text-sm text-slate-800">{result.risk_matrix.traditional_knowledge}</p>
                <div className="text-xs text-purple-800 font-mono pt-1">Authority: TKDL & AYUSH Pharmacopoeia</div>
              </div>

              {/* Biological Diversity ABS */}
              <div className="p-4 border border-emerald-200 bg-emerald-50/50 rounded-lg space-y-1">
                <div className="text-xs font-bold text-emerald-900 uppercase">National Biodiversity Authority (ABS)</div>
                <p className="text-sm text-slate-800">{result.risk_matrix.biodiversity_abs}</p>
                <div className="text-xs text-emerald-800 font-mono pt-1">Authority: Biological Diversity Act 2002 § 3 / 6</div>
              </div>
            </div>
          </div>

          {/* Missing Information / Controlled Warnings */}
          {result.missing_information && result.missing_information.length > 0 && (
            <div className="p-6 bg-slate-50 space-y-3">
              <h3 className="text-sm font-bold text-gov-navy uppercase tracking-wider flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                Missing Information Warnings (Crucial for Final IP Clearance)
              </h3>
              <ul className="space-y-1">
                {result.missing_information.map((info, idx) => (
                  <li key={idx} className="text-xs text-slate-700 flex items-start gap-2">
                    <span className="text-amber-500 font-bold">•</span>
                    <span>{info}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Evidence-Backed Next Steps */}
          {result.evidence_backed_next_steps && result.evidence_backed_next_steps.length > 0 && (
            <div className="p-6 space-y-3">
              <h3 className="text-sm font-bold text-gov-navy uppercase tracking-wider flex items-center gap-2">
                <ArrowRight className="w-4 h-4 text-gov-blue" />
                Evidence-Backed Actionable Next Steps
              </h3>
              <div className="space-y-2">
                {result.evidence_backed_next_steps.map((step, idx) => (
                  <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-800 flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-blue-900 text-white flex items-center justify-center text-xs font-bold flex-shrink-0">
                      {idx + 1}
                    </span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
