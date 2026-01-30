import io
from pypdf import PdfReader, PdfWriter

def generate_character_pdf(template_path, data):
    """
    Fills the Fabula Ultima template with dictionary data.
    """
    # SAFETY CHECK: Ensure data is actually a dictionary
    if not isinstance(data, dict):
        raise TypeError(f"Expected dictionary for 'data', got {type(data).__name__}: {data}")

    reader = PdfReader(template_path)
    writer = PdfWriter()

    # 1. Copy pages from template
    writer.append_pages_from_reader(reader)

    # 2. Map Dictionary Keys to PDF Field Names (Italian)
    # We use str() on everything to ensure pypdf doesn't crash on numbers
    field_mapping = {
        # --- IDENTITY ---
        "Nome":      str(data.get("name", "")),
        "Identita":  str(data.get("identity", "")),
        "Tema":      str(data.get("theme", "")),
        "Origine":   str(data.get("origin", "")),
        "Livello":   str(data.get("level", "1")),
        "Zenit":     str(data.get("zenit", "0")),
        "PuntiFabula": str(data.get("fabula_points", "0")),
        "PuntiEsperienza": str(data.get("exp", "0")),

        # --- ATTRIBUTES (Base Die Sizes) ---
        "DestrezzaBase": f"d{data.get('dex', 6)}",
        "IntuitoBase":   f"d{data.get('ins', 6)}",
        "VigoreBase":    f"d{data.get('mig', 6)}",
        "VolontaBase":   f"d{data.get('wil', 6)}",

        # --- STATUS ---
        "PVmax":      str(data.get("hp_max", 0)),
        "PVattuali":  str(data.get("hp_current", 0)),
        "PVcrisi":    str(int(int(data.get("hp_max", 0)) / 2)),
        
        "PMmax":      str(data.get("mp_max", 0)),
        "PMattuali":  str(data.get("mp_current", 0)),
        
        "PImax":      str(data.get("ip_max", 6)),
        "PIattuali":  str(data.get("ip_current", 6)),
        
        "ModIniziativa": str(data.get("init", 0)),
        "Difesa":        str(data.get("def", 0)),
        "DifesaMagica":  str(data.get("mdef", 0)),
        
        # --- EQUIPMENT ---
        "Mano1Equip":    str(data.get("main_hand", "")),
        "Mano2Equip":    str(data.get("off_hand", "")),
        "ArmaturaEquip": str(data.get("armor", "")),
    }

    # 3. Handle Classes (List of strings)
    # data['classes'] should be a list like ["Elementalist (Lv 2)", "Tinkerer (Lv 1)"]
    classes = data.get("classes", [])
    for i, cls_str in enumerate(classes):
        idx = i + 1 
        if idx > 7: break 
        field_mapping[f"Classe{idx}"] = str(cls_str)

    # 4. Fill the fields
    writer.update_page_form_field_values(
        writer.pages[0], field_mapping, auto_regenerate=False
    )

    # 5. Export to Memory
    output_stream = io.BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)
    
    return output_stream
