# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 22:57:47 2026

@author: 1
"""

"""
RSM转换页面
"""

import streamlit as st

st.set_page_config(
    page_title="RSM转换 - pyCXIM",
    page_icon="🔄"
)

st.title("🔄 RSM转换")
st.markdown("倒易空间图转换功能正在开发中...")

st.info("""
支持的RSM转换功能：

1. **六圆衍射仪校准** (Calibration_6C.py)
2. **CDI数据转RSM** (CDI2RSM.py)
3. **二圆衍射仪RSM转换** (RC2RSM_2C.py)
4. **六圆衍射仪RSM转换** (RC2RSM_6C.py)
5. **RSM后处理** (RSM_post_processing.py)
""")