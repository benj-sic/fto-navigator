import { useState } from 'react';
import axios from 'axios';
import { api } from '../config';
import { FaInfoCircle } from 'react-icons/fa';

const ResearchForm = ({ onAnalysisComplete, onLoadingStart }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    field_of_study: 'Biotechnology',
    keywords: '',
    researcher_name: ''
  });

  const [errors, setErrors] = useState({});

  const fields = [
    'Biotechnology',
    'Software',
    'Mechanical',
    'Electrical',
    'Chemical',
    'Medical'
  ];

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    
    if (formData.description.length < 50) {
      newErrors.description = 'Description must be at least 50 characters';
    }
    
    const keywordList = formData.keywords.split(',').filter(k => k.trim());
    if (keywordList.length === 0) {
      newErrors.keywords = 'At least one keyword is required';
    } else if (keywordList.length > 10) {
      newErrors.keywords = 'Maximum 10 keywords allowed';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    onLoadingStart();

    try {
      // Prepare data for API
      const keywordList = formData.keywords
        .split(',')
        .map(k => k.trim())
        .filter(k => k);

      const requestData = {
        ...formData,
        keywords: keywordList
      };

      const response = await axios.post(api.analyze, requestData);
      
      // Pass the results to parent component
      onAnalysisComplete(response.data.analysis_id, response.data);
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Analysis failed. Please try again.');
      window.location.reload();
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  return (
    <div className="form-container">
      <div className="form-header">
        <h2>Analyze Your Research</h2>
        <p>Describe your research and we'll check for potential patent conflicts</p>
      </div>

      <form onSubmit={handleSubmit} className="research-form">
        <div className="form-group">
          <label htmlFor="title">
            Research Title <span className="required">*</span>
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="e.g., Novel CRISPR-Cas9 Delivery Method"
            className={errors.title ? 'error' : ''}
          />
          {errors.title && <span className="error-message">{errors.title}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="description">
            Research Description <span className="required">*</span>
            <span className="help-text">
              <FaInfoCircle /> Minimum 50 characters
            </span>
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows="4"
            placeholder="Describe your research approach, methods, and innovations..."
            className={errors.description ? 'error' : ''}
          />
          <div className="char-count">
            {formData.description.length}/50 characters
          </div>
          {errors.description && <span className="error-message">{errors.description}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="field_of_study">
            Field of Study <span className="required">*</span>
          </label>
          <select
            id="field_of_study"
            name="field_of_study"
            value={formData.field_of_study}
            onChange={handleChange}
          >
            {fields.map(field => (
              <option key={field} value={field}>{field}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="keywords">
            Keywords <span className="required">*</span>
            <span className="help-text">
              <FaInfoCircle /> Comma-separated, max 10 keywords
            </span>
          </label>
          <input
            type="text"
            id="keywords"
            name="keywords"
            value={formData.keywords}
            onChange={handleChange}
            placeholder="e.g., CRISPR, gene editing, viral vectors, delivery"
            className={errors.keywords ? 'error' : ''}
          />
          {errors.keywords && <span className="error-message">{errors.keywords}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="researcher_name">
            Researcher Name <span className="optional">(optional)</span>
          </label>
          <input
            type="text"
            id="researcher_name"
            name="researcher_name"
            value={formData.researcher_name}
            onChange={handleChange}
            placeholder="Your name"
          />
        </div>

        <button type="submit" className="submit-button">
          Analyze Patent Landscape
        </button>
      </form>

      <div className="form-info">
        <h3>What happens next?</h3>
        <ul>
          <li>We'll search the USPTO database for relevant patents</li>
          <li>Analyze potential conflicts with your research</li>
          <li>Generate a risk assessment report</li>
          <li>Provide actionable recommendations</li>
        </ul>
      </div>
    </div>
  );
};

export default ResearchForm;