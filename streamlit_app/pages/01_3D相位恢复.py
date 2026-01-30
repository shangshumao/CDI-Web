"""
3D相位恢复页面 - 完整功能修复版
"""

import streamlit as st
import sys
import os
import json
import time
import threading
import queue
from pathlib import Path
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 页面配置
st.set_page_config(
    page_title="3D相位恢复 - pyCXIM",
    page_icon="🔮",
    layout="wide"
)

# ==================== 会话状态初始化 ====================
def init_session_state():
    """初始化所有必要的会话状态"""
    if 'pr_processing' not in st.session_state:
        st.session_state.pr_processing = False
    if 'pr_logs' not in st.session_state:
        st.session_state.pr_logs = []
    if 'pr_progress' not in st.session_state:
        st.session_state.pr_progress = 0
    if 'pr_results' not in st.session_state:
        st.session_state.pr_results = []
    if 'pr_config' not in st.session_state:
        st.session_state.pr_config = {}
    if 'pr_log_queue' not in st.session_state:
        st.session_state.pr_log_queue = queue.Queue()
    if 'result_queue' not in st.session_state:
        st.session_state.result_queue = queue.Queue()
    if 'imported_config' not in st.session_state:
        st.session_state.imported_config = None
    if 'last_update' not in st.session_state:
        st.session_state.last_update = 0

init_session_state()

# ==================== 导入模块 ====================
PY_CXIM_AVAILABLE = False
try:
    from pyCXIM.utils.phase_retrieval_runner import (
        PhaseRetrieval3DConfig,
        run_phase_retrieval_3d
    )
    PY_CXIM_AVAILABLE = True
except ImportError as e:
    st.error(f"无法导入pyCXIM模块: {e}")

# ==================== 线程函数 ====================
def phase_retrieval_thread_worker(config_dict, log_queue, result_queue):
    """相位恢复的线程工作函数"""
    try:
        config = PhaseRetrieval3DConfig(config_dict)
        
        def thread_log(message):
            try:
                log_queue.put(message)
                print(f"[THREAD] {message}")
            except:
                print(f"[THREAD-FALLBACK] {message}")
        
        def thread_progress(percent, message):
            try:
                log_queue.put(f"PROGRESS:{percent}:{message}")
                thread_log(f"进度 {percent}%: {message}")
            except:
                print(f"[PROGRESS-FALLBACK] {percent}%: {message}")
        
        thread_log("=" * 60)
        thread_log("🚀 开始3D相位恢复")
        thread_log("=" * 60)
        
        start_time = time.time()
        
        # 运行相位恢复
        success, message = run_phase_retrieval_3d(
            config,
            progress_callback=thread_progress,
            log_callback=thread_log
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        result = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "success": success,
            "message": message,
            "duration": duration,
            "scan_num": config.scan_num,
            "config": config_dict
        }
        
        try:
            result_queue.put(result)
        except:
            thread_log(f"无法发送结果")
        
        thread_log("=" * 60)
        if success:
            thread_log(f"✅ 处理完成！耗时: {duration:.2f}秒")
        else:
            thread_log(f"❌ 处理失败！耗时: {duration:.2f}秒")
        thread_log("=" * 60)
        
    except Exception as e:
        import traceback
        error_msg = f"❌ 线程执行出错: {str(e)}\n{traceback.format_exc()}"
        try:
            log_queue.put(error_msg)
        except:
            print(error_msg)
    finally:
        try:
            log_queue.put("THREAD_END")
        except:
            pass

