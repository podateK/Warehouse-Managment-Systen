from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.graphics.barcode import code128
import random
import string
from datetime import datetime, timedelta
import os

class ShipmentLabelGenerator:
    
    LABEL_TYPES = {
        'PACZKA': {'color': '#ef4444', 'name': 'PACZKA'},
        'PALETA': {'color': '#f59e0b', 'name': 'PALETA'},
        'POBRANIE': {'color': '#8b5cf6', 'name': 'POBRANIE'},
        'ZWROT': {'color': '#6366f1', 'name': 'ZWROT'},
    }
    
    def __init__(self, output_dir="labels"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    @staticmethod
    def generate_random_barcode():
        """Generate random barcode (13 digits - EAN)"""
        return ''.join(random.choices(string.digits, k=13))
    
    @staticmethod
    def generate_random_serial():
        """Generate random WZ number"""
        return 'WZ/' + datetime.now().strftime('%Y%m%d') + '/' + ''.join(random.choices(string.digits, k=5))
    
    @staticmethod
    def generate_random_date(days_range=30):
        """Generate random date within range"""
        random_days = random.randint(0, days_range)
        return (datetime.now() - timedelta(days=random_days)).strftime('%Y-%m-%d')
    
    def create_shipment_label(self, recipient, address, postal_code, city, sender_notes, label_type='PACZKA'):
        """
        Create shipment label (WZ) with customizable shipping information
        
        Args:
            recipient (str): Recipient name
            address (str): Street address
            postal_code (str): Postal code
            city (str): City name
            sender_notes (str): Sender notes/remarks
            label_type (str): Type of label (PACZKA, PALETA, POBRANIE, ZWROT)
        
        Returns:
            tuple: (filepath, label_data_dict)
        """
        barcode_code = self.generate_random_barcode()
        wz_number = self.generate_random_serial()
        label_date = datetime.now().strftime('%Y-%m-%d')
        
        label_info = self.LABEL_TYPES.get(label_type, self.LABEL_TYPES['PACZKA'])
        label_color = label_info['color']
        
        filename = f"WZ_{wz_number.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = f"{self.output_dir}/{filename}"
        
        doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=0.5*cm, bottomMargin=0.5*cm)
        story = []
        
        title_style = ParagraphStyle(
            'Title',
            fontSize=16,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor(label_color),
            spaceAfter=8,
        )
        story.append(Paragraph(f"ETYKIETA WYSYŁKI - {label_info['name']}", title_style))
        story.append(Spacer(1, 0.2*cm))
        
        try:
            barcode_drawing = code128.Code128(barcode_code, barHeight=0.8*cm)
            story.append(barcode_drawing)
        except:
            story.append(Paragraph(f"Kod: {barcode_code}", ParagraphStyle('Code', fontSize=10)))
        
        story.append(Spacer(1, 0.2*cm))
        
        shipping_data = [
            ['Lp./Number:', wz_number, 'Data/Date:', label_date],
            ['Odbiorca/Recipient:', recipient, '', ''],
            ['Adres/Address:', address, 'Kod pocztowy/Postal:', postal_code],
            ['Miasto/City:', city, 'Typ/Type:', label_info['name']],
        ]
        
        shipping_table = Table(shipping_data, colWidths=[2.5*cm, 6*cm, 2.5*cm, 4.5*cm])
        shipping_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(label_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
        ]))
        
        story.append(shipping_table)
        story.append(Spacer(1, 0.3*cm))
        
        if sender_notes and sender_notes.strip():
            notes_style = ParagraphStyle(
                'NotesTitle',
                fontSize=10,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor(label_color),
                spaceAfter=4,
            )
            story.append(Paragraph("Uwagi nadawcy/Sender Notes:", notes_style))
            
            notes_content_style = ParagraphStyle(
                'NotesContent',
                fontSize=9,
                fontName='Helvetica',
                textColor=colors.black,
                wordWrap='CJK',
            )
            story.append(Paragraph(sender_notes, notes_content_style))
            story.append(Spacer(1, 0.2*cm))
        
        footer_style = ParagraphStyle(
            'Footer',
            fontSize=7,
            fontName='Helvetica',
            textColor=colors.grey,
            alignment=1,
        )
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(f"Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
        
        doc.build(story)
        
        return filepath, {
            'type': 'WZ',
            'label_type': label_type,
            'wz_number': wz_number,
            'barcode': barcode_code,
            'recipient': recipient,
            'address': address,
            'postal_code': postal_code,
            'city': city,
            'sender_notes': sender_notes,
            'date': label_date
        }
