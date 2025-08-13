
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';
import type { AnalysisResult } from '@/types/types';
import { formatCurrency } from '@/lib/utils';

// Extend the autoTable interface to include the didDrawCell hook
interface jsPDFWithAutoTable extends jsPDF {
  autoTable: (options: any) => jsPDF;
}

export function generatePdfReport(result: AnalysisResult, currency: string, thousandSeparator: ',' | '.') {
    const doc = new jsPDF() as jsPDFWithAutoTable;
    const { anomalies, caseName, analysisSummary } = result;

    // Header
    doc.setFontSize(18);
    doc.text(`IntelliAudit AI Report: ${caseName}`, 14, 22);
    doc.setFontSize(11);
    doc.setTextColor(100);
    doc.text(`Report generated on: ${new Date().toLocaleString()}`, 14, 29);

    // Summary Section
    doc.setFontSize(14);
    doc.text("Executive Summary & AI Narrative", 14, 45);
    doc.setFontSize(11);
    
    // Add a border around the summary text
    const summaryLines = doc.splitTextToSize(analysisSummary, 180);
    const summaryHeight = summaryLines.length * 5 + 10;
    doc.setDrawColor(200, 200, 200);
    doc.rect(14, 50, 182, summaryHeight);
    doc.text(summaryLines, 16, 56);

    // Anomalies Table
    const tableStartY = 55 + summaryHeight;
    doc.addPage();
    doc.setFontSize(14);
    doc.text("Anomalies Report", 14, 20);

    const head = [['Risk', 'Date', 'Description', 'Category', 'Reason', 'Legal Tags', 'Amount']];
    const body = anomalies.map(a => [
        `${a.riskScore} (${a.caseLinkabilityScore || 'N/A'})`,
        a.date,
        a.description,
        a.category,
        a.reason,
        a.legalRiskTags?.join(', ') || 'N/A',
        formatCurrency(a.amount, currency, thousandSeparator),
    ]);

    doc.autoTable({
        startY: 25,
        head,
        body,
        theme: 'striped',
        headStyles: { fillColor: [22, 163, 74] },
        didDrawCell: (data) => {
            // Custom rendering for risk score to add color
            if (data.section === 'body' && data.column.index === 0) {
                const anomaly = anomalies[data.row.index];
                let riskColor: [number, number, number] | null = null;
                if (anomaly.riskScore > 80) riskColor = [220, 38, 38]; // Red
                else if (anomaly.riskScore > 40) riskColor = [245, 158, 11]; // Amber

                if (riskColor) {
                    doc.setFillColor(...riskColor);
                    doc.rect(data.cell.x, data.cell.y, data.cell.width, data.cell.height, 'F');
                }
            }
        }
    });

    doc.save(`${caseName.replace(/\s+/g, '_')}_audit_report.pdf`);
}
