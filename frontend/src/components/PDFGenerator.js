import jsPDF from 'jspdf';
import 'jspdf-autotable';

export const generatePDFReport = (reportData, riskData) => {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.width;
  
  // Header
  doc.setFontSize(24);
  doc.setTextColor(102, 126, 234); // Purple color
  doc.text('FTO Navigator Report', pageWidth / 2, 20, { align: 'center' });
  
  doc.setFontSize(12);
  doc.setTextColor(100);
  doc.text(`Generated: ${new Date().toLocaleDateString()}`, pageWidth / 2, 30, { align: 'center' });
  
  // Executive Summary
  doc.setFontSize(16);
  doc.setTextColor(0);
  doc.text('Executive Summary', 14, 45);
  
  doc.setFontSize(11);
  doc.setTextColor(60);
  const summaryLines = doc.splitTextToSize(reportData.executive_summary, pageWidth - 28);
  doc.text(summaryLines, 14, 55);
  
  let yPosition = 55 + (summaryLines.length * 5) + 10;
  
  // Risk Assessment Overview
  doc.setFontSize(16);
  doc.setTextColor(0);
  doc.text('Risk Assessment', 14, yPosition);
  yPosition += 10;
  
  // Risk level box
  const riskLevel = riskData.overall_risk_level;
  const riskColor = riskLevel === 'HIGH' ? [229, 62, 62] : 
                   riskLevel === 'MEDIUM' ? [221, 107, 32] : 
                   [72, 187, 120];
  
  doc.setFillColor(...riskColor);
  doc.roundedRect(14, yPosition, 40, 10, 3, 3, 'F');
  doc.setTextColor(255);
  doc.setFontSize(10);
  doc.text(riskLevel + ' RISK', 34, yPosition + 7, { align: 'center' });
  
  doc.setTextColor(60);
  doc.setFontSize(11);
  doc.text(`Risk Score: ${(riskData.overall_risk_score * 100).toFixed(0)}%`, 60, yPosition + 7);
  doc.text(`Patents Analyzed: ${riskData.total_patents_analyzed}`, 120, yPosition + 7);
  
  yPosition += 20;
  
  // Risk Factors
  doc.setFontSize(14);
  doc.setTextColor(0);
  doc.text('Risk Factors:', 14, yPosition);
  yPosition += 8;
  
  doc.setFontSize(11);
  doc.setTextColor(60);
  riskData.risk_factors.forEach(factor => {
    doc.text(`• ${factor}`, 20, yPosition);
    yPosition += 6;
  });
  
  yPosition += 10;
  
  // Check if we need a new page
  if (yPosition > 250) {
    doc.addPage();
    yPosition = 20;
  }
  
  // Top Patents Table
  if (riskData.analyzed_patents && riskData.analyzed_patents.length > 0) {
    doc.setFontSize(16);
    doc.setTextColor(0);
    doc.text('Relevant Patents', 14, yPosition);
    yPosition += 10;
    
    const patentData = riskData.analyzed_patents.slice(0, 5).map(patent => [
      patent.patent_number,
      patent.title.substring(0, 50) + '...',
      patent.risk_level,
      (patent.risk_score * 100).toFixed(0) + '%'
    ]);
    
    doc.autoTable({
      startY: yPosition,
      head: [['Patent #', 'Title', 'Risk Level', 'Risk Score']],
      body: patentData,
      theme: 'striped',
      headStyles: { fillColor: [102, 126, 234] },
      columnStyles: {
        0: { cellWidth: 30 },
        1: { cellWidth: 90 },
        2: { cellWidth: 30 },
        3: { cellWidth: 25 }
      }
    });
    
    yPosition = doc.lastAutoTable.finalY + 15;
  }
  
  // Check if we need a new page
  if (yPosition > 200) {
    doc.addPage();
    yPosition = 20;
  }
  
  // Recommendations
  doc.setFontSize(16);
  doc.setTextColor(0);
  doc.text('Recommendations', 14, yPosition);
  yPosition += 10;
  
  doc.setFontSize(12);
  doc.setTextColor(0);
  doc.text('Immediate Actions:', 14, yPosition);
  yPosition += 8;
  
  doc.setFontSize(11);
  doc.setTextColor(60);
  reportData.recommendations.immediate_actions.forEach(action => {
    const actionLines = doc.splitTextToSize(`• ${action}`, pageWidth - 28);
    doc.text(actionLines, 20, yPosition);
    yPosition += actionLines.length * 5 + 2;
    
    if (yPosition > 270) {
      doc.addPage();
      yPosition = 20;
    }
  });
  
  yPosition += 5;
  
  doc.setFontSize(12);
  doc.setTextColor(0);
  doc.text('General Recommendations:', 14, yPosition);
  yPosition += 8;
  
  doc.setFontSize(11);
  doc.setTextColor(60);
  reportData.recommendations.general_recommendations.forEach(rec => {
    const recLines = doc.splitTextToSize(rec, pageWidth - 28);
    doc.text(recLines, 20, yPosition);
    yPosition += recLines.length * 5 + 2;
    
    if (yPosition > 270) {
      doc.addPage();
      yPosition = 20;
    }
  });
  
  // Disclaimer at the bottom of the last page
  doc.addPage();
  doc.setFontSize(14);
  doc.setTextColor(229, 62, 62);
  doc.text('Important Notice', 14, 20);
  
  doc.setFontSize(10);
  doc.setTextColor(60);
  const disclaimerLines = doc.splitTextToSize(reportData.disclaimer, pageWidth - 28);
  doc.text(disclaimerLines, 14, 30);
  
  // Save the PDF
  const fileName = `FTO-Report-${new Date().toISOString().split('T')[0]}.pdf`;
  doc.save(fileName);
};