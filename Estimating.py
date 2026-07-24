
import streamlit as st
import math

# Page Configuration for Mobile Screens
st.set_page_config(page_title="Houston Electrical Estimator", page_icon="⚡", layout="centered")

st.title("⚡ Houston Master Estimator")
st.caption("NEC Compliant | Home Depot Pricing | Resi & Comm")

# ==========================================
# SIDEBAR: SETTINGS & CUSTOMIZATION
# ==========================================
with st.sidebar:
    st.header("⚙️ Rates & Overhead")
    res_hourly = st.number_input("Residential Rate ($/hr)", value=75.0, step=5.0)
    comm_hourly = st.number_input("Commercial Rate ($/hr)", value=95.0, step=5.0)
    trip_fee = st.number_input("Gas / Dispatch Fee ($)", value=95.0, step=5.0)
    mat_markup = st.slider("Material Markup (%)", min_value=0, max_value=50, value=15) / 100.0 + 1.0
    
    st.header("👥 Crew Setup")
    crew_type = st.selectbox("Crew", ["1 Journeyman (Solo)", "1 Journeyman + 1 Apprentice (0.65 Multiplier)"])
    crew_mult = 1.0 if "Solo" in crew_type else 0.65

# ==========================================
# MAIN APP WIZARD
# ==========================================
env = st.radio("Select Job Environment", ["Residential", "Commercial"], horizontal=True)
hourly_rate = res_hourly if env == "Residential" else comm_hourly

category = st.selectbox(
    "Select Scope Category",
    [
        "Lighting & Fans (Resi)",
        "Commercial Lighting & LED Retrofits",
        "Devices & Receptacles",
        "Conduit & Dedicated Circuit Runs",
        "Trenching & Underground Burial",
        "Generators & Interlock Kits"
    ]
)

st.markdown("---")

# --- CATEGORY 1: RESIDENTIAL LIGHTING & FANS ---
if category == "Lighting & Fans (Resi)":
    st.subheader("🏠 Residential Lighting & Fans")
    
    stories = st.radio("House Height / Stories", [1, 2, 3], horizontal=True)
    ceiling_ht = st.selectbox("Ceiling Height", ["Standard (8-10 ft)", "High Ceiling (12-14 ft)", "Foyer / Vaulted (16+ ft)"])
    
    light_type = st.selectbox("Fixture Type", ["Recessed Pop-in / Canless Wafer", "Standard Surface Light", "Ceiling Fan", "Heavy Chandelier"])
    qty = st.number_input("Quantity of Fixtures", min_value=1, value=4)
    
    needs_new_wire = st.checkbox("Requires new box cut-in & wire pull? (Uncheck if replacing existing)")
    
    # Logic
    base_hrs_per_unit = 0.75 if "Pop-in" in light_type else (1.25 if "Surface" in light_type else (2.0 if "Fan" in light_type else 3.5))
    if needs_new_wire: base_hrs_per_unit += 1.25
    
    # Height adders
    height_adder = 0.0 if "8-10" in ceiling_ht else (1.5 if "12-14" in ceiling_ht else 3.0)
    story_adder = 0.0 if stories == 1 else (1.5 if stories == 2 else 3.0)
    
    mat_per_unit = 22.00 if "Pop-in" in light_type else (35.00 if "Surface" in light_type else (120.00 if "Fan" in light_type else 180.00))
    raw_mat = (mat_per_unit * qty) + (35.00 * qty if needs_new_wire else 0)
    
    total_hours = (base_hrs_per_unit * qty + height_adder + story_adder) * crew_mult

