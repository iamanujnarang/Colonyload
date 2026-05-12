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
X_ICON = "https://upload.wikimedia.org/wikipedia/commons/5/53/X_logo_2023_original.svg"
LINKEDIN_ICON = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"

st.set_page_config(page_title="Colony Load Calculator", layout="wide", page_icon="⚡")

# Custom CSS for UI
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .footer-container { text-align: center; margin-top: 80px; padding: 40px 20px; border-top: 1px solid #ddd; }
    .made-with-love { font-size: 1.2rem; color: #334155; margin-bottom: 20px; }
    .heart-symbol { color: #e63946; }
    .social-icon { width: 30px; margin: 0 10px; transition: 0.3s; }
    .social-icon:hover { transform: scale(1.2); }
    .powered-text { color: #94a3b8; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 10px; text-transform: uppercase; }
    .beeclue-img { width: 180px; height: auto; }
    .summary-card { background: white; padding: 25px; border-radius: 15px; border: 2px solid #0b79d0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def get_dt_combination(target_kva):
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
    st.markdown(f'<div style="text-align: center;"><img src="{PSPCL_LOGO_URL}" width="150"></div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; color: #1e293b;">⚡ Colony Load Calculator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #64748b;">Supply Code 2024 Framework (Reg. 12)</p>', unsafe_allow_html=True)
    st.divider()

    if 'service_rows' not in st.session_state: st.session_state.service_rows = 1
    if 'comm_rows' not in st.session_state: st.session_state.comm_rows = 1

    c1, c2 = st.columns(2)
    with c1: project_name = st.text_input("Project Name / Site Address", placeholder="e.g. Canal Colony")
    with c2: developer_name = st.text_input("Developer Name", placeholder="e.g. Er. ADA/PUDA")

    all_calculated_items = []
    tab_res, tab_comm, tab_services = st.tabs(["🏡 Residential (40%)", "🏢 Commercial (50%)", "🛠️ Public Utilities"])

    # --- RESIDENTIAL TAB ---
    with tab_res:
        with st.expander("📝 Residential Plots", expanded=True):
            res_plots = [
                ("Up to 100 Square Yards", 5), ("Above 100 to 200 Square Yards", 8),
                ("Above 200 to 250 Square Yards", 10), ("Above 250 to 350 Square Yards", 12),
                ("Above 350 to 500 Square Yards", 20), ("Above 500 to 1000 Square Yards", 30),
                ("Above 1000 to 2000 Square Yards", 40), ("Above 2000 Square Yards", 50)
            ]
            r_cols = st.columns(2)
            for i, (label, norm) in enumerate(res_plots):
                qty = r_cols[i%2].number_input(f"{label} ({norm} kW)", min_value=0, step=1, key=f"rp_{i}")
                if qty > 0:
                    all_calculated_items.append({"Description": f"{label} ({norm} kW)", "Norms": norm, "Qty": qty, "Load Factor": 0.40, "Type": "Residential"})

        with st.expander("🏢 Residential Flats", expanded=False):
            res_flats = [("Upto 350 sq.ft", 4), ("350-600 sq.ft", 5), ("600-900 sq.ft", 7), ("900-1200 sq.ft", 8), ("1200-1600 sq.ft", 10), ("1600-1900 sq.ft", 12), ("Above 1900 sq.ft", 15)]
            f_cols = st.columns(2)
            for i, (label, norm) in enumerate(res_flats):
                qty = f_cols[i%2].number_input(f"Flat: {label} ({norm} kW)", min_value=0, step=1, key=f"rf_{i}")
                if qty > 0:
                    all_calculated_items.append({"Description": f"Flat {label} ({norm} kW)", "Norms": norm, "Qty": qty, "Load Factor": 0.40, "Type": "Residential"})

    # --- COMMERCIAL TAB ---
    with tab_comm:
        st.subheader("Commercial Space Assessment")
        uniform_far_check = st.checkbox("Apply Uniform FAR (Floor Area Ratio) for all commercial load?", value=True)
        uniform_far_val = 1.0
        if uniform_far_check:
            uniform_far_val = st.number_input("Enter Uniform FAR value", min_value=1.0, value=1.0, step=0.1)

        st.divider()
        st.write("**Shops/Showrooms (Upto 50 Square Yards)**")
        sc1, sc2 = st.columns(2)
        shop_qty = sc1.number_input("Number of Shops", min_value=0, step=1)
        shop_far = uniform_far_val if uniform_far_check else sc2.number_input("Individual FAR for Shops", min_value=1.0, value=1.0, step=0.1, key="shop_far_ind")
        
        if shop_qty > 0:
            all_calculated_items.append({"Description": "Shops (Upto 50 SY)", "Norms": 10.0 * shop_far, "Qty": shop_qty, "Load Factor": 0.50, "Type": "Commercial"})
        
        st.divider()
        st.write("**Commercial Plots (Above 50 Square Yards)**")
        for j in range(st.session_state.comm_rows):
            cc1, cc2, cc3, cc4 = st.columns([3, 2, 1, 1])
            with cc1: c_desc = st.text_input(f"Comm Plot Label {j+1}", key=f"cn_{j}", value=f"Comm Plot {j+1}")
            with cc2: c_area = st.number_input(f"Area (Square Yards) {j+1}", min_value=0.0, key=f"ca_{j}")
            with cc3: c_qty = st.number_input(f"Qty {j+1}", min_value=0, step=1, key=f"cq_{j}")
            c_far_final = uniform_far_val if uniform_far_check else cc4.number_input(f"FAR {j+1}", min_value=1.0, value=1.0, key=f"cf_{j}")
            
            if c_area > 0 and c_qty > 0:
                all_calculated_items.append({"Description": f"{c_desc} ({c_area} SY)", "Norms": c_area * 0.175 * c_far_final, "Qty": c_qty, "Load Factor": 0.50, "Type": "Commercial"})
        if st.button("➕ Add Commercial Category"): st.session_state.comm_rows += 1; st.rerun()

    # --- PUBLIC SERVICES TAB ---
    with tab_services:
        for k in range(st.session_state.service_rows):
            sc1, sc2, sc3, sc4 = st.columns([3, 2, 1, 2])
            with sc1: desc = st.text_input(f"Service {k+1}", key=f"sn_{k}", placeholder="e.g. STP")
            with sc2: s_load = st.number_input(f"Load(kW) {k+1}", min_value=0.0, key=f"sl_{k}")
            with sc3: s_qty = st.number_input(f"Qty {k+1}", min_value=0, value=1, key=f"sq_{k}")
            with sc4: s_fac = st.number_input(f"Load Factor {k+1}", min_value=0.0, value=1.0, key=f"sf_{k}")
            if desc and s_load > 0:
                all_calculated_items.append({"Description": desc, "Norms": s_load, "Qty": s_qty, "Load Factor": s_fac, "Type": "Utility"})
        if st.button("➕ Add Service Row"): st.session_state.service_rows += 1; st.rerun()

    # ==========================================
    # 4. FINAL CALCULATION ENGINE
    # ==========================================
    if all_calculated_items:
        df = pd.DataFrame(all_calculated_items)
        df['Total_Load_kW'] = df['Norms'] * df['Qty']
        
        # Calculation Fix: Standardized to 'Load Factor'
        df['Net_Load_kW'] = df['Total_Load_kW'] * df['Load Factor']
        
        grand_total_net_kw = df['Net_Load_kW'].sum()
        total_kva = grand_total_net_kw / 0.95
        dt_req_kva = math.ceil(total_kva)

        st.divider()
        st.header("📋 Load Assessment Summary")
        display_df = df.copy()
        display_df['Norms'] = display_df['Norms'].apply(lambda x: f"{x:.3f} kW")
        st.table(display_df[['Description', 'Norms', 'Qty', 'Total_Load_kW', 'Load Factor', 'Net_Load_kW']].rename(columns={'Total_Load_kW': 'Total Load (kW)', 'Net_Load_kW': 'Net Load (kW)'}))

        # SUMMARY CARDS
        res_col1, res_col2, res_col3, res_col4 = st.columns(4)
        with res_col1:
            st.markdown(f'<div class="summary-card"><p>Net Load</p><h3>{grand_total_net_kw:.2f} kW</h3></div>', unsafe_allow_html=True)
        with res_col2:
            st.markdown(f'<div class="summary-card"><p>PF Applied</p><h3>0.95</h3></div>', unsafe_allow_html=True)
        with res_col3:
            st.markdown(f'<div class="summary-card"><p>Total kVA</p><h3 style="color: #0b79d0;">{total_kva:.2f} kVA</h3></div>', unsafe_allow_html=True)
        with res_col4:
            st.markdown(f'<div class="summary-card"><p>DT Capacity Needed</p><h3>{dt_req_kva} kVA</h3></div>', unsafe_allow_html=True)

        dt_combo = get_dt_combination(total_kva)
        dt_str = ", ".join([f"{v} Nos. {k}" for k, v in dt_combo.items()])
        st.success(f"**Recommended Transformer Configuration (100% Loading):** {dt_str}")

        # Excel Export
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('Load Sheet')
            bold = workbook.add_format({'bold': True, 'border': 1})
            center = workbook.add_format({'border': 1, 'align': 'center'})
            worksheet.write(0, 1, f"PROJECT: {project_name.upper()}", bold)
            headers = ["Sr", "Description", "Norms (kW)", "Qty", "Total Load (kW)", "Net Load"]
            for col, h in enumerate(headers): worksheet.write(2, col, h, bold)
            for i, row in enumerate(df.to_dict('records')):
                worksheet.write(i+3, 0, i+1, center)
                worksheet.write(i+3, 1, row['Description'], center)
                worksheet.write(i+3, 2, f"{row['Norms']:.2f} kW", center)
                worksheet.write(i+3, 3, row['Qty'], center)
                worksheet.write(i+3, 4, row['Total_Load_kW'], center)
                worksheet.write(i+3, 5, row['Net_Load_kW'], center)
            
            lrow = len(df)+4
            worksheet.write(lrow, 1, "GRAND TOTAL NET LOAD (kW)", bold); worksheet.write(lrow, 5, grand_total_net_kw, bold)
            worksheet.write(lrow+1, 1, "TOTAL LOAD IN kVA (0.95 PF)", bold); worksheet.write(lrow+1, 5, total_kva, bold)
            worksheet.write(lrow+2, 1, "DT CAPACITY REQUIRED (kVA)", bold); worksheet.write(lrow+2, 5, dt_req_kva, bold)
            worksheet.set_column(1, 1, 40)

        st.download_button("📥 Download Excel Assessment", output.getvalue(), f"{project_name}_Load.xlsx")

    # ==========================================
    # 5. FOOTER
    # ==========================================
    footer_html = f"""
    <div class="footer-container">
    <div class="made-with-love">Made with <span class="heart-symbol">❤️</span> by <b>Er. Anuj Narang, JE PSPCL</b></div>
    <div style="margin-bottom: 25px;">
    <a href="https://instagram.com/iamanujnarang" target="_blank"><img src="{INSTA_ICON}" class="social-icon"></a>
    <a href="https://facebook.com/iamanujnarang" target="_blank"><img src="{FB_ICON}" class="social-icon"></a>
    <a href="https://x.com/iamanujnarang" target="_blank"><img src="{X_ICON}" class="social-icon"></a>
    <a href="https://linkedin.com/in/iamanujnarang" target="_blank"><img src="{LINKEDIN_ICON}" class="social-icon"></a>
    </div>
    <div style="margin-top: 25px;">
        <div class="powered-text">In Strategic Collaboration with</div>
        <a href="https://beeclue.com" target="_blank">
            <img src="{BEECLUE_LOGO_PNG}" class="beeclue-img">
        </a>
    </div>
    <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 25px;">© 2026 | PSPCL Guidelines | CC 45/2024</div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
