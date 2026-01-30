# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 22:50:18 2026

@author: 1
"""

"""
pyCXIM Streamlit 主应用
作者: Ren Zhe
邮箱: renzhe@ihep.ac.cn
"""

import streamlit as st
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 页面配置
st.set_page_config(
    page_title="pyCXIM - CDI数据处理平台",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': """
        # pyCXIM Web界面
        
        CDI实验数据处理平台
        
        版本: 1.0.0
        作者: Ren Zhe
        邮箱: renzhe@ihep.ac.cn
        
        基于Streamlit构建的pyCXIM库Web界面。
        """
    }
)

# 加载自定义CSS
def load_custom_css():
    """加载自定义CSS样式"""
    css_file = Path(__file__).parent / "assets" / "styles.css"
    if css_file.exists():
        with open(css_file, 'r', encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # 内联CSS作为备用
        st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        h1, h2, h3 {
            color: #1E3A8A;
        }
        
        .stButton > button {
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .card {
            background-color: #F8F9FA;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            border-left: 4px solid #3B82F6;
        }
        
        .success-box {
            background-color: #D1FAE5;
            border: 1px solid #10B981;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .warning-box {
            background-color: #FEF3C7;
            border: 1px solid #F59E0B;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .error-box {
            background-color: #FEE2E2;
            border: 1px solid #EF4444;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        </style>
        """, unsafe_allow_html=True)

load_custom_css()

# 初始化会话状态
def init_session_state():
    """初始化会话状态"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.processing = False
        st.session_state.results = []
        st.session_state.current_config = None
        st.session_state.log_messages = []

init_session_state()

# 侧边栏
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/3B82F6/FFFFFF?text=pyCXIM", 
             caption="CDI数据处理平台", use_column_width=True)
    
    st.markdown("---")
    
    # 页面导航
    st.header("📚 功能导航")
    page_options = {
        "🏠 主页": "app.py",
        "🔮 3D相位恢复": "pages/01_3D相位恢复.py",
        "📁 数据读取": "pages/02_数据读取.py",
        "🔄 RSM转换": "pages/03_RSM转换.py",
        "📊 结果可视化": "pages/04_结果可视化.py"
    }
    
    for page_name, page_path in page_options.items():
        if st.button(page_name, use_container_width=True, 
                    type="primary" if page_name == "🏠 主页" else "secondary"):
            st.switch_page(page_path)
    
    st.markdown("---")
    
    # 系统状态
    st.header("⚙️ 系统状态")
    
    # 检查pyCXIM
    try:
        import pyCXIM
        pycxim_status = "✅ 已加载"
    except ImportError:
        pycxim_status = "❌ 未找到"
    
    # 检查数据目录
    data_dir = project_root / "data"
    if data_dir.exists():
        data_status = f"✅ {len(list(data_dir.glob('*')))} 个文件"
    else:
        data_status = "📁 目录不存在"
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("pyCXIM", pycxim_status)
    with col2:
        st.metric("数据目录", data_status)
    
    st.markdown("---")
    
    # 快速链接
    st.header("🔗 快速链接")
    if st.button("📖 查看文档", use_container_width=True):
        st.info("文档链接: https://github.com/yourusername/pyCXIM")
    
    if st.button("🐛 报告问题", use_container_width=True):
        st.info("请提交到GitHub Issues")

# 主页面内容
st.title("🔬 pyCXIM - CDI实验数据处理平台")
st.markdown("欢迎使用pyCXIM的Web界面！")

# 功能简介
st.header("✨ 主要功能")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # 直接修改背景色
    st.markdown("""
    <div style="background-color: #2c3e50; color: white; padding: 20px; border-radius: 10px; height: 150px; margin: 10px;">
    <h3 style="color: white;">🔮 3D相位恢复</h3>
    <p>支持多种相位恢复算法，包括HIO、RAAR、ER、DIF等。</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background-color: #2c3e50; color: white; padding: 20px; border-radius: 10px; height: 150px; margin: 10px;">
    <h3 style="color: white;">📁 数据读取</h3>
    <p>支持DESY、ESRF、MAX IV、BSRF等同步辐射装置的数据格式。</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background-color: #2c3e50; color: white; padding: 20px; border-radius: 10px; height: 150px; margin: 10px;">
    <h3 style="color: white;">🔄 RSM转换</h3>
    <p>将衍射数据转换为倒易空间图，支持多种衍射仪配置。</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style="background-color: #2c3e50; color: white; padding: 20px; border-radius: 10px; height: 150px; margin: 10px;">
    <h3 style="color: white;">📊 结果分析</h3>
    <p>提供3D可视化、SVD分析、误差分析等后处理功能。</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 快速开始指南
st.header("🚀 快速开始")

with st.expander("点击查看完整指南", expanded=True):
    tab1, tab2, tab3 = st.tabs(["第一步", "第二步", "第三步"])
    
    with tab1:
        st.markdown("""
        ### 1. 数据准备
        
        确保你的数据文件在正确的目录结构中：
        
        ```
        pyCXIM_master/
        ├── data/
        │   ├── scan0069.npz
        │   ├── scan0069_mask.npz
        │   └── scan_0069_information.txt
        └── streamlit_app/
        ```
        
        或者可以在界面中指定自定义路径。
        """)
    
    with tab2:
        st.markdown("""
        ### 2. 配置参数
        
        1. 选择左侧的 **"3D相位恢复"** 功能
        2. 在参数配置页面设置：
           - 扫描编号
           - 文件路径
           - 算法参数
           - 分析选项
        3. 点击 **"运行"** 开始处理
        """)
    
    with tab3:
        st.markdown("""
        ### 3. 查看结果
        
        处理完成后：
        
        1. 查看实时日志输出
        2. 下载生成的结果文件
        3. 使用 **"结果可视化"** 功能查看3D图像
        4. 保存配置以便重复使用
        """)

st.markdown("---")

# 系统要求
st.header("📋 系统要求")

col_req1, col_req2 = st.columns(2)

with col_req1:
    st.markdown("""
    #### 软件要求
    - Python 3.8+
    - pyCXIM库
    - Streamlit 1.28+
    - NumPy, SciPy, Matplotlib
    - PyVista (用于3D可视化)
    """)

with col_req2:
    st.markdown("""
    #### 硬件建议
    - 8GB+ RAM
    - 10GB+ 可用磁盘空间
    - GPU支持（可选，用于加速）
    - 稳定的网络连接
    """)

# 底部信息
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
<p>pyCXIM Web界面 | 版本 1.0.0 | © 2024 CDI数据处理平台</p>
<p>中国科学院高能物理研究所 | 同步辐射实验室</p>
</div>
""", unsafe_allow_html=True)

# 开发说明
with st.expander("🧑‍💻 开发者信息"):
    st.markdown("""
    ### 项目结构
    
    ```
    pyCXIM_master/
    ├── pyCXIM/                 # 核心库
    ├── scripts/                # 示例脚本
    ├── streamlit_app/         # Web界面
    │   ├── app.py             # 主应用
    │   ├── pages/             # 功能页面
    │   └── utils/             # 工具函数
    └── data/                  # 数据目录（可选）
    ```
    
    ### 技术栈
    
    - **后端**: pyCXIM库（Python）
    - **前端**: Streamlit
    - **可视化**: Matplotlib, PyVista
    - **数据处理**: NumPy, SciPy
    
    ### 开发说明
    
    1. 确保pyCXIM库已正确安装
    2. 运行 `streamlit run streamlit_app/app.py`
    3. 在浏览器中打开 `http://localhost:8501`
    
    ### 贡献指南
    
    欢迎提交Issue和Pull Request！
    """)