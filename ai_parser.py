"""
Analyse d'une demande client et proposition de lignes de devis
via Claude API
"""

import anthropic
import json


def parse_demande_client(texte: str, api_key: str) -> dict:
    """
    Analyse un texte de demande client et retourne les infos structurées.

    Retourne:
    {
        "client": {"nom": "", "societe": "", "adresse": "", "ville": "", "email": ""},
        "objet": "Séjour du ...",
        "lignes": [{"description": "...", "qte": 1, "prix": 0.0}],
        "notes": "..."
    }
    """
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Tu es un assistant pour une agence de voyage à l'île Maurice : Visiter Île-Maurice (visiterilemaurice.com).

Analyse cette demande client et extrais les informations pour préparer un devis :

---
{texte}
---

Réponds UNIQUEMENT en JSON valide avec cette structure exacte :
{{
    "client": {{
        "nom": "NOM PRÉNOM en majuscules (ou vide si pas mentionné)",
        "societe": "Société si mentionnée, sinon vide",
        "adresse": "Adresse si mentionnée, sinon vide",
        "ville": "Ville et code postal si mentionnés, sinon vide",
        "email": "Email si mentionné, sinon vide"
    }},
    "objet": "Description courte du séjour (ex: Séjour du 15 au 22 mars 2026)",
    "lignes": [
        {{
            "description": "Nom exact de la prestation",
            "qte": 1,
            "prix": 0.0,
            "note": "Indication sur le prix si connu, sinon À CONFIRMER"
        }}
    ],
    "notes": "Autres informations importantes du message"
}}

Règles :
- Si le prix est mentionné dans le message, utilise-le
- Si le prix n'est pas mentionné, mets 0.0 et indique "À CONFIRMER" dans note
- Identifie toutes les prestations : hébergements, transferts, activités, excursions
- La quantité correspond au nombre de nuits pour les hébergements, ou au nombre de personnes/unités
- Sois précis sur les noms des hébergements si mentionnés"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()

    # Nettoyer si entouré de ```json
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]

    return json.loads(response_text)
