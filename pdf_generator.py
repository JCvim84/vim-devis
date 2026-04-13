"""
Génération de PDF Devis - Visiter Ile-Maurice
Style identique à la facture template
"""

import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate

# Couleurs
TEAL = colors.HexColor("#3AAFA9")
DARK_TEXT = colors.HexColor("#2B2B2B")
LIGHT_GRAY = colors.HexColor("#F5F5F5")
MID_GRAY = colors.HexColor("#CCCCCC")

COUNTER_FILE = os.path.join(os.path.dirname(__file__), "devis_counter.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "devis_output")

COMPANY = {
    "name": "LOCAL EXPLORERS VENTURES LTD.",
    "address": "29, CHEMIN DU BENJOIN",
    "city": "MORC. CAMBIER, LE MORNE",
    "phone": "+23055097142",
    "website": "WWW.VISITERILEMAURICE.COM",
    "brn": "BRN : C24205966",
}

BANK = {
    "bic": "BOUS FRPP XXX",
    "iban": "FR76 4061 8803 3200 0404 6756 431",
    "domiciliation": "44 RUE TRAVERSIÈRE, CS 80134, 92772 BOULOGNE-BILLANCOURT CEDEX, FRANCE",
    "titulaire": "M. MARTIN JEAN-CHRISTOPHE",
    "code_banque": "40618",
    "code_guichet": "80332",
    "num_compte": "00040467564",
    "cle_rib": "31",
}


def get_next_number(prefix="DEVIS"):
    """Retourne le prochain numéro de devis (DEVIS N° 0001)"""
    os.makedirs(os.path.dirname(COUNTER_FILE) if os.path.dirname(COUNTER_FILE) else ".", exist_ok=True)
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"devis": 0, "facture": 0}

    key = prefix.lower()
    data[key] = data.get(key, 0) + 1

    with open(COUNTER_FILE, "w") as f:
        json.dump(data, f)

    return f"{data[key]:04d}"


