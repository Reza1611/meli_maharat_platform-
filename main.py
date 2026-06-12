import streamlit as st
import os
import sys

# مدیریت مسیرها برای استریم‌لیت کلاود
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

import pandas as pd
import database as db
from utils.pdf_handler import extract_text_from_pdfs
from utils.ai_engine import generate_chat_response, extract_important_sentences, test_api_key

# تنظیمات اصلی
st.set_page_config(page_title="دستیار هوشمند دانشگاه", page_icon="🎓", layout="wide")
db.init_db()

# ظاهر برنامه
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn&display=swap');
    body, div, span, h1, h2, h3, p { font-family: 'Vazirmatn', sans-serif !important; direction: rtl; text-align: right; }
    .stChatFloatingInputContainer { direction: ltr; }
    .main-header { background: linear-gradient(90deg, #1e3a8a, #3b82f6); color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# سیستم ورود
if "authentication_status" not in st.session_state:
    st.markdown("<div class='main-header'><h1>سامانه هوشمند مستندات دانشگاه</h1></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["ورود", "ثبت‌نام"])
        with tab1:
            u = st.text_input("نام کاربری")
            p = st.text_input("رمز عبور", type="password")
            if st.button("ورود", use_container_width=True):
                success, user_data = db.verify_user(u, p)
                if success:
                    st.session_state.authentication_status = True
                    st.session_state.user = user_data
                    st.rerun()
                else: st.error("اطلاعات ورود اشتباه است.")
        with tab2:
            nu = st.text_input("نام کاربری جدید")
            np = st.text_input("رمز عبور جدید", type="password")
            if st.button("ایجاد حساب", use_container_width=True):
                ok, msg = db.register_user(nu, np, nu, f"{nu}@example.com")
                if ok: st.success(msg)
                else: st.error(msg)
else:
    # پنل اصلی
    user = st.session_state.user
    
    # تست وضعیت API در سایدبار
    with st.sidebar:
        st.title("پنل تنظیمات")
        if st.button("بررسی وضعیت اتصال"):
            if test_api_key(): st.success("اتصال برقرار است ✅")
            else: st.error("عدم اتصال ❌")
        
        if st.button("خروج از حساب"):
            del st.session_state.authentication_status
            st.rerun()

    # محتوای چت
    st.title(f"خوش آمدید، {user['name']}")
    
    c1, c2 = st.columns([2, 1])
    
    with c2:
        st.subheader("📁 آپلود اسناد (PDF)")
        files = st.file_uploader("فایل‌ها را اینجا بکشید", type="pdf", accept_multiple_files=True)
        if st.button("پردازش فایل‌ها", use_container_width=True):
            if files:
                with st.spinner("در حال خواندن فایل‌ها..."):
                    text, names = extract_text_from_pdfs(files)
                    st.session_state.pdf_text = text
                    st.success(f"{len(names)} فایل با موفقیت بارگذاری شد.")
            else: st.warning("لطفاً ابتدا فایل انتخاب کنید.")

    with c1:
        st.subheader("💬 گفتگو")
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("سوال شما..."):
            if "pdf_text" not in st.session_state:
                st.error("لطفاً ابتدا اسناد را آپلود و پردازش کنید.")
            else:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"): st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    response = generate_chat_response(st.session_state.messages, st.session_state.pdf_text)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    db.add_question(user['username'], prompt, len(st.session_state.pdf_text))
