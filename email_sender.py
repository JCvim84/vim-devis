"""
Envoi d'email avec pièce jointe PDF via Gmail SMTP
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "email_config.json")


def send_devis_email(
    to_email: str,
    client_nom: str,
    objet: str,
    pdf_path: str,
    gmail_user: str,
    gmail_password: str,
    message_perso: str = "",
):
    """
    Envoie le devis PDF par email Gmail.
    gmail_password = mot de passe d'application Gmail (16 caractères)
    """
    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = to_email
    msg["Subject"] = f"Votre devis - Visiter Île Maurice | {objet}"

    body = f"""Bonjour {client_nom},

Veuillez trouver ci-joint votre devis pour : {objet}

{message_perso if message_perso else ""}

N'hésitez pas à nous contacter pour toute question.

Cordialement,
L'équipe Visiter Île-Maurice
+230 5509 7142
www.visiterilemaurice.com
"""

    msg.attach(MIMEText(body, "plain", "utf-8"))

    # Pièce jointe PDF
    pdf_filename = os.path.basename(pdf_path)
    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())

    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        "attachment",
        filename=("utf-8", "", pdf_filename)
    )
    part.add_header("Content-Type", "application/pdf", name=pdf_filename)
    msg.attach(part)

    # Envoi
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to_email, msg.as_string())

    return True
