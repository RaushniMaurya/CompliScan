from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO


def generate_pdf_report(scan):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=25*mm, bottomMargin=20*mm,
        leftMargin=20*mm, rightMargin=20*mm
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=20, spaceAfter=4)
    sub_style = ParagraphStyle("SubStyle", parent=styles["Normal"], textColor=colors.grey, spaceAfter=16)
    heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6)

    # Small style used INSIDE table cells so text wraps instead of overflowing
    cell_style = ParagraphStyle("CellStyle", parent=styles["Normal"], fontSize=8.5, leading=11)
    header_cell_style = ParagraphStyle("HeaderCellStyle", parent=styles["Normal"], fontSize=8.5, leading=11, textColor=colors.white, fontName="Helvetica-Bold")

    elements = []
    elements.append(Paragraph("CompliScan — Inspection Report", title_style))
    elements.append(Paragraph(
        "AI-assisted screening under the Legal Metrology (Packaged Commodities) Rules, 2011",
        sub_style
    ))

    # --- Summary table ---
    summary_data = [
        [Paragraph("Product image", cell_style), Paragraph(scan["image_name"], cell_style)],
        [Paragraph("Scanned at", cell_style), Paragraph(scan["scanned_at"], cell_style)],
        [Paragraph("Overall status", cell_style), Paragraph(scan["overall_status"].replace("_", " "), cell_style)],
        [Paragraph("Missing required declarations", cell_style), Paragraph(str(scan["missing_required_count"]), cell_style)],
    ]
    summary_table = Table(summary_data, colWidths=[170, 200])
    summary_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(summary_table)

    elements.append(Paragraph("Declaration-by-declaration breakdown", heading_style))

    # --- Detail table, all cells wrapped in Paragraph so text wraps ---
    detail_rows = [[
        Paragraph("Declaration", header_cell_style),
        Paragraph("Status", header_cell_style),
        Paragraph("Detected value", header_cell_style),
        Paragraph("Rule reference", header_cell_style),
    ]]

    for item in scan["details"]:
        detail_rows.append([
            Paragraph(item["label"], cell_style),
            Paragraph(item["status"].replace("_", " "), cell_style),
            Paragraph(str(item["detected_value"]) if item["detected_value"] else "Not found", cell_style),
            Paragraph(item["rule_reference"], cell_style),
        ])

    # Column widths sum to ~455pt, fits within A4 minus 20mm margins each side
    detail_table = Table(detail_rows, colWidths=[125, 75, 100, 155])
    detail_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#14103A")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(detail_table)

    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "This is an automated preliminary screening result. Final compliance determination requires manual verification by an authorized inspector.",
        ParagraphStyle("Disclaimer", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer