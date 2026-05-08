import streamlit as st
import pandas as pd
import math
from io import BytesIO

# --- ASSETS ---
PSPCL_LOGO_URL = "https://pspcl.in/assets/images/logo.png"
BEECLUE_LOGO_PNG = "https://raw.githubusercontent.com/iamanujnarang/LDHF/e5748e037b76a52a47d610a88c3a3c70f72f1c9a/BEECLUE.png"

# --- CONFIG ---
st.set_page_config(page_title="Colony Load Calculator", layout="wide")

def format_indian_currency(number):
    return "{:,.2f}".format(number)

def get_dt_combination(target_kva):
    """Finds a combination of standard DTs (25, 63, 100, 200, 300, 315, 500, 800, 1000)"""
    available_dts = [1000, 800, 500, 315, 300, 200, 100, 63, 25]
    remaining = target_kva
    combination = {}
    for dt in available_dts:
        count = int(remaining // dt)
        if count > 0:
            combination[f"{dt} kVA"] = count
            remaining -= (count * dt)
    
    # If still remaining, add one smallest DT to cover it
    if remaining > 0:
        combination["25 kVA"] = combination.get("25 kVA", 0) + 1
    
    return combination

def main():
    # Header with Styling
    st.markdown(f'<div style="text-align: center;"><img src="{PSPCL_LOGO_URL}" width="120"></div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center;">Colony Connected Load Calculator (Supply Code 2024)</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #64748b;">As per Regulation 12 Norms (Annexure-1)</p>', unsafe_allow_html=True)

    # Project Info
    project_name = st.text_input("Project Name", "New Colony Project")

    # Inputs Layout
    tab1, tab2 = st.tabs(["🏡 Residential Plots/Flats", "🏢 Commercial & Other Services"])
    
    inputs = []
    
    with tab1:
        st.subheader("Residential Plots (Area Based) ")
        res_col1, res_col2 = st.columns(2)
        
        # Residential Plots Data Mapping 
        res_plots = [
            ("Up to 100 Sq. Yards", 5), ("100 to 200 Sq. Yards", 8),
            ("200 to 250 Sq. Yards", 10), ("250 to 350 Sq. Yards", 12),
            ("350 to 500 Sq. Yards", 20), ("500 to 1000 Sq. Yards", 30),
            ("1000 to 2000 Sq. Yards", 40), ("Above 2000 Sq. Yards", 50)
        ]
        
        for i, (label, load) in enumerate(res_plots):
            col = res_col1 if i < 4 else res_col2
            qty = col.number_input(f"{label} ({load} kW)", min_value=0, step=1, key=f"res_{i}")
            if qty > 0:
                inputs.append({"Category": label, "Load/Unit (kW)": load, "Qty": qty, "Total Load (kW)": qty * load, "Type": "Residential"})

        st.divider()
        st.subheader("Residential Flats (Covered Area) ")
        flat_col1, flat_col2 = st.columns(2)
        
        # Flats Data Mapping 
        flats = [
            ("Upto 350 sq. ft", 4), ("350 to 600 sq. ft", 5), ("600 to 900 sq. ft", 7),
            ("900 to 1200 sq. ft", 8), ("1200 to 1600 sq. ft", 10), ("1600 to 1900 sq. ft", 12),
            ("1900 to 2200 sq. ft", 13), ("2200 to 2600 sq. ft", 15), ("2600 to 3000 sq. ft", 17),
            ("3000 to 3500 sq. ft", 20), ("Above 3500 sq. ft", 25)
        ]
        for i, (label, load) in enumerate(flats):
            col = flat_col1 if i < 6 else flat_col2
            qty = col.number_input(f"{label} ({load} kW)", min_value=0, step=1, key=f"flat_{i}")
            if qty > 0:
                inputs.append({"Category": f"Flat: {label}", "Load/Unit (kW)": load, "Qty": qty, "Total Load (kW)": qty * load, "Type": "Residential"})

    with tab2:
        st.subheader("Commercial Space [cite: 2521, 2522]")
        comm_col1, comm_col2 = st.columns(2)
        
        # Shops 
        shop_qty = comm_col1.number_input("Shops/Showrooms (Upto 50 Sq. Yards) - 10 kW/Floor", min_value=0, step=1)
        if shop_qty > 0:
            inputs.append({"Category": "Shops (Upto 50 SY)", "Load/Unit (kW)": 10, "Qty": shop_qty, "Total Load (kW)": shop_qty * 10, "Type": "Commercial"})
        
        # Other Utilities [cite: 2522]
        st.subheader("Common Services")
        stp_load = st.number_input("STP/Water Works/Street Light (kW)", min_value=0.0, step=1.0)
        if stp_load > 0:
            inputs.append({"Category": "Common Utilities", "Load/Unit (kW)": stp_load, "Qty": 1, "Total Load (kW)": stp_load, "Type": "Utility"})

    # --- CALCULATIONS ---
    df_calc = pd.DataFrame(inputs)
    
    total_res_kw = df_calc[df_calc['Type'] == 'Residential']['Total Load (kW)'].sum()
    total_comm_kw = df_calc[df_calc['Type'] == 'Commercial']['Total Load (kW)'].sum()
    total_utility_kw = df_calc[df_calc['Type'] == 'Utility']['Total Load (kW)'].sum()

    # Applying Diversity/Demand Factors 
    # Residential 40%, Commercial 50% 
    net_res_load = total_res_kw * 0.40 
    net_comm_load = total_comm_kw * 0.50
    net_total_kw = net_res_load + net_comm_load + total_utility_kw
    
    # KVA Conversion (PF 0.95) 
    total_kva = net_total_kw / 0.95

    # Results Display
    st.divider()
    st.header("📊 Load Summary Sheet")
    
    if not df_calc.empty:
        st.table(df_calc)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Net Load (kW)", f"{net_total_kw:.2f} kW")
        c2.metric("Total Load in kVA", f"{total_kva:.2f} kVA")
        
        # DT Logic
        # Capacities available: 25 63 100 200 300 315 500 800 1000kVA
        st.subheader(f"🛠️ DT Capacity Required: {math.ceil(total_kva)} kVA")
        dt_combo = get_dt_combination(total_kva)
        
        dt_details = []
        for dt, count in dt_combo.items():
            dt_details.append(f"{count} x {dt}")
        st.success(f"Recommended Combination: {', '.join(dt_details)}")

        # Competency Logic
        st.subheader("⚖️ NOC Approval Competency")
        if total_kva <= 2000:
            competency = "Dy.CE/DS or SE/DS of Concerned Circle"
        elif 2000 < total_kva <= 4000:
            competency = "Chief Engineer/DS of Concerned Zone"
        else:
            competency = "Chief Engineer Commercial, PSPCL Patiala"
        st.info(f"Approving Authority: **{competency}**")

        # Excel Export
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_calc.to_excel(writer, index=False, sheet_name='Load Sheet')
            summary_df = pd.DataFrame({
                "Parameter": ["Net Total kW", "Total kVA", "Authority"],
                "Value": [net_total_kw, total_kva, competency]
            })
            summary_df.to_excel(writer, index=False, startrow=len(df_calc)+2)
        
        st.download_button(label="📥 Export to Excel", data=output.getvalue(), file_name=f"{project_name}_Load.xlsx")

if __name__ == "__main__":
    main()
