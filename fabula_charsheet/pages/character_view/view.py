import sys
import os
# Ensure we can import modules from the root if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import streamlit as st
import pdf_export
import config

from data.models import Status, AttributeName, Weapon, GripType, WeaponCategory, \
    WeaponRange, ClassName, LocNamespace, HeroicSkillName
from pages.controller import CharacterController
from pages.utils import WeaponTableWriter, ArmorTableWriter, SkillTableWriter, SpellTableWriter, DanceTableWriter, InventionTableWriter, \
    AccessoryTableWriter, ItemTableWriter, TherioformTableWriter, ShieldTableWriter, BondTableWriter, ArcanumTableWriter, \
    show_martial, set_view_state, get_avatar_path, avatar_update, level_up, add_chimerist_spell, \
    remove_chimerist_spell, add_item, remove_item, unequip_item, add_heroic_skill, add_spell, add_bond, remove_bond, \
    increase_attribute, add_therioform, add_dance, add_arcanum, manifest_therioform, display_equipped_item, add_invention, \
    colored_attr
from pages.character_view.view_state import ViewState

# --- HARDCODED PROFICIENCIES (Since not in model) ---
CLASS_PROFICIENCIES = {
    "Guardian": ["armor", "shield", "melee"],
    "Dark Knight": ["armor", "melee"],
    "Weaponmaster": ["melee", "shield"],
    "Sharpshooter": ["ranged"],
    "Commander": ["melee", "shield"],
    "Fury": ["melee"],
    "Tinkerer": [],
    "Lorist": [],
    "Entropist": [],
    "Spiritist": [],
    "Elementalist": [],
    "Wayfarer": [],
    "Rogue": [],
    "Dancer": [],
    "Symbolist": [],
    "Mutant": [],
    "Chimerist": [],
    "Orator": [],
    "Arcanist": []
}

