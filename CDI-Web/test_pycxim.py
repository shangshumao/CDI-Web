import streamlit as st
import sys
import os

st.title("🧪 pyCXIM 集成测试 - 成功！")

# 1. 设置路径
project_path = r"D:\桌面\pyCXIM_master"
sys.path.append(project_path)

st.success(f"✅ pyCXIM导入成功！路径: `{project_path}`")

# 2. 导入pyCXIM
import pyCXIM

# 3. 显示模块信息
st.write("### 📦 pyCXIM模块信息")
st.write(f"模块文件位置: `{pyCXIM.__file__}`")
st.write(f"模块名称: `{pyCXIM.__name__}`")

# 4. 正确显示模块列表
st.write("### 📋 可用模块和函数列表")

# 获取所有非私有成员
all_members = dir(pyCXIM)
public_members = [m for m in all_members if not m.startswith('_')]

st.write(f"总共找到 {len(public_members)} 个公共成员:")

# 分组显示
col1, col2 = st.columns(2)

with col1:
    st.write("#### 🔧 主要模块")
    modules = []
    for member in public_members:
        try:
            # 尝试获取成员，看是否是模块
            obj = getattr(pyCXIM, member)
            if hasattr(obj, '__file__'):  # 是模块
                modules.append(member)
        except:
            pass
    
    for module in sorted(modules):
        st.write(f"- **{module}**")
        
    if not modules:
        st.info("未找到子模块，可能需要直接导入子模块")

with col2:
    st.write("#### ⚙️ 函数和变量")
    functions_vars = []
    for member in public_members:
        if member not in modules:  # 不是模块的成员
            functions_vars.append(member)
    
    for item in sorted(functions_vars):
        st.write(f"- `{item}`")

# 5. 测试核心模块导入
st.write("### 🧪 核心模块导入测试")

test_modules = [
    ("scan_reader", "数据读取"),
    ("RSM", "倒易空间图转换"), 
    ("phase_retrieval", "相位恢复"),
    ("Common", "工具函数")
]

for module_name, description in test_modules:
    try:
        module = __import__(f'pyCXIM.{module_name}', fromlist=[''])
        st.success(f"✅ {module_name} - {description} 导入成功")
        
        # 显示该模块的内容
        with st.expander(f"查看 {module_name} 的内容"):
            module_members = [m for m in dir(module) if not m.startswith('_')]
            if module_members:
                st.write(f"包含 {len(module_members)} 个成员:")
                for i, member in enumerate(module_members[:10]):  # 只显示前10个
                    st.write(f"- `{member}`")
                if len(module_members) > 10:
                    st.info(f"... 还有 {len(module_members)-10} 个成员")
            else:
                st.info("没有公共成员")
                
    except ImportError as e:
        st.error(f"❌ {module_name} - 导入失败: {e}")

# 6. 查看pyCXIM文件夹结构
st.write("### 📁 pyCXIM文件夹结构")

pycxim_folder = os.path.join(project_path, "pyCXIM")
if os.path.exists(pycxim_folder):
    st.success(f"✅ pyCXIM文件夹: `{pycxim_folder}`")
    
    # 显示.py文件
    py_files = []
    for root, dirs, files in os.walk(pycxim_folder):
        for file in files:
            if file.endswith('.py'):
                rel_path = os.path.relpath(os.path.join(root, file), pycxim_folder)
                py_files.append(rel_path)
    
    if py_files:
        st.write(f"找到 {len(py_files)} 个Python文件:")
        for py_file in sorted(py_files):
            st.code(py_file, language=None)
    else:
        st.warning("未找到Python文件")
else:
    st.error(f"❌ pyCXIM文件夹不存在: {pycxim_folder}")

# 7. 环境信息
st.write("### 🌍 环境信息")
col1, col2 = st.columns(2)

with col1:
    st.write("**Python信息**")
    st.write(f"- Python版本: `{sys.version}`")
    st.write(f"- Python路径: `{sys.executable}`")
    st.write(f"- 当前目录: `{os.getcwd()}`")

with col2:
    st.write("**路径信息**")
    st.write(f"- sys.path长度: {len(sys.path)}")
    with st.expander("查看sys.path"):
        for i, path in enumerate(sys.path[:10]):  # 只显示前10个
            st.write(f"{i}. `{path}`")
        if len(sys.path) > 10:
            st.info(f"... 还有 {len(sys.path)-10} 个路径")

st.balloons()
st.success("🎉 pyCXIM集成测试完成！")