# ==================== 侧边栏 ====================
with st.sidebar:
    st.header("⚙️ 配置管理")
    
    # 配置导入
    st.subheader("📥 导入配置")
    uploaded_config = st.file_uploader("选择JSON配置文件", type=['json'])
    
    if uploaded_config is not None:
        try:
            imported_config = json.load(uploaded_config)
            st.session_state.imported_config = imported_config
            st.success("✅ 配置导入成功！")
        except Exception as e:
            st.error(f"❌ 导入失败: {str(e)}")
    
    # 应用导入的配置
    if st.session_state.imported_config and st.button("🔄 应用导入的配置", use_container_width=True):
        # 更新当前配置
        st.session_state.pr_config = st.session_state.imported_config.copy()
        st.success("✅ 配置已应用")
        time.sleep(0.5)
        st.rerun()
    
    st.divider()
    
    # 快速配置模板
    st.subheader("🚀 快速模板")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔬 快速测试", use_container_width=True):
            test_config = {
                'scan_num': 43,
                'SeedNum': 2,
                'algorithm': 'ER**5',
                'support_type': 'auto_correlation',
                'support_from_trial': 0
            }
            st.session_state.pr_config = {**st.session_state.pr_config, **test_config}
            st.success("✅ 已应用测试配置")
            st.rerun()
    
    with col2:
        if st.button("📊 BCDI标准", use_container_width=True):
            bcdi_config = {
                'scan_num': 43,
                'SeedNum': 50,
                'algorithm': 'HIO**100*ER**20*Sup*(HIO**50*ER**10)**5',
                'support_type': 'support_selected',
                'support_from_trial': 1
            }
            st.session_state.pr_config = {**st.session_state.pr_config, **bcdi_config}
            st.success("✅ 已应用BCDI配置")
            st.rerun()
    
    st.divider()
    
    # 导出配置
    st.subheader("📤 导出配置")
    if st.session_state.pr_config:
        config_json = json.dumps(st.session_state.pr_config, indent=2)
        st.download_button(
            label="💾 下载当前配置",
            data=config_json,
            file_name=f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    st.divider()
    
    # 历史记录
    st.subheader("📊 历史记录")
    if st.session_state.pr_results:
        for i, result in enumerate(reversed(st.session_state.pr_results[-3:])):
            with st.expander(f"运行 {result.get('time', 'N/A')}"):
                st.write(f"扫描: {result.get('scan_num', 'N/A')}")
                st.write(f"状态: {'✅' if result.get('success', False) else '❌'}")
                st.write(f"耗时: {result.get('duration', 0):.1f}秒")
    else:
        st.info("暂无历史记录")

# ==================== 页面标题 ====================
st.title("🔮 3D相位恢复")
st.markdown("基于pyCXIM库的3D相位恢复功能。")

# ==================== 参数配置 ====================
st.header("🔧 参数配置")

# 获取当前配置（优先使用导入的配置）
current_config = st.session_state.pr_config.copy() if st.session_state.pr_config else {}

# 使用标签页组织所有参数
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📁 文件设置", 
    "🔬 支撑参数", 
    "⚡ 算法参数", 
    "📊 Free LLK参数",
    "🌀 Shrink-wrap参数",
    "🎯 分析显示"
])

config_dict = {}

# 1. 文件设置
with tab1:
    st.subheader("基本文件参数")
    col1, col2 = st.columns(2)
    
    with col1:
        scan_num = st.number_input(
            "扫描编号", 
            value=current_config.get('scan_num', 43),
            min_value=1, 
            max_value=99999
        )
        config_dict['scan_num'] = scan_num
        
        data_description = st.selectbox(
            "数据类型",
            ["reciprocal_space_map_BCDI", "reciprocal_space_map_CDI", "stacked_detector_images_BCDI"],
            index=0
        )
        config_dict['data_description'] = data_description
        
        pathsave = st.text_input(
            "结果保存路径", 
            value=current_config.get('pathsave', f"./results/scan_{scan_num:04d}")
        )
        config_dict['pathsave'] = pathsave
    
    with col2:
        intensity_pattern = st.text_input(
            "强度文件模式", 
            value=current_config.get('intensity_file', "data/scan%04d.npz")
        )
        config_dict['intensity_file'] = intensity_pattern
        
        mask_pattern = st.text_input(
            "掩模文件模式", 
            value=current_config.get('mask_file', "data/scan%04d_mask.npz")
        )
        config_dict['mask_file'] = mask_pattern
        
        info_file = st.text_input(
            "扫描信息文件", 
            value=current_config.get('path_scan_infor', f"data/scan_{scan_num:04d}_information.txt")
        )
        config_dict['path_scan_infor'] = info_file

# 2. 支撑参数
with tab2:
    st.subheader("初始支撑参数")
    
    col1, col2 = st.columns(2)
    
    with col1:
        support_type = st.selectbox(
            "支撑类型",
            ["auto_correlation", "import", "average", "support_selected", "modulus_selected"],
            index=0
        )
        config_dict['support_type'] = support_type
        
        support_from_trial = st.number_input(
            "从哪个试验导入支撑",
            value=current_config.get('support_from_trial', 0),
            min_value=0,
            max_value=100
        )
        config_dict['support_from_trial'] = support_from_trial
        
        auto_corr_thrpara = st.slider(
            "自相关阈值参数",
            min_value=0.001,
            max_value=0.1,
            value=current_config.get('auto_corr_thrpara', 0.04),
            step=0.001,
            format="%.3f"
        )
        config_dict['auto_corr_thrpara'] = auto_corr_thrpara
        
        Initial_support_threshold = st.slider(
            "初始支撑阈值",
            min_value=0.1,
            max_value=1.0,
            value=current_config.get('Initial_support_threshold', 0.8),
            step=0.01,
            format="%.2f"
        )
        config_dict['Initial_support_threshold'] = Initial_support_threshold
    
    with col2:
        percent_selected = st.number_input(
            "选择百分比",
            value=current_config.get('percent_selected', 10),
            min_value=1,
            max_value=100
        )
        config_dict['percent_selected'] = percent_selected
        
        modulus_smooth_width = st.slider(
            "模量平滑宽度",
            min_value=0.1,
            max_value=2.0,
            value=current_config.get('modulus_smooth_width', 0.3),
            step=0.1,
            format="%.1f"
        )
        config_dict['modulus_smooth_width'] = modulus_smooth_width

