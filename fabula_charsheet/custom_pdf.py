import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

def create_custom_sheet(character, loc):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # Custom Styles
    title_style = styles['Title']
    h1_style = styles['Heading1']
    h2_style = styles['Heading2']
    normal_style = styles['Normal']
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=8, leading=10)

    # --- HEADER ---
    story.append(Paragraph(f"{character.name}", title_style))
    story.append(Paragraph(f"<b>Identity:</b> {character.identity} | <b>Theme:</b> {character.theme} | <b>Origin:</b> {character.origin}", normal_style))
    story.append(Paragraph(f"<b>Level:</b> {character.level} | <b>Fabula Points:</b> 0 | <b>Zenit:</b> {character.inventory.zenit}", normal_style))
    story.append(Spacer(1, 0.5*cm))

    # --- ATTRIBUTES & STATS ---
    # Create a nice grid for stats
    data_stats = [
        ["Attribute", "Base", "Current", "Status Effect"],
        ["DEXTERITY", f"d{character.dexterity.base}", f"d{character.dexterity.current}", "☐ Slow  ☐ Enraged"],
        ["INSIGHT",   f"d{character.insight.base}",   f"d{character.insight.current}",   "☐ Dazed  ☐ Poisoned"],
        ["MIGHT",     f"d{character.might.base}",     f"d{character.might.current}",     "☐ Weak   ☐ Shaken"],
        ["WILLPOWER", f"d{character.willpower.base}", f"d{character.willpower.current}", ""]
    ]
    
    t_stats = Table(data_stats, colWidths=[3*cm, 2*cm, 2*cm, 5*cm])
    t_stats.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))
    story.append(t_stats)
    story.append(Spacer(1, 0.5*cm))

    # --- DERIVED STATS ---
    # Calculate derived stats dynamically just in case
    hp_max = character.might.base * 5 + character.level + getattr(character, "hp_bonus", 0)
    mp_max = character.willpower.base * 5 + character.level + getattr(character, "mp_bonus", 0)
    ip_max = 6 + getattr(character, "ip_bonus", 0)
    
    # Init logic (simple extraction)
    raw_init = str(getattr(character, "initiative", lambda: 0)())
    
    data_derived = [
        [f"HP: {hp_max} / {hp_max/2}", f"MP: {mp_max}", f"IP: {ip_max}"],
        [f"Defense: {getattr(character, 'defense', lambda: 0)()}", f"M.Defense: {getattr(character, 'magic_defense', lambda: 0)()}", f"Initiative: {raw_init}"]
    ]
    t_derived = Table(data_derived, colWidths=[5*cm, 5*cm, 5*cm])
    t_derived.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_derived)
    story.append(Spacer(1, 0.5*cm))

    # --- EQUIPMENT ---
    story.append(Paragraph("Equipment", h2_style))
    
    # Helper to get name safely
    def get_name(item):
        if not item: return "None"
        if hasattr(item, "localized_name"):
            return str(item.localized_name(loc)).replace("_", " ").title()
        return str(item.name).replace("_", " ").title()

    eq = character.inventory.equipped
    eq_data = [
        ["Slot", "Item Name"],
        ["Main Hand", get_name(eq.main_hand)],
        ["Off Hand", get_name(eq.off_hand)],
        ["Armor", get_name(eq.armor)],
        ["Accessory", get_name(eq.accessory)]
    ]
    t_eq = Table(eq_data, colWidths=[3*cm, 12*cm])
    t_eq.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))
    story.append(t_eq)
    story.append(Spacer(1, 0.5*cm))

    # --- CLASSES & SKILLS ---
    story.append(Paragraph("Classes & Skills", h2_style))
    
    for c in character.classes:
        c_name = str(c.name.localized_name(loc)) if hasattr(c.name, "localized_name") else str(c.name)
        story.append(Paragraph(f"<b>{c_name}</b> (Lv {c.class_level()})", h1_style))
        
        # Skills
        active_skills = [s for s in c.skills if s.current_level > 0]
        if not active_skills:
            story.append(Paragraph("No skills learned.", normal_style))
        
        for skill in active_skills:
            s_name = skill.name
            if hasattr(skill, "localized_name"): s_name = skill.localized_name(loc)
            
            # Clean Description
            raw_desc = ""
            if hasattr(skill, "localized_description"):
                try: raw_desc = skill.localized_description(loc)
                except: pass
            if not raw_desc:
                for attr in ["description", "text", "effect"]:
                    if getattr(skill, attr, None):
                        raw_desc = str(getattr(skill, attr))
                        break
            
            # Clean HTML
            clean_desc = raw_desc.replace("**", "").replace("__", "").replace("&nbsp;", " ").replace("【", "[").replace("】", "]")
            
            story.append(KeepTogether([
                Paragraph(f"<b>• {s_name} (Lv {skill.current_level})</b>", normal_style),
                Paragraph(clean_desc, small_style),
                Spacer(1, 0.2*cm)
            ]))
        story.append(Spacer(1, 0.2*cm))

    # --- SPELLS ---
    story.append(Paragraph("Spells", h2_style))
    spells_exist = False
    for class_key, spell_group in character.spells.items():
        if not spell_group: continue
        spells_exist = True
        
        c_name = str(class_key.localized_name(loc)) if hasattr(class_key, "localized_name") else str(class_key)
        story.append(Paragraph(f"<b>{c_name} Spells</b>", h1_style))
        
        spell_data = [["Name", "MP", "Target", "Duration", "Effect"]]
        
        for spell in spell_group:
            s_name = getattr(spell, "name", "Unknown")
            if hasattr(s_name, "localized_name"): s_name = s_name.localized_name(loc)
            
            # Get MP
            s_mp = "0"
            for attr in ["mp", "cost", "mp_cost"]:
                if getattr(spell, attr, None): s_mp = str(getattr(spell, attr)); break
            
            s_target = str(getattr(spell, "target", "")).replace("_", " ").title()
            s_duration = str(getattr(spell, "duration", "")).replace("_", " ").title()
            
            # Desc
            raw_desc = ""
            if hasattr(spell, "localized_description"):
                try: raw_desc = spell.localized_description(loc)
                except: pass
            if not raw_desc:
                for attr in ["description", "text", "effect"]:
                    if getattr(spell, attr, None): raw_desc = str(getattr(spell, attr)); break
            
            clean_desc = raw_desc.replace("**", "").replace("__", "").replace("&nbsp;", " ").replace("【", "[").replace("】", "]")
            
            spell_data.append([
                Paragraph(f"<b>{s_name}</b>", small_style),
                Paragraph(s_mp, small_style),
                Paragraph(s_target, small_style),
                Paragraph(s_duration, small_style),
                Paragraph(clean_desc, small_style)
            ])
            
        t_spells = Table(spell_data, colWidths=[3*cm, 1.5*cm, 2.5*cm, 2.5*cm, 7.5*cm])
        t_spells.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t_spells)
        story.append(Spacer(1, 0.5*cm))

    if not spells_exist:
        story.append(Paragraph("No spells learned.", normal_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
