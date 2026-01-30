import io
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

def generate_character_pdf(template_path, data):
    """
    Fills the Fabula Ultima template with dictionary data.
    """
    if not isinstance(data, dict):
        raise TypeError(f"Expected dictionary for 'data', got {type(data).__name__}: {data}")

    reader = PdfReader(template_path)
    writer = PdfWriter()

    writer.append_pages_from_reader(reader)

    # --- FIX: FORCE COPY ACROFORM DICTIONARY ---
    if "/AcroForm" in reader.root_object:
        writer.root_object[NameObject("/AcroForm")] = reader.root_object["/AcroForm"]
    else:
        print(f"WARNING: The file at {template_path} has no Form Fields (AcroForm). Returning flat PDF.")
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream

    # 1. Base Stats Mapping
    field_mapping = {
        # Identity
        "Nome":      str(data.get("name", "")),
        "Identita":  str(data.get("identity", "")),
        "Tema":      str(data.get("theme", "")),
        "Origine":   str(data.get("origin", "")),
        "Livello":   str(data.get("level", "1")),
        "Zenit":     str(data.get("zenit", "0")),
        "PuntiFabula": str(data.get("fabula_points", "0")),
        "PuntiEsperienza": str(data.get("exp", "0")),

        # Attributes
        "DestrezzaBase": f"d{data.get('dex', 6)}",
        "IntuitoBase":   f"d{data.get('ins', 6)}",
        "VigoreBase":    f"d{data.get('mig', 6)}",
        "VolontaBase":   f"d{data.get('wil', 6)}",

        # Status
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
        
        # Equipment
        "Mano1Equip":    str(data.get("main_hand", "")),
        "Mano2Equip":    str(data.get("off_hand", "")),
        "ArmaturaEquip": str(data.get("armor", "")),
    }

    # 2. Handle Classes & Skills (Looping)
    # data['classes_info'] is a list of dicts: {'name': 'Guardian (Lv 1)', 'benefits': '...', 'skills': '...'}
    classes = data.get("classes_info", [])
    for i, cls_info in enumerate(classes):
        idx = i + 1 
        if idx > 7: break # Sheet limit
        
        field_mapping[f"Classe{idx}"] = cls_info.get("name", "")
        field_mapping[f"Benefici{idx}"] = cls_info.get("benefits", "")
        field_mapping[f"Info{idx}"] = cls_info.get("skills", "")

    # 3. Handle Spells (Looping)
    # data['spells'] is a list of dicts
    spells = data.get("spells", [])
    for i, spell in enumerate(spells):
        idx = i + 1
        if idx > 20: break # Sheet limit approx 20 slots
        
        field_mapping[f"ArcanaNome{idx}"] = spell.get("name", "")
        field_mapping[f"ArcanaPM{idx}"] = spell.get("mp", "")
        field_mapping[f"ArcanaBersagli{idx}"] = spell.get("target", "")
        field_mapping[f"ArcanaDurata{idx}"] = spell.get("duration", "")
        field_mapping[f"ArcanaNote{idx}"] = spell.get("effect", "")

    # 4. Fill the fields
    writer.update_page_form_field_values(
        writer.pages[0], field_mapping, auto_regenerate=False
    )

    output_stream = io.BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)
    
    return output_stream
Phase 2: Update the View (view.py)
Now we update the UI logic to gather the skills/spells data and format the strings correctly before sending them to the exporter.

Run this command:

Bash
vim fabula_charsheet/pages/character_view/view.py
Find the if st.button("📄 Generate PDF Character Sheet"): block (at the bottom) and replace ONLY that if block with this updated logic:

Python
        if st.button("📄 Generate PDF Character Sheet"):
            # --- PREPARE DATA HELPERS ---
            
            # 1. Clean Equipment Names (Replace underscores and Title Case)
            def clean_name(item):
                if not item: return ""
                # If it's an object with a name attribute
                raw_name = item.name if hasattr(item, "name") else str(item)
                return raw_name.replace("_", " ").title()

            eq = controller.character.inventory.equipped
            main_hand_name = clean_name(eq.main_hand)
            off_hand_name = clean_name(eq.off_hand)
            armor_name = clean_name(eq.armor)

            # 2. Fix Initiative (Extract modifier only)
            # Assumes format like "d8 + d8 - 2". We split by spaces and look for the last part.
            raw_init = controller.initiative() # e.g., "d8 + d8 -2"
            init_mod = "0"
            if "-" in raw_init:
                init_mod = "-" + raw_init.split("-")[-1].strip()
            elif "+" in raw_init and raw_init.split("+")[-1].strip().isdigit():
                init_mod = "+" + raw_init.split("+")[-1].strip()
            else:
                init_mod = "0" # Default if just dice

            # 3. Gather Classes & Skills
            classes_info_list = []
            for c in controller.character.classes:
                # Format: "Guardian (Lv 2)"
                c_name_str = c.name.localized_name(loc)
                full_name = f"{c_name_str} (Lv {c.class_level()})"
                
                # Gather active skills for this class into one text block
                active_skills = [s for s in c.skills if s.current_level > 0]
                skills_text = ""
                for skill in active_skills:
                    s_name = skill.name # Or localized name if available
                    # Formatting: "SkillName (Lv X): Description"
                    skills_text += f"• {s_name.replace('_', ' ').title()} (Lv {skill.current_level})\n"
                
                classes_info_list.append({
                    "name": full_name,
                    "benefits": getattr(c, "free_benefits", ""), # Placeholder if model has this
                    "skills": skills_text
                })

            # 4. Gather Spells
            spells_list = []
            # 'controller.character.spells' is a Dict[ClassName, List[Spell]]
            for class_key, spell_group in controller.character.spells.items():
                for spell in spell_group:
                    spells_list.append({
                        "name": spell.name.replace("_", " ").title(),
                        "mp": str(spell.mp),
                        "target": spell.target,
                        "duration": spell.duration,
                        "effect": spell.description # Or spell.effect
                    })

            # --- BUILD PDF DATA ---
            pdf_data = {
                "name": controller.character.name,
                "identity": controller.character.identity,
                "theme": controller.character.theme,
                "origin": controller.character.origin,
                "level": controller.character.level,
                "fabula_points": 0,
                "zenit": controller.character.inventory.zenit,
                "exp": 0, 
                
                # Attributes
                "dex": controller.character.dexterity.base,
                "ins": controller.character.insight.base,
                "mig": controller.character.might.base,
                "wil": controller.character.willpower.base,
                
                # Stats
                "hp_current": controller.current_hp(),
                "hp_max": controller.max_hp(),
                "mp_current": controller.current_mp(),
                "mp_max": controller.max_mp(),
                "ip_current": controller.current_ip(),
                "ip_max": controller.max_ip(),
                
                # Corrections
                "init": init_mod,          # Fixed Initiative
                "def": controller.defense(),
                "mdef": controller.magic_defense(),
                
                # Equipment (Cleaned)
                "main_hand": main_hand_name, 
                "off_hand": off_hand_name,
                "armor": armor_name,
                
                # Lists
                "classes_info": classes_info_list, # Now contains skills text
                "spells": spells_list
            }

            try:
                pdf_file = pdf_export.generate_character_pdf("fabula_charsheet/template_sheet.pdf", pdf_data)
                
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_file,
                    file_name=f"{controller.character.name}_Sheet.pdf",
                    mime="application/pdf"
                )
                st.success("PDF Generated! Click above to download.")
                
            except FileNotFoundError:
                st.error("Error: 'template_sheet.pdf' not found.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
