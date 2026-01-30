# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 22:47:22 2026

@author: 1
"""

# -*- coding: utf-8 -*-
"""
3D Phase retrieval runner module - 重构为可配置的函数
位于: pyCXIM/utils/phase_retrieval_runner.py
"""

import os
import sys
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple

# 导入pyCXIM核心模块
from pyCXIM.Common.Information_file_generator import InformationFileIO
from pyCXIM.phase_retrieval.phase_retrieval_widget import PhaseRetrievalWidget


class PhaseRetrieval3DConfig:
    """3D相位恢复配置类 - 对应scripts中的硬编码参数"""
    
    def __init__(self, config_dict: Optional[Dict] = None):
        # 设置默认值，对应原始脚本中的参数
        self._set_defaults()
        
        # 如果提供了配置字典，则更新配置
        if config_dict:
            self.update_from_dict(config_dict)
    
    def _set_defaults(self):
        """设置默认配置（对应原始脚本）"""
        # 基本文件参数
        self.scan_num = 69
        self.pathsave = r'./results'
        self.intensity_file = 'scan%04d.npz'
        self.mask_file = 'scan%04d_mask.npz'
        self.path_scan_infor = None
        self.data_description = 'reciprocal_space_map_BCDI'
        
        # 初始支撑参数
        self.support_type = 'support_selected'
        self.support_from_trial = 1
        self.auto_corr_thrpara = 0.04
        self.Initial_support_threshold = 0.8
        self.percent_selected = 10
        self.modulus_smooth_width = 0.3
        self.path_import_initial_support = None
        
        # 算法参数
        self.start_trial_num = 0
        self.SeedNum = 100
        self.precision = '32'
        self.algorithm = "DETWIN*DIF**200*DETWIN*(ADMM**60*ER**10)**40"
        
        # Free Log likelihood参数
        self.Free_LLK = False
        self.FLLK_percentage = 0.01
        self.FLLK_radius = 3
        
        # Shrink wrap参数
        self.threhold_update_method = 'exp_increase'
        self.support_para_update_precent = 0.8
        self.thrpara_min = 0.08
        self.thrpara_max = 0.1
        self.support_smooth_width_begin = 3.5
        self.support_smooth_width_end = 1.0
        self.hybrid_para = 0.2
        
        # Detwin参数
        self.detwin_axis = 0
        
        # 翻转参数
        self.flip_condition = 'Support'
        self.first_seed_flip = True
        self.phase_unwrap_method = 0
        
        # 分析参数
        self.further_analysis_selected = 10
        self.error_type_for_selection = 'Fourier space error'
        
        # 显示参数
        self.display_range = [500, 500, 500]
        self.display_image_num = 10
    
    def update_from_dict(self, config_dict: Dict):
        """从字典更新配置"""
        for key, value in config_dict.items():
            if hasattr(self, key):
                # 特殊处理某些字段
                if key == 'display_range' and isinstance(value, list) and len(value) == 3:
                    self.display_range = value
                elif key == 'path_scan_infor' and value == '':
                    self.path_scan_infor = None
                else:
                    setattr(self, key, value)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = {}
        for key in dir(self):
            if not key.startswith('_') and not callable(getattr(self, key)):
                value = getattr(self, key)
                # 序列化可序列化的类型
                if isinstance(value, (int, float, str, bool, list, dict, type(None))):
                    result[key] = value
        return result
    
    def validate(self) -> Tuple[bool, str]:
        """验证配置是否有效"""
        # 检查必要参数
        if not self.pathsave:
            return False, "请指定结果保存路径"
        if not self.intensity_file:
            return False, "请指定强度数据文件"
        
        # 检查数据类型
        valid_data_descriptions = [
            'reciprocal_space_map_CDI',
            'reciprocal_space_map_BCDI', 
            'stacked_detector_images_BCDI'
        ]
        if self.data_description not in valid_data_descriptions:
            return False, f"数据类型必须是: {', '.join(valid_data_descriptions)}"
        
        # 检查算法格式
        if not self.algorithm or len(self.algorithm.strip()) == 0:
            return False, "请指定算法表达式"
        
        return True, "配置有效"
    
    def format_file_paths(self, base_path: str = None) -> None:
        """格式化文件路径"""
        if base_path and not os.path.isabs(self.pathsave):
            self.pathsave = os.path.join(base_path, self.pathsave)
        
        # 确保路径存在
        os.makedirs(self.pathsave, exist_ok=True)


# 找到 run_phase_retrieval_3d 函数中的路径处理部分（大约第150行），修改：

def run_phase_retrieval_3d(config: PhaseRetrieval3DConfig, 
                          progress_callback=None, 
                          log_callback=None) -> Tuple[bool, str]:
    
    def log(message: str):
        """内部日志函数"""
        if log_callback:
            log_callback(message)
        else:
            print(f"[LOG] {message}")
    
    def progress(percent: int, message: str):
        """内部进度函数"""
        if progress_callback:
            progress_callback(percent, message)
        log(f"进度 {percent}%: {message}")
    
    try:
        starting_time = time.time()
        
        # 验证配置
        is_valid, error_msg = config.validate()
        if not is_valid:
            return False, f"配置错误: {error_msg}"
        
        log("开始3D相位恢复...")
        progress(5, "初始化配置")
        
        # 构建实际文件路径 - 修复路径拼接问题
        # 确保使用正确的基目录
        import os
        from pathlib import Path
        
        # 获取当前工作目录
        current_dir = Path.cwd()
        
        # 处理强度文件路径
        intensity_file_pattern = config.intensity_file
        if '%' in intensity_file_pattern:
            intensity_file = intensity_file_pattern % config.scan_num
        else:
            intensity_file = intensity_file_pattern
        
        # 处理掩模文件路径
        mask_file_pattern = config.mask_file
        if '%' in mask_file_pattern:
            mask_file = mask_file_pattern % config.scan_num
        else:
            mask_file = mask_file_pattern
        
        log(f"扫描编号: {config.scan_num}")
        log(f"强度文件: {intensity_file}")
        log(f"掩模文件: {mask_file}")
        log(f"数据描述: {config.data_description}")
        log(f"保存路径: {config.pathsave}")
        
        # 检查文件是否存在
        if not os.path.exists(intensity_file):
            # 尝试在当前目录、data目录等多个位置查找
            possible_paths = [
                intensity_file,
                os.path.join(current_dir, intensity_file),
                os.path.join('data', intensity_file),
                os.path.join(current_dir, 'data', intensity_file)
            ]
            
            found = False
            for path in possible_paths:
                if os.path.exists(path):
                    intensity_file = path
                    found = True
                    log(f"✓ 找到强度文件: {intensity_file}")
                    break
            
            if not found:
                return False, f"强度文件不存在。尝试了以下位置:\n" + "\n".join(possible_paths)
        
        # 检查掩模文件
        if mask_file and not os.path.exists(mask_file):
            possible_paths = [
                mask_file,
                os.path.join(current_dir, mask_file),
                os.path.join('data', mask_file),
                os.path.join(current_dir, 'data', mask_file)
            ]
            
            found = False
            for path in possible_paths:
                if os.path.exists(path):
                    mask_file = path
                    found = True
                    log(f"✓ 找到掩模文件: {mask_file}")
                    break
            
            if not found:
                log("⚠ 掩模文件不存在，将继续处理")
                mask_file = None
        
        # 创建保存目录
        os.makedirs(config.pathsave, exist_ok=True)
        
        # ... 后续代码保持不变 ...
        
        # 根据数据类型确定参数列表
        progress(10, "准备参数列表")
        if config.data_description == 'reciprocal_space_map_CDI':
            para_name_list = [
                'year', 'beamtimeID', 'scan_number', 'p10_newfile',
                'detector_distance', 'energy', 'pixelsize', 'unit']
        elif config.data_description == 'reciprocal_space_map_BCDI':
            para_name_list = [
                'year', 'beamtimeID', 'scan_number', 'p10_newfile',
                'detector_distance', 'energy', 'pixelsize', 'q_vector', 'unit']
        elif config.data_description == 'stacked_detector_images_BCDI':
            para_name_list = [
                'year', 'beamtimeID', 'scan_number', 'p10_newfile', 'omega', 'delta',
                'omegastep', 'detector_distance', 'energy', 'pixelsize', 'q_vector', 'unit']
        else:
            return False, f"未知的数据类型: {config.data_description}"
        
        # 加载信息文件
        progress(15, "加载信息文件")
        path_retrieval_infor = os.path.join(config.pathsave, "Phase_retrieval_information.txt")
        pr_infor = InformationFileIO(path_retrieval_infor)
        
        if not os.path.exists(path_retrieval_infor):
            trial_num = 1
            start_trial_num = 0
            if os.path.exists(config.path_scan_infor):
                scan_infor = InformationFileIO(config.path_scan_infor)
                pr_infor.add_para('total_trial_num', 'General Information', 0)
                pr_infor.copy_para_values(scan_infor, para_name_list, 'General Information')
                
                if config.data_description == 'reciprocal_space_map_BCDI':
                    pr_infor.copy_para_values(scan_infor, ['RSM_q_center', 'RSM_unit'], 
                                            'General Information', ['q_vector', 'unit'])
                elif config.data_description == 'stacked_detector_images_BCDI':
                    pr_infor.copy_para_values(scan_infor, ['direct_cut_q_center', 'DC_unit'], 
                                            'General Information', ['q_vector', 'unit'])
                elif config.data_description == 'reciprocal_space_map_CDI':
                    pr_infor.copy_para_values(scan_infor, ['RSM_unit'], 'General Information', ['unit'])
                
                log("✓ 从扫描信息文件复制参数成功")
            else:
                log("⚠ 扫描信息文件不存在，生成空参数文件")
                pr_infor.gen_empty_para_file(para_name_list, 'General Information')
        else:
            pr_infor.infor_reader()
            trial_num = pr_infor.get_para_value('total_trial_num') + 1
            log(f"✓ 加载现有信息文件，试验编号: {trial_num}")
        
        # 创建PhaseRetrievalWidget并加载数据
        progress(20, "创建相位恢复组件")
        pr_file = PhaseRetrievalWidget(config.pathsave, trial_num, config.data_description, mode='w')
        
        progress(25, "加载图像数据")
        pr_file.load_image_data(intensity_file, mask_file)
        pr_file.load_para_from_infor_file(path_retrieval_infor, para_name_list)
        
        # 创建初始支撑
        progress(30, f"创建初始支撑 ({config.support_type})")
        pr_file.create_initial_support(
            config.support_type, 
            config.auto_corr_thrpara, 
            config.support_from_trial,
            config.Initial_support_threshold, 
            config.percent_selected, 
            config.modulus_smooth_width,
            config.path_import_initial_support
        )
        
        # 开始相位恢复过程
        progress(40, f"开始相位恢复算法: {config.algorithm}")
        log(f"算法参数: SeedNum={config.SeedNum}, precision={config.precision}")
        
        pr_file.phase_retrieval_main(
            config.algorithm, 
            config.SeedNum, 
            config.start_trial_num, 
            config.precision, 
            config.Free_LLK,
            config.FLLK_percentage, 
            config.FLLK_radius, 
            config.threhold_update_method,
            config.support_para_update_precent, 
            config.thrpara_min, 
            config.thrpara_max,
            config.support_smooth_width_begin, 
            config.support_smooth_width_end,
            config.hybrid_para, 
            config.detwin_axis, 
            config.flip_condition,
            config.first_seed_flip, 
            config.phase_unwrap_method, 
            config.display_image_num
        )
        
        # 分析、绘图和保存最终结果
        progress(70, "分析并绘制结果")
        log("生成结果图像...")
        
        pr_file.plot_3D_intensity(
            array_group='Average_All', 
            save_image=True, 
            filename=f"Intensity_difference_Trial{trial_num}.png"
        )
        
        array_names = ('Modulus_sum', 'Phase_sum', 'Support_sum')
        pr_file.analysis_and_plot_3D(
            'Average_All', 
            array_names,
            title=f'Average results of {pr_file.get_para("nb_run")} runs',
            filename=f"Trial{trial_num}", 
            save_image=True,
            save_as_vti=True, 
            display_range=config.display_range
        )
        
        # 选择结果用于SVD分析或平均
        progress(80, "选择最佳结果进行进一步分析")
        pr_file.further_analysis(
            config.further_analysis_selected, 
            error_type=config.error_type_for_selection
        )
        
        pr_file.plot_3D_intensity(
            array_group='Selected_average', 
            save_image=True, 
            filename=f"Selected_intensity_difference_Trial{trial_num}.png"
        )
        
        pr_file.plot_error_matrix(filename=f"Error_Trial{trial_num}.png")
        
        array_names = ('Modulus_sum', 'Phase_sum', 'Support_sum')
        pr_file.analysis_and_plot_3D(
            'Selected_average', 
            array_names,
            title=f'Average results of {pr_file.get_para("further_analysis_selected")} runs with minimum error',
            filename=f"Trial{trial_num:02d}_selected_average", 
            save_image=True,
            save_as_vti=True, 
            display_range=config.display_range
        )
        
        if pr_file.get_para('further_analysis_method') == 'SVD':
            evalue = pr_file.get_dataset("SVD_analysis/evalue")
            log(f"SVD分析结果 - 模式1: {evalue[0]*100:.2f}%, 模式2: {evalue[1]*100:.2f}%")
            
            array_names = ('Mode1_Modulus', 'Mode1_Phase')
            pr_file.analysis_and_plot_3D(
                'SVD_analysis', 
                array_names,
                title=f'SVD Mode1 {evalue[0] * 100:.2f}%',
                filename=f"Trial{trial_num}_svd_mode1", 
                save_image=True,
                save_as_vti=True, 
                display_range=config.display_range
            )
            
            array_names = ('Mode2_Modulus', 'Mode2_Phase')
            pr_file.analysis_and_plot_3D(
                'SVD_analysis', 
                array_names,
                title=f'SVD Mode2 {evalue[1] * 100:.2f}%',
                filename=f"Trial{trial_num}_svd_mode2", 
                save_image=True,
                save_as_vti=True, 
                display_range=config.display_range
            )
        
        # 保存相位恢复信息
        progress(90, "保存结果信息")
        ending_time = time.time()
        total_time = ending_time - starting_time
        
        pr_file.add_para('total_calculation_time', total_time)
        pr_file.save_para_list()
        
        section = 'General Information'
        para_name_list = [
            'year', 'beamtimeID', 'scan_number', 'p10_newfile', 'data_description', 'omega',
            'delta', 'omegastep', 'detector_distance', 'energy', 'pixelsize', 'intensity_file',
            'mask_file', 'pathsave']
        pr_file.save_para_to_infor_file(path_retrieval_infor, section, para_name_list)
        
        pr_infor.add_para('total_trial_num', section, trial_num)
        pr_infor.infor_writer()
        
        section = f'Trial {trial_num:02d}'
        para_name_list = [
            'pathresult', 'data_shape', 'use_mask', 'start_trial_num', 'nb_run',
            'voxel_size', 'Ortho_voxel_size', 'algorithm', 'precision', 'flip_condition',
            'first_seed_flip', 'total_calculation_time', 'support_type',
            'support_from_trial', 'start_trial_num', 'auto_corr_thrpara',
            'Initial_support_threshold', 'percent_selected',
            'modulus_smooth_width', 'path_import_initial_support', 'Free_LLK',
            'FLLK_percentage', 'FLLK_radius', 'support_update', 'threhold_update_method',
            'support_update_loops', 'support_threshold_min', 'support_threshold_max',
            'support_smooth_width_begin', 'support_smooth_width_end', 'threhold_increase_rate',
            'hybrid_para', 'detwin_axis', 'further_analysis_selected', 'further_analysis_method',
            'phase_unwrap_method', 'error_for_further_analysis_selection']
        
        pr_file.save_para_to_infor_file(path_retrieval_infor, section, para_name_list)
        
        progress(100, "相位恢复完成")
        log("=" * 60)
        log(f"✅ 3D相位恢复完成！")
        log(f"   试验编号: {trial_num}")
        log(f"   总耗时: {total_time:.2f}秒")
        log(f"   结果保存于: {config.pathsave}")
        log("=" * 60)
        
        return True, f"相位恢复成功完成。试验编号: {trial_num}, 耗时: {total_time:.2f}秒"
        
    except Exception as e:
        import traceback
        error_msg = f"""
❌ 相位恢复过程中发生错误:
错误信息: {str(e)}

详细追踪:
{traceback.format_exc()}
        """
        log(error_msg)
        return False, error_msg


# 兼容性：保持与原脚本相同的函数名
def phase_retrieval_3D(scan_num: int = 69, **kwargs) -> Tuple[bool, str]:
    """
    兼容原始脚本的调用方式
    
    Args:
        scan_num: 扫描编号
        **kwargs: 其他配置参数
    
    Returns:
        bool: 是否成功
        str: 结果信息
    """
    config_dict = {'scan_num': scan_num}
    config_dict.update(kwargs)
    config = PhaseRetrieval3DConfig(config_dict)
    return run_phase_retrieval_3d(config)


# 测试代码
if __name__ == '__main__':
    print("测试3D相位恢复运行器...")
    
    # 创建测试配置
    test_config = PhaseRetrieval3DConfig({
        'scan_num': 69,
        'pathsave': './test_results',
        'SeedNum': 5,  # 测试时用较小的值
        'algorithm': 'ER**10'  # 测试时用简单的算法
    })
    
    # 运行测试
    success, message = run_phase_retrieval_3d(test_config)
    
    if success:
        print(f"测试成功: {message}")
    else:
        print(f"测试失败: {message}")