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

st.set_page_config(page_title="Colony Load Master Pro", layout="wide", page_icon="⚡")

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
    .beeclue-box { background: #1e293b; padding: 20px; border-radius: 12px; display: inline-block; margin-top: 20px; }
    .powered-text { color: #94a3b8; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 10px; text-transform: uppercase; }
    
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

def format_indian(num):
    return "{:,.2f}".format(num)

# ==========================================
# 3. MAIN APPLICATION
# ==========================================
def main():
    # Centered Header
    st.markdown(f'<div style="text-align: center;"><img src="{PSPCL_LOGO_URL}" width="150"></div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; color: #1e293b;">⚡ Colony Load Assessment Master</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #64748b;">Official Framework as per Supply Code 2024 (Reg. 12)</p>', unsafe_allow_html=True)
    st.divider()

    # Session State for Dynamic Rows
    if 'service_rows' not in st.session_state:
        st.session_state.service_rows = 1

    # Basic Project Data
    c1, c2 = st.columns(2)
    with c1:
        project_name = st.text_input("Project Name / Site Address", placeholder="e.g. Omaxe City, Extension-1")
    with c2:
        developer_name = st.text_input("Developer / Promoter Name", placeholder="e.g. ABC Infrastructure Pvt Ltd")

    # Load Database List
    all_calculated_items = []

    # UI Tabs
    tab_res, tab_comm, tab_services = st.tabs(["🏡 Residential (40%)", "🏢 Commercial (50%)", "🛠️ Common Services (Custom Factor)"])

    # --- RESIDENTIAL TAB ---
    with tab_res:
        with st.expander("📝 Enter Residential Plot Details", expanded=True):
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

        with st.expander("🏢 Enter Residential Flat Details", expanded=False):
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
        with st.expander("🛍️ Enter Commercial Space Details", expanded=False):
            shop_qty = st.number_input("Number of Shops/Showrooms (Upto 50 Sq. Yards) [10 kW per Floor]", min_value=0, step=1)
            if shop_qty > 0:
                all_calculated_items.append({"Description": "Shops/Showrooms (Upto 50 SY)", "Norms": 10.0, "Qty": shop_qty, "Factor": 0.50, "Type": "Commercial"})
            
            comm_area = st.number_input("Commercial Area (Above 50 Sq. Yards) in Sq. Yards [175 Watt/Sq. Yard]", min_value=0.0)
            if comm_area > 0:
                load_comm = (comm_area * 175) / 1000
                all_calculated_items.append({"Description": "Large Commercial Area", "Norms": load_comm, "Qty": 1, "Factor": 0.50, "Type": "Commercial"})

    # --- COMMON SERVICES TAB (Dynamic) ---
    with tab_services:
        st.subheader("Public Utilities & Common Services")
        for i in range(st.session_state.service_rows):
            sc1, sc2, sc3, sc4 = st.columns([3, 2, 2, 2])
            with sc1: desc = st.text_input(f"Service Name {i+1}", value="", key=f"s_name_{i}", placeholder="e.g. STP / Street Light")
            with sc2: s_load = st.number_input(f"Load (kW)", min_value=0.0, key=f"s_load_{i}")
            with sc3: s_qty = st.number_input(f"Qty", min_value=0, step=1, key=f"s_qty_{i}", value=1)
            with sc4: s_fac = st.number_input(f"Demand Factor", min_value=0.0, max_value=1.0, value=1.0, key=f"s_fac_{i}")
            
            if desc and s_load > 0 and s_qty > 0:
                all_calculated_items.append({"Description": desc, "Norms": s_load, "Qty": s_qty, "Factor": s_fac, "Type": "Utility"})

        if st.button("➕ Add Another Service"):
            st.session_state.service_rows += 1
            st.rerun()

    # ==========================================
    # 4. CALCULATION ENGINE
    # ==========================================
    if all_calculated_items:
        df = pd.DataFrame(all_calculated_items)
        df['Total kW'] = df['Norms'] * df['Qty']
        df['Net Load'] = df['Total kW'] * df['Factor']

        # Aggregates
        total_residential_kw = df[df['Type'] == 'Residential']['Total kW'].sum()
        total_commercial_kw = df[df['Type'] == 'Commercial']['Total kW'].sum()
        
        grand_total_net_kw = df['Net Load'].sum()
        total_kva = grand_total_net_kw / 0.95

        # Results Summary
        st.divider()
        st.header("📋 Assessment Result")
        
        # Display Table
        display_df = df.copy()
        display_df.index = range(1, len(display_df) + 1)
        st.table(display_df[['Description', 'Norms', 'Qty', 'Total kW', 'Factor', 'Net Load']])

        # Summary Metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="summary-card"><h5>Net Colony Load</h5><h2>{grand_total_net_kw:.2f} kW</h2></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="summary-card"><h5>Total kVA (0.95 PF)</h5><h2 style="color: #0b79d0;">{total_kva:.2f} kVA</h2></div>', unsafe_allow_html=True)
        with m3:
            dt_req = math.ceil(total_kva)
            st.markdown(f'<div class="summary-card"><h5>DT Capacity Needed</h5><h2>{dt_req} kVA</h2></div>', unsafe_allow_html=True)

        # DT Combination Box
        st.write("")
        dt_combo = get_dt_combination(total_kva)
        dt_str = ", ".join([f"({v}) Nos. {k}" for k, v in dt_combo.items()])
        st.success(f"**Recommended Transformer Configuration:** {dt_str}")

        # Competency Section
        st.subheader("⚖️ NOC Competency Authority")
        if total_kva <= 2000:
            auth, rank = "Dy.CE / SE (DS)", "Concerned Distribution Circle"
        elif 2000 < total_kva <= 4000:
            auth, rank = "Chief Engineer (DS)", "Concerned Zone"
        else:
            auth, rank = "Chief Engineer (Commercial)", "PSPCL HQ, Patiala"
        
        st.info(f"The approving authority for this NOC is **{auth}**, {rank}.")

        # ==========================================
        # 5. EXCEL EXPORT (YOUR SPECIFIC FORMAT)
        # ==========================================
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('Load Sheet')
            
            # Formatting
            fmt_header = workbook.add_format({'bold': True, 'bg_color': '#0b79d0', 'font_color': 'white', 'border': 1, 'align': 'center'})
            fmt_cell = workbook.add_format({'border': 1, 'align': 'center'})
            fmt_bold = workbook.add_format({'bold': True, 'border': 1})
            fmt_title = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})

            # Title
            worksheet.merge_range('A1:F1', f"LOAD CALCULATIONS FOR PROJECT: {project_name.upper()}", fmt_title)
            
            # Headers
            headers = ["Sr. No", "Description", "Norms (kW)", "Qty", "Total Load (kW)", "Net Load (After Factor)"]
            for col, text in enumerate(headers):
                worksheet.write(2, col, text, fmt_header)

            # Rows
            for i, row in enumerate(df.itertuples()):
                idx = i + 3
                worksheet.write(idx, 0, i+1, fmt_cell)
                worksheet.write(idx, 1, row.Description, fmt_cell)
                worksheet.write(idx, 2, row.Norms, fmt_cell)
                worksheet.write(idx, 3, row.Qty, fmt_cell)
                worksheet.write(idx, 4, row.Total_kW, fmt_cell)
                worksheet.write(idx, 5, row.Net_Load, fmt_cell)

            last_row = len(df) + 4
            worksheet.write(last_row, 1, "Total Residential Load (kW)", fmt_bold)
            worksheet.write(last_row, 4, total_residential_kw, fmt_bold)
            
            worksheet.write(last_row+1, 1, "GRAND TOTAL NET LOAD (kW)", fmt_bold)
            worksheet.write(last_row+1, 5, grand_total_net_kw, fmt_bold)

            worksheet.write(last_row+2, 1, "TOTAL LOAD IN kVA (0.95 PF)", fmt_bold)
            worksheet.write(last_row+2, 5, round(total_kva, 2), fmt_bold)

            worksheet.write(last_row+4, 1, f"Recommended DTs: {dt_str}", workbook.add_format({'bold': True, 'font_color': 'red'}))
            worksheet.write(last_row+5, 1, f"Authority: {auth}", fmt_bold)

            worksheet.set_column(1, 1, 35)
            worksheet.set_column(2, 5, 15)

        st.download_button(label="📥 Export Assessment to Excel", data=output.getvalue(), file_name=f"{project_name}_Assessment.xlsx")

    else:
        st.warning("Please enter at least one plot or service quantity to see results.")

    # ==========================================
    # 6. FOOTER (BEECLUE & BRANDING)
    # ==========================================
    footer_html = f"""
    <div class="footer-container">
        <div style="font-size: 1.2rem; color: #334155; margin-bottom: 20px;">
            Made with <span style="color: #e63946;">❤️</span> by <b>Er. Anuj Narang, JE PSPCL</b>
        </div>
        <div style="margin-bottom: 25px;">
            <a href="https://instagram.com/iamanujnarang" target="_blank"><img src="{INSTA_ICON}" class="social-icon"></a>
            <a href="https://facebook.com/iamanujnarang" target="_blank"><img src="{FB_ICON}" class="social-icon"></a>
            <a href="https://x.com/iamanujnarang" target="_blank"><img src="{X_ICON}" class="social-icon"></a>
            <a href="https://linkedin.com/in/iamanujnarang" target="_blank"><img src="{LINKEDIN_ICON}" class="social-icon"></a>
        </div>
        <div class="beeclue-box">
            <div class="powered-text">In Strategic Collaboration with</div>
            <a href="https://beeclue.com" target="_blank">
                <img src="{BEECLUE_LOGO_PNG}" class="beeclue-img" style="width: 180px;">
            </a>
        </div>
        <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 25px;">© 2026 | Supply Code 2024 Compliance | Punjab State Power Corp Ltd.</div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
