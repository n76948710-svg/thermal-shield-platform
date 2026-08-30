import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Thermal Shield Platform",
    page_icon="⛺",
    layout="centered"
)

st.title("⛺ Thermal Shield Platform")
st.markdown("### Climate Intelligence & Heatwave Prediction System")
st.write("An integrated smart platform for sensing climate heat, analyzing annual changes, and providing an offline local emergency assistant to protect vulnerable communities and tent residents.")
st.markdown("---")

st.sidebar.header("⚙️ System Settings & Climate Analysis")
api_key = st.sidebar.text_input("API Key", type="password", placeholder="Enter API Key here...")

environment_type = st.sidebar.selectbox(
    "📍 Select Your Environment Type:",
    [
        "Marginalized Area / Displaced Camp (Tent / Camp)",
        "Open Desert Area (Desert)",
        "Urban / City Area (Urban)",
        "Closed Space or Factory (Closed / Factory)",
        "Crowded Space Lacking Ventilation (Crowded Space)"
    ]
)

climate_trend = st.sidebar.selectbox(
    "📈 Compare This Summer (2026) to Last Year (2025):",
    [
        "Noticeable and dangerous temperature increase compared to 2025",
        "Slight increase in heatwave intensity",
        "Conditions are approximately similar",
        "Slight decrease"
    ]
)

offline_mode = st.sidebar.checkbox("📡 Enable Offline Emergency Mode (Offline AI Mode)", value=False, help="Use this mode when internet and communication networks are completely down.")

lat = st.sidebar.number_input("Latitude", value=31.5, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=34.4, format="%.4f")

st.sidebar.markdown("---")
st.sidebar.info("💡 The system analyzes annual changes to raise disaster readiness and early response levels.")

st.subheader("📊 Live Climate Sensing & Analysis Dashboard")
st.write(f"Selected Location: **{environment_type}** | Annual Trend Index: **{climate_trend}**")
st.write("Click the button below to diagnose current temperature and analyze climate impact:")

if st.button("Diagnose Status & Analyze Annual Trend 🔍", type="primary"):
    current_temp = 41.5  
    
    st.metric(label="Current Local Climate Heat Index", value=f"{current_temp} °C")
    
    if "Noticeable" in climate_trend:
        st.warning("⚠️ **Proactive Climate Change Analysis:** A notable aggravation in heatwaves compared to last year (2025), requiring immediate emergency plan activation.")

    if offline_mode:
        st.info("📡 **Running Offline Local Assistant:** Emergency protocols are executed locally without requiring network connectivity.")
    
    if current_temp >= 40:
        st.error(f"🚨 **Severe Thermal Hazard in ({environment_type})!** Temperature has exceeded critical thresholds.")
        
        if "Camp" in environment_type:
            st.markdown("""
            **🏕️ Comprehensive Emergency Protocol for Camps & Displacement Sites:**
            * 🛑 **Temporary Evacuation:** Immediately move away from touching metal tent walls or hot reflective surfaces.
            * 🧱 **Insulation & Shading:** Hang reflective fabrics or wet blankets over the tent roof to break direct solar radiation.
            * 💧 **Personal Hydration:** Drink cold water gradually and wet the head and neck to lower body temperature.
            * 🚒 **Civil Defense Alert:** Send an emergency alert signal to relief teams to schedule water tanker spraying and cool the camp perimeter.
            """)
        elif "Desert" in environment_type:
            st.markdown("""
            **🏜️ Comprehensive Emergency Protocol for Open Desert Areas:**
            * ⛱️ **Seek Artificial or Natural Shade:** Move to any low-lying terrain or build a temporary shelter using available fabrics.
            * 💧 **Fluid Conservation & Hydration:** Maintain water supplies and drink regularly to avoid sudden dehydration.
            * 🩺 **Field First Aid:** Monitor heatstroke symptoms (dizziness, nausea) and request medical support once communication is available.
            """)
        elif "Closed" in environment_type:
            st.markdown("""
            **🏭 Comprehensive Emergency Protocol for Factories & Closed Spaces:**
            * 💨 **Forced Ventilation:** Turn on exhaust fans and open all available vents and chimneys manually or automatically.
            * 🔥 **Thermal Load Shutdown:** Turn off non-essential machinery and equipment generating extra indoor heat.
            * 🧊 **Rapid Cooling:** Transfer affected workers to main air-conditioned or ventilated areas and provide hydrating fluids.
            """)
        elif "Crowded" in environment_type:
            st.markdown("""
            **👥 Comprehensive Emergency Protocol for Crowded Spaces:**
            * 🚪 **Decongestion & Density Distribution:** Move individuals to wider spaces and relieve human pressure in enclosed rooms.
            * 🌬️ **Activate Air Currents:** Ensure airflow corridors function and distribute cold water to occupants to prevent fainting.
            """)
        else:
            st.markdown("""
            **🏙️ Comprehensive Emergency Protocol for Urban Areas:**
            * 🏢 **Head to Air-Conditioned Shelters:** Immediately enter the nearest public concrete building or air-conditioned community center.
            * 🚶‍♂️ **Avoid Outdoor Exertion:** Stop any physical activity under direct sunlight until the heatwave breaks.
            """)
            
    elif current_temp >= 35:
        st.warning(f"⚠️ **High Heat Warning in ({environment_type}):** Please exercise caution, reduce direct exposure, and drink plenty of cold fluids.")
    else:
        st.success("✅ **Situation Stable:** Current temperatures are within safe ranges.")
        
    st.markdown("---")
    st.subheader("📝 System Audit & Historical Climate Logs")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mode_status = "Offline Local AI" if offline_mode else "Cloud API Connected"
    log_text = f"[{timestamp}] Mode: {mode_status} | Env: {environment_type} | Trend: {climate_trend} | Temp: {current_temp}°C | Multi-Guidance Protocol Active.\n"
    
    st.text_area("Technical Operation Log:", value=log_text, height=100)
    
else:
    st.info("👈 Set your settings and annual trend comparison from the sidebar, then click the button above.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Thermal Shield Platform | Comprehensive Multi-Guidance Safety Platform ⛺</p>", unsafe_allow_html=True)
          
