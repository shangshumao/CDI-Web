# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 22:57:07 2026

@author: 1
"""

"""
数据读取页面
"""

import streamlit as st

st.set_page_config(
    page_title="数据读取 - pyCXIM",
    page_icon="📁"
)

st.title("📁 数据读取")
st.markdown("数据读取功能正在开发中...")

st.info("""
当前支持的数据格式：

1. **DESY (P10, P08光束线)**
   - Eiger探测器数据 (.h5)
   - FIO扫描文件 (.fio)

2. **ESRF**
   - HDF5格式 (.h5)
   - NeXus格式 (.nxs)
   - EDF格式 (.edf)
   - SPEC文件 (.spec)

3. **MAX IV (nanoMAX)**
   - Merlin探测器数据
   - 扫描数据文件

4. **BSRF**
   - Pilatus探测器数据
   - SPEC文件
""")