import streamlit as st
import pandas as pd
import math
from io import BytesIO

# --- ASSETS ---
PSPCL_LOGO_URL = "https://pspcl.in/assets/images/logo.png"
BEECLUE_LOGO_PNG = "https://raw.githubusercontent.com/iamanujnarang/LDHF/e5748e037b76a52a47d610a88c3a3c70f72f1c9a/BEECLUE.png"

# --- CONFIG ---
st.set_page_config(page_title="Colony Load Calculator", layout="wide")

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

def main():
    st.markdown(f'<div style="text-align: center;"><img src="{PSPCL_LOGO_URL}" width="120"></div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center;">Colony Load Assessment Sheet</h1>', unsafe_allow_html=True)

    project_name = st.text_input("Project Name/Location", "New Colony")
    
    # Data structure as per your sample format
    res_plots = [
        ("Up to 100 Sq. Yards", 5), ("Above 100 to 200 Sq. Yards", 8),
        ("Above 200 to 250 Sq. Yards", 10), ("Above 250 to 350 Sq. Yards", 12),
        ("Above 350 to 500 Sq. Yards", 20), ("Above 500 to 1000 Sq. Yards", 30),
        ("Above 1000 to 2000 Sq. Yards", 40), ("Above 2000 Sq. Yards", 50)
    ]
    
    inputs = []
    
    st.subheader("Residential Plots Data Entry")
    col1, col2 = st.columns(2)
    for i, (label, load) in enumerate(res_plots):
        c = col1 if i < 4 else col2
        qty = c.number_input(f"{label} ({load} kW)", min_value=0, step=1, key=f"p_{i}")
        if qty > 0:
            inputs.append({
                "Sr. No.": len(inputs) + 1,
                "Description / Plot Size": label,
                "Norms (kW)": load,
                "Quantity": qty,
                "Total Load (kW)": qty * load,
                "Type": "Residential"
            })

    with st.expander("Add Residential Flats / Commercial / Others", expanded=False):
        # Additional inputs can be added here following same pattern
        other_qty = st.number_input("Common Utilities / Others (kW)", min_value=0.0)
        if other_qty > 0:
            inputs.append({
                "Sr. No.": len(inputs) + 1,
                "Description / Plot Size": "Common Utilities",
                "Norms (kW)": other_qty,
                "Quantity": 1,
                "Total Load (kW)": other_qty,
                "Type": "Utility"
            })

    if inputs:
        df = pd.DataFrame(inputs)
        
        # Calculations
        total_res_kw = df[df['Type'] == 'Residential']['Total Load (kW)'].sum()
        net_res_load = total_res_kw * 0.40 # 40% DS Factor
        total_utility = df[df['Type'] == 'Utility']['Total Load (kW)'].sum()
        
        grand_total_kw = net_res_load + total_utility
        total_kva = grand_total_kw / 0.95
        
        st.divider()
        st.subheader("Assessment Preview")
        st.table(df.drop(columns=['Type']))

        # DT Combination
        dt_combo = get_dt_combination(total_kva)
        dt_text = ", ".join([f"{v}x{k}" for k, v in dt_combo.items()])

        # --- EXCEL EXPORT (AS PER YOUR IMAGE FORMAT) ---
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('Load Assessment')
            
            # Formats
            header_fmt = workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#D9EAD3', 'align': 'center'})
            cell_fmt = workbook.add_format({'border': 1, 'align': 'center'})
            bold_fmt = workbook.add_format({'bold': True})

            # Headers
            headers = ["Sr. No.", "Description / Plot Size", "Norms (kW)", "Quantity", "Total Load (kW)"]
            for col_num, header in enumerate(headers):
                worksheet.write(0, col_num, header, header_fmt)

            # Data rows
            for row_num, row_data in enumerate(df.values):
                worksheet.write(row_num + 1, 0, row_data[0], cell_fmt) # Sr
                worksheet.write(row_num + 1, 1, row_data[1], cell_fmt) # Desc
                worksheet.write(row_num + 1, 2, row_data[2], cell_fmt) # Norms
                worksheet.write(row_num + 1, 3, row_data[3], cell_fmt) # Qty
                worksheet.write(row_num + 1, 4, row_data[4], cell_fmt) # Total

            curr_row = len(df) + 2
            worksheet.write(curr_row, 1, "Total Residential Connected Load (kW):", bold_fmt)
            worksheet.write(curr_row, 4, total_res_kw, bold_fmt)
            
            worksheet.write(curr_row + 1, 1, "Colony Load (40% of Residential):", bold_fmt)
            worksheet.write(curr_row + 1, 4, net_res_load, bold_fmt)
            
            worksheet.write(curr_row + 2, 1, f"Grand Total in kVA (at 0.95 PF):", bold_fmt)
            worksheet.write(curr_row + 2, 4, round(total_kva, 2), bold_fmt)

            worksheet.write(curr_row + 4, 1, f"Recommended DT Capacity: {dt_text}", bold_fmt)
            
            worksheet.set_column(1, 1, 30) # Width adjustment
            
        st.download_button(
            label="📥 Export to Excel (Sample Format)",
            data=output.getvalue(),
            file_name=f"Load_Assessment_{project_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
