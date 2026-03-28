"""
PDF Invoice Generator for WMS - Warehouse Management System
Generates PZ (Receipt) and WZ (Issue) documents
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from datetime import datetime
import os


class PDFInvoiceGenerator:
    """Generate WMS documents (PZ/WZ) as PDF files"""
    
    # Document Type Names (Polish)
    DOC_TYPES = {
        'PZ': 'PRZYJĘCIE ZEWNĘTRZNE',
        'WZ': 'WYDANIE ZEWNĘTRZNE'
    }
    
    def __init__(self, company_name="Magazyn Główny", output_dir="invoices"):
        self.company_name = company_name
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_invoice(self, data, filename=None):
        """
        Generate a PDF invoice from document data
        
        Args:
            data (dict): Document data with keys:
                - doc_type: 'PZ' or 'WZ'
                - number: Document number (e.g., 'PZ/001/2026')
                - date: Document date (YYYY-MM-DD)
                - contractor: Dostawca/Klient
                - receiver: Odbiorca (place)
                - original_number: Original doc number (if any)
                - items: List of dicts with keys:
                    - name: Item name
                    - quantity: Quantity delivered
                    - quantity_delivered: Actually received
                    - unit: Unit of measure (szt., kg, m, etc)
                    - price_netto: Net price per unit
                    - value_netto: Net value
                - total_value: Total document value
            filename (str): Output filename (optional, auto-generated if None)
        
        Returns:
            str: Path to generated PDF file
        """
        doc_type = data.get('doc_type', 'PZ')
        doc_number = data.get('number', 'DOC/001/2026')
        doc_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Generate filename if not provided
        if filename is None:
            safe_number = doc_number.replace('/', '_').replace(' ', '')
            filename = f"{safe_number}_{doc_date}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        # Build story (content)
        story = []
        
        # Add header
        story.extend(self._build_header(doc_type, data))
        
        # Add document info
        story.extend(self._build_document_info(data, doc_type))
        
        # Add items table
        story.extend(self._build_items_table(data))
        
        # Add totals and signature
        story.extend(self._build_footer(data))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def _build_header(self, doc_type, data):
        """Build header section with company name and document type"""
        styles = getSampleStyleSheet()
        story = []
        
        # Company header
        company_title = ParagraphStyle(
            'CompanyTitle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#003d7a'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        story.append(Paragraph(self.company_name, company_title))
        story.append(Spacer(1, 0.3*cm))
        
        # Document type
        doc_type_style = ParagraphStyle(
            'DocType',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#003d7a'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        doc_type_name = self.DOC_TYPES.get(doc_type, 'DOKUMENT')
        story.append(Paragraph(doc_type_name, doc_type_style))
        story.append(Spacer(1, 0.5*cm))
        
        return story
    
    def _build_document_info(self, data, doc_type):
        """Build document information section"""
        styles = getSampleStyleSheet()
        story = []
        
        label_style = ParagraphStyle(
            'FieldLabel',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            fontName='Helvetica-Bold',
            alignment=TA_LEFT
        )
        
        value_style = ParagraphStyle(
            'FieldValue',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            alignment=TA_LEFT
        )
        
        # Create info table
        info_data = [
            [
                Paragraph('Numer dokumentu:', label_style),
                Paragraph(data.get('number', ''), value_style),
                Paragraph('Data wystawienia:', label_style),
                Paragraph(data.get('date', ''), value_style)
            ],
            [
                Paragraph('Numer oryginału:', label_style),
                Paragraph(data.get('original_number', '-'), value_style),
                Paragraph('', label_style),
                Paragraph('', value_style)
            ],
            [
                Paragraph('Dostawca / Klient:', label_style),
                Paragraph(data.get('contractor', ''), value_style),
                Paragraph('Odbiorca (Docelowy):', label_style),
                Paragraph(data.get('receiver', ''), value_style)
            ],
        ]
        
        info_table = Table(info_data, colWidths=[2.5*cm, 4.5*cm, 3*cm, 4.5*cm])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.grey),
            ('LINEBELOW', (0, 1), (-1, 1), 0.5, colors.grey),
            ('LINEBELOW', (0, 2), (-1, 2), 0.5, colors.grey),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0.5*cm),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.5*cm))
        
        return story
    
    def _build_items_table(self, data):
        """Build items/goods table"""
        styles = getSampleStyleSheet()
        story = []
        
        # Table header style
        header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.white,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_LEFT
        )
        
        number_style = ParagraphStyle(
            'TableNumber',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_RIGHT
        )
        
        # Prepare table data
        table_data = [
            [
                Paragraph('Lp.', header_style),
                Paragraph('Nazwa towaru', header_style),
                Paragraph('Jm', header_style),
                Paragraph('Ilość dostarczenia', header_style),
                Paragraph('Ilość przyjęcia', header_style),
                Paragraph('Cena netto', header_style),
                Paragraph('Wartość netto', header_style)
            ]
        ]
        
        # Add items
        items = data.get('items', [])
        for idx, item in enumerate(items, 1):
            table_data.append([
                Paragraph(str(idx), number_style),
                Paragraph(item.get('name', ''), cell_style),
                Paragraph(item.get('unit', 'szt.'), cell_style),
                Paragraph(f"{item.get('quantity', 0):.2f}", number_style),
                Paragraph(f"{item.get('quantity_delivered', 0):.2f}", number_style),
                Paragraph(f"{item.get('price_netto', 0):.2f} PLN", number_style),
                Paragraph(f"{item.get('value_netto', 0):.2f} PLN", number_style)
            ])
        
        # Add summary row if no items
        if not items:
            table_data.append([
                Paragraph('-', cell_style),
                Paragraph('Brak pozycji', cell_style),
                Paragraph('', cell_style),
                Paragraph('0.00', number_style),
                Paragraph('0.00', number_style),
                Paragraph('0.00 PLN', number_style),
                Paragraph('0.00 PLN', number_style)
            ])
        
        # Create table
        col_widths = [0.8*cm, 5*cm, 1.2*cm, 2*cm, 2*cm, 2*cm, 2*cm]
        items_table = Table(table_data, colWidths=col_widths)
        
        items_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003d7a')),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # All cells
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            
            # Alternate row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 0.3*cm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0.3*cm),
            ('TOPPADDING', (0, 0), (-1, -1), 0.2*cm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0.2*cm),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 0.3*cm))
        
        return story
    
    def _build_footer(self, data):
        """Build footer with totals and signatures"""
        styles = getSampleStyleSheet()
        story = []
        
        total_style = ParagraphStyle(
            'TotalLabel',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            alignment=TA_RIGHT
        )
        
        total_value_style = ParagraphStyle(
            'TotalValue',
            parent=styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#003d7a'),
            alignment=TA_RIGHT
        )
        
        # Totals table
        total_amount = data.get('total_value', 0)
        
        totals_data = [
            ['', 'RAZEM WARTOŚĆ NETTO:', f'{total_amount:.2f} PLN'],
            ['', 'VAT (23%):', f'{total_amount * 0.23:.2f} PLN'],
            ['', 'RAZEM WARTOŚĆ BRUTTO:', f'{total_amount * 1.23:.2f} PLN']
        ]
        
        totals_table = Table(totals_data, colWidths=[4.5*cm, 4*cm, 3*cm])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, -1), (2, -1), 11),
            ('TEXTCOLOR', (2, -1), (2, -1), colors.HexColor('#003d7a')),
            ('LINEABOVE', (1, -1), (2, -1), 1.5, colors.HexColor('#003d7a')),
            ('LINEBELOW', (1, -1), (2, -1), 1.5, colors.HexColor('#003d7a')),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0.5*cm),
        ]))
        
        story.append(totals_table)
        story.append(Spacer(1, 0.8*cm))
        
        # Signature section
        sig_style = ParagraphStyle(
            'SignatureLabel',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        
        sig_data = [
            [
                Paragraph('_________________________', sig_style),
                Paragraph('', sig_style),
                Paragraph('_________________________', sig_style)
            ],
            [
                Paragraph('Magazynier', sig_style),
                Paragraph('', sig_style),
                Paragraph('Kierownik magazynu', sig_style)
            ]
        ]
        
        sig_table = Table(sig_data, colWidths=[5*cm, 2*cm, 5*cm])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(sig_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Footer text
        footer_text = ParagraphStyle(
            'FooterText',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=0
        )
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        story.append(Paragraph(f'Wygenerowano: {now}', footer_text))
        
        return story


def generate_pdf_from_database(db_manager, doc_id, output_dir="invoices"):
    """
    Generate PDF from database document record
    
    Args:
        db_manager: DatabaseManager instance
        doc_id (int): Document ID
        output_dir (str): Output directory for PDF
    
    Returns:
        str: Path to generated PDF or None if doc not found
    """
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Get document data
    cursor.execute('''
        SELECT id, doc_type, date, number, original_number, contractor, receiver, value, cost
        FROM warehouse_data
        WHERE id = ?
    ''', (doc_id,))
    
    doc_row = cursor.fetchone()
    if not doc_row:
        conn.close()
        return None
    
    doc_id, doc_type, date, number, original_number, contractor, receiver, value, cost = doc_row
    
    # Get items
    cursor.execute('''
        SELECT name, quantity, quantity_delivered, unit, price_netto, value_netto
        FROM warehouse_receipt_items
        WHERE receipt_id = ?
    ''', (doc_id,))
    
    items_rows = cursor.fetchall()
    items = [
        {
            'name': row[0],
            'quantity': row[1],
            'quantity_delivered': row[2],
            'unit': row[3],
            'price_netto': row[4],
            'value_netto': row[5]
        }
        for row in items_rows
    ]
    
    conn.close()
    
    # Prepare data for generator
    data = {
        'doc_type': doc_type,
        'number': number,
        'date': date,
        'original_number': original_number,
        'contractor': contractor,
        'receiver': receiver,
        'items': items,
        'total_value': value
    }
    
    # Generate PDF
    generator = PDFInvoiceGenerator(output_dir=output_dir)
    return generator.generate_invoice(data)
