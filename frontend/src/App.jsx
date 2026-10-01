import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import AIAssistant from './components/AIAssistant';
import FormulationAssessment from './components/FormulationAssessment';
import SourceExplorer from './components/SourceExplorer';
import HumanReviewCases from './components/HumanReviewCases';
import CitationModal from './components/CitationModal';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [demoMode, setDemoMode] = useState(true);
  const [confidentialMode, setConfidentialMode] = useState(false);
  const [language, setLanguage] = useState('en');

  // Initial query state passed from Dashboard demo chips
  const [assistantInitialQuery, setAssistantInitialQuery] = useState('');
  const [selectedCitation, setSelectedCitation] = useState(null);

  const handleSelectDemoQuery = (queryText) => {
    setAssistantInitialQuery(queryText);
    setActiveTab('assistant');
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans text-slate-900 antialiased selection:bg-amber-200 selection:text-amber-900">
      {/* Top Enterprise GovTech Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        demoMode={demoMode}
        setDemoMode={setDemoMode}
        confidentialMode={confidentialMode}
        setConfidentialMode={setConfidentialMode}
        language={language}
        setLanguage={setLanguage}
      />

      {/* Main Content Area */}
      <main className="flex-1">
        {activeTab === 'dashboard' && (
          <Dashboard
            setActiveTab={setActiveTab}
            onSelectDemoQuery={handleSelectDemoQuery}
          />
        )}

        {activeTab === 'assistant' && (
          <AIAssistant
            initialQuery={assistantInitialQuery}
            language={language}
            setLanguage={setLanguage}
            confidentialMode={confidentialMode}
            onOpenCitationModal={(cit) => setSelectedCitation(cit)}
          />
        )}

        {activeTab === 'assessment' && (
          <FormulationAssessment
            confidentialMode={confidentialMode}
            onOpenCitationModal={(cit) => setSelectedCitation(cit)}
          />
        )}

        {activeTab === 'explorer' && (
          <SourceExplorer />
        )}

        {activeTab === 'cases' && (
          <HumanReviewCases />
        )}
      </main>

      {/* Interactive Citation Provenance Modal */}
      {selectedCitation && (
        <CitationModal
          citation={selectedCitation}
          onClose={() => setSelectedCitation(null)}
        />
      )}

      {/* Footer Disclaimer */}
      <footer className="bg-slate-900 text-slate-400 border-t border-slate-800 py-6 px-4 text-center text-xs">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-3">
          <div>
            <span className="font-bold text-slate-200">IP-SAKTI Sahayak</span> — Evidence-Grounded IP & Regulatory Intelligence for Ayurveda
          </div>
          <div className="text-slate-500">
            Authoritative Knowledge Base & Evidence Verification Engine
          </div>
        </div>
      </footer>
    </div>
  );
}
