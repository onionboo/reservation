import streamlit as st
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import tempfile
import json

# ---- Deep convert AttrDict to native dict ----
def deep_convert(attr_dict):
    if isinstance(attr_dict, dict):
        return {k: deep_convert(v) for k, v in attr_dict.items()}
    return attr_dict

# ---- Initialize Firebase only once ----
if "firebase_app" not in st.session_state:
    firebase_dict = deep_convert(st.secrets["firebase"])
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        json.dump(firebase_dict, f)
        f.flush()
        cred = credentials.Certificate(f.name)
        firebase_admin.initialize_app(cred)
        st.session_state.firebase_app = True

db = firestore.client()
collection_name = "reservations"

# ---- Load all reservations from Firebase ----
def load_reservations():
    docs = db.collection(collection_name).stream()
    reservations = {}
    for doc in docs:
        data = doc.to_dict()
        date = data["date"]
        if date not in reservations:
            reservations[date] = []
        reservations[date].append({
            "name": data["name"],
            "time": data["time"],
            "package": data["package"]
        })
    return reservations

# ---- Save new reservation to Firebase ----
def save_reservation(name, date_str, time_slot, package):
    db.collection(collection_name).add({
        "name": name,
        "date": date_str,
        "time": time_slot,
        "package": package,
        "timestamp": datetime.now()
    })

# ---- Initialize reservations in session from Firestore ----
if "reservations" not in st.session_state:
    st.session_state.reservations = load_reservations()

st.title("🕑 Corridor of Crocus 🕊️")

tab1, tab2 = st.tabs(["📝 จองเวลา", "📅 เวลาที่ถูกจอง"])

# ---- Tab 1: Make Reservation ----
with tab1:
    st.header("📝 จองเวลา")

    name = st.text_input("ชื่อ (ชื่อเล่น)")
    date = st.date_input("วันที่ต้องการจอง", datetime.today())
    date_str = str(date)

    time_options = [f"{hour:02d}:00" for hour in range(9, 24)]
    time_slot = st.selectbox("เวลาที่ต้องการจอง", time_options)
    package = st.selectbox("แพคเกจ", ['Premium A', 'Premium B'])

    if date_str not in st.session_state.reservations:
        st.session_state.reservations[date_str] = []

    booked_times = [entry['time'] for entry in st.session_state.reservations[date_str]]
    if time_slot in booked_times:
        st.warning("⚠️ วัน/เวลานี้มีการจองไว้แล้ว โปรดเลือกช่วงเวลาอื่น ๆ")
    else:
        if st.button("จอง"):
            st.session_state.reservations[date_str].append({
                'name': name,
                'time': time_slot,
                'package': package
            })
            save_reservation(name, date_str, time_slot, package)
            st.session_state.reservations = load_reservations()  # ✅ Reload all data
            st.success(f"🈯 จองสำเร็จ: คุณ{name} วันที่ {date} เวลา {time_slot} [{package}]")

# ---- Tab 2: View Bookings ----
with tab2:
    st.header("📅 เวลาที่ถูกจอง")

    view_date = st.date_input("เลือกวันที่", datetime.today())
    view_date_str = str(view_date)

    booked_list = st.session_state.reservations.get(view_date_str, [])
    time_options = [f"{hour:02d}:00" for hour in range(8, 24)]

    for t in time_options:
        match = next((entry for entry in booked_list if entry['time'] == t), None)
        if match:
            st.markdown(f"- ⛔ {t} (จองแล้ว โดยคุณ{match['name']} [{match['package']}])")
        else:
            st.markdown(f"- ✅ {t} (ว่าง)")