def generate_pdf(client: dict, items: list, objet: str, doc_type: str = "DEVIS", numero: str = None) -> str:
    """
    Génère un PDF devis/facture.

    client = {
        "nom": "RÉMI BENSABATH",
        "societe": "HOLDING GROUPE SABA",  # optionnel
        "adresse": "7 RUE DE LA PRÉFECTURE",
        "ville": "06300 NICE",
    }

    items = [
        {"description": "O'Biches - Deluxe Apartment by Horizon", "qte": 7, "prix": 1984.50},
        ...
    ]

    objet = "Séjour du 21 au 28 février 2026"
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if numero is None:
        numero = get_next_number(doc_type)

    date_str = datetime.now().strftime("%d %B %Y").upper()
    filename = f"{doc_type}_{numero}_{client['nom'].replace(' ', '_')}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Calculs
    for item in items:
        item["total"] = round(item["qte"] * item["prix"], 2)
    montant_total = round(sum(i["total"] for i in items), 2)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4  # 595.27 x 841.89 points

    _draw_header(c, width, height)
    _draw_doc_info(c, width, height, doc_type, numero, date_str, client)
    _draw_objet(c, width, height, objet)
    y_after_table = _draw_items_table(c, width, height, items)
    _draw_totals(c, width, height, montant_total, y_after_table)
    _draw_footer(c, width, height)

    c.save()
    return filepath


def _draw_header(c, width, height):
    """Logo + infos société"""
    # Bandeau teal gauche
    c.setFillColor(TEAL)
    c.rect(15*mm, height - 45*mm, 85*mm, 35*mm, fill=1, stroke=0)

    # Texte logo
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 20)
    c.drawString(20*mm, height - 22*mm, "VISITER")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(20*mm, height - 34*mm, "ILE-MAURICE")
    # Tilde décoratif
    c.setFont("Helvetica", 14)
    c.drawString(64*mm, height - 22*mm, "~")

    # Infos société (droite)
    c.setFillColor(DARK_TEXT)
    c.setFont("Helvetica-Bold", 7)
    c.drawRightString(width - 15*mm, height - 14*mm, COMPANY["name"])
    c.setFont("Helvetica", 7)
    for i, line in enumerate([COMPANY["address"], COMPANY["city"], COMPANY["phone"], COMPANY["website"], COMPANY["brn"]]):
        c.drawRightString(width - 15*mm, height - (20 + i * 5)*mm, line)

    # Ligne séparatrice
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.5)
    c.line(15*mm, height - 50*mm, width - 15*mm, height - 50*mm)


def _draw_doc_info(c, width, height, doc_type, numero, date_str, client):
    """Numéro de doc, date, adresse client"""
    # Doc type + numéro
    c.setFillColor(DARK_TEXT)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(15*mm, height - 62*mm, f"{doc_type} N° {numero}")

    c.setFont("Helvetica", 8)
    c.drawString(15*mm, height - 70*mm, f"DATE DE DÉLIVRANCE : {date_str}")

    # Adresse client (droite)
    c.setFont("Helvetica-Bold", 7)
    c.drawRightString(width - 15*mm, height - 62*mm, "ADRESSÉE À :")
    c.setFont("Helvetica", 8)
    lines = [client.get("nom", ""), client.get("societe", ""), client.get("adresse", ""), client.get("ville", "")]
    lines = [l for l in lines if l]
    for i, line in enumerate(lines):
        c.drawRightString(width - 15*mm, height - (68 + i * 6)*mm, line)


def _draw_objet(c, width, height, objet):
    """Ligne objet"""
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(DARK_TEXT)
    c.drawString(15*mm, height - 100*mm, f"Objet : {objet}")


def _draw_items_table(c, width, height, items):
    """Tableau des prestations"""
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors as rcolors

    table_top = height - 108*mm
    col_widths = [95*mm, 20*mm, 35*mm, 35*mm]

    # Header
    header = [["DESCRIPTION", "QTÉ", "PRIX", "TOTAL"]]
    data = header + [
        [
            item["description"],
            str(item["qte"]),
            f"{item['prix']:,.2f} €".replace(",", " "),
            f"{item['total']:,.2f} €".replace(",", " "),
        ]
        for item in items
    ]

    style = TableStyle([
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), rcolors.white),
        ("TEXTCOLOR", (0, 0), (-1, 0), DARK_TEXT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4*mm),
        ("TOPPADDING", (0, 0), (-1, 0), 3*mm),
        # Header bottom line
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, TEAL),
        # Rows
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("TEXTCOLOR", (0, 1), (-1, -1), DARK_TEXT),
        ("TOPPADDING", (0, 1), (-1, -1), 4*mm),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4*mm),
        # Row separators
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, MID_GRAY),
        # Alignements
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 0),
    ])

    t = Table(data, colWidths=col_widths, style=style)
    t.wrapOn(c, width - 30*mm, 200*mm)

    table_height = t._height
    t.drawOn(c, 15*mm, table_top - table_height)

    # Ligne finale du tableau
    y_end = table_top - table_height
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.2)
    c.line(15*mm, y_end, width - 15*mm, y_end)

    return y_end


def _draw_totals(c, width, height, montant_total, y_table_end):
    """Bloc totaux"""
    y = y_table_end - 15*mm

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(DARK_TEXT)
    c.drawRightString(width - 60*mm, y, "MONTANT TOTAL :")
    c.drawRightString(width - 15*mm, y, f"{montant_total:,.2f} €".replace(",", " "))

    y -= 7*mm
    c.setFont("Helvetica", 9)
    c.drawRightString(width - 60*mm, y, "TVA :")
    c.drawRightString(width - 15*mm, y, "0 €")

    y -= 3*mm
    c.setStrokeColor(TEAL)
    c.setLineWidth(0.8)
    c.line(width - 120*mm, y, width - 15*mm, y)

    y -= 8*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(width - 60*mm, y, "MONTANT DÛ TTC :")
    c.drawRightString(width - 15*mm, y, f"{montant_total:,.2f} €".replace(",", " "))


def _draw_footer(c, width, height):
    """Coordonnées bancaires en bas"""
    y_footer = 30*mm

    c.setStrokeColor(MID_GRAY)
    c.setLineWidth(0.5)
    c.line(15*mm, y_footer + 15*mm, width - 15*mm, y_footer + 15*mm)

    c.setFont("Helvetica", 6.5)
    c.setFillColor(DARK_TEXT)

    left_lines = [
        f"CODE B.I.C : {BANK['bic']}",
        f"CODE I.B.A.N : {BANK['iban']}",
        f"DOMICILIATION : {BANK['domiciliation']}",
    ]
    right_lines = [
        f"TITULAIRE DU COMPTE : {BANK['titulaire']}",
        f"CODE BANQUE : {BANK['code_banque']}",
        f"CODE GUICHET : {BANK['code_guichet']}",
        f"N° COMPTE : {BANK['num_compte']}     CLÉ RIB : {BANK['cle_rib']}",
    ]

    for i, line in enumerate(left_lines):
        c.drawString(15*mm, y_footer + (10 - i * 5)*mm, line)

    for i, line in enumerate(right_lines):
        c.drawRightString(width - 15*mm, y_footer + (10 - i * 4)*mm, line)
