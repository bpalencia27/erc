"""
Generador avanzado de reportes médicos con IA
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, List
import uuid
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import structlog

from app.api.gemini_helpers import get_gemini_client

logger = structlog.get_logger()

class AdvancedReportGenerator:
    """Generador de reportes médicos con formato profesional"""
    
    def __init__(self):
        self.gemini_client = get_gemini_client()
        self.styles = self._setup_styles()
        self.report_dir = Path(os.environ.get('REPORT_FOLDER', 'app/static/reports'))
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_styles(self):
        """Configura estilos para el reporte"""
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para título
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Estilo para secciones
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=20
        ))
        
        # Estilo para contenido
        styles.add(ParagraphStyle(
            name='ContentText',
            parent=styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))
        
        return styles
    
    def generate_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera un reporte completo en PDF
        
        Args:
            data: Datos del análisis del paciente
            
        Returns:
            Dict con información del reporte generado
        """
        try:
            report_id = str(uuid.uuid4())
            filename = f"reporte_erc_{report_id}.pdf"
            filepath = self.report_dir / filename
            
            # Crear documento PDF
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )
            
            # Construir contenido
            story = []
            
            # Encabezado
            story.append(Paragraph("INFORME DE ANÁLISIS CLÍNICO", self.styles['CustomTitle']))
            story.append(Paragraph("Evaluación de Enfermedad Renal Crónica", self.styles['Heading3']))
            story.append(Spacer(1, 0.5*inch))
            
            # Información del paciente
            patient_info = data.get('patient_data', {})
            story.append(Paragraph("DATOS DEL PACIENTE", self.styles['SectionHeader']))
            story.append(self._create_patient_info_table(patient_info))
            story.append(Spacer(1, 0.3*inch))
            
            # Evaluación básica
            if 'basic_evaluation' in data:
                story.append(Paragraph("EVALUACIÓN RENAL", self.styles['SectionHeader']))
                story.append(self._create_evaluation_table(data['basic_evaluation']))
                story.append(Spacer(1, 0.3*inch))
            
            # Análisis de IA
            if data.get('ai_analysis', {}).get('success'):
                story.append(Paragraph("ANÁLISIS CLÍNICO DETALLADO", self.styles['SectionHeader']))
                ai_text = data['ai_analysis'].get('analysis', '')
                story.extend(self._format_ai_analysis(ai_text))
                story.append(Spacer(1, 0.3*inch))
            
            # Valores de laboratorio
            if 'lab_values' in patient_info:
                story.append(Paragraph("VALORES DE LABORATORIO", self.styles['SectionHeader']))
                story.append(self._create_lab_table(patient_info['lab_values']))
                story.append(Spacer(1, 0.3*inch))
            
            # Objetivos terapéuticos
            if data.get('therapeutic_goals', {}).get('success'):
                story.append(PageBreak())
                story.append(Paragraph("OBJETIVOS TERAPÉUTICOS", self.styles['SectionHeader']))
                goals_text = data['therapeutic_goals'].get('goals', '')
                story.extend(self._format_therapeutic_goals(goals_text))
                story.append(Spacer(1, 0.3*inch))
            
            # Recomendaciones
            if 'recommendations' in data:
                story.append(Paragraph("RECOMENDACIONES", self.styles['SectionHeader']))
                story.extend(self._format_recommendations(data['recommendations']))
            
            # Pie de página
            story.append(Spacer(1, 0.5*inch))
            story.append(self._create_footer())
            
            # Generar PDF
            doc.build(story)
            
            logger.info(f"Report generated successfully: {filename}")
            
            return {
                "success": True,
                "report_id": report_id,
                "filename": filename,
                "filepath": str(filepath),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_patient_info_table(self, patient_info: Dict[str, Any]) -> Table:
        """Crea tabla con información del paciente"""
        data = [
            ['ID Paciente:', patient_info.get('patient_id', 'N/A')],
            ['Edad:', f"{patient_info.get('age', 'N/A')} años"],
            ['Sexo:', 'Masculino' if patient_info.get('sex') in ['M', 'male'] else 'Femenino'],
            ['Peso:', f"{patient_info.get('weight', 'N/A')} kg"],
            ['Altura:', f"{patient_info.get('height', 'N/A')} cm"],
            ['IMC:', self._calculate_bmi(patient_info.get('weight'), patient_info.get('height'))],
            ['Fecha:', datetime.now().strftime('%d/%m/%Y %H:%M')]
        ]
        
        table = Table(data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        
        return table
    
    def _create_evaluation_table(self, evaluation: Dict[str, Any]) -> Table:
        """Crea tabla con evaluación renal"""
        data = [
            ['Parámetro', 'Valor', 'Referencia'],
            ['TFG (MDRD)', f"{evaluation.get('tfg', 'N/A')} ml/min/1.73m²", '>90'],
            ['Etapa ERC', evaluation.get('stage', 'N/A'), '-'],
            ['Creatinina', f"{evaluation.get('creatinine', 'N/A')} mg/dL", '0.7-1.3'],
            ['Proteinuria', evaluation.get('proteinuria', 'No evaluada'), '<150 mg/día']
        ]
        
        table = Table(data, colWidths=[2*inch, 2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        return table
    
    def _create_lab_table(self, lab_values: Dict[str, Any]) -> Table:
        """Crea tabla con valores de laboratorio"""
        data = [['Categoría', 'Parámetro', 'Valor', 'Unidad', 'Referencia']]
        
        # Organizar valores por categoría
        categories = {
            'Hemograma': ['hemoglobina', 'hematocrito', 'leucocitos', 'plaquetas'],
            'Función Renal': ['creatinina', 'bun', 'acido_urico'],
            'Electrolitos': ['sodio', 'potasio', 'cloro', 'calcio', 'fosforo'],
            'Perfil Lipídico': ['colesterol_total', 'ldl', 'hdl', 'trigliceridos']
        }
        
        references = {
            'hemoglobina': '12-16 g/dL',
            'hematocrito': '36-46%',
            'leucocitos': '4.5-11 x10³/μL',
            'plaquetas': '150-400 x10³/μL',
            'creatinina': '0.7-1.3 mg/dL',
            'bun': '7-20 mg/dL',
            'acido_urico': '3.5-7.2 mg/dL',
            'sodio': '136-145 mEq/L',
            'potasio': '3.5-5.1 mEq/L',
            'cloro': '98-107 mEq/L',
            'calcio': '8.5-10.5 mg/dL',
            'fosforo': '2.5-4.5 mg/dL',
            'colesterol_total': '<200 mg/dL',
            'ldl': '<100 mg/dL',
            'hdl': '>40 mg/dL',
            'trigliceridos': '<150 mg/dL'
        }
        
        for category, params in categories.items():
            for param in params:
                if param in lab_values:
                    value_data = lab_values[param]
                    if isinstance(value_data, dict):
                        value = value_data.get('valor', 'N/A')
                        unit = value_data.get('unidad', '')
                    else:
                        value = value_data
                        unit = ''
                    
                    data.append([
                        category,
                        param.replace('_', ' ').title(),
                        str(value),
                        unit,
                        references.get(param, '-')
                    ])
        
        if len(data) > 1:
            table = Table(data, colWidths=[1.5*inch, 1.5*inch, 0.8*inch, 0.8*inch, 1.2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
            ]))
            return table
        else:
            return Paragraph("No hay valores de laboratorio disponibles", self.styles['ContentText'])
    
    def _format_ai_analysis(self, analysis_text: str) -> List:
        """Formatea el análisis de IA para el PDF"""
        story = []
        
        # Dividir por secciones
        sections = analysis_text.split('###')
        
        for section in sections:
            if section.strip():
                lines = section.strip().split('\n')
                if lines:
                    # Primer línea es el título de la sección
                    title = lines[0].strip()
                    if title:
                        story.append(Paragraph(title, self.styles['Heading4']))
                    
                    # Resto del contenido
                    for line in lines[1:]:
                        line = line.strip()
                        if line.startswith('-'):
                            # Es un item de lista
                            story.append(Paragraph(f"• {line[1:].strip()}", self.styles['ContentText']))
                        elif line:
                            story.append(Paragraph(line, self.styles['ContentText']))
        
        return story
    
    def _format_therapeutic_goals(self, goals_text: str) -> List:
        """Formatea los objetivos terapéuticos"""
        return self._format_ai_analysis(goals_text)
    
    def _format_recommendations(self, recommendations: List[Dict[str, Any]]) -> List:
        """Formatea las recomendaciones"""
        story = []
        
        # Agrupar por prioridad
        high_priority = [r for r in recommendations if r.get('priority') == 'high']
        medium_priority = [r for r in recommendations if r.get('priority') == 'medium']
        low_priority = [r for r in recommendations if r.get('priority') == 'low']
        
        if high_priority:
            story.append(Paragraph("Alta Prioridad:", self.styles['Heading4']))
            for rec in high_priority:
                story.append(Paragraph(
                    f"• {rec['recommendation']} ({rec.get('category', 'general')})",
                    self.styles['ContentText']
                ))
            story.append(Spacer(1, 0.1*inch))
        
        if medium_priority:
            story.append(Paragraph("Prioridad Media:", self.styles['Heading4']))
            for rec in medium_priority:
                story.append(Paragraph(
                    f"• {rec['recommendation']} ({rec.get('category', 'general')})",
                    self.styles['ContentText']
                ))
            story.append(Spacer(1, 0.1*inch))
        
        if low_priority:
            story.append(Paragraph("Prioridad Baja:", self.styles['Heading4']))
            for rec in low_priority:
                story.append(Paragraph(
                    f"• {rec['recommendation']} ({rec.get('category', 'general')})",
                    self.styles['ContentText']
                ))
        
        return story
    
    def _calculate_bmi(self, weight: float, height: float) -> str:
        """Calcula el IMC"""
        try:
            if weight and height:
                height_m = height / 100
                bmi = weight / (height_m ** 2)
                return f"{bmi:.1f} kg/m²"
        except:
            pass
        return "N/A"
    
    def _create_footer(self) -> Paragraph:
        """Crea el pie de página del reporte"""
        footer_text = (
            "<font size=8>"
            "Este informe ha sido generado automáticamente por ERC Insight. "
            "Los resultados deben ser interpretados por un profesional médico calificado. "
            "La información contenida es confidencial y está protegida por el secreto médico."
            "</font>"
        )
        return Paragraph(footer_text, self.styles['ContentText'])
    
    def generate_summary_report(self, patient_id: str, date_range: Dict[str, str]) -> Dict[str, Any]:
        """
        Genera un reporte resumido del progreso del paciente
        
        Args:
            patient_id: ID del paciente
            date_range: Rango de fechas para el reporte
            
        Returns:
            Dict con información del reporte generado
        """
        # Implementación para reportes de seguimiento
        # TODO: Implementar cuando se tenga sistema de persistencia
        pass