def build(controller: CharacterController):
    st.set_page_config(layout="wide")
    loc: LocNamespace = st.session_state.localizator.get(st.session_state.language)

    @st.dialog(loc.page_view_avatar_update_dialog_title)
    def avatar_update_dialog(controller: CharacterController, loc: LocNamespace):
        avatar_update(controller, loc)

    @st.dialog(loc.page_view_level_up_dialog_title, width="large")
    def level_up_dialog(controller: CharacterController, loc: LocNamespace):
        level_up(controller, loc)

    @st.dialog(loc.page_view_add_heroic_skill_dialog_title, width="large")
    def add_heroic_skill_dialog(controller: CharacterController, loc: LocNamespace):
        add_heroic_skill(controller, loc)

    @st.dialog(loc.page_view_add_chimerist_spell_dialog_title, width="large")
    def add_chimerist_spell_dialog(controller: CharacterController, loc: LocNamespace):
        add_chimerist_spell(controller, loc)

    @st.dialog(loc.page_view_add_spell_dialog_title, width="large")
    def add_spell_dialog(
            controller: CharacterController,
            class_name: ClassName,
            loc: LocNamespace
    ):
        add_spell(controller, class_name, loc)

    @st.dialog(loc.page_view_remove_chimerist_spell_dialog_title, width="large")
    def remove_chimerist_spell_dialog(controller: CharacterController, loc: LocNamespace):
        remove_chimerist_spell(controller, loc)

    @st.dialog(loc.page_view_add_item_dialog_title, width="large")
    def add_item_dialog(controller: CharacterController, loc: LocNamespace):
        add_item(controller, loc)

    @st.dialog(loc.page_view_remove_item_dialog_title, width="large")
    def remove_item_dialog(controller: CharacterController, loc: LocNamespace):
        remove_item(controller, loc)

    @st.dialog(loc.page_view_add_bond_dialog_title, width="large")
    def add_bond_dialog(controller: CharacterController, loc: LocNamespace):
        add_bond(controller, loc)

    @st.dialog(loc.page_view_remove_bond_dialog_title, width="large")
    def remove_bond_dialog(controller: CharacterController, loc: LocNamespace):
        remove_bond(controller, loc)

    @st.dialog(loc.page_view_increase_attribute_dialog_title, width="small")
    def increase_attribute_dialog(controller: CharacterController, loc: LocNamespace):
        increase_attribute(controller, loc)

    @st.dialog(loc.page_view_add_therioform_dialog_title, width="large")
    def add_therioform_dialog(controller: CharacterController, loc: LocNamespace):
        add_therioform(controller, loc)

    @st.dialog(loc.page_view_add_dance_dialog_title, width="large")
    def add_dance_dialog(controller: CharacterController, loc: LocNamespace):
        add_dance(controller, loc)

    @st.dialog(loc.page_view_manifest_therioform_dialog_title, width="large")
    def manifest_therioform_dialog(controller: CharacterController, loc: LocNamespace):
        manifest_therioform(controller, loc)

    @st.dialog(loc.page_view_add_arcanum_dialog_title, width="large")
    def add_arcanum_dialog(controller: CharacterController, loc: LocNamespace):
        add_arcanum(controller, loc)

    @st.dialog(loc.page_view_add_invention_dialog_title, width="large")
    def add_invention_dialog(controller: CharacterController, loc: LocNamespace):
        add_invention(controller, loc)

    st.title(f"{controller.character.name}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        loc.page_view_tab_overview,
        loc.page_view_tab_skills,
        loc.page_view_tab_spells,
        loc.page_view_tab_equipment,
        loc.page_view_tab_special,
    ])

    # Overview
    with tab1:
        base_col, points_col, attributes_col = st.columns([0.35, 0.4, 0.25], gap="medium")
        with base_col:
            col1, col2 = st.columns(2)
            with col1:
                avatar_path = get_avatar_path(controller.character.id)
                if avatar_path:
                    st.image(avatar_path, use_container_width=True)
                else:
                    st.image(config.default_avatar_path, width=150)
                if st.button(loc.update_avatar_button):
                    avatar_update_dialog(controller, loc)
            with col2:
                st.write(loc.page_view_identity_origin.format(
                    identity=controller.character.identity,
                    origin=controller.character.origin
                ))
                st.markdown(f"**{loc.page_view_level}:** {controller.character.level}")
                st.markdown(f"**{loc.page_view_theme}:** {controller.character.theme}")
                st.number_input(loc.page_view_fabula_points, min_value=0)
                if controller.current_hp() <= controller.crisis_value():
                    st.write(f":red[{loc.page_view_crisis_text}]")
                else:
                    st.write("")
                if st.button(loc.page_view_level_up_button):
                    level_up_dialog(controller, loc)
                if controller.can_add_heroic_skill():
                    if st.button(loc.heroic_skill_button):
                        add_heroic_skill_dialog(controller, loc)
                if controller.can_increase_attribute():
                    if st.button(loc.increase_attribute_button):
                        increase_attribute_dialog(controller, loc)

            st.markdown(f"##### {loc.page_view_base_attributes}")
            st.write(f"{loc.attr_dexterity}: {loc.dice_prefix}{controller.character.dexterity.base}")
            st.write(f"{loc.attr_might}: {loc.dice_prefix}{controller.character.might.base}")
            st.write(f"{loc.attr_insight}: {loc.dice_prefix}{controller.character.insight.base}")
            st.write(f"{loc.attr_willpower}: {loc.dice_prefix}{controller.character.willpower.base}")
            st.write("")
            st.markdown(
                f"**{loc.hp}**: {controller.max_hp()} | **{loc.mp}**: {controller.max_mp()} | **{loc.ip}**: {controller.max_ip()}")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"##### {loc.bonds}")
            with col2:
                if st.button(loc.add_bond_button):
                    add_bond_dialog(controller, loc)
            with col3:
                if st.button(loc.remove_bond_button):
                    remove_bond_dialog(controller, loc)

            writer = BondTableWriter(loc)
            writer.write_in_columns(controller.character.bonds, header=False)


        with points_col:
            col1, col2, col3, col4, col5 = st.columns([0.5, 0.2, 0.1, 0.1, 0.1])
            with col1:
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: green;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                st.progress(
                    max((controller.current_hp() / controller.max_hp()), 0),
                    text=f"{loc.hp} {controller.current_hp()} / {controller.max_hp()}"
                )
                st.write("")
                st.write("")

                st.progress(
                    max((controller.current_mp() / controller.max_mp()), 0),
                    text=f"{loc.mp} {controller.current_mp()} / {controller.max_mp()}"
                )
                st.write("")
                st.write("")

                st.progress(
                    max((controller.current_ip() / controller.max_ip()), 0),
                    text=f"{loc.ip} {controller.current_ip()} / {controller.max_ip()}"
                )
            with col2:
                hp_input = st.number_input("hp_input", min_value=0, label_visibility="hidden", value=10)
                mp_input = st.number_input("mp_input", min_value=0, label_visibility="hidden", value=10)
                ip_input = st.number_input("ip_input", min_value=0, label_visibility="hidden", value=3)
            with col3:
                st.write("")
                if st.button("", icon=":material/add:", key="add_hp"):
                    controller.state.minus_hp = max(0, controller.state.minus_hp - hp_input)
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/add:", key="add_mp"):
                    controller.state.minus_mp = max(0, controller.state.minus_mp - mp_input)
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/add:", key="add_ip"):
                    controller.state.minus_ip = max(0, controller.state.minus_ip - ip_input)
                    st.rerun()
                st.write("")
                st.write("")
            with col4:
                st.write("")
                if st.button("", icon=":material/remove:", key="subtract_hp"):
                    controller.state.minus_hp = min(controller.max_hp(), controller.state.minus_hp + hp_input)
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/remove:", key="subtract_mp"):
                    controller.state.minus_mp = min(controller.max_mp(), controller.state.minus_mp + mp_input)
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/remove:", key="subtract_ip"):
                    controller.state.minus_ip = min(controller.max_ip(), controller.state.minus_ip + ip_input)
                    st.rerun()
                st.write("")
                st.write("")
            with col5:
                st.write("")
                if st.button("", icon=":material/laps:", key="reset_hp", help="Reset HP"):
                    controller.state.minus_hp = 0
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/laps:", key="reset_mp", help="Reset MP"):
                    controller.state.minus_mp = 0
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/laps:", key="reset_ip", help="Reset IP"):
                    controller.state.minus_ip = 0
                    st.rerun()
                st.write("")
                st.write("")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(loc.page_view_health_potion,
                    disabled=not controller.can_use_potion(),
                    use_container_width=True,
                ):
                    controller.use_health_potion()
                    st.rerun()
            with col2:
                if st.button(loc.page_view_mana_potion,
                    disabled=not controller.can_use_potion(),
                    use_container_width=True
                ):
                    controller.use_mana_potion()
                    st.rerun()
            with col3:
                if st.button(loc.page_view_magic_tent,
                    disabled=not controller.can_use_magic_tent(),
                    use_container_width=True
                ):
                    controller.use_magic_tent()
                    st.rerun()

            st.write(f"##### {loc.page_view_equipped}")
            main_hand = controller.character.inventory.equipped.main_hand or Weapon(
                name="unarmed_strike",
                cost=0,
                quality=loc.unarmed_strike_quality,
                martial=False,
                grip_type=GripType.one_handed,
                range=WeaponRange.melee,
                weapon_category=WeaponCategory.brawling,
                accuracy=[AttributeName.dexterity, AttributeName.might],
            )
            display_equipped_item(controller, main_hand, "main_hand", loc)

            # Off-hand
            off_hand = controller.character.inventory.equipped.off_hand
            if off_hand:
                display_equipped_item(controller, off_hand, "off_hand", loc)

            # Armor
            armor = controller.character.inventory.equipped.armor
            if armor:
                display_equipped_item(controller, armor, "armor", loc)

            # Accessory
            accessory = controller.character.inventory.equipped.accessory
            if accessory:
                display_equipped_item(controller, accessory, "accessory", loc)

            show_martial(controller.character)


        with attributes_col:
            st.markdown(f"##### {loc.page_view_current_attributes}")
            att_col1, att_col2 = st.columns(2)
            initiative_column, _ = st.columns([0.9, 0.1])

            st.markdown(f"##### {loc.page_view_statuses}")
            col1, col2 = st.columns(2)
            for idx, stat in enumerate(Status):
                col = col1 if idx < 3 else col2
                with col:
                    checked = st.checkbox(stat.localized_name(loc),
                                          value=(stat in controller.state.statuses))
                    if checked:
                        controller.add_status(stat)
                    else:
                        controller.remove_status(stat)

            st.markdown(f"##### {loc.page_view_bonus_to_attributes}")
            col1, col2 = st.columns(2)
            for idx, attribute in enumerate(AttributeName):
                col = col1 if idx < 2 else col2
                with col:
                    checked = st.checkbox(attribute.localized_name(loc),
                                          value=(stat in controller.state.improved_attributes))
                    if checked and attribute not in controller.state.improved_attributes:
                        controller.state.improved_attributes.append(attribute)
                    if not checked and attribute in controller.state.improved_attributes:
                        controller.state.improved_attributes.remove(attribute)

            controller.apply_status()

            if st.button(loc.page_view_refresh_attributes):
                st.rerun()

            with att_col1:
                st.markdown(colored_attr(loc.attr_dexterity, loc.dice_prefix, controller.character.dexterity.current,
                                         controller.character.dexterity.base), unsafe_allow_html=True)
                st.markdown(colored_attr(loc.attr_might, loc.dice_prefix, controller.character.might.current,
                                         controller.character.might.base), unsafe_allow_html=True)
                st.markdown(f"**{loc.column_defense}**: {controller.defense()}")

            with att_col2:
                st.markdown(colored_attr(loc.attr_insight, loc.dice_prefix, controller.character.insight.current,
                                         controller.character.insight.base), unsafe_allow_html=True)
                st.markdown(colored_attr(loc.attr_willpower, loc.dice_prefix, controller.character.willpower.current,
                                         controller.character.willpower.base), unsafe_allow_html=True)
                st.markdown(f"**{loc.column_magic_defense}**: {controller.magic_defense()}")

            with initiative_column:
                st.markdown(f"**{loc.column_initiative}**: {controller.initiative()}")

            if ClassName.mutant in [char_class.name for char_class in controller.character.classes]:
                st.markdown(f"##### {loc.page_view_manifested_terioforms}")
                st.markdown(" • ".join(t.localized_name(loc) for t in controller.state.active_therioforms))
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(loc.manifest_therioform_button):
                        manifest_therioform_dialog(controller, loc)
                with col2:
                    if st.button(loc.page_view_end_therioform_effect):
                        controller.state.active_therioforms = list()
                        st.rerun()

        st.divider()

    # Skills
    with tab2:
        sorted_classes = sorted(controller.character.classes, key=lambda x: x.class_level(), reverse=True)
        writer = SkillTableWriter(loc)
        writer.columns = writer.level_readonly_columns
        for char_class in sorted_classes:
            st.markdown(f"#### {char_class.name.localized_name(loc)}")
            writer.write_in_columns([skill for skill in char_class.skills if skill.current_level > 0])
        if controller.character.heroic_skills:
            st.markdown(f"#### {loc.heroic_skills}")
            writer = SkillTableWriter(loc)
            writer.columns = writer.heroic_skills_columns
            writer.write_in_columns(controller.character.heroic_skills)

        st.divider()

    # Spells
    with tab3:
        for class_name, spell_list in controller.character.spells.items():
            chimerist_skills = controller.get_skills(ClassName.chimerist)
            chimerist_condition = (class_name == ClassName.chimerist
                                   and "spell_mimic" in [s.name for s in chimerist_skills])
            if spell_list or chimerist_condition:
                writer = SpellTableWriter(loc)
                writer.columns = writer.columns[:-1]
                chimerist_message = ""
                if chimerist_condition:
                    max_n_spells = controller.get_skill_level(ClassName.chimerist, "spell_mimic") + 2
                    if controller.character.has_heroic_skill(HeroicSkillName.chimeric_mastery):
                        max_n_spells += 2
                    chimerist_message = loc.page_view_chimerist_spell_count.format(
                        current=len(spell_list),
                        max=max_n_spells
                    )
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"#### {loc.page_view_class_spells.format(
                        class_name=class_name.localized_name(loc),
                        chimerist_message=chimerist_message
                    )}")
                with c2:
                    if chimerist_condition:
                        if st.button(loc.learn_chimerist_spell_button, disabled=(len(spell_list) == max_n_spells)):
                            add_chimerist_spell_dialog(controller, loc)
                    else:
                        char_class = controller.character.get_class(class_name)
                        casting_skill = char_class.get_spell_skill()
                        can_add_spell = False
                        if casting_skill:
                            can_add_spell = casting_skill.current_level > len(controller.character.get_spells_by_class(class_name))
                        if st.button(
                                loc.learn_spell_button,
                                disabled=not can_add_spell,
                                key=f"{class_name}-add-spell"
                        ):
                            add_spell_dialog(controller, class_name, loc)

                with c3:
                    if chimerist_condition:
                        if st.button(loc.forget_chimerist_spell_button, disabled=(len(spell_list) < 1)):
                            remove_chimerist_spell_dialog(controller, loc)
                if class_name == ClassName.chimerist:
                    writer.columns = writer.chimerist_columns
                writer.write_in_columns(spell_list)

    #Equipment
    with tab4:
        col1, col2, col3, col4 = st.columns([0.2, 0.2, 0.2, 0.4])
        with col1:
            if st.button(loc.add_item_button):
                add_item_dialog(controller, loc)
        with col2:
            if st.button(loc.remove_item_button):
                remove_item_dialog(controller, loc)
        with col3:
            st.metric(
                loc.page_view_remaining_zenit,
                value=loc.page_view_remaining_zenit_value.format(zenits=controller.character.inventory.zenit),
                delta=None,
            )
        with col4:
            c1, c2, c3 = st.columns([0.7, 0.15, 0.15])
            with c1:
                zenit_input = st.number_input("zenit_input", min_value=0, label_visibility="hidden", value=10, step=10)
            with c2:
                st.write("")
                if st.button("", icon=":material/add:", key="add_zenit"):
                    controller.character.inventory.zenit += zenit_input
                    st.rerun()
            with c3:
                st.write("")
                if st.button("", icon=":material/remove:", key="subtract_zenit"):
                    controller.character.inventory.zenit -= zenit_input
                    st.rerun()

        backpack = controller.character.inventory.backpack
        if backpack.weapons:
            weapon_writer = WeaponTableWriter(loc)
            weapon_writer.columns = weapon_writer.equip_columns
            weapon_writer.write_in_columns(backpack.weapons)
        if backpack.armors:
            armor_writer = ArmorTableWriter(loc)
            armor_writer.columns = armor_writer.equip_columns
            armor_writer.write_in_columns(backpack.armors)
        if backpack.shields:
            shield_writer = ShieldTableWriter(loc)
            shield_writer.columns = shield_writer.equip_columns
            shield_writer.write_in_columns(backpack.shields)
        if backpack.accessories:
            AccessoryTableWriter(loc).write_in_columns(backpack.accessories)
        if backpack.other:
            ItemTableWriter(loc).write_in_columns(backpack.other)
    # Special
    with tab5:
        st.divider()
        if controller.is_class_added(ClassName.mutant) and controller.has_skill("theriomorphosis"):
            added_therioforms = [t for t in controller.character.special.therioforms]
            col1, col2 = st.columns([0.25, 0.75])
            with col1:
                st.markdown(f"##### {loc.page_view_therioforms}")
            with col2:
                if len(added_therioforms) < controller.get_skill_level(ClassName.mutant, "theriomorphosis"):
                    if st.button(loc.add_therioform_button):
                        add_therioform_dialog(controller, loc)
            TherioformTableWriter(loc).write_in_columns(added_therioforms)
            st.divider()

        if controller.is_class_added(ClassName.dancer) and controller.has_skill("dance"):
            added_dances = [t for t in controller.character.special.dances]
            col1, col2 = st.columns([0.25, 0.75])
            with col1:
                st.markdown(f"##### {loc.page_view_dances}")
            with col2:
                if len(added_dances) < controller.get_skill_level(ClassName.dancer, "dance"):
                    if st.button(loc.add_dance_button):
                        add_dance_dialog(controller, loc)
            DanceTableWriter(loc).write_in_columns(added_dances)
            st.divider()

        if controller.is_class_added(ClassName.arcanist) and controller.has_skill("bind_and_summon"):
            added_arcana = [t for t in controller.character.special.arcana]
            col1, col2 = st.columns([0.25, 0.75])
            with col1:
                st.markdown(f"##### {loc.page_view_arcana}")
            with col2:
                if st.button(loc.add_arcanum_button):
                    add_arcanum_dialog(controller, loc)
            ArcanumTableWriter(loc).write_in_columns(added_arcana)
            st.divider()

        if controller.is_class_added(ClassName.tinkerer) and controller.has_skill("gadgets"):
            added_inventions = [i for i in controller.character.special.inventions]
            col1, col2 = st.columns([0.25, 0.75])
            with col1:
                st.markdown(f"##### {loc.page_view_inventions}")
            with col2:
                if len(added_inventions) < controller.get_skill_level(ClassName.tinkerer, "gadgets"):
                    if st.button(loc.add_invention_button):
                        add_invention_dialog(controller, loc)
            InventionTableWriter(loc).write_in_columns(added_inventions)
            st.divider()

        # --- PDF EXPORT SECTION ---
        st.subheader("🛠️ System Tools")
        st.write("Export your character to a printable PDF file.")

        if st.button("📄 Generate PDF Character Sheet"):
            # --- DATA PREPARATION ---
            
            # Helper to clean strings
            def clean_str(val):
                if not val: return ""
                return str(val).replace("_", " ").title()

            # Helper to safely get description (Deep Search)
            def get_desc(obj):
                # 1. Try standard attributes
                for attr in ["description", "text", "effect", "rules", "rules_text", "summary"]:
                    val = getattr(obj, attr, None)
                    if val: return str(val)
                
                # 2. Try nested 'data' object (common in some frameworks)
                data_obj = getattr(obj, "data", None)
                if data_obj:
                    for attr in ["description", "text", "effect"]:
                        val = getattr(data_obj, attr, None)
                        if val: return str(val)

                # 3. Fallback: Check internal dictionary
                if hasattr(obj, "__dict__"):
                    for k, v in obj.__dict__.items():
                        if k in ["description", "text", "effect"] and v:
                            return str(v)
                            
                return ""

            # Helper for MP cost
            def get_mp(obj):
                for attr in ["mp", "cost", "mp_cost", "mind_points", "mp_text"]:
                    val = getattr(obj, attr, None)
                    if val is not None: return str(val)
                return "0"

            eq = controller.character.inventory.equipped
            main_hand_name = clean_str(eq.main_hand.name) if eq.main_hand else ""
            off_hand_name = clean_str(eq.off_hand.name) if eq.off_hand else ""
            armor_name = clean_str(eq.armor.name) if eq.armor else ""

            # 2. Fix Initiative
            raw_init = str(controller.initiative())
            init_mod = "0"
            if "-" in raw_init:
                parts = raw_init.split("-")
                if parts[-1].strip().isdigit():
                    init_mod = "-" + parts[-1].strip()
            elif "+" in raw_init:
                parts = raw_init.split("+")
                if parts[-1].strip().isdigit():
                    init_mod = "+" + parts[-1].strip()

            # 3. Check Proficiencies (Checkbox Logic)
            has_armor = False
            has_shield = False
            has_melee = False
            has_ranged = False

            # Check classes against hardcoded knowledge
            for c in controller.character.classes:
                # Convert Enum or Name to string
                c_name = str(c.name.name if hasattr(c.name, "name") else c.name).replace("_", " ").title()
                
                # Match against dictionary
                # Use fuzzy match in case of "Dark_Knight" vs "Dark Knight"
                found_profs = []
                for key, profs in CLASS_PROFICIENCIES.items():
                    if key.lower() == c_name.lower():
                        found_profs = profs
                        break
                
                if "armor" in found_profs: has_armor = True
                if "shield" in found_profs: has_shield = True
                if "melee" in found_profs: has_melee = True
                if "ranged" in found_profs: has_ranged = True

            # 4. Gather Classes & Skills
            classes_info_list = []
            for c in controller.character.classes:
                c_name_str = c.name.localized_name(loc)
                full_name = f"{c_name_str} (Lv {c.class_level()})"
                
                active_skills = [s for s in c.skills if s.current_level > 0]
                skills_text = ""
                for skill in active_skills:
                    s_name = skill.name 
                    if hasattr(s_name, "localized_name"): 
                        s_name = s_name.localized_name(loc)
                    
                    s_desc = get_desc(skill)
                    
                    # Using dash instead of bullet
                    skills_text += f"- {clean_str(s_name)} (Lv {skill.current_level}): {s_desc}\n"
                
                classes_info_list.append({
                    "name": full_name,
                    "skills": skills_text
                })

            # 5. Gather Spells
            spells_list = []
            for class_key, spell_group in controller.character.spells.items():
                for spell in spell_group:
                    s_name = getattr(spell, "name", "Unknown Spell")
                    if hasattr(s_name, "localized_name"): 
                         s_name = s_name.localized_name(loc)
                    
                    spells_list.append({
                        "name": clean_str(s_name),
                        "mp": get_mp(spell),
                        "target": clean_str(getattr(spell, "target", "")),
                        "duration": clean_str(getattr(spell, "duration", "")),
                        "effect": get_desc(spell)
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
                "init": init_mod,
                "def": controller.defense(),
                "mdef": controller.magic_defense(),
                
                # Equipment (Cleaned)
                "main_hand": main_hand_name, 
                "off_hand": off_hand_name,
                "armor": armor_name,
                
                # Proficiencies
                "prof_armor": has_armor,
                "prof_shield": has_shield,
                "prof_melee": has_melee,
                "prof_ranged": has_ranged,

                # Lists
                "classes_info": classes_info_list, 
                "spells": spells_list
            }

            try:
                pdf_file = pdf_export.generate_character_pdf("fabula_charsheet/template_sheet.pdf", pdf_data)
                
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_file,
                    file_name=f"{controller.cracter.name}_Sheet.pdf",
                    mime="application/pdf"
                )
                st.success("PDF Generated! Click above to download.")
                
            except FileNotFoundError:
                st.error("Error: 'template_sheet.pdf' not found. Please upload it to the 'fabula_charsheet' folder.")
            except NameError:
                 st.error("Error: 'pdf_export' module not found. Did you add the import at the top of view.py?")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        
        st.divider()

    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        if st.button(loc.save_current_character_button):
            controller.dump_character()
            controller.dump_state()
    with col2:
        if st.button(loc.load_another_character_button):
            set_view_state(ViewState.load)
