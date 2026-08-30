import streamlit as st
import pandas as pd
from datetime import datetime
# الإحداثيات المعتمدة لمشروعك في غزة
lat = 31.427537
lon = 34.475026

st.set_page_config(
    page_title="منصة الدرع الحراري",
    page_icon="⛺",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg, #0e1117 0%, #1e2130 50%, #2c3348 100%);
    background-size: 200% 200%;
    animation: gradientAnimation 15s ease infinite;
}

@keyframes gradientAnimation {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

h1, h2, h3 {
    color: #ffffff !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

div.stButton > button {
    background: linear-gradient(135deg, #FF4B2B 0%, #FF416C 100%);
    color: white;
    border-radius: 12px;
    padding: 10px 24px;
    font-weight: bold;
    border: none;
    box-shadow: 0 4px 15px rgba(255, 75, 43, 0.4);
    transition: all 0.3s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255, 75, 43, 0.6);
}
</style>
""", unsafe_allow_html=True)

st.title("⛺ منصة الدرع الحراري")
st.markdown("### نظام ذكاء المناخ والتنبؤ بموجات الحر والتخفيض السعر لحماية المجتمعات الضعيفة وسكان الخيام.")
st.markdown("---")

st.sidebar.header("إعدادات النظام وتحليل المناخ")
api_key = st.sidebar.text_input("مفتاح API", type="password")

environment_type = st.sidebar.selectbox(
    "نوع البيئة",
    ["خيمة قماشية عادية", "خيمة معزولة", "مأوى مؤقت غير عازل", "منزل متنقل (كرافان)"]
)

locations_dict = {
    "غزة - الشجاعية": {"lat": 31.527, "lon": 34.482, "temp_offset": 3.5},
    "غزة - الرمال": {"lat": 31.519, "lon": 34.448, "temp_offset": 2.5},
    "خان يونس - الأطراف": {"lat": 31.346, "lon": 34.306, "temp_offset": 4.0},
    "دير البلح - المخيمات": {"lat": 31.417, "lon": 34.350, "temp_offset": 3.0},
    "رفح - المواصي": {"lat": 31.019, "lon": 34.253, "temp_offset": 4.5},
    "إدخال إحداثيات مخصصة يدويًا": {"lat": 0.0, "lon": 0.0, "temp_offset": 3.0}
}

selected_location = st.sidebar.selectbox("حدد مكانك أو المخيم", list(locations_dict.keys()))

if selected_location == "إدخال إحداثيات مخصصة يدويًا":
    lat = st.sidebar.number_input("خط العرض (Latitude)", value=31.5, format="%.4f")
    lon = st.sidebar.number_input("خط الطول (Longitude)", value=34.4, format="%.4f")
else:
    lat = locations_dict[selected_location]["lat"]
    lon = locations_dict[selected_location]["lon"]

st.sidebar.markdown("---")
st.sidebar.info("💡 النظام مصمم خصيصاً لمساعدة الأهالي والفرق الإنسانية في رصد خطورة الحرارة الشديدة داخل الخيام.")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 لوحة المؤشرات البيئية الحالية")
    
    base_temp = 36.5
    offset = locations_dict[selected_location]["temp_offset"] if selected_location != "إدخال إحداثيات مخصصة يدويًا" else 3.5
    
    if environment_type == "خيمة قماشية عادية":
        tent_temp = base_temp + offset + 6.0
    elif environment_type == "مأوى مؤقت غير عازل":
        tent_temp = base_temp + offset + 7.5
    elif environment_type == "خيمة معزولة":
        tent_temp = base_temp + offset + 2.5
    else:
        tent_temp = base_temp + offset + 4.0

    st.metric(label="درجة الحرارة المتوقعة داخل المأوى / الخيمة", value=f"{tent_temp:.1f} °C", delta="+6.5 °C عن الخارج")
    st.metric(label="درجة الحرارة الخارجية التقريبية", value=f"{base_temp} °C")

with col2:
    st.subheader("⚠️ تقييم الخطورة")
    if tent_temp > 42:
        st.error("🚨 خطر قصوى: موجة حر قاتلة! يرجى الإخلاء المؤقت أو تبريد الخيمة فوراً.")
    elif tent_temp > 39:
        st.warning("⚠️ خطر مرتفع: احذر من ضربات الشمس والإجهاد الحراري.")
    else:
        st.info("✅ الوضع مستقر نسبياً مع ضرورة الإكثار من شرب السوائل.")

st.markdown("---")
st.subheader("🛡️ توصيات الإسعاف والتخفيف الفوري للحرارة")
st.markdown("""
* **التهوية النشطة:** ارفع أطراف القماش السفلي للخيمة قدر الإمكان للسماح بمرور الهواء وتخفيض التكدس الحراري.
* **التبريد بالماء:** رش أسطح الخيام الخارجية بالماء كل بضع ساعات للمساعدة في التبريد التبخيري.
* **الفئات الهشة:** إعطاء الأولوية القصوى للأطفال وكبار السن والأشخاص ذوي الأمراض المزمنة بنقلهم للظلال وأماكن التبريد الجماعية.
""")