# --- CATEGORY 2: COMMERCIAL LIGHTING & RETROFITS ---
elif category == "Commercial Lighting & LED Retrofits":
    st.subheader("🏢 Commercial Lighting & Troffers")
    
    comm_light_type = st.selectbox("Fixture Style", ["2x4 Troffer", "2x2 Troffer", "4ft Industrial Strip", "8ft High Bay"])
    job_scope = st.radio("Scope of Work", ["Repair Bulb & Ballast", "Bypass Ballast (Direct-Wire LED Conversion)", "Full Fixture Replacement"])
    
    qty = st.number_input("Quantity of Fixtures", min_value=1, value=10)
    
    if job_scope == "Repair Bulb & Ballast":
        lamp_type = st.selectbox("Lamp Type", ["T8", "T12", "T5"])
        lamps_per_fix = st.slider("Lamps per Fixture", 2, 4, 3)
        
        base_hrs = 0.75 * qty
        raw_mat = (qty * 28.50) + (qty * lamps_per_fix * 6.50) # Ballast + Lamps
        mat_notes = f"{qty}x Electronic Ballasts, {qty * lamps_per_fix}x {lamp_type} Tubes"
        
    elif job_scope == "Bypass Ballast (Direct-Wire LED Conversion)":
        base_hrs = 0.60 * qty
        raw_mat = qty * 2 * 9.50 # Direct Wire LED Tubes + Non-shunted tombstones
        mat_notes = f"{qty * 2}x Type-B Direct-Wire LED Tubes & Tombstones (Ballast Removed)"
        
    else: # Full Replacement
        base_hrs = 1.25 * qty
        raw_mat = qty * 85.00
        mat_notes = f"{qty}x Integrated LED Commercial Fixtures"
        
    total_hours = base_hrs * crew_mult

# --- CATEGORY 3: DEVICES & RECEPTACLES ---
elif category == "Devices & Receptacles":
    st.subheader("🔌 Devices & Switches")
    
    device_type = st.selectbox("Device Type", ["Standard 15A/20A Outlet", "GFCI Outlet (Outdoor/Wet)", "Single Pole Switch", "3-Way Switch", "Smart Switch"])
    qty = st.number_input("Quantity to Swap", min_value=1, value=5)
    
    is_outdoor = st.checkbox("Outdoor Weatherproof Box / While-In-Use Cover Needed?")
    
    unit_mat = 2.25 if "Standard Outlet" in device_type else (22.00 if "GFCI" in device_type else (3.50 if "Single" in device_type else 18.00))
    if is_outdoor: unit_mat += 18.50 # Weatherproof cover + box
    
    raw_mat = unit_mat * qty
    total_hours = (0.35 * qty + (0.5 if is_outdoor else 0)) * crew_mult
    mat_notes = f"{qty}x {device_type}" + (" + Weatherproof Covers" if is_outdoor else "")

# --- CATEGORY 4: CONDUIT & DEDICATED CIRCUITS ---
elif category == "Conduit & Dedicated Circuit Runs":
    st.subheader("⚡ Dedicated Circuit Runs & Hybrid Conduit")
    
    amps = st.selectbox("Circuit Amperage", ["20A (12 AWG)", "30A (10 AWG)", "40A (8 AWG)", "50A (6 AWG)"])
    run_length = st.number_input("Total Run Distance (Feet)", min_value=10, value=60)
    
    wiring_style = st.selectbox("Wiring Method / Transition", ["100% EMT Conduit", "100% PVC Conduit", "100% Romex / MC", "Hybrid: EMT outside -> Junction Box -> Romex/MC inside"])
    
    breaker_cost = 15.00 if "20A" in amps else (32.00 if "30A" in amps else 125.00) # GFCI breaker assumed for 50A
    
    if "100% EMT" in wiring_style:
        raw_mat = breaker_cost + (run_length * 1.2) + (run_length * 0.35 * 3) # Pipe + THHN
        base_hrs = 2.5 + (run_length / 100.0) * 4.0
    elif "Hybrid" in wiring_style:
        emt_ft = st.number_input("Feet of EMT on Exterior", value=20)
        raw_mat = breaker_cost + (emt_ft * 1.2) + ((run_length - emt_ft) * 1.8) + 18.50 # Pipe + Cable + J-Box
        base_hrs = 2.5 + (run_length / 100.0) * 3.0
    else:
        raw_mat = breaker_cost + (run_length * 2.10)
        base_hrs = 2.0 + (run_length / 100.0) * 2.0
        
    total_hours = base_hrs * crew_mult
    mat_notes = f"Breaker, {run_length}ft Wire/Conduit package for {amps}"

