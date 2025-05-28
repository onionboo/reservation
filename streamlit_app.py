import streamlit as st
from datetime import datetime

# ---- Initialize reservations as dictionary ----
if 'reservations' not in st.session_state:
    st.session_state.reservations = {}

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

    # Check for duplicate
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
            st.success(f"🈯 จองสำเร็จ: คุณ{name} วันที่ {date} เวลา {time_slot} [{package}]")

# ---- Tab 2: View Bookings ----
with tab2:
    st.header("📅 เวลาที่ถูกจอง")

    view_date = st.date_input("เลือกวันที่", datetime.today())
    view_date_str = str(view_date)

    booked_list = st.session_state.reservations.get(view_date_str, [])
    time_options = [f"{hour:02d}:00" for hour in range(9, 24)]

    for t in time_options:
        match = next((entry for entry in booked_list if entry['time'] == t), None)
        if match:
            st.markdown(f"- ⛔ {t} (จองแล้ว โดยคุณ{match['name']} [{match['package']}])")
        else:
            st.markdown(f"- ✅ {t} (ว่าง)")