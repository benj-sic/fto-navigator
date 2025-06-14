import { useState, useEffect } from 'react';
import axios from 'axios';
import { api } from '../config';
import { FaDownload, FaExclamationTriangle, FaCheckCircle, FaInfoCircle } from 'react-icons/fa';

const AnalysisResults = ({ analysisId, initialData, onNewAnalysis }) => {
  const [riskData, setRiskData] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchCompleteData();
  }, [analysisId]);

  const fetchCompleteData = async () => {
    try {
      const [riskResponse, reportResponse] = await Promise.all([
        axios.get(api.getRisk(analysisId)),
        axios.get(api.getReport(analysisId))
      ]);
      
      setRiskData(riskResponse.data);
      setReportData(reportResponse.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      setLoading(false);
    }
  };

  const downloadReport = () => {
    const dataStr = JSON.stringify(reportData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `fto-report-${analysisId.slice(0, 8)}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const getRiskIcon = (level) => {
    switch(level) {
      case 'HIGH':
        return <FaExclamationTriangle className="risk-icon high" />;
      case 'MEDIUM':
        return <FaInfoCircle className="risk-icon medium" />;
      default:
        return <FaCheckCircle className="risk-icon low" />;
    }
  };

  const getRiskClass = (level) => {
    return `risk-badge ${level.toLowerCase()}`;
  };

  if (loading) {
    return <div className="loading-container">Loading results...</div>;
  }

  return (
    <div className="results-container">
      <div className="results-header">
        <h2>FTO Analysis Complete</h2>
        <div className="header-actions">
          <button onClick={downloadReport} className="download-button">
            <FaDownload /> Download Report
          </button>
          <button onClick={onNewAnalysis} className="new-analysis-button">
            New Analysis
          </button>
        </div>
      </div>

      {/* Risk Summary Card */}
      <div className="risk-summary-card">
        <div className="risk-level">
          {getRiskIcon(riskData?.overall_risk_level)}
          <div>
            <h3>Overall Risk Level</h3>
            <span className={getRiskClass(riskData?.overall_risk_level)}>
              {riskData?.overall_risk_level}
            </span>
          </div>
        </div>
        <div className="risk-stats">
          <div className="stat">
            <span className="stat-value">{riskData?.total_patents_analyzed}</span>
            <span className="stat-label">Patents Analyzed</span>
          </div>
          <div className="stat">
            <span className="stat-value">{riskData?.high_risk_patents}</span>
            <span className="stat-label">High Risk Patents</span>
          </div>
          <div className="stat">
            <span className="stat-value">{(riskData?.overall_risk_score * 100).toFixed(0)}%</span>
            <span className="stat-label">Risk Score</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab ${activeTab === 'patents' ? 'active' : ''}`}
          onClick={() => setActiveTab('patents')}
        >
          Patent Details
        </button>
        <button 
          className={`tab ${activeTab === 'recommendations' ? 'active' : ''}`}
          onClick={() => setActiveTab('recommendations')}
        >
          Recommendations
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="executive-summary">
              <h3>Executive Summary</h3>
              <p>{reportData?.executive_summary}</p>
            </div>
            
            <div className="risk-factors">
              <h3>Risk Factors</h3>
              <ul>
                {riskData?.risk_factors?.map((factor, index) => (
                  <li key={index}>{factor}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'patents' && (
          <div className="patents-tab">
            <h3>Relevant Patents Found</h3>
            {riskData?.analyzed_patents?.length === 0 ? (
              <p>No relevant patents found - this is good news!</p>
            ) : (
              <div className="patent-list">
                {riskData?.analyzed_patents?.map((patent, index) => (
                  <div key={index} className="patent-card">
                    <div className="patent-header">
                      <h4>{patent.title}</h4>
                      <span className={getRiskClass(patent.risk_level)}>
                        {patent.risk_level} RISK
                      </span>
                    </div>
                    <div className="patent-details">
                      <p><strong>Patent #:</strong> {patent.patent_number}</p>
                      <p><strong>Grant Date:</strong> {patent.grant_date}</p>
                      <p><strong>Applicants:</strong> {patent.applicants.join(', ')}</p>
                      <p><strong>Relevance:</strong> {patent.relevance_explanation}</p>
                    </div>
                    <div className="risk-scores">
                      <div className="score-item">
                        <span>Keyword Match:</span>
                        <span>{(patent.risk_factors.keyword_overlap * 100).toFixed(0)}%</span>
                      </div>
                      <div className="score-item">
                        <span>Field Match:</span>
                        <span>{(patent.risk_factors.classification_match * 100).toFixed(0)}%</span>
                      </div>
                      <div className="score-item">
                        <span>Recency:</span>
                        <span>{(patent.risk_factors.recency * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'recommendations' && (
          <div className="recommendations-tab">
            <div className="immediate-actions">
              <h3>Immediate Actions</h3>
              <ul className="action-list">
                {reportData?.recommendations?.immediate_actions?.map((action, index) => (
                  <li key={index}>{action}</li>
                ))}
              </ul>
            </div>
            
            <div className="general-recommendations">
              <h3>General Recommendations</h3>
              <ul className="recommendation-list">
                {reportData?.recommendations?.general_recommendations?.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>

            <div className="disclaimer">
              <h4>Important Notice</h4>
              <p>{reportData?.disclaimer}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisResults;