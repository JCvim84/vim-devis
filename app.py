"""
Agent Devis - Visiter Île-Maurice
Interface Streamlit pour créer et envoyer des devis PDF
"""

import streamlit as st
import os
import json
import base64
from datetime import datetime
from pdf_generator import generate_pdf, OUTPUT_DIR
from email_sender import send_devis_email
from google_drive import upload_pdf

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
IS_CLOUD = not os.path.exists(CONFIG_FILE) and hasattr(st, "secrets")

# ─────────────────────────────────────────────
# Config — local ou Streamlit Cloud (secrets)
# ─────────────────────────────────────────────

def load_config():
    """Charge la config depuis fichier local ou st.secrets (cloud)."""
    if IS_CLOUD:
        try:
            return {
                "gmail_user": st.secrets.get("gmail_user", ""),
                "gmail_password": st.secrets.get("gmail_password", ""),
                "gdrive_folder_id": st.secrets.get("gdrive_folder_id", ""),
                "gdrive_credentials": dict(st.secrets.get("gdrive_credentials", {})),
            }
        except Exception:
            return {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"gmail_user": "", "gmail_password": "", "gdrive_folder_id": "", "gdrive_credentials": {}}


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)


# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Devis - Visiter Île-Maurice",
    page_icon="🌴",
    layout="wide",
)

