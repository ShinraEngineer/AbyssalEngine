# FILE: fabula_charsheet/pdf_export.py
# AUTHOR: Rose (Virtual Assistant) // SCook (Computer Systems Engineering)

import io
from pypdf import PdfReader, PdfWriter

def generate_character_pdf(template_path, char_data):
    """
    Fills the Fabula Ultima template with character data.
    char_data: A dictionary containing the character's stats from Session State.
    """
    reader = PdfReader(template_path)
    writer = PdfWriter()

    # 1. Copy pages from template
    writer.append_pages_from_reader(reader)

    # 2. Map Streamlit/English variables to Italian PDF Fields
    # Note: We convert all integers to strings because PDFs expect text.
    field_mapping = {
        # --- IDENTITY ---
        "Nome": char_data.get("name", ""),
        "Genere": char_data.get("pronouns", ""), # or identity
        "Identita": char_data.get("identity", ""),
        "Tema": char_data.get("theme", ""),
        "Origine": char_data.get("origin", ""),
        "Livello": str(char_data.get("level", 1)),
        "Zenit": str(char_data.get("zenit", 0)),

        # --- ATTRIBUTES (Base Die Sizes) ---
        "DestrezzaBase": f"d{char_data.get("dex", 6)}",
        "IntuitoBase":   f"d{char_data.get("ins", 6)}",
        "VigoreBase":    f"d{char_data.get("mig", 6)}",
        "VolontaBase":   f"d{char_data.get("wil", 6)}",

        # --- STATUS ---
        "PVmax":      str(char_data.get("hp_max", 0)),
        "PVattuali":  str(char_data.get("hp_current", 0)),
        "PVcrisi":    str(int(char_data.get("hp_max", 0) / 2)), # Auto-calc crisis
        
        "PMmax":      str(char_data.get("mp_max", 0)),
        "PMattuali":  str(char_data.get("mp_current", 0)),
        
        "PImax":      str(char_data.get("ip_max", 6)),
        "PIattuali":  str(char_data.get("ip_current", 6)),
        
        "ModIniziativa": str(char_data.get("init_mod", 0)),
        "Difesa":        str(char_data.get("def", 0)),
        "DifesaMagica":  str(char_data.get("mdef", 0)),
        
        # --- EQUIPMENT ---
        "ArmaturaEquip": char_data.get("armor_name", ""),
        "Mano1Equip":    char_data.get("main_hand", ""),
        "Mano2Equip":    char_data.get("off_hand", ""),
    }

    # 3. Handle Classes (Looping through list if available)
    # Assumes char_data['classes'] is a list of dicts: [{'name': 'Elementalist', 'level': 2}, ...]
    classes = char_data.get("classes", [])
    for i, cls in enumerate(classes):
        # The PDF uses 1-based indexing (Classe1, Classe2...)
        idx = i + 1 
        if idx > 7: break # Sheet only supports 7 classes
        
        field_mapping[f"Classe{idx}"] = f"{cls.get('name', '')} (Lv {cls.get('level', '')})"
        # You would need logic here to map Class Skills to "Benefici" fields if desired

    # 4. Fill the fields
    writer.update_page_form_field_values(
        writer.pages[0], field_mapping, auto_regenerate=False
    )

    # 5. Export to Memory
    output_stream = io.BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)
    
    return output_stream
