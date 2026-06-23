from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from datetime import datetime
import re

# Read the markdown content
with open('RESUME_MATCHER_GUIDE.md', 'r') as f:
    content = f.read()

# Create PDF
pdf_filename = "Resume_Matcher_Application_Guide.pdf"
doc = SimpleDocTemplate(pdf_filename, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)

# Container for PDF elements
elements = []

# Define styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#0056b3'),
    spaceAfter=30,
    alignment=1,
    leading=28
)

heading2_style = ParagraphStyle(
    'CustomHeading2',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#0056b3'),
    spaceAfter=12,
    spaceBefore=12,
    leading=18
)

heading3_style = ParagraphStyle(
    'CustomHeading3',
    parent=styles['Heading3'],
    fontSize=12,
    textColor=colors.HexColor('#1a5a96'),
    spaceAfter=8,
    spaceBefore=8,
    leading=14
)

normal_style = ParagraphStyle(
    'CustomNormal',
    parent=styles['Normal'],
    fontSize=11,
    leading=14,
    spaceAfter=6
)

# Helper function to escape HTML in markdown
def escape_and_convert(text):
    # Basic markdown to HTML conversion
    text = text.strip()
    if not text:
        return ""
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = text.replace('`', '')
    
    # Escape remaining HTML special characters that shouldn't be there
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # Restore our intentional tags
    text = text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
    text = text.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
    
    return text

# Title
title = Paragraph("Resume Matcher Application<br/>Complete User Guide", title_style)
elements.append(title)
elements.append(Spacer(1, 0.1*inch))

# Add metadata
metadata = Paragraph(
    f"<b>Version:</b> 1.0 | <b>Generated:</b> {datetime.now().strftime('%B %d, %Y')} | <b>Application:</b> Resume Matcher System",
    normal_style
)
elements.append(metadata)
elements.append(Spacer(1, 0.3*inch))

# Process markdown content line by line
lines = content.split('\n')
i = 0
page_break_count = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Skip empty lines
    if not stripped:
        elements.append(Spacer(1, 0.05*inch))
        i += 1
        continue
    
    # H1 - Skip (main title)
    if stripped.startswith('# '):
        pass
    
    # H2 - Section heading with page break
    elif stripped.startswith('## '):
        if page_break_count > 0:
            elements.append(PageBreak())
        elements.append(Paragraph(stripped[3:], heading2_style))
        page_break_count += 1
        elements.append(Spacer(1, 0.1*inch))
    
    # H3 - Subsection heading
    elif stripped.startswith('### '):
        elements.append(Paragraph(stripped[4:], heading3_style))
        elements.append(Spacer(1, 0.05*inch))
    
    # Code/pre-formatted blocks
    elif stripped.startswith('```'):
        code_lines = []
        i += 1
        while i < len(lines) and not lines[i].strip().startswith('```'):
            code_lines.append(lines[i])
            i += 1
        if code_lines:
            code_text = '\n'.join(code_lines).strip()
            # Create a box for code
            elements.append(Paragraph(f"<font face='Courier' size='9'>{code_text}</font>", styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
    
    # Bullet points
    elif stripped.startswith('- '):
        bullet_text = stripped[2:]
        elements.append(Paragraph(f"• {bullet_text}", normal_style))
    
    # Ordered list
    elif stripped[0].isdigit() and '. ' in stripped:
        parts = stripped.split('. ', 1)
        if len(parts) == 2:
            elements.append(Paragraph(f"{parts[0]}. {parts[1]}", normal_style))
    
    # Tables (skip for now)
    elif stripped.startswith('|'):
        pass
    
    # Regular paragraph
    else:
        if stripped and not stripped.startswith('---'):
            try:
                para = Paragraph(stripped, normal_style)
                elements.append(para)
            except:
                # If it fails, just add simple text
                elements.append(Paragraph(stripped[:100], normal_style))
        elements.append(Spacer(1, 0.05*inch))
    
    i += 1

# Add footer
elements.append(Spacer(1, 0.2*inch))
footer = Paragraph(
    "<i>This document provides a complete guide to the Resume Matcher Application.<br/>For support, contact the application administrator.</i>",
    ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
)
elements.append(footer)

# Build PDF
try:
    doc.build(elements)
    print(f"✓ PDF generated successfully: {pdf_filename}")
    print(f"✓ Location: c:\\Users\\rahul\\OneDrive\\Desktop\\web_app\\{pdf_filename}")
except Exception as e:
    print(f"✗ Error generating PDF: {e}")
    import traceback
    traceback.print_exc()
