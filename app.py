
import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from functools import lru_cache
import plotly.graph_objects as go

st.set_page_config(
    page_title="Tent Thermal Guardian",
    page_icon="⛺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CONFIGURATION
# ============================================================

APP_TITLE = "⛺ Tent Thermal Guardian"

zones_data = {
    "دير البلح": {
        "lat": 31.417,
        "lon": 34.351,
        "demo_population": 8500,
        "demo_tents": 1200,
        "vulnerable_ratio": 0.35
    },
    "خان يونس": {
        "lat": 31.346,
        "lon": 34.306,
        "demo_population": 6200,
        "demo_tents": 850,
        "vulnerable_ratio": 0.32
    },
    "رفح": {
        "lat": 31.018,
        "lon": 34.254,
        "demo_population": 4800,
        "demo_tents": 680,
        "vulnerable_ratio": 0.30
    },
    "النصيرات": {
        "lat": 31.467,
        "lon": 34.391,
        "demo_population": 5200,
        "demo_tents": 740,
        "vulnerable_ratio": 0.34
    }
}

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>

* {
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: "Segoe UI", Tahoma, Arial, sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0b0807 0%, #17100b 50%, #0f0906 100%);
    color: #fff5ef;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1c1009 0%, #2a1307 100%);
    border-right: 2px solid #ff5a00;
}

[data-testid="stHeader"] {
    background: transparent;
}

h1 {
    color: #ff5a00 !important;
    font-size: 3rem !important;
    font-weight: 800 !important;
}

h2, h3 {
    color: #ffb703 !important;
}

p, li, label {
    color: #fff5ef !important;
}

.stMetric {
    background: linear-gradient(135deg, #241209, #160c07);
    border: 1px solid #ff5a00;
    border-radius: 16px;
    padding: 15px;
    box-shadow: 0 8px 30px rgba(255,90,0,.15);
}

.hero {
    background:
        radial-gradient(circle at top right, rgba(255,183,3,.18), transparent 35%),
        linear-gradient(135deg, #241008, #100805);
    border: 2px solid #ff5a00;
    border-radius: 22px;
    padding: 35px;
    margin: 15px 0 25px 0;
    box-shadow: 0 15px 50px rgba(255,90,0,.18);
}

.risk-card {
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    margin: 20px 0;
}

.risk-critical {
    background: linear-gradient(135deg,#780000,#c1121f);
    border: 2px solid #ff3b00;
}

.risk-high {
    background: linear-gradient(135deg,#9f1d20,#ff5400);
    border: 2px solid #ff9d00;
}

.risk-medium {
    background: linear-gradient(135deg,#b77900,#ff9f1c);
    border: 2px solid #ffd166;
}

.risk-low {
    background: linear-gradient(135deg,#075985,#0891b2);
    border: 2px solid #22d3ee;
}

.score {
    font-size: 4rem;
    font-weight: 900;
    color: #fff;
}

.badge {
    display: inline-block;
    padding: 7px 16px;
    border-radius: 20px;
    background: linear-gradient(135deg,#ff5400,#ffb703);
    color: #130a05;
    font-weight: 800;
}

.info-box {
    background: linear-gradient(135deg,#211109,#150a06);
    border: 1px solid #ff5a00;
    border-radius: 15px;
    padding: 22px;
    margin: 15px 0;
}

.warning-box {
    background: rgba(193,18,31,.18);
    border-left: 5px solid #c1121f;
    padding: 18px;
    border-radius: 10px;
    margin: 15px 0;
}

.success-box {
    background: rgba(6,182,212,.12);
    border-left: 5px solid #06b6d4;
    padding: 18px;
    border-radius: 10px;
    margin: 15px 0;
}

.priority-card {
    background: linear-gradient(135deg,#211109,#130906);
    border: 1px solid #ff5a00;
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
}

.footer {
    text-align: center;
    padding: 35px 10px;
    margin-top: 40px;
    border-top: 1px solid #ff5a00;
    color: #ddd;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# WEATHER API
# ============================================================

@st.cache_data(ttl=600)
def fetch_weather_api(lat, lon):

    try:

        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}"
            f"&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m"
            "&hourly=temperature_2m,relative_humidity_2m"
            "&forecast_days=2"
            "&timezone=auto"
        )

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        current = data.get("current", {})
        hourly = data.get("hourly", {})

        return {
            "success": True,
            "temp": float(current.get("temperature_2m")),
            "humidity": float(current.get("relative_humidity_2m")),
            "hourly_temps": hourly.get("temperature_2m", []),
            "hourly_humidity": hourly.get(
                "relative_humidity_2m", []
            ),
            "hourly_times": hourly.get("time", []),
            "timezone": data.get("timezone", "auto")
        }

    except Exception:
        return {
            "success": False,
            "temp": 35.0,
            "humidity": 60.0,
            "hourly_temps": [],
            "hourly_humidity": [],
            "hourly_times": [],
            "timezone": "auto"
        }

# ============================================================
# THERMAL MODEL
# ============================================================

def calculate_tent_temperature(
    external_temp,
    humidity,
    ventilation,
    solar_exposure=4
):

    external_temp = float(external_temp)
    humidity = float(np.clip(humidity, 0, 100))

    ventilation_effect = {
        "ضعيف (خيمة مغلقة)": 0.24,
        "متوسط": 0.14,
        "جيد": 0.07
    }

    vent_factor = ventilation_effect.get(
        ventilation,
        0.14
    )

    solar_gain = min(
        max(float(solar_exposure), 0),
        8
    ) * 0.75

    humidity_gain = max(
        humidity - 40,
        0
    ) * 0.025

    temperature_gain = max(
        external_temp - 20,
        0
    ) * vent_factor

    estimated_temp = (
        external_temp
        + temperature_gain
        + solar_gain
        + humidity_gain
    )

    return round(estimated_temp, 1)

# ============================================================
# DEW POINT
# ============================================================

def calculate_dew_point(temp_c, humidity):

    try:

        temp_c = float(temp_c)
        humidity = float(np.clip(humidity, 1, 100))

        a = 17.27
        b = 237.7

        alpha = (
            (a * temp_c) /
            (b + temp_c)
        ) + np.log(humidity / 100)

        dew_point = (
            b * alpha /
            (a - alpha)
        )

        return round(dew_point, 1)

    except Exception:
        return temp_c

# ============================================================
# ESTIMATED THERMAL STRESS
# ============================================================

@lru_cache(maxsize=512)
def calculate_estimated_thermal_stress_index(
    temp_c,
    humidity_pct,
    solar_radiation=500
):

    try:

        temp = float(temp_c)
        humidity = float(
            np.clip(humidity_pct, 1, 100)
        )

        dew_point = calculate_dew_point(
            temp,
            humidity
        )

        solar_factor = (
            min(max(float(solar_radiation), 0), 1000)
            / 1000
        )

        humidity_factor = (
            max(humidity - 40, 0)
            * 0.025
        )

        dew_factor = max(
            dew_point - 15,
            0
        ) * 0.08

        solar_component = (
            solar_factor * 2.5
        )

        index = (
            temp
            + humidity_factor
            + dew_factor
            + solar_component
        )

        return round(index, 1)

    except Exception:
        return float(temp_c)

# ============================================================
# HEAT INDEX
# ============================================================

def calculate_heat_index(temp_c, humidity):

    try:

        temp_c = float(temp_c)
        rh = float(
            np.clip(humidity, 0, 100)
        )

        if temp_c < 27:
            return round(temp_c, 1)

        temp_f = (
            temp_c * 9 / 5
        ) + 32

        hi_f = (
            -42.379
            + 2.04901523 * temp_f
            + 10.14333127 * rh
            - 0.22475541 * temp_f * rh
            - 0.00683783 * temp_f ** 2
            - 0.05481717 * rh ** 2
            + 0.00122874 * temp_f ** 2 * rh
            + 0.00085282 * temp_f * rh ** 2
            - 0.00000199 * temp_f ** 2 * rh ** 2
        )

        hi_c = (
            hi_f - 32
        ) * 5 / 9

        return round(hi_c, 1)

    except Exception:
        return round(float(temp_c), 1)

# ============================================================
# RISK ENGINE
# ============================================================

def assess_thermal_risk(index):

    index = float(index)

    if index >= 38:
        return {
            "score": 100,
            "level": "🔴 حرج جداً",
            "color": "#c1121f",
            "css": "risk-critical",
            "action": "تدخل فوري",
            "reason": "المؤشر الحراري المقدّر مرتفع جداً"
        }

    if index >= 35:
        return {
            "score": 90,
            "level": "🔴 خطير جداً",
            "color": "#e63946",
            "css": "risk-critical",
            "action": "تقليل التعرض فوراً",
            "reason": "الظروف الحرارية تشير إلى خطر مرتفع"
        }

    if index >= 32:
        return {
            "score": 78,
            "level": "🟠 خطر مرتفع",
            "color": "#ff5400",
            "css": "risk-high",
            "action": "زيادة التهوية والتبريد",
            "reason": "المؤشر يتجاوز مستوى التحذير المرتفع"
        }

    if index >= 29:
        return {
            "score": 62,
            "level": "🟡 تحذير",
            "color": "#ffb703",
            "css": "risk-medium",
            "action": "مراقبة مستمرة",
            "reason": "وجود إجهاد حراري محتمل"
        }

    if index >= 26:
        return {
            "score": 45,
            "level": "🟡 منخفض-متوسط",
            "color": "#ffd166",
            "css": "risk-medium",
            "action": "مراقبة روتينية",
            "reason": "الظروف تحتاج إلى متابعة"
        }

    return {
        "score": 20,
        "level": "🟢 منخفض",
        "color": "#06b6d4",
        "css": "risk-low",
        "action": "مراقبة روتينية",
        "reason": "المؤشر الحراري المقدّر منخفض نسبياً"
    }

# ============================================================
# PRIORITY ENGINE
# ============================================================

def calculate_priority_score(
    thermal_score,
    population,
    tents,
    vulnerable_ratio
):

    population_factor = min(
        population / 10000,
        1
    ) * 15

    tent_factor = min(
        tents / 1500,
        1
    ) * 10

    vulnerable_factor = (
        vulnerable_ratio * 20
    )

    score = (
        thermal_score * 0.55
        + population_factor
        + tent_factor
        + vulnerable_factor
    )

    return round(
        min(score, 100),
        1
    )

# ============================================================
# FORECAST
# ============================================================

def get_forecast(weather, ventilation):

    results = []

    times = weather.get(
        "hourly_times",
        []
    )

    temps = weather.get(
        "hourly_temps",
        []
    )

    humidity = weather.get(
        "hourly_humidity",
        []
    )

    if not weather.get("success") or not temps:

        return results

    now = datetime.now()

    target_index = None

    for i, value in enumerate(times):

        try:
            api_time = datetime.fromisoformat(
                value
            )

            if api_time >= now:
                target_index = i
                break

        except Exception:
            continue

    if target_index is None:
        target_index = 0

    for hour_ahead in range(1, 7):

        idx = target_index + hour_ahead

        if idx >= len(temps):
            break

        ext_temp = float(
            temps[idx]
        )

        rh = float(
            humidity[idx]
        )

        tent_temp = calculate_tent_temperature(
            ext_temp,
            rh,
            ventilation,
            4
        )

        thermal_index = calculate_estimated_thermal_stress_index(
            tent_temp,
            rh
        )

        risk = assess_thermal_risk(
            thermal_index
        )

        time_display = times[idx]

        try:

            time_display = datetime.fromisoformat(
                time_display
            ).strftime("%H:%M")

        except Exception:
            pass

        results.append({
            "hour": hour_ahead,
            "time": time_display,
            "external": round(ext_temp, 1),
            "tent": round(tent_temp, 1),
            "humidity": round(rh, 1),
            "index": thermal_index,
            "risk": risk
        })

    return results

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">

<h1>⛺ Tent Thermal Guardian</h1>

<p style="
font-size:1.25rem;
color:#ffb703 !important;
font-weight:600;
">
نظام ذكي للمراقبة والتنبؤ بالمخاطر الحرارية في مخيمات النزوح
</p>

<p>
تحليل بيانات الطقس الحقيقية، تقدير الظروف الحرارية داخل الخيام،
وتحديد المناطق ذات الأولوية للتدخل.
</p>

<br>

<span class="badge">
🌦️ Real-Time Weather
</span>

<span class="badge">
🧠 Intelligent Risk Engine
</span>

<span class="badge">
📊 Priority Analysis
</span>

<span class="badge">
⏰ Forecasting
</span>

</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ⚙️ إعدادات النظام")

    selected_zone_name = st.selectbox(
        "📍 المنطقة",
        list(zones_data.keys())
    )

    ventilation = st.selectbox(
        "🌬️ مستوى التهوية",
        [
            "ضعيف (خيمة مغلقة)",
            "متوسط",
            "جيد"
        ]
    )

    solar_hours = st.slider(
        "☀️ التعرض الشمسي المتوقع",
        min_value=0,
        max_value=8,
        value=4
    )

    st.divider()

    if st.button(
        "🔄 تحديث بيانات الطقس",
        use_container_width=True
    ):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    st.markdown(
        "### 🛰️ مصدر البيانات"
    )

    st.info(
        "Open-Meteo Weather API"
    )

    st.caption(
        "البيانات الجوية يتم جلبها من API مفتوح."
    )

    st.divider()

    st.caption(
        "Tent Thermal Guardian v7.0"
    )

# ============================================================
# SELECTED ZONE
# ============================================================

zone = zones_data[
    selected_zone_name
]

weather = fetch_weather_api(
    zone["lat"],
    zone["lon"]
)

external_temp = weather["temp"]
humidity = weather["humidity"]

tent_temp = calculate_tent_temperature(
    external_temp,
    humidity,
    ventilation,
    solar_hours
)

heat_index = calculate_heat_index(
    tent_temp,
    humidity
)

thermal_index = calculate_estimated_thermal_stress_index(
    tent_temp,
    humidity,
    solar_hours * 125
)

risk = assess_thermal_risk(
    thermal_index
)

priority = calculate_priority_score(
    risk["score"],
    zone["demo_population"],
    zone["demo_tents"],
    zone["vulnerable_ratio"]
)

# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 المراقبة",
    "🗺️ خريطة المخاطر",
    "📈 التنبؤ والتحليل",
    "🧠 المنهجية"
])

# ============================================================
# TAB 1
# ============================================================

with tab1:

    st.markdown(
        f"## 📍 الوضع الحالي — {selected_zone_name}"
    )

    if not weather["success"]:

        st.warning(
            "تعذر الوصول إلى بيانات الطقس الحالية. "
            "يتم استخدام قيم احتياطية للعرض."
        )

        st.markdown(
        f"""
        <div class="risk-card {risk['css']}">
            <div style="font-size:1.4rem;">مستوى الخطر الحالي</div>
            <div class="score">{risk['score']}/100</div>
            <div style="font-size:2rem;font-weight:800;">{risk['level']}</div>
            <p style="margin-top:15px;">{risk['reason']}</p>
            <p style="color:#fff !important; font-size:1.15rem; font-weight:700;">
                الإجراء المقترح: {risk['action']}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "🌡️ حرارة الخارج",
            f"{external_temp:.1f} °C"
        )

    with c2:
        st.metric(
            "⛺ حرارة الخيمة المقدّرة",
            f"{tent_temp:.1f} °C"
        )

    with c3:
        st.metric(
            "💧 الرطوبة",
            f"{humidity:.0f}%"
        )

    with c4:
        st.metric(
            "🔥 Heat Index",
            f"{heat_index:.1f} °C"
        )

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "🎯 Thermal Score",
            f"{risk['score']}/100"
        )

    with c2:
        st.metric(
            "🚨 Priority Score",
            f"{priority}/100"
        )

    with c3:
        st.metric(
            "👥 السكان المحاكى",
            f"{zone['demo_population']:,}"
        )

    st.markdown(
        '<div class="info-box">'
        '<b>📌 Priority Score</b><br>'
        'درجة أولوية التدخل تجمع بين مستوى الخطر الحراري، '
        'حجم السكان، عدد الخيام، ونسبة الفئات الهشة.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("## 🎯 الإجراءات المقترحة")

    a1, a2, a3 = st.columns(3)

    with a1:

        st.markdown("""
        <div class="priority-card">

        <h3>1️⃣ التبريد والتهوية</h3>

        <ul>
        <li>تحسين حركة الهواء داخل الخيمة</li>
        <li>توفير مناطق مظللة</li>
        <li>تقليل التعرض المباشر للشمس</li>
        </ul>

        </div>
        """, unsafe_allow_html=True)

    with a2:

        st.markdown("""
        <div class="priority-card">

        <h3>2️⃣ مراقبة الفئات الهشة</h3>

        <ul>
        <li>الأطفال</li>
        <li>كبار السن</li>
        <li>الأشخاص الأكثر عرضة للإجهاد الحراري</li>
        </ul>

        </div>
        """, unsafe_allow_html=True)

        
        with a3:
            st.markdown("""
             <div class="priority-card">
             <h3>3️⃣ الاستعداد والاستجابة</h3>
             <ul>
             <li>توفير مياه وسوائل مناسبة</li>
            <li>رفع مستوى المراقبة</li>
            <li>طلب المساعدة الطبية عند الحاجة</li>
            </ul>
            </div>
             """, unsafe_allow_html=True)


    st.markdown(
        """
        <div class="warning-box">
        ⚠️ <b>تنبيه:</b>
        المؤشر الحراري المستخدم هنا تقديري وليس قياس WBGT مباشر.
        القرارات الطبية يجب أن تعتمد على التقييم الطبي والقياسات الميدانية المناسبة.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## 📊 بيانات المنطقة")

    d1, d2, d3 = st.columns(3)

    with d1:
        st.metric(
            "👥 السكان",
            f"{zone['demo_population']:,}"
        )

    with d2:
        st.metric(
            "⛺ الخيام",
            f"{zone['demo_tents']:,}"
        )

    with d3:
        st.metric(
            "🧑‍🤝‍🧑 نسبة الفئات الهشة",
            f"{zone['vulnerable_ratio'] * 100:.0f}%"
        )

    st.markdown(
        '<span class="badge">Demo / Simulated Data</span>',
        unsafe_allow_html=True
    )


    

# ============================================================
# TAB 2
# ============================================================

with tab2:

    st.markdown(
        "## 🗺️ خريطة المخاطر لجميع المناطق"
    )

    all_zones = []

    for name, info in zones_data.items():

        w = fetch_weather_api(
            info["lat"],
            info["lon"]
        )

        t = calculate_tent_temperature(
            w["temp"],
            w["humidity"],
            "متوسط",
            4
        )

        idx = calculate_estimated_thermal_stress_index(
            t,
            w["humidity"],
            500
        )

        r = assess_thermal_risk(idx)

        p = calculate_priority_score(
            r["score"],
            info["demo_population"],
            info["demo_tents"],
            info["vulnerable_ratio"]
        )

        all_zones.append({
            "المنطقة": name,
            "الخارج": round(w["temp"], 1),
            "الرطوبة": round(w["humidity"], 1),
            "حرارة الخيمة": round(t, 1),
            "المؤشر": idx,
            "الخطر": r["score"],
            "الأولوية": p,
            "المستوى": r["level"],
            "lat": info["lat"],
            "lon": info["lon"]
        })

    zones_df = pd.DataFrame(
        all_zones
    )

    zones_df = zones_df.sort_values(
        "الأولوية",
        ascending=False
    ).reset_index(drop=True)

    zones_df.insert(
        0,
        "الترتيب",
        range(1, len(zones_df) + 1)
    )

    st.dataframe(
        zones_df[
            [
                "الترتيب",
                "المنطقة",
                "الخارج",
                "الرطوبة",
                "حرارة الخيمة",
                "المؤشر",
                "الخطر",
                "الأولوية",
                "المستوى"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        "### 🚨 ترتيب أولويات التدخل"
    )

    for _, row in zones_df.iterrows():

        if row["الأولوية"] >= 75:
            icon = "🔴"
        elif row["الأولوية"] >= 55:
            icon = "🟠"
        elif row["الأولوية"] >= 40:
            icon = "🟡"
        else:
            icon = "🟢"

        st.markdown(
            f"""
            <div class="priority-card">

            <h3>
            {icon} #{int(row['الترتيب'])}
            {row['المنطقة']}
            </h3>

            <p>
            Thermal Risk:
            <b>{row['الخطر']}/100</b>
            |
            Priority:
            <b>{row['الأولوية']}/100</b>
            |
            Tent:
            <b>{row['حرارة الخيمة']}°C</b>
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### 📊 مقارنة الأولويات")

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=zones_df["المنطقة"],
            y=zones_df["الأولوية"],
            text=zones_df["الأولوية"],
            textposition="auto",
            name="Priority Score"
        )
    )

    fig.update_layout(
        height=420,
        title="Priority Score حسب المنطقة",
        xaxis_title="المنطقة",
        yaxis_title="Priority Score",
        yaxis=dict(range=[0, 100]),
        plot_bgcolor="#170c07",
        paper_bgcolor="#170c07",
        font=dict(color="#ffffff")
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("### 🌍 الموقع الجغرافي")

    map_df = zones_df[
        ["lat", "lon"]
    ].copy()

    map_df["size"] = zones_df[
        "الأولوية"
    ]

    st.map(
        map_df,
        latitude="lat",
        longitude="lon",
        size="size"
    )

# ============================================================
# TAB 3
# ============================================================

with tab3:

    st.markdown(
        "## 📈 التنبؤ الحراري للساعات القادمة"
    )

    forecast = get_forecast(
        weather,
        ventilation
    )

    if not forecast:

        st.warning(
            "بيانات التنبؤ غير متاحة حالياً."
        )

    else:

        forecast_df = pd.DataFrame([
            {
                "الوقت": x["time"],
                "الخارج": x["external"],
                "الخيمة": x["tent"],
                "الرطوبة": x["humidity"],
                "المؤشر": x["index"],
                "الخطر": x["risk"]["score"]
            }
            for x in forecast
        ])

        st.dataframe(
            forecast_df,
            use_container_width=True,
            hide_index=True
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=forecast_df["الوقت"],
                y=forecast_df["الخارج"],
                mode="lines+markers",
                name="الخارج"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=forecast_df["الوقت"],
                y=forecast_df["الخيمة"],
                mode="lines+markers",
                name="الخيمة المقدّرة"
            )
        )

        fig.update_layout(
            title="درجة الحرارة المتوقعة",
            xaxis_title="الوقت",
            yaxis_title="°C",
            height=420,
            plot_bgcolor="#170c07",
            paper_bgcolor="#170c07",
            font=dict(color="#ffffff")
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        fig2 = go.Figure()

        fig2.add_trace(
            go.Scatter(
                x=forecast_df["الوقت"],
                y=forecast_df["المؤشر"],
                mode="lines+markers",
                fill="tozeroy",
                name="Thermal Stress"
            )
        )

        fig2.add_hline(
            y=29,
            line_dash="dash",
            annotation_text="تحذير"
        )

        fig2.add_hline(
            y=32,
            line_dash="dash",
            annotation_text="خطر مرتفع"
        )

        fig2.add_hline(
            y=35,
            line_dash="dash",
            annotation_text="خطر شديد"
        )

        fig2.update_layout(
            title="التغير المتوقع في المؤشر الحراري",
            xaxis_title="الوقت",
            yaxis_title="Estimated Thermal Stress",
            height=420,
            plot_bgcolor="#170c07",
            paper_bgcolor="#170c07",
            font=dict(color="#ffffff")
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        max_prediction = max(
            forecast,
            key=lambda x: x["index"]
        )

        st.markdown(
            f"""
            <div class="info-box">

            <h3>🔮 أعلى خطر متوقع</h3>

            <p>
            الوقت:
            <b>{max_prediction['time']}</b>
            </p>

            <p>
            المؤشر:
            <b>{max_prediction['index']}°C</b>
            </p>

            <p>
            الحالة:
            <b>{max_prediction['risk']['level']}</b>
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

# ============================================================
# TAB 4
# ============================================================

with tab4:

    st.markdown(
        "## 🧠 منهجية Tent Thermal Guardian"
    )

    st.markdown("""
    <div class="info-box">

    <h3>1️⃣ Weather Data</h3>

    يتم الحصول على درجة الحرارة والرطوبة الحالية
    وتوقعات الساعات القادمة من Open-Meteo API.

    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">

    <h3>2️⃣ Tent Temperature Estimation</h3>

    يتم تقدير درجة الحرارة داخل الخيمة اعتماداً على
    درجة الحرارة الخارجية والرطوبة ومستوى التهوية
    والتعرض الشمسي.

    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">

    <h3>3️⃣ Estimated Thermal Stress Index</h3>

    يتم دمج درجة الحرارة والرطوبة ونقطة الندى
    والتعرض الشمسي في مؤشر حراري تقديري.

    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">

    <h3>4️⃣ Intelligent Risk Engine</h3>

    محرك Rule-Based قابل للتفسير يقوم بتحويل
    المؤشر الحراري إلى مستوى خطر ودرجة من 100.

    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">

    <h3>5️⃣ Priority Engine</h3>

    يتم دمج الخطر الحراري مع حجم السكان وعدد الخيام
    ونسبة الفئات الهشة لإنشاء Priority Score.

    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">

    <h3>6️⃣ Forecasting</h3>

    يتم تطبيق النموذج نفسه على بيانات الساعات القادمة
    لإظهار التغير المتوقع في الخطر الحراري.

    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("## 🔬 حدود النظام")

    st.markdown("""
    <div class="warning-box">

    <b>المؤشر المستخدم Estimated وليس WBGT مباشر.</b>

    <br><br>

    القياس الدقيق لـ WBGT يحتاج إلى قياسات ميدانية
    وأجهزة مناسبة تشمل ظروف الإشعاع والحرارة والرطوبة
    وحركة الهواء.

    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="success-box">

    <b>قابلية التطوير إلى Machine Learning</b>

    <br><br>

    عند توفر بيانات ميدانية حقيقية من الخيام،
    يمكن استخدام درجة الحرارة الداخلية المقاسة
    وحالات الإجهاد الحراري لمعايرة النموذج
    وتدريب نموذج ML أكثر دقة.

    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 🚀 التطوير المستقبلي")

    future_features = [
        "📡 ربط مستشعرات ESP32 لقياس الحرارة والرطوبة داخل الخيمة",
        "🌡️ استخدام مستشعرات ميدانية لمعايرة النموذج",
        "🤖 تدريب Machine Learning Model على بيانات حقيقية",
        "🚨 إرسال تنبيهات تلقائية",
        "📱 تطبيق هاتف للفرق الميدانية",
        "🗺️ خريطة أكثر تفصيلاً للمخاطر",
        "📊 تخزين البيانات التاريخية وتحليلها",
        "🏥 ربط النظام ببيانات الحالات الحرارية عند توفرها"
    ]

    for item in future_features:
        st.markdown(
            f"- {item}"
        )

# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">

<h3>⛺ Tent Thermal Guardian</h3>

<p>
Intelligent Thermal Risk Monitoring for Displacement Camps
</p>

<br>

<span class="badge">🌦️ Real Weather</span>
<span class="badge">🧠 Explainable Risk Engine</span>
<span class="badge">🎯 Priority Scoring</span>
<span class="badge">⏰ Forecasting</span>
<span class="badge">🌍 Humanitarian Technology</span>

<br><br>

<p>
Developed for FortyGuard Hackathon 2026
</p>

<p>
Version 7.0
</p>

</div>
""", unsafe_allow_html=True)