# 3. 算法参数
with tab3:
    st.subheader("核心算法参数")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_trial_num = st.number_input(
            "起始试验编号",
            value=current_config.get('start_trial_num', 0),
            min_value=0,
            max_value=1000
        )
        config_dict['start_trial_num'] = start_trial_num
        
        SeedNum = st.number_input(
            "随机起点数量",
            value=current_config.get('SeedNum', 10),
            min_value=1,
            max_value=1000
        )
        config_dict['SeedNum'] = SeedNum
        
        precision = st.selectbox(
            "计算精度",
            ["32", "64"],
            index=0
        )
        config_dict['precision'] = precision
    
    with col2:
        algorithm = st.text_input(
            "算法表达式", 
            value=current_config.get('algorithm', "ER**20")
        )
        config_dict['algorithm'] = algorithm
        
        with st.expander("📚 算法语法帮助"):
            st.markdown("""
            **语法说明：**
            - `ER**20`: ER算法迭代20次
            - `HIO**100*ER**10`: 先HIO 100次，再ER 10次
            - `(HIO**50*ER**10)**5`: 括号内的组合重复5次
            - `DETWIN`: 去孪晶操作
            - `Sup`: 更新支撑
            
            **可用算法：**
            - `ER`: Error Reduction
            - `HIO`: Hybrid Input-Output
            - `RAAR`: Relaxed Averaged Alternating Reflections
            - `DIF`: Difference Map
            - `ADMM`: Alternating Direction Method of Multipliers
            """)
    
    with col3:
        detwin_axis = st.number_input(
            "去孪晶轴",
            value=current_config.get('detwin_axis', 0),
            min_value=0,
            max_value=2
        )
        config_dict['detwin_axis'] = detwin_axis
        
        flip_condition = st.selectbox(
            "翻转条件",
            ["Support", "Error", "None"],
            index=0
        )
        config_dict['flip_condition'] = flip_condition
        
        first_seed_flip = st.checkbox(
            "首次种子翻转",
            value=current_config.get('first_seed_flip', True)
        )
        config_dict['first_seed_flip'] = first_seed_flip

# 4. Free Log Likelihood参数
with tab4:
    st.subheader("Free Log-Likelihood参数")
    
    col1, col2 = st.columns(2)
    
    with col1:
        Free_LLK = st.checkbox(
            "启用Free LLK",
            value=current_config.get('Free_LLK', False)
        )
        config_dict['Free_LLK'] = Free_LLK
    
    with col2:
        if Free_LLK:
            FLLK_percentage = st.slider(
                "LLK像素百分比",
                min_value=0.001,
                max_value=0.1,
                value=current_config.get('FLLK_percentage', 0.01),
                step=0.001,
                format="%.3f"
            )
            config_dict['FLLK_percentage'] = FLLK_percentage
            
            FLLK_radius = st.number_input(
                "LLK半径",
                value=current_config.get('FLLK_radius', 3),
                min_value=1,
                max_value=10
            )
            config_dict['FLLK_radius'] = FLLK_radius

# 5. Shrink-wrap参数
with tab5:
    st.subheader("Shrink-wrap参数")
    
    col1, col2 = st.columns(2)
    
    with col1:
        threhold_update_method = st.selectbox(
            "阈值更新方法",
            ["exp_increase", "linear", "constant"],
            index=0
        )
        config_dict['threhold_update_method'] = threhold_update_method
        
        support_para_update_precent = st.slider(
            "支撑更新百分比",
            min_value=0.1,
            max_value=1.0,
            value=current_config.get('support_para_update_precent', 0.8),
            step=0.01,
            format="%.2f"
        )
        config_dict['support_para_update_precent'] = support_para_update_precent
    
    with col2:
        thrpara_min = st.slider(
            "最小阈值",
            min_value=0.01,
            max_value=0.2,
            value=current_config.get('thrpara_min', 0.08),
            step=0.01,
            format="%.2f"
        )
        config_dict['thrpara_min'] = thrpara_min
        
        thrpara_max = st.slider(
            "最大阈值",
            min_value=0.05,
            max_value=0.3,
            value=current_config.get('thrpara_max', 0.1),
            step=0.01,
            format="%.2f"
        )
        config_dict['thrpara_max'] = thrpara_max

