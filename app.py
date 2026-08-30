import streamlit as st
import pandas as pd

st.set_page_config(page_title="منصة الدرع الحراري", page_icon="⛺", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1e2130 50%, #2c3348 100%);
        background-size: 200% 200%;
        animation: gradientAnimation 15s ease infinite;
    }
    
    @keyframes gradientAnimation {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    .stSelectbox label, .stHeader { color: #FFD700 !important; font-size: 22px !important; font-weight: bold !important; }
    
    .status-card {
        background-color: rgba(30, 33, 48, 0.8);
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .instruction-box {
        background-color: rgba(38, 39, 48, 0.9);
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #5a5a5a;
        margin-top: 12px;
        color: #f0f0f0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        font-size: 18px;
        padding: 10px 24px;
        border-radius: 10px;
        border: none;
        width: 100%;
        box-shadow: 0 4px 0 #bf3939;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ff6b6b;
        box-shadow: 0 6px 0 #bf3939;
        transform: translateY(-2px);
    }
    
    p, li { color: #e0e0e0; font-size: 17px; }
    </style>
    """, unsafe_allow_state_context=True)

st.title("⛺ منصة الدرع الحراري الذكية")
st.subheader("نظام حماية المجتمعات وسكان الخيام من موجات الحر")

st.markdown("---")

st.write("### 📍 حدد موقعك للحصول على تعليمات مخصصة:")
location = st.selectbox(
    "اختر المنطقة أو نوع السكن:",
    ["اختر من القائمة...", "مخيم نازحين (خيمة قماشية)", "مخيم لاجئين (غرف زينكو/معدن)", "منطقة ريفية (بيوت طينية/قديمة)", "منطقة حضرية مهمشة"]
)

data = {
    "مخيم نازحين (خيمة قماشية)": {
        "temp": 42.5,
        "risk": "مرتفع جداً (خطر ضربة شمس)",
        "tips": [
            "🔴 إخلاء فوري: ابتعد عن ملامسة جدران الخيمة الساخنة.",
            "💧 ترطيب مكثف: بلل أغطية الخيمة بالماء لخفض الحرارة داخلياً.",
            "🧴 وقاية شخصية: استخدام مناشف مبللة على الرأس والرقبة باستمرار."
        ]
    },
    "مخيم لاجئين (غرف زينكو/معدن)": {
        "temp": 44.0,
        "risk": "حرج (تأثير الصوبات المعدنية)",
        "tips": [
            "🧱 العزل الحراري: ضع كرتون أو قماش سميك تحت سقف الزينكو مباشرة.",
            "🌬️ التهوية المتصالبة: افتح النوافذ المتقابلة لخلق تيار هوائي.",
            "🥤 السوائل: شرب لتر ماء كل ساعتين على الأقل حتى بدون عطش."
        ]
    },
    "منطقة ريفية (بيوت طينية/قديمة)": {
        "temp": 39.5,
        "risk": "متوسط (احتباس حراري)",
        "tips": [
            "🐑 حماية الماشية: تأكد من وجود ظل كافٍ ومياه باردة للحيوانات.",
            "🪟 الإغلاق الذكي: أغلق النوافذ تماماً في ساعات الذروة (12-4 ظهراً).",
            "🥗 التغذية: تجنب الوجبات الدسمة التي تزيد حرارة الجسم."
        ]
    },
    "منطقة حضرية مهمشة": {
        "temp": 41.0,
        "risk": "مرتفع (تأثير الجزر الحرارية)",
        "tips": [
            "🌳 البحث عن الظل: التوجه لأقرب منطقة خضراء أو عامة مظللة.",
            "🚫 الأجهزة: إطفاء كافة الأجهزة الكهربائية غير الضرورية لتقليل الحرارة.",
            "📞 الطوارئ: تفعيل خط الاتصال المباشر مع فرق الدفاع المدني."
        ]
    }
}

if location != "اختر من القائمة...":
    loc_data = data[location]
    
    st.markdown(f"""
    <div class="status-card">
        <h2 style='color:#FFD700;'>تحليل حالة الموقع: {location}</h2>
        <p style='font-size:26px;'>درجة الحرارة المتوقعة: <b>{loc_data['temp']}°C</b></p>
        <p style='font-size:22px;'>مستوى الخطر: <span style='color:#FFA500;'>{loc_data['risk']}</span></p>
    </div>
    """, unsafe_allow_html=True)

    st.write("### 📋 بروتوكول الطوارئ المخصص لك:")
    for tip in loc_data['tips']:
        st.markdown(f"<div class='instruction-box'>{tip}</div>", unsafe_allow_html=True)
    
    if st.button("تأكيد استلام التعليمات وتفعيل نظام الإنذار 🔔"):
        st.success(f"تم تفعيل بروتوكول الطوارئ لمنطقة {location}. ابقَ آمناً!")

else:
    st.info("الرجاء اختيار موقعك من القائمة أعلاه لعرض لوحة التحكم والتعليمات الخاصة بك.")

st.markdown("---")
st.caption("تم تطوير هذه المنصة لحماية الأرواح في الهاكاثون - الدرع الحراري 2026")

          
