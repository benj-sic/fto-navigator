from typing import Dict, List
from datetime import datetime
import json

class ReportGenerator:
    """
    Generates structured FTO reports from risk assessment data
    """
    
    def generate_report(self, research_data: Dict, risk_assessment: Dict) -> Dict:
        """
        Create a comprehensive FTO report
        """
        report = {
            "report_metadata": {
                "generated_date": datetime.now().isoformat(),
                "report_version": "1.0",
                "analysis_id": research_data.get('analysis_id'),
                "report_type": "Freedom to Operate Analysis"
            },
            "executive_summary": self._create_executive_summary(research_data, risk_assessment),
            "research_overview": {
                "title": research_data.get('title'),
                "field": research_data.get('field_of_study'),
                "keywords": research_data.get('keywords', []),
                "researcher": research_data.get('researcher_name', 'Not provided')
            },
            "risk_assessment": {
                "overall_risk": risk_assessment.get('overall_risk_level'),
                "risk_score": risk_assessment.get('overall_risk_score'),
                "risk_factors": risk_assessment.get('risk_factors', []),
                "patents_analyzed": risk_assessment.get('total_patents_analyzed'),
                "high_risk_count": risk_assessment.get('high_risk_patents')
            },
            "patent_analysis": self._format_patent_analysis(risk_assessment.get('analyzed_patents', [])),
            "recommendations": {
                "immediate_actions": self._get_immediate_actions(risk_assessment),
                "general_recommendations": risk_assessment.get('recommendations', [])
            },
            "educational_notes": self._generate_educational_content(risk_assessment),
            "disclaimer": self._generate_disclaimer()
        }
        
        return report
    
    def _create_executive_summary(self, research_data: Dict, risk_assessment: Dict) -> str:
        """
        Create a clear, concise summary for researchers
        """
        risk_level = risk_assessment.get('overall_risk_level', 'UNKNOWN')
        patent_count = risk_assessment.get('total_patents_analyzed', 0)
        
        if risk_level == 'HIGH':
            summary = f"""
Your research "{research_data.get('title')}" has been analyzed for patent conflicts. 
We found {patent_count} relevant patents with HIGH freedom-to-operate risk. 
This suggests significant overlap with existing patents in your field. 
Immediate consultation with IP legal counsel is strongly recommended before proceeding.
            """
        elif risk_level == 'MEDIUM':
            summary = f"""
Your research "{research_data.get('title')}" shows MODERATE freedom-to-operate risk. 
We identified {patent_count} patents with some overlap to your work. 
While you can proceed with caution, reviewing the specific patents listed below 
and potentially modifying your approach could reduce legal risks.
            """
        else:
            summary = f"""
Good news! Your research "{research_data.get('title')}" shows LOW freedom-to-operate risk. 
We analyzed {patent_count} patents and found minimal overlap with your work. 
This suggests good potential for novel contributions and potential IP protection.
            """
        
        return summary.strip()
    
    def _format_patent_analysis(self, analyzed_patents: List[Dict]) -> List[Dict]:
        """
        Format patent data for the report
        """
        formatted_patents = []
        
        for patent in analyzed_patents[:5]:  # Top 5 most relevant
            formatted = {
                "patent_number": patent.get('patent_number'),
                "title": patent.get('title'),
                "risk_level": patent.get('risk_level'),
                "risk_score": patent.get('risk_score'),
                "grant_date": patent.get('grant_date'),
                "applicants": ', '.join(patent.get('applicants', [])[:2]),  # First 2 applicants
                "relevance": patent.get('relevance_explanation'),
                "risk_breakdown": patent.get('risk_factors', {})
            }
            formatted_patents.append(formatted)
        
        return formatted_patents
    
    def _get_immediate_actions(self, risk_assessment: Dict) -> List[str]:
        """
        Provide clear next steps based on risk level
        """
        risk_level = risk_assessment.get('overall_risk_level')
        
        if risk_level == 'HIGH':
            return [
                "STOP: Do not proceed without legal review",
                "Contact your institution's technology transfer office",
                "Prepare detailed documentation of your research approach",
                "Schedule consultation with IP attorney"
            ]
        elif risk_level == 'MEDIUM':
            return [
                "Review the identified patents carefully",
                "Document differences between your work and existing patents",
                "Consider minor modifications to avoid conflicts",
                "Monitor new patent filings in your area"
            ]
        else:
            return [
                "Proceed with your research",
                "Consider filing a provisional patent application",
                "Keep records of your development process",
                "Set up patent alerts for your keywords"
            ]
    
    def _generate_educational_content(self, risk_assessment: Dict) -> Dict:
        """
        Add educational content to help researchers understand FTO
        """
        return {
            "what_is_fto": "Freedom to Operate (FTO) analysis determines whether your research might infringe on existing patents.",
            "risk_levels_explained": {
                "HIGH": "Significant overlap with existing patents. Legal review essential.",
                "MEDIUM": "Some overlap exists. Proceed with caution and consider modifications.",
                "LOW": "Minimal overlap. Good opportunity for innovation."
            },
            "understanding_scores": "Risk scores range from 0 (no risk) to 1 (high risk), based on keyword matches, technical classifications, and patent recency.",
            "next_steps": "This automated analysis is a starting point. For final decisions, always consult with qualified IP professionals."
        }
    
    def _generate_disclaimer(self) -> str:
        """
        Important legal disclaimer
        """
        return """
This report is generated by an automated system for educational and preliminary assessment purposes only. 
It does not constitute legal advice. Patent law is complex and fact-specific. 
For definitive FTO analysis, please consult with a qualified patent attorney or IP professional.
The absence of identified patents does not guarantee freedom to operate, as this search may not be exhaustive.
        """.strip()