# 6. 分析和显示参数
with tab6:
    st.subheader("分析和显示参数")
    
    col1, col2 = st.columns(2)
    
    with col1:
        further_analysis_selected = st.number_input(
            "进一步分析选择数量",
            value=current_config.get('further_analysis_selected', 10),
            min_value=1,
            max_value=100
        )
        config_dict['further_analysis_selected'] = further_analysis_selected
        
        error_type_for_selection = st.selectbox(
            "选择误差类型",
            ["Fourier space error", "Poisson logLikelihood error", "Object domain error", "Modulus STD"],
            index=0
        )
        config_dict['error_type_for_selection'] = error_type_for_selection
    
    with col2:
        display_range = [500, 500, 500]
        config_dict['display_range'] = display_range
        
        display_image_num = st.number_input(
            "显示图像数量",
            value=current_config.get('display_image_num', 10),
            min_value=1,
            max_value=100
        )
        config_dict['display_image_num'] = display_image_num

# 显示当前配置
with st.expander("📋 查看当前完整配置"):
    st.json(config_dict)

# 保存配置到会话状态
st.session_state.pr_config = config_dict

# ==================== 运行控制 ====================
st.markdown("---")
st.header("🚀 运行控制")

run_disabled = not PY_CXIM_AVAILABLE or st.session_state.pr_processing

if st.button(
    "🚀 开始相位恢复" if not st.session_state.pr_processing else "⏳ 处理中...",
    type="primary",
    disabled=run_disabled,
    use_container_width=True,
    key="run_btn"
):
    # 重置状态
    st.session_state.pr_processing = True
    st.session_state.pr_logs = []
    st.session_state.pr_progress = 0
    
    # 清空队列
    while not st.session_state.pr_log_queue.empty():
        try:
            st.session_state.pr_log_queue.get_nowait()
        except:
            pass
    
    while not st.session_state.result_queue.empty():
        try:
            st.session_state.result_queue.get_nowait()
        except:
            pass
    
    # 启动线程
    try:
        thread = threading.Thread(
            target=phase_retrieval_thread_worker,
            args=(config_dict, st.session_state.pr_log_queue, st.session_state.result_queue),
            daemon=True,
            name=f"PhaseRetrieval-{config_dict.get('scan_num', 43)}"
        )
        thread.start()
        st.session_state.pr_thread = thread
        st.session_state.pr_start_time = time.time()
        
        st.success("✅ 处理已启动")
        
    except Exception as e:
        st.error(f"启动失败: {e}")
        st.session_state.pr_processing = False

# ==================== 处理显示 ====================
if st.session_state.pr_processing:
    st.markdown("---")
    st.header("📊 处理进度")
    
    progress_bar = st.progress(st.session_state.pr_progress / 100)
    log_container = st.container()
    
    if time.time() - st.session_state.last_update > 0.5:
        st.session_state.last_update = time.time()
        
        # 处理日志队列
        new_logs = []
        try:
            while not st.session_state.pr_log_queue.empty():
                msg = st.session_state.pr_log_queue.get_nowait()
                
                if msg.startswith("PROGRESS:"):
                    try:
                        parts = msg.split(":", 2)
                        if len(parts) == 3:
                            percent = int(parts[1])
                            progress_msg = parts[2]
                            st.session_state.pr_progress = percent
                            new_logs.append(f"[进度 {percent}%] {progress_msg}")
                    except:
                        new_logs.append(msg)
                else:
                    new_logs.append(msg)
        except:
            pass
        
        if new_logs:
            st.session_state.pr_logs.extend(new_logs)
        
        # 检查结果队列
        try:
            while not st.session_state.result_queue.empty():
                result = st.session_state.result_queue.get_nowait()
                st.session_state.pr_results.append(result)
                st.session_state.pr_processing = False
        except:
            pass
        
        # 显示日志
        with log_container:
            st.subheader("📝 实时日志")
            if st.session_state.pr_logs:
                display_logs = st.session_state.pr_logs[-30:]
                st.code("\n".join(display_logs))
            else:
                st.info("等待日志输出...")
        
        progress_bar.progress(st.session_state.pr_progress / 100)
        st.rerun()

# ==================== 结果显示 ====================
if not st.session_state.pr_processing and st.session_state.pr_results:
    latest_result = st.session_state.pr_results[-1]
    
    st.markdown("---")
    st.header("📊 处理结果")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("状态", "✅ 成功" if latest_result['success'] else "❌ 失败")
    with col2:
        st.metric("耗时", f"{latest_result['duration']:.1f}秒")
    with col3:
        st.metric("扫描", latest_result.get('scan_num', 'N/A'))
    
    with st.expander("查看详情"):
        if latest_result['success']:
            st.success(latest_result['message'])
        else:
            st.error(latest_result['message'])

# ==================== 系统状态 ====================
if not PY_CXIM_AVAILABLE:
    st.error("""
    ⚠️ **pyCXIM不可用**
    
    请确保：
    1. 在项目根目录运行
    2. pyCXIM已正确安装
    """)

# 页面底部
st.markdown("---")
st.caption("pyCXIM Web界面 v1.0")