# CSS
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .main-title { color: #3AAFA9; font-size: 2rem; font-weight: bold; margin-bottom: 0; }
    .sub-title { color: #666; font-size: 0.9rem; margin-top: 0; }
    .section-header {
        background: #3AAFA9; color: white;
        padding: 8px 12px; border-radius: 6px;
        font-weight: bold; margin: 10px 0;
    }
    div[data-testid="stNumberInput"] label { font-size: 0.85rem; }
    div[data-testid="stTextInput"] label { font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar - Config email
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    config = load_config()

    if not IS_CLOUD:
        with st.expander("📧 Paramètres Gmail", expanded=not config.get("gmail_user")):
            gmail_user = st.text_input("Email Gmail", value=config.get("gmail_user", ""), placeholder="votre@gmail.com")
            gmail_password = st.text_input(
                "Mot de passe d'application",
                value=config.get("gmail_password", ""),
                type="password",
                help="Générer dans Gmail > Sécurité > Mots de passe d'application (16 caractères)"
            )
            gdrive_folder_id = st.text_input(
                "ID dossier Google Drive",
                value=config.get("gdrive_folder_id", ""),
                help="L'ID dans l'URL du dossier Drive : drive.google.com/drive/folders/[ID]"
            )
            if st.button("💾 Sauvegarder"):
                save_config({
                    "gmail_user": gmail_user,
                    "gmail_password": gmail_password,
                    "gdrive_folder_id": gdrive_folder_id,
                    "gdrive_credentials": config.get("gdrive_credentials", {}),
                })
                st.success("Sauvegardé !")
    else:
        st.info("🔒 Config chargée depuis les secrets Streamlit Cloud")

    st.markdown("---")
    st.markdown("### 📁 Devis générés")
    if os.path.exists(OUTPUT_DIR):
        files = sorted(os.listdir(OUTPUT_DIR), reverse=True)[:10]
        for f in files:
            filepath = os.path.join(OUTPUT_DIR, f)
            with open(filepath, "rb") as fh:
                b64 = base64.b64encode(fh.read()).decode()
            st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="{f}">📄 {f}</a>', unsafe_allow_html=True)
    else:
        st.caption("Aucun devis encore généré")

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────

col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.markdown("""
    <div style="background:#3AAFA9; padding:15px 20px; border-radius:8px; text-align:center; margin-top:10px;">
        <div style="color:white; font-size:1.1rem; font-weight:300; letter-spacing:4px;">VISITER</div>
        <div style="color:white; font-size:1rem; font-weight:bold; letter-spacing:2px;">ILE-MAURICE</div>
    </div>
    """, unsafe_allow_html=True)
with col_title:
    st.markdown('<p class="main-title">Créer un Devis</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Local Explorers Ventures Ltd.</p>', unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# Formulaire
# ─────────────────────────────────────────────

col1, col2 = st.columns(2)

# ── Infos client ──────────────────────────────
with col1:
    st.markdown('<div class="section-header">👤 Informations Client</div>', unsafe_allow_html=True)

    client_nom = st.text_input("Nom complet *", placeholder="RÉMI BENSABATH")
    client_societe = st.text_input("Société (optionnel)", placeholder="HOLDING GROUPE SABA")
    client_adresse = st.text_input("Adresse *", placeholder="7 RUE DE LA PRÉFECTURE")
    client_ville = st.text_input("Ville & Code postal *", placeholder="06300 NICE")
    client_email = st.text_input("Email client *", placeholder="client@email.com")

# ── Détails devis ─────────────────────────────
with col2:
    st.markdown('<div class="section-header">📋 Détails du Devis</div>', unsafe_allow_html=True)

    doc_type = st.selectbox("Type de document", ["DEVIS", "FACTURE"])
    objet = st.text_input("Objet *", placeholder="Séjour du 21 au 28 février 2026")

    col_d, col_n = st.columns(2)
    with col_d:
        date_devis = st.date_input("Date", value=datetime.today())
    with col_n:
        numero_auto = st.checkbox("Numérotation auto", value=True)
        if not numero_auto:
            numero_manuel = st.text_input("Numéro", placeholder="0001")

# ── Prestations ───────────────────────────────
st.markdown('<div class="section-header">🏝️ Prestations</div>', unsafe_allow_html=True)

if "lignes" not in st.session_state:
    st.session_state.lignes = [{"description": "", "qte": 1, "prix": 0.0}]


def add_item():
    st.session_state.lignes.append({"description": "", "qte": 1, "prix": 0.0})


def remove_item(idx):
    if len(st.session_state.lignes) > 1:
        st.session_state.lignes.pop(idx)


# Header colonnes
h1, h2, h3, h4, h5 = st.columns([5, 1.2, 2, 2, 0.6])
h1.markdown("**Description**")
h2.markdown("**Qté**")
h3.markdown("**Prix unitaire (€)**")
h4.markdown("**Total**")

total_general = 0.0

for idx, item in enumerate(st.session_state.lignes):
    c1, c2, c3, c4, c5 = st.columns([5, 1.2, 2, 2, 0.6])

    with c1:
        item["description"] = st.text_input(
            f"desc_{idx}", value=item["description"],
            label_visibility="collapsed",
            placeholder="Ex: O'Biches - Deluxe Apartment by Horizon Holidays",
            key=f"desc_{idx}"
        )
    with c2:
        item["qte"] = st.number_input(
            f"qte_{idx}", value=item["qte"], min_value=1, step=1,
            label_visibility="collapsed", key=f"qte_{idx}"
        )
    with c3:
        item["prix"] = st.number_input(
            f"prix_{idx}", value=float(item["prix"]), min_value=0.0, step=10.0, format="%.2f",
            label_visibility="collapsed", key=f"prix_{idx}"
        )
    with c4:
        total_item = round(item["qte"] * item["prix"], 2)
        total_general += total_item
        st.markdown(f"<div style='padding-top:8px; font-weight:bold;'>{total_item:,.2f} €</div>".replace(",", " "), unsafe_allow_html=True)
    with c5:
        if st.button("🗑️", key=f"del_{idx}", help="Supprimer"):
            remove_item(idx)
            st.rerun()

st.button("➕ Ajouter une prestation", on_click=add_item)

# Total
st.markdown(f"""
<div style="text-align:right; margin-top:15px; padding:12px; background:#e8f7f6; border-radius:8px; border-left:4px solid #3AAFA9;">
    <span style="font-size:1.1rem; font-weight:bold; color:#2B2B2B;">
        TOTAL TTC : {total_general:,.2f} €
    </span>
</div>
""".replace(",", " "), unsafe_allow_html=True)

# ── Message email ─────────────────────────────
st.markdown('<div class="section-header">✉️ Email d\'accompagnement</div>', unsafe_allow_html=True)
message_perso = st.text_area(
    "Message personnalisé (optionnel)",
    placeholder="Comme convenu lors de notre échange, voici votre devis...",
    height=100
)
envoyer_email = st.checkbox("Envoyer par email au client", value=True)

# ─────────────────────────────────────────────
# Génération
# ─────────────────────────────────────────────
st.markdown("---")

col_gen, col_info = st.columns([2, 3])

with col_gen:
    generate_btn = st.button("🖨️ Générer le PDF", type="primary", use_container_width=True)

with col_info:
    if not client_nom or not client_adresse or not client_ville or not objet:
        st.warning("Remplis les champs obligatoires (*) pour générer le devis.")
    elif envoyer_email and not client_email:
        st.warning("Renseigne l'email du client pour l'envoi.")

if generate_btn:
    # Validation
    errors = []
    if not client_nom:
        errors.append("Nom client requis")
    if not client_adresse:
        errors.append("Adresse client requise")
    if not client_ville:
        errors.append("Ville/CP client requis")
    if not objet:
        errors.append("Objet requis")
    if envoyer_email and not client_email:
        errors.append("Email client requis pour l'envoi")
    if envoyer_email and not config.get("gmail_user"):
        errors.append("Configure ton email Gmail dans la barre latérale")

    valid_items = [i for i in st.session_state.lignes if i["description"].strip() and i["prix"] > 0]
    if not valid_items:
        errors.append("Ajoute au moins une prestation avec description et prix")

    if errors:
        for e in errors:
            st.error(f"❌ {e}")
    else:
        with st.spinner("Génération du PDF..."):
            client = {
                "nom": client_nom.upper(),
                "societe": client_societe.upper() if client_societe else "",
                "adresse": client_adresse.upper(),
                "ville": client_ville.upper(),
            }

            numero = None if numero_auto else numero_manuel

            try:
                pdf_path = generate_pdf(
                    client=client,
                    items=valid_items,
                    objet=objet,
                    doc_type=doc_type,
                    numero=numero,
                )
                st.success(f"✅ PDF généré : {os.path.basename(pdf_path)}")

                # Téléchargement
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                st.download_button(
                    label="⬇️ Télécharger le PDF",
                    data=pdf_bytes,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    use_container_width=True,
                )

                # Sauvegarde Google Drive
                cfg = load_config()
                gdrive_creds = cfg.get("gdrive_credentials", {})
                gdrive_folder = cfg.get("gdrive_folder_id", "")
                if gdrive_creds and gdrive_folder:
                    with st.spinner("Sauvegarde sur Google Drive..."):
                        drive_link = upload_pdf(pdf_path, gdrive_folder, gdrive_creds)
                    st.success(f"✅ Sauvegardé sur Drive")
                    if drive_link:
                        st.markdown(f"[📂 Voir sur Google Drive]({drive_link})")

                # Envoi email
                if envoyer_email:
                    with st.spinner("Envoi de l'email..."):
                        send_devis_email(
                            to_email=client_email,
                            client_nom=client_nom,
                            objet=objet,
                            pdf_path=pdf_path,
                            gmail_user=cfg["gmail_user"],
                            gmail_password=cfg["gmail_password"],
                            message_perso=message_perso,
                        )
                    st.success(f"✅ Email envoyé à {client_email}")

            except Exception as e:
                st.error(f"❌ Erreur : {e}")
                st.exception(e)
