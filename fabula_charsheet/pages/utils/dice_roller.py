import streamlit as st
import random
from data.models import AttributeName

def render_dice_roller(controller=None):
    """
    Renders the Dice Roller widget in the sidebar.
    """
    with st.expander("🎲 Dice Roller", expanded=True):
        
        # --- 1. STATE MANAGEMENT ---
        dice_types = [4, 6, 8, 10, 12, 20]
        for d in dice_types:
            key = f"dice_count_d{d}"
            if key not in st.session_state:
                st.session_state[key] = 0

        # --- 2. ATTRIBUTE BUTTONS (PILLS) ---
        selected_attrs = []
        if controller:
            st.caption("Check (Max 2)")
            attr_opts = [a for a in AttributeName]
            
            # Using pills for "Buttons" feel
            selected_attrs = st.pills(
                "Attributes",
                options=attr_opts,
                selection_mode="multi",
                label_visibility="collapsed",
                format_func=lambda x: f"{x.name.title()} (d{getattr(controller.character, x.name).current})"
            )
            
            if len(selected_attrs) > 2:
                st.error("Max 2!")
                # Slice logic doesn't work well with pill state return, so we warn instead

        # --- 3. DICE ICONS ---
        st.caption("Manual Dice Pool")
        chunks = [dice_types[i:i+3] for i in range(0, len(dice_types), 3)]
        
        for chunk in chunks:
            cols = st.columns(len(chunk))
            for i, d in enumerate(chunk):
                with cols[i]:
                    count = st.session_state[f"dice_count_d{d}"]
                    st.markdown(f"**d{d}** <span style='color:orange; font-size:0.8em'>x{count}</span>", unsafe_allow_html=True)
                    
                    b_sub, b_add = st.columns(2)
                    with b_sub:
                        if st.button("−", key=f"sub_d{d}", width="stretch"):
                            if st.session_state[f"dice_count_d{d}"] > 0:
                                st.session_state[f"dice_count_d{d}"] -= 1
                                st.rerun()
                    with b_add:
                        if st.button("＋", key=f"add_d{d}", width="stretch"):
                            st.session_state[f"dice_count_d{d}"] += 1
                            st.rerun()

        # --- 4. MODIFIER ---
        st.caption("Modifier")
        modifier = st.number_input("Mod", value=0, step=1, label_visibility="collapsed")

        st.divider()

        # --- 5. ACTIONS ---
        c_roll, c_clear = st.columns([0.6, 0.4])
        with c_roll:
            do_roll = st.button("🎲 ROLL", type="primary", width="stretch")
        with c_clear:
            if st.button("Clear", width="stretch"):
                for d in dice_types:
                    st.session_state[f"dice_count_d{d}"] = 0
                st.rerun()

        # --- 6. ROLL LOGIC ---
        if do_roll:
            results_log = []
            total = 0
            
            # Attribute Rolls
            if selected_attrs and controller:
                # Enforce limit here just in case
                for attr in selected_attrs[:2]:
                    die_size = getattr(controller.character, attr.name).current
                    roll = random.randint(1, die_size)
                    results_log.append(f"**{attr.name.title()} (d{die_size})**: :orange[{roll}]")
                    total += roll
            
            # Manual Dice Rolls
            for d in dice_types:
                count = st.session_state[f"dice_count_d{d}"]
                if count > 0:
                    rolls = [random.randint(1, d) for _ in range(count)]
                    subtotal = sum(rolls)
                    roll_str = ", ".join(map(str, rolls))
                    results_log.append(f"**{count}d{d}**: `{roll_str}`")
                    total += subtotal
            
            # Modifier
            if modifier != 0:
                results_log.append(f"**Mod**: `{modifier}`")
                total += modifier

            if not results_log and modifier == 0:
                st.warning("No dice selected.")
            else:
                st.markdown(
                    f"""
                    <div style="background-color: #1e293b; border: 1px solid #475569; border-radius: 8px; padding: 10px; margin-top: 10px; text-align: center;">
                        <div style="font-size: 0.8em; color: #94a3b8; margin-bottom: 5px;">RESULT</div>
                        <div style="font-size: 2em; font-weight: bold; color: #a78bfa; line-height: 1;">{total}</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                with st.expander("Breakdown", expanded=True):
                    for line in results_log:
                        st.markdown(line)