# --- CATEGORY 5: TRENCHING & UNDERGROUND ---
elif category == "Trenching & Underground Burial":
    st.subheader("🚜 NEC Underground Trenching & Cable")
    
    nec_method = st.selectbox(
        "NEC Wiring Method & Burial Depth (Table 300.5)",
        [
            "Direct Burial UF-B Cable (24 Inches Min Depth)",
            "Schedule 40/80 PVC Conduit (18 Inches Min Depth)",
            "120V Resi GFCI Protected Circuit (12 Inches Min Depth)",
            "Rigid Metal Conduit - RMC (6 Inches Min Depth)"
        ]
    )
    
    trench_len = st.number_input("Trench Length (Linear Feet)", min_value=5, value=30)
    dig_type = st.radio("Digging Method", ["Hand Digging (Standard Clay/Soil)", "Machine / Trenching Tool"], horizontal=True)
    
    depth_inches = 24 if "24 Inches" in nec_method else (18 if "18 Inches" in nec_method else (12 if "12 Inches" in nec_method else 6))
    
    hrs_per_10ft = (2.5 if dig_type == "Hand Digging" else 1.0) * (depth_inches / 12.0)
    total_hours = ((trench_len / 10.0) * hrs_per_10ft + 2.0) * crew_mult
    
    wire_cost_per_ft = 2.25 if "Direct Burial" in nec_method else 3.10
    raw_mat = trench_len * wire_cost_per_ft
    mat_notes = f"{trench_len}ft Wire/Conduit rated for {depth_inches}\" underground burial"

# --- CATEGORY 6: GENERATORS & INTERLOCKS ---
elif category == "Generators & Interlock Kits":
    st.subheader("🔋 Generator Solutions")
    
    gen_type = st.selectbox("Generator Package", ["Portable Generator Interlock Kit + 30A/50A Inlet Box", "Full Generac Whole-Home Standby System"])
    
    if "Interlock" in gen_type:
        amps = st.radio("Inlet Box Amperage", ["30 Amp", "50 Amp"], horizontal=True)
        dist = st.number_input("Distance from Panel to Inlet Box (Feet)", min_value=5, value=20)
        
        raw_mat = (85.00 if "30" in amps else 135.00) + 75.00 + (dist * 3.50) # Inlet + Interlock + Wire
        total_hours = (3.5 + (dist / 50.0)) * crew_mult
        mat_notes = f"Panel Interlock Kit, {amps} Outdoor Power Inlet Box, {dist}ft Heavy Wire"
    else:
        kw_size = st.selectbox("Generac System Size", ["22kW Standby", "24kW Standby", "26kW Standby"])
        raw_mat = (5800.00 if "22kW" in kw_size else 6400.00) + 850.00 # Gen + ATS + Pad/Materials
        total_hours = 16.0 * crew_mult # 2-day install base
        mat_notes = f"{kw_size} Generac Generator, Whole House Transfer Switch, Concrete Pad & Battery"

# ==========================================
# ESTIMATE SUMMARY OUTPUT
# ==========================================
st.markdown("---")
st.header("📊 Job Estimate Summary")

marked_mat = raw_mat * mat_markup
labor_cost = total_hours * hourly_rate
grand_total = labor_cost + marked_mat + trip_fee

col1, col2 = st.columns(2)
with col1:
    st.metric("Labor Charge", f"${labor_cost:.2f}", f"{total_hours:.1f} Hours")
    st.metric("Materials (Marked Up)", f"${marked_mat:.2f}", f"{mat_markup*100-100:.0f}% Markup")

with col2:
    st.metric("Gas / Dispatch Fee", f"${trip_fee:.2f}")
    st.metric("GRAND TOTAL", f"${grand_total:.2f}")

st.info(f"**Material Notes:** {mat_notes if 'mat_notes' in locals() else 'Standard materials included.'}")
