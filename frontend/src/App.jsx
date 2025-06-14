import { useState } from 'react';
import './App.css';
import ResearchForm from './components/ResearchForm';
import AnalysisResults from './components/AnalysisResults';
import { FaFlask } from 'react-icons/fa';

function App() {
  const [currentView, setCurrentView] = useState('form'); // 'form', 'loading', 'results'
  const [analysisId, setAnalysisId] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);

  const handleAnalysisComplete = (id, data) => {
    setAnalysisId(id);
    setAnalysisData(data);
    setCurrentView('results');
  };

  const handleNewAnalysis = () => {
    setCurrentView('form');
    setAnalysisId(null);
    setAnalysisData(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <FaFlask className="logo" />
          <h1>FTO Navigator</h1>
          <p>Patent Freedom-to-Operate Analysis for Researchers</p>
        </div>
      </header>

      <main className="app-main">
        {currentView === 'form' && (
          <ResearchForm 
            onAnalysisComplete={handleAnalysisComplete}
            onLoadingStart={() => setCurrentView('loading')}
          />
        )}
        
        {currentView === 'loading' && (
          <div className="loading-container">
            <div className="loader"></div>
            <p>Searching patents and analyzing risks...</p>
            <p className="loading-note">This may take up to 30 seconds</p>
          </div>
        )}
        
        {currentView === 'results' && (
          <AnalysisResults 
            analysisId={analysisId}
            initialData={analysisData}
            onNewAnalysis={handleNewAnalysis}
          />
        )}
      </main>
    </div>
  );
}

export default App;