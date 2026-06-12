import streamlit as st
import os
import sys

# --- حل مشکل مسیرها در Streamlit Cloud ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

import pandas as pd
import datetime
import database as db
from utils.pdf_handler import extract_text_from_pdfs
from utils.ai_engine import generate_chat_response, extract_important_sentences, test_api_key

# --- تنظیمات صفحه ---
st.set_page_config(page_title="سامانه هوشمند دانشگاه ملی مهارت", page_icon="💎", layout="wide")

# مقداردهی اولیه دیتابیس
db.init_db()

# چک کردن اتصال API (به صورت کش شده برای سرعت بالاتر)
@st.cache_resource
def check_api():
    return test_api_key()

if not check_api():
    st.error("❌ خطای سیستمی: اتصال به سرویس هوش مصنوعی برقرار نشد.")
    st.stop()

# --- CSS حرفه‌ای ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Vazirmatn', sans-serif !important; direction: rtl; text-align: right; }
    .stApp { background: #0f172a; color: #e2e8f0; }
    .top-bar {
        background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1); border-radius: 15px;
        padding: 15px 25px; margin-bottom: 25px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .welcome-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(30, 41, 59, 0.7) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 25px;
        padding: 30px; margin-bottom: 30px; text-align: center;
    }
    .status-badge {
        background: rgba(34, 197, 94, 0.1); color: #4ade80; padding: 5px 15px;
        border-radius: 20px; font-size: 13px; display: inline-flex; align-items: center; gap: 8px;
    }
    .custom-card { 
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(59, 130, 246, 0.2); 
        border-radius: 20px; padding: 20px; text-align: center; margin-bottom: 15px; 
    }
</style>
""", unsafe_allow_html=True)

def logout():
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- سیستم احراز هویت ---
if "authentication_status" not in st.session_state:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>ورود به سامانه هوشمند</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["ورود", "عضویت"])
        with t1:
            u = st.text_input("نام کاربری", key="login_u")
            p = st.text_input("رمز عبور", type="password", key="login_p")
            if st.button("ورود به پنل", use_container_width=True):
                ok, res = db.verify_user(u, p)
                if ok:
                    st.session_state.authentication_status = True
                    st.session_state.user = res
                    st.rerun()
                else: st.error("نام کاربری یا رمز عبور اشتباه است")
        with t2:
            nu = st.text_input("شناسه کاربری جدید")
            np = st.text_input("کلمه عبور جدید", type="password")
            if st.button("ثبت‌نام", use_container_width=True):
                ok, msg = db.register_user(nu, np, nu, f"{nu}@nus.ac.ir")
                if ok: st.success(msg)
                else: st.error(msg)
else:
    # --- داشبورد اصلی ---
    user = st.session_state.user
    today_count = db.get_today_question_count(user['username'])
    is_admin = (user['role'] == 'admin')
    
    # نوار ابزار بالا
    st.markdown(f"""
    <div class="top-bar">
        <div style="text-align: right;">
            <strong style="font-size: 18px;">{user['name']} خوش آمدید</strong><br>
            <small style="color: #94a3b8;">{('مدیر سیستم' if is_admin else 'پژوهشگر')}</small>
        </div>
        <div style="background: rgba(59, 130, 246, 0.1); padding: 8px 15px; border-radius: 15px;">
            <small style="color: #60a5fa;">پیام‌های امروز: {today_count} از ۲۰</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("خروج از حساب"): logout()

    col_chat, col_tools = st.columns([1.5, 1], gap="large")

    with col_chat:
        st.subheader("💬 گفتگو با دستیار هوشمند")
        if not is_admin and today_count >= 20:
            st.warning("⚠️ سقف مجاز پیام‌های شما برای امروز (۲۰ پیام) به پایان رسیده است.")
        else:
            chat_container = st.container(height=500)
            if "messages" not in st.session_state: st.session_state.messages = []
            
            with chat_container:
                st.markdown('<div class="welcome-card">دستیار آماده پاسخگویی به سوالات شما بر اساس فایل‌های آپلود شده است.</div>', unsafe_allow_html=True)
                for m in st.session_state.messages:
                    with st.chat_message(m["role"]): st.markdown(m["content"])

            if prompt := st.chat_input("سوال خود را بپرسید..."):
                if "pdf_text" not in st.session_state or not st.session_state.pdf_text:
                    st.error("❌ ابتدا فایل PDF را در منوی سمت چپ بارگذاری و تحلیل کنید.")
                else:
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with chat_container:
                        with st.chat_message("user"): st.markdown(prompt)
                        with st.chat_message("assistant"):
                            with st.spinner("در حال تفکر..."):
                                response = generate_chat_response(st.session_state.messages, st.session_state.pdf_text)
                                st.markdown(response)
                                db.add_question(user['username'], prompt, len(st.session_state.pdf_text))
                                st.session_state.messages.append({"role": "assistant", "content": response})
                                st.rerun()

    with col_tools:
        st.subheader("📂 مدیریت اسناد")
        files = st.file_uploader("فایل‌های PDF را انتخاب کنید", type="pdf", accept_multiple_files=True)
        if st.button("🔍 تحلیل و استخراج محتوا", use_container_width=True):
            if files:
                with st.spinner("در حال پردازش اسناد..."):
                    txt, names = extract_text_from_pdfs(files)
                    st.session_state.pdf_text = txt
                    st.session_state.pdf_names = names
                    st.success(f"تعداد {len(names)} فایل با موفقیت تحلیل شد.")
                    
                    points = extract_important_sentences(txt)
                    st.markdown("### 📌 نکات کلیدی:")
                    for p in points: st.markdown(f"- {p}")
            else: st.error("فایلی انتخاب نشده است.")
        
        if is_admin:
            with st.expander("📊 مدیریت کاربران (ادمین)"):
                users = db.get_all_users()
                st.dataframe(pd.DataFrame(users, columns=['User', 'Name', 'Email', 'Role', 'Date', 'Qs', 'Status']))
