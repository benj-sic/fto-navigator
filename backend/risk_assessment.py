from typing import List, Dict, Any
from datetime import datetime, timedelta
import re

class RiskAssessmentService:
    """
    Analyzes patent data to assess freedom-to-operate risks
    """
    
    def __init__(self):
        # Risk thresholds
        self.HIGH_RISK_THRESHOLD = 0.7
        self.MEDIUM_RISK_THRESHOLD = 0.4
        
        # Weights for different factors
        self.KEYWORD_WEIGHT = 0.4
        self.CLASSIFICATION_WEIGHT = 0.3
        self.RECENCY_WEIGHT = 0.2
        self.APPLICANT_TYPE_WEIGHT = 0.1
    
    def assess_patents(self, research_data: Dict, patents: List[Dict]) -> Dict:
        """
        Main assessment function that analyzes all patents
        """
        if not patents:
            return self._create_low_risk_report(research_data)
        
        # Analyze each patent
        analyzed_patents = []
        for patent in patents:
            analysis = self._analyze_single_patent(research_data, patent)
            analyzed_patents.append(analysis)
        
        # Sort by risk score
        analyzed_patents.sort(key=lambda x: x['risk_score'], reverse=True)
        
        # Calculate overall risk
        overall_risk = self._calculate_overall_risk(analyzed_patents)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(overall_risk, analyzed_patents)
        
        return {
            "overall_risk_level": overall_risk['level'],
            "overall_risk_score": overall_risk['score'],
            "risk_factors": overall_risk['factors'],
            "total_patents_analyzed": len(patents),
            "high_risk_patents": len([p for p in analyzed_patents if p['risk_level'] == 'HIGH']),
            "analyzed_patents": analyzed_patents[:10],  # Top 10 most relevant
            "recommendations": recommendations,
            "assessment_date": datetime.now().isoformat()
        }
    
    def _analyze_single_patent(self, research_data: Dict, patent: Dict) -> Dict:
        """
        Analyze a single patent for FTO risk
        """
        # Extract research keywords
        research_keywords = [kw.lower() for kw in research_data.get('keywords', [])]
        research_field = research_data.get('field_of_study', '').lower()
        
        # Calculate individual risk factors
        keyword_score = self._calculate_keyword_overlap(
            research_keywords, 
            patent.get('title', '').lower()
        )
        
        classification_score = self._calculate_classification_relevance(
            research_field,
            patent.get('classifications', [])
        )
        
        recency_score = self._calculate_recency_score(
            patent.get('grant_date', '')
        )
        
        applicant_score = self._calculate_applicant_type_score(
            patent.get('applicants', [])
        )
        
        # Calculate weighted risk score
        risk_score = (
            keyword_score * self.KEYWORD_WEIGHT +
            classification_score * self.CLASSIFICATION_WEIGHT +
            recency_score * self.RECENCY_WEIGHT +
            applicant_score * self.APPLICANT_TYPE_WEIGHT
        )
        
        # Determine risk level
        if risk_score >= self.HIGH_RISK_THRESHOLD:
            risk_level = "HIGH"
        elif risk_score >= self.MEDIUM_RISK_THRESHOLD:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "patent_number": patent.get('patent_number', 'N/A'),
            "title": patent.get('title', 'No title'),
            "risk_score": round(risk_score, 3),
            "risk_level": risk_level,
            "risk_factors": {
                "keyword_overlap": round(keyword_score, 3),
                "classification_match": round(classification_score, 3),
                "recency": round(recency_score, 3),
                "applicant_type": round(applicant_score, 3)
            },
            "grant_date": patent.get('grant_date', 'N/A'),
            "applicants": patent.get('applicants', []),
            "relevance_explanation": self._generate_relevance_explanation(
                risk_level, keyword_score, classification_score
            )
        }
    
    def _calculate_keyword_overlap(self, research_keywords: List[str], patent_title: str) -> float:
        """
        Calculate how many research keywords appear in patent title
        """
        if not research_keywords or not patent_title:
            return 0.0
        
        matches = 0
        for keyword in research_keywords:
            # Use word boundaries for more accurate matching
            if re.search(r'\b' + re.escape(keyword) + r'\b', patent_title):
                matches += 1
        
        return matches / len(research_keywords)
    
    def _calculate_classification_relevance(self, research_field: str, classifications: List[str]) -> float:
        """
        Check if patent classifications match research field
        """
        # Map research fields to relevant CPC classifications
        field_mappings = {
            'biotechnology': ['C12', 'C07K', 'A61K', 'C07H'],
            'software': ['G06F', 'G06N', 'H04L', 'G06Q'],
            'mechanical': ['F16', 'B25', 'F01', 'F02'],
            'electrical': ['H01', 'H02', 'H03', 'H04'],
            'chemical': ['C07', 'C08', 'C09', 'C01'],
            'medical': ['A61', 'A62B', 'G16H']
        }
        
        relevant_codes = field_mappings.get(research_field, [])
        if not relevant_codes or not classifications:
            return 0.3  # Default medium relevance if can't determine
        
        matches = 0
        for classification in classifications[:5]:  # Check top 5
            for code in relevant_codes:
                if classification.startswith(code):
                    matches += 1
                    break
        
        return min(matches / 3.0, 1.0)  # Cap at 1.0
    
    def _calculate_recency_score(self, grant_date: str) -> float:
        """
        More recent patents pose higher risk
        """
        try:
            patent_date = datetime.strptime(grant_date, '%Y-%m-%d')
            years_old = (datetime.now() - patent_date).days / 365.25
            
            if years_old < 5:
                return 1.0  # Very recent
            elif years_old < 10:
                return 0.7
            elif years_old < 15:
                return 0.4
            else:
                return 0.2  # Older patents less risky
        except:
            return 0.5  # Default if can't parse date
    
    def _calculate_applicant_type_score(self, applicants: List[str]) -> float:
        """
        Large companies and universities pose different risks
        """
        if not applicants:
            return 0.5
        
        applicant_text = ' '.join(applicants).lower()
        
        # High risk: Large tech/pharma companies
        if any(corp in applicant_text for corp in ['inc.', 'corp.', 'company', 'llc']):
            return 0.8
        # Medium risk: Universities (may license)
        elif any(uni in applicant_text for uni in ['university', 'institute', 'college']):
            return 0.5
        # Lower risk: Individuals
        else:
            return 0.3
    
    def _calculate_overall_risk(self, analyzed_patents: List[Dict]) -> Dict:
        """
        Calculate overall FTO risk based on all patents
        """
        if not analyzed_patents:
            return {"level": "LOW", "score": 0.0, "factors": []}
        
        # Get top risk scores
        top_scores = [p['risk_score'] for p in analyzed_patents[:5]]
        
        # Overall score based on highest risks
        if analyzed_patents[0]['risk_score'] >= self.HIGH_RISK_THRESHOLD:
            overall_score = analyzed_patents[0]['risk_score']
            level = "HIGH"
        else:
            overall_score = sum(top_scores) / len(top_scores)
            if overall_score >= self.MEDIUM_RISK_THRESHOLD:
                level = "MEDIUM"
            else:
                level = "LOW"
        
        # Identify main risk factors
        factors = []
        high_risk_count = len([p for p in analyzed_patents if p['risk_level'] == 'HIGH'])
        
        if high_risk_count > 0:
            factors.append(f"{high_risk_count} high-risk patents identified")
        
        if analyzed_patents[0]['risk_factors']['keyword_overlap'] > 0.6:
            factors.append("Strong keyword overlap with existing patents")
        
        if analyzed_patents[0]['risk_factors']['recency'] > 0.8:
            factors.append("Recent patents in your research area")
        
        return {
            "level": level,
            "score": round(overall_score, 3),
            "factors": factors
        }
    
    def _generate_recommendations(self, overall_risk: Dict, analyzed_patents: List[Dict]) -> List[str]:
        """
        Generate actionable recommendations based on risk assessment
        """
        recommendations = []
        
        if overall_risk['level'] == 'HIGH':
            recommendations.extend([
                "🚨 Consult with a patent attorney before proceeding",
                "📊 Conduct a detailed patent landscape analysis",
                "🔍 Consider freedom-to-operate opinion from legal counsel",
                "💡 Explore licensing opportunities for high-risk patents"
            ])
        elif overall_risk['level'] == 'MEDIUM':
            recommendations.extend([
                "⚠️ Review high-risk patents carefully",
                "📝 Document how your research differs from existing patents",
                "🤝 Consider collaboration with patent holders",
                "🛡️ Design around existing patent claims"
            ])
        else:
            recommendations.extend([
                "✅ Low patent conflict risk identified",
                "📚 Continue monitoring new patents in your field",
                "💪 Consider filing your own patents",
                "🔄 Update this analysis periodically"
            ])
        
        # Add specific recommendations based on patterns
        if analyzed_patents and analyzed_patents[0]['risk_factors']['keyword_overlap'] > 0.7:
            recommendations.append("🎯 Refine your research keywords to differentiate from existing work")
        
        return recommendations
    
    def _generate_relevance_explanation(self, risk_level: str, keyword_score: float, class_score: float) -> str:
        """
        Explain why a patent is relevant
        """
        if risk_level == "HIGH":
            if keyword_score > 0.7:
                return "Strong keyword match indicates direct overlap with your research"
            else:
                return "Patent classifications suggest work in the same technical field"
        elif risk_level == "MEDIUM":
            return "Moderate overlap - patent may cover related technology"
        else:
            return "Limited overlap - patent appears to be in a different area"
    
    def _create_low_risk_report(self, research_data: Dict) -> Dict:
        """
        Create report when no patents are found
        """
        return {
            "overall_risk_level": "LOW",
            "overall_risk_score": 0.0,
            "risk_factors": ["No relevant patents found"],
            "total_patents_analyzed": 0,
            "high_risk_patents": 0,
            "analyzed_patents": [],
            "recommendations": [
                "✅ No existing patents found for your keywords",
                "🎉 Excellent opportunity for novel IP",
                "📝 Consider filing a provisional patent",
                "🔄 Re-run analysis with broader keywords to ensure coverage"
            ],
            "assessment_date": datetime.now().isoformat()
        }