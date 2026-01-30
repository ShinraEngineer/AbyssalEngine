import io
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

def generate_character_pdf(template_path, data):
    """
    Fills the Fabula Ultima template (all pages) with dictionary data.
    """
    if not isinstance(data, dict):
        raise TypeError(f"Expected dictionary for 'data', got {type(data).__name__}: {data}")

    reader = PdfReader(template_path)
    writer = PdfWriter()

    writer.append_pages_from_reader(reader)

    # Force Copy AcroForm to ensure fields are writable
    if "/AcroForm" in reader.root_object:
        writer.root_object[NameObject("/AcroForm")] = reader.root_object["/AcroForm"]

    # 1. Base Stats Mapping
    field_mapping = {
        # Identity
        "Nome":      str(data.get("name", "")),
        "Name":      str(data.get("name", "")),
        "Character Name": str(data.get("name", "")),
        
        "Identita":  str(data.get("identity", "")),
        "Identity":  str(data.get("identity", "")),
        # Fallback: Sometimes Genere is used for Identity/Pronouns
        "Genere":    str(data.get("identity", "")), 
        
        "Tema":      str(data.get("theme", "")),
        "Theme":     str(data.get("theme", "")),
        
        "Origine":   str(data.get("origin", "")),
        "Origin":    str(data.get("origin", "")),
        
        "Livello":   str(data.get("level", "1")),
        "Level":     str(data.get("level", "1")),
        
        "Zenit":     str(data.get("zenit", "0")),
        "PuntiFabula": str(data.get("fabula_points", "0")),
        "FabulaPoints": str(data.get("fabula_points", "0")),
        
        "PuntiEsperienza": str(data.get("exp", "0")),
        "ExperiencePoints": str(data.get("exp", "0")),

        # Attributes
        "DestrezzaBase": f"d{data.get('dex', 6)}",
        "DexterityBase": f"d{data.get('dex', 6)}",
        
        "IntuitoBase":   f"d{data.get('ins', 6)}",
        "InsightBase":   f"d{data.get('ins', 6)}",
        
        "VigoreBase":    f"d{data.get('mig', 6)}",
        "MightBase":     f"d{data.get('mig', 6)}",
        
        "VolontaBase":   f"d{data.get('wil', 6)}",
        "WillpowerBase": f"d{data.get('wil', 6)}",

        # Status
        "PVmax":      str(data.get("hp_max", 0)),
        "HPmax":      str(data.get("hp_max", 0)),
        
        "PVattuali":  str(data.get("hp_current", 0)),
        "HPcurrent":  str(data.get("hp_current", 0)),
        
        "PVcrisi":    str(int(int(data.get("hp_max", 0)) / 2)),
        "HPcrisis":   str(int(int(data.get("hp_max", 0)) / 2)),
        
        "PMmax":      str(data.get("mp_max", 0)),
        "MPmax":      str(data.get("mp_max", 0)),
        
        "PMattuali":  str(data.get("mp_current", 0)),
        "MPcurrent":  str(data.get("mp_current", 0)),
        
        "PImax":      str(data.get("ip_max", 6)),
        "IPmax":      str(data.get("ip_max", 6)),
        
        "PIattuali":  str(data.get("ip_current", 6)),
        "IPcurrent":  str(data.get("ip_current", 6)),
        
        "ModIniziativa": str(data.get("init", 0)),
        "InitiativeMod": str(data.get("init", 0)),
        
        "Difesa":        str(data.get("def", 0)),
        "Defense":       str(data.get("def", 0)),
        
        "DifesaMagica":  str(data.get("mdef", 0)),
        "MagicDefense":  str(data.get("mdef", 0)),
        
        # Equipment
        "Mano1Equip":    str(data.get("main_hand", "")),
        "MainHand":      str(data.get("main_hand", "")),
        
        "Mano2Equip":    str(data.get("off_hand", "")),
        "OffHand":       str(data.get("off_hand", "")),
        
        "ArmaturaEquip": str(data.get("armor", "")),
        "Armor":         str(data.get("armor", "")),
    }

    # 2. Handle Classes & Skills
    classes = data.get("classes_info", [])
    for i, cls_info in enumerate(classes):
        idx = i + 1 
        if idx > 7: break 
        
        field_mapping[f"Classe{idx}"] = cls_info.get("name", "")
        field_mapping[f"Class{idx}"] = cls_info.get("name", "")
        
        field_mapping[f"Info{idx}"] = cls_info.get("skills", "")
        field_mapping[f"SkillInfo{idx}"] = cls_info.get("skills", "")

    # 3. Handle Spells
    spells = data.get("spells", [])
    for i, spell in enumerate(spells):
        idx = i + 1
        if idx > 20: break 
        
        field_mapping[f"ArcanaNome{idx}"] = spell.get("name", "")
        field_mapping[f"SpellName{idx}"] = spell.get("name", "")
        
        field_mapping[f"ArcanaPM{idx}"] = spell.get("mp", "")
        field_mapping[f"SpellMP{idx}"] = spell.get("mp", "")
        
        field_mapping[f"ArcanaBersagli{idx}"] = spell.get("target", "")
        field_mapping[f"SpellTarget{idx}"] = spell.get("target", "")
        
        field_mapping[f"ArcanaDurata{idx}"] = spell.get("duration", "")
        field_mapping[f"SpellDuration{idx}"] = spell.get("duration", "")
        
        field_mapping[f"ArcanaNote{idx}"] = spell.get("effect", "")
        field_mapping[f"SpellEffect{idx}"] = spell.get("effect", "")

    # 4. Handle Checkboxes (Proficiencies)
    # Using standard Italian template names based on Fabula Ultima community sheets
    prof_map = {
        "prof_armor": ["Armature", "ArmatureMarziali", "MartialArmor", "ArmorProficiency", "Check Box 1"],
        "prof_shield": ["Scudi", "ScudiMarziali", "MartialShields", "ShieldProficiency", "Check Box 2"],
        "prof_melee": ["Marziali", "ArmiMarziali", "MartialMelee", "MeleeProficiency", "Check Box 3"],
        "prof_ranged": ["Distanza", "ArmiDistanza", "MartialRanged", "RangedProficiency", "Check Box 4"]
    }

    # FIX: Apply fields to ALL pages
    for page in writer.pages:
        writer.update_page_form_field_values(
            page, field_mapping, auto_regenerate=False
        )
        
        # Apply Checkboxes
        for data_key, pdf_key_list in prof_map.items():
            if data.get(data_key, False):
                for pdf_key in pdf_key_list:
                    # Try setting to /Yes (Standard PDF ON value)
                    writer.update_page_form_field_values(page, {pdf_key: NameObject("/Yes")})

    output_stream = io.BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)
    
    return output_stream
