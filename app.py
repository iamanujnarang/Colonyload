import streamlit as st
import pandas as pd
import math
from io import BytesIO

# ==========================================
# 1. ASSETS & CONFIGURATION
# ==========================================
PSPCL_LOGO_URL = "https://pspcl.in/assets/images/logo.png"
BEECLUE_LOGO_PNG = "https://raw.githubusercontent.com/iamanujnarang/LDHF/e5748e037b76a52a47d610a88c3a3c70f72f1c9a/BEECLUE.png"
INSTA_ICON = "https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png"
FB_ICON = "https://upload.wikimedia.org/wikipedia/commons/1/1b/Facebook_icon.svg"
X_ICON = "https://upload.wikimedia.org/wikipedia/commons/b/b7/X_logo.jpg"
LINKEDIN_ICON = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"

st.set_page_config(page_title="Colony Load Calculator", layout="wide", page_icon="⚡")

# Custom CSS for UI and Footer
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #f1f5f9; border-radius: 10px 10px 0 0; padding: 0 20px; }
    .stTabs [aria-selected="true"] { background-color: #0b79d0 !important; color: white !important; }
    
    .footer-container { text-align: center; margin-top: 80px; padding: 40px 20px; border-top: 1px solid #ddd; background: white; }
    .social-icon { width: 30px; margin: 0 10px; transition: 0.3s; }
    .social-icon:hover { transform: scale(1.2); }
    .beeclue-box { background: #1e293b; padding: 25px; border-radius: 12px; display: inline-block; margin-top: 20px; text-align: center; }
    .powered-text { color: #94a3b8; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 15px; text-transform: uppercase; }
    
    .summary-card { background: white; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def get_dt_combination(target_kva):
    """Calculates optimal combination of standard PSPCL DTs"""
    available_dts = [1000, 800, 500, 315, 300, 200, 100, 63, 25]
    remaining = target_kva
    combination = {}
    for dt in available_dts:
        count = int(remaining // dt)
        if count > 0:
            combination[f"{dt} kVA"] = count
            remaining -= (count * dt)
    if remaining > 0:
        for dt in reversed(available_dts):
            if dt >= remaining:
                combination[f"{dt} kVA"] = combination.get(f"{dt} kVA", 0) + 1
                break
    return combination

# ==========================================
# 3. MAIN APPLICATION
# ==========================================
def main():
    # Centered Header
    st.markdown(f'<div style="text-align: center;"><img src="{PSPCL_LOGO_URL}" width="150"></div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; color: #1e293b;">⚡ Colony Load Calculator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #64748b;">Official Framework as per Supply Code 2024 (Reg. 12)</p>', unsafe_allow_html=True)
    st.divider()

    # Session States for Dynamic Rows
    if 'service_rows' not in st.session_state: st.session_state.service_rows = 1
    if 'comm_rows' not in st.session_state: st.session_state.comm_rows = 1

    # Project Data
    c1, c2 = st.columns(2)
    with c1:
        project_name = st.text_input("Project Name / Site Address", placeholder="e.g. Venus Green Enclave")
    with c2:
        developer_name = st.text_input("Developer Name", placeholder="e.g. Er. Anuj Narang")

    # List to store all calculation results
    all_calculated_items = []

    # UI Tabs
    tab_res, tab_comm, tab_services = st.tabs(["🏡 Residential (40%)", "🏢 Commercial (50%)", "🛠️ Public Utilities"])

    # --- RESIDENTIAL TAB ---
    with tab_res:
        with st.expander("📝 Residential Plot Details", expanded=True):
            res_plots = [
                ("Up to 100 Sq. Yards", 5), ("Above 100 to 200 Sq. Yards", 8),
                ("Above 200 to 250 Sq. Yards", 10), ("Above 250 to 350 Sq. Yards", 12),
                ("Above 350 to 500 Sq. Yards", 20), ("Above 500 to 1000 Sq. Yards", 30),
                ("Above 1000 to 2000 Sq. Yards", 40), ("Above 2000 Sq. Yards", 50)
            ]
            r_cols = st.columns(2)
            for i, (label, norm) in enumerate(res_plots):
                target_col = r_cols[0] if i < 4 else r_cols[1]
                qty = target_col.number_input(f"{label} ({norm} kW)", min_value=0, step=1, key=f"rp_{i}")
                if qty > 0:
                    all_calculated_items.append({"Description": label, "Norms": norm, "Qty": qty, "Factor": 0.40, "Type": "Residential"})

        with st.expander("🏢 Residential Flat Details", expanded=False):
            res_flats = [
                ("Upto 350 sq. ft", 4), ("350 to 600 sq. ft", 5), ("600 to 900 sq. ft", 7),
                ("900 to 1200 sq. ft", 8), ("1200 to 1600 sq. ft", 10), ("1600 to 1900 sq. ft", 12),
                ("Above 1900 sq. ft", 15)
            ]
            f_cols = st.columns(2)
            for i, (label, norm) in enumerate(res_flats):
                target_col = f_cols[0] if i < 4 else f_cols[1]
                qty = target_col.number_input(f"Flat: {label} ({norm} kW)", min_value=0, step=1, key=f"rf_{i}")
                if qty > 0:
                    all_calculated_items.append({"Description": f"Flat ({label})", "Norms": norm, "Qty": qty, "Factor": 0.40, "Type": "Residential"})

    # --- COMMERCIAL TAB ---
    with tab_comm:
        st.subheader("Commercial Space Assessment")
        
        # Part A: Small Shops (Upto 50 SY) [cite: 2521]
        st.write("**Shops/Showrooms (Upto 50 Sq. Yards)**")
        sc1, sc2, sc3 = st.columns([3, 2, 2])
        with sc1:
            shop_qty = st.number_input("Number of Shops", min_value=0, step=1)
        with sc2:
            # Added FAR option for small shops as requested
            shop_far = st.number_input("FAR (Floor Area Ratio) for Shops", min_value=1.0, value=1.0, key="shop_far")
        
        if shop_qty > 0:
            # Base norm is 10 kW per Floor [cite: 2521]
            shop_norm = 10.0 * shop_far
            all_calculated_items.append({"Description": "Shops (Upto 50 SY)", "Norms": shop_norm, "Qty": shop_qty, "Factor": 0.50, "Type": "Commercial"})
        
        st.divider()
        st.write("**Commercial Plots (Above 50 Sq. Yards) - 175 Watt/SY Norm** [cite: 2524, 2525]")
        
        for j in range(st.session_state.comm_rows):
            cc1, cc2, cc3, cc4 = st.columns([3, 2, 2, 2])
            with cc1: c_desc = st.text_input(f"Plot Label {j+1}", key=f"cn_{j}", value=f"Comm Plot {j+1}")
            with cc2: c_area = st.number_input(f"Area in SY {j+1}", min_value=0.0, key=f"ca_{j}")
            with cc3: c_qty = st.number_input(f"Qty {j+1}", min_value=0, step=1, key=f"cq_{j}")
            with cc4: c_far = st.number_input(f"FAR {j+1}", min_value=1.0, value=1.0, key=f"cf_{j}", help="Floor Area Ratio")
            
            if c_area > 0 and c_qty > 0:
                # Norm is 175 Watt per SY = 0.175 kW per SY [cite: 2525]
                # Calculation: Qty * Area * 0.175 * FAR
                norm_val = c_area * 0.175 * c_far
                all_calculated_items.append({"Description": f"{c_desc} ({c_area} SY)", "Norms": norm_val, "Qty": c_qty, "Factor": 0.50, "Type": "Commercial"})
        
        if st.button("➕ Add Commercial Category"):
            st.session_state.comm_rows += 1
            st.rerun()

    # --- PUBLIC SERVICES TAB ---
    with tab_services:
        st.subheader("Public Utility Loads")
        for k in range(st.session_state.service_rows):
            sc1, sc2, sc3, sc4 = st.columns([3, 2, 1, 2])
            with sc1: desc = st.text_input(f"Service Name {k+1}", key=f"sn_{k}", placeholder="e.g. STP")
            with sc2: s_load = st.number_input(f"Load (kW) {k+1}", min_value=0.0, key=f"sl_{k}")
            with sc3: s_qty = st.number_input(f"Qty {k+1}", min_value=0, step=1, key=f"sq_{k}", value=1)
            with sc4: s_fac = st.number_input(f"Demand Factor {k+1}", min_value=0.0, max_value=1.0, value=1.0, key=f"sf_{k}")
            if desc and s_load > 0:
                all_calculated_items.append({"Description": desc, "Norms": s_load, "Qty": s_qty, "Factor": s_fac, "Type": "Utility"})
        
        if st.button("➕ Add Service Row"):
            st.session_state.service_rows += 1
            st.rerun()

    # ==========================================
    # 4. CALCULATION & DISPLAY
    # ==========================================
    if all_calculated_items:
        df = pd.DataFrame(all_calculated_items)
        df['Total_Load_kW'] = df['Norms'] * df['Qty']
        df['Net_Load_kW'] = df['Total_Load_kW'] * df['Factor'] [cite: 2534]

        grand_total_net_kw = df['Net_Load_kW'].sum()
        total_kva = grand_total_net_kw / 0.95 [cite: 2535]

        st.divider()
        st.header("📋 Assessment Summary Table")
        
        display_df = df.copy()
        display_df['Norms'] = display_df['Norms'].apply(lambda x: f"{x:.3f} kW")
        st.table(display_df[['Description', 'Norms', 'Qty', 'Total_Load_kW', 'Factor', 'Net_Load_kW']].rename(
            columns={'Total_Load_kW': 'Total Load (kW)', 'Net_Load_kW': 'Net Load (After Factor)'}
        ))

        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f'<div class="summary-card"><h5>Net Colony Load</h5><h2>{grand_total_net_kw:.2f} kW</h2></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="summary-card"><h5>Total kVA (0.95 PF)</h5><h2 style="color: #0b79d0;">{total_kva:.2f} kVA</h2></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="summary-card"><h5>DT Capacity Needed</h5><h2>{math.ceil(total_kva)} kVA</h2></div>', unsafe_allow_html=True)

        dt_combo = get_dt_combination(total_kva)
        dt_str = ", ".join([f"({v}) Nos. {k}" for k, v in dt_combo.items()])
        st.success(f"**Recommended Transformer Combination (100% Loading):** {dt_str}")

        if total_kva <= 2000: auth = "Dy.CE / SE (DS) Concerned Circle"
        elif 2000 < total_kva <= 4000: auth = "Chief Engineer (DS) Concerned Zone"
        else: auth = "Chief Engineer (Commercial) PSPCL, Patiala"
        st.info(f"**NOC Approving Authority:** {auth}")

        # ==========================================
        # 5. EXCEL EXPORT
        # ==========================================
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('Load Assessment')
            
            title_fmt = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#0b79d0', 'font_color': 'white', 'border': 1, 'align': 'center'})
            cell_fmt = workbook.add_format({'border': 1, 'align': 'center'})
            bold_cell = workbook.add_format({'bold': True, 'border': 1})

            worksheet.merge_range('A1:F1', f"LOAD CALCULATIONS FOR PROJECT: {project_name.upper()}", title_fmt)
            headers = ["Sr. No", "Description", "Norms (kW)", "Quantity", "Total Load (kW)", "Net Load"]
            for col, text in enumerate(headers): worksheet.write(2, col, text, header_fmt)

            for i, row in enumerate(df.to_dict('records')):
                idx = i + 3
                worksheet.write(idx, 0, i+1, cell_fmt)
                worksheet.write(idx, 1, row['Description'], cell_fmt)
                worksheet.write(idx, 2, f"{row['Norms']:.3f} kW", cell_fmt)
                worksheet.write(idx, 3, row['Qty'], cell_fmt)
                worksheet.write(idx, 4, row['Total_Load_kW'], cell_fmt)
                worksheet.write(idx, 5, row['Net_Load_kW'], cell_fmt)

            last_row = len(df) + 4
            worksheet.write(last_row, 1, "GRAND TOTAL NET LOAD (kW)", bold_cell)
            worksheet.write(last_row, 5, grand_total_net_kw, bold_cell)
            worksheet.write(last_row+1, 1, "TOTAL LOAD IN kVA (0.95 PF)", bold_cell)
            worksheet.write(last_row+1, 5, round(total_kva, 2), bold_cell)
            worksheet.write(last_row+3, 1, f"Recommended DTs: {dt_str}", workbook.add_format({'bold': True, 'font_color': 'red'}))
            worksheet.write(last_row+4, 1, f"Authority: {auth}", bold_cell)
            worksheet.set_column(1, 1, 35)

        st.download_button(label="📥 Export Assessment to Excel", data=output.getvalue(), file_name=f"{project_name}_Load_Sheet.xlsx")

    # ==========================================
    # 6. FOOTER
    # ==========================================
    st.markdown(f"""
    <div class="footer-container">
        <div style="font-size: 1.1rem; color: #334155; margin-bottom: 20px;">
            Made with ❤️ by <b>Er. Anuj Narang, JE PSPCL</b>
        </div>
        <div style="margin-bottom: 25px;">
            <a href="https://instagram.com/iamanujnarang"><img src="{INSTA_ICON}" class="social-icon"></a>
            <a href="https://facebook.com/iamanujnarang"><img src="{FB_ICON}" class="social-icon"></a>
            <a href="https://x.com/iamanujnarang"><img src="{X_ICON}" class="social-icon"></a>
            <a href="https://linkedin.com/in/iamanujnarang"><img src="{LINKEDIN_ICON}" class="social-icon"></a>
        </div>
        <div class="beeclue-box">
            <div class="powered-text">In Strategic Collaboration with</div>
            <a href="https://beeclue.com" target="_blank">
                <img src="{BEECLUE_LOGO_PNG}" width="180" style="display: block; margin: 0 auto;">
            </a>
        </div>
        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 25px;">© 2026 | Supply Code 2024 Compliance | Punjab State Power Corporation Ltd.</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
