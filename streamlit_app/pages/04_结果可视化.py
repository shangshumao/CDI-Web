# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 22:59:13 2026

@author: 1
"""

"""
结果可视化页面
"""

import streamlit as st
import os
from pathlib import Path

st.set_page_config(
    page_title="结果可视化 - pyCXIM",
    page_icon="📊",
    layout="wide"
)

st.title("📊 结果可视化")
st.markdown("结果可视化功能正在开发中...")

# 选择结果目录
result_dir = st.text_input("结果目录", value="./results")

if os.path.exists(result_dir):
    # 列出文件
    import glob
    files = glob.glob(os.path.join(result_dir, "*.*"))
    
    if files:
        st.subheader("📁 可用文件")
        
        # 按扩展名分组
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        data_files = [f for f in files if f.lower().endswith(('.npz', '.npy', '.txt'))]
        
        if image_files:
            st.write("**图像文件**:")
            for img_file in image_files[:5]:  # 显示前5个
                st.image(img_file, caption=os.path.basename(img_file))
        
        if data_files:
            st.write("**数据文件**:")
            for data_file in data_files[:10]:  # 显示前10个
                st.write(f"- {os.path.basename(data_file)}")
else:
    st.warning(f"目录不存在: {result_dir}")