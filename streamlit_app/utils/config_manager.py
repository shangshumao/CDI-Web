# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 22:59:50 2026

@author: 1
"""

"""
配置管理工具
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "./configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """保存配置"""
        try:
            config_path = self.config_dir / f"{config_name}.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def load_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """加载配置"""
        try:
            config_path = self.config_dir / f"{config_name}.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
        return None
    
    def list_configs(self) -> list:
        """列出所有配置"""
        configs = []
        for config_file in self.config_dir.glob("*.json"):
            configs.append({
                "name": config_file.stem,
                "path": str(config_file),
                "size": config_file.stat().st_size
            })
        return configs
    
    def delete_config(self, config_name: str) -> bool:
        """删除配置"""
        try:
            config_path = self.config_dir / f"{config_name}.json"
            if config_path.exists():
                config_path.unlink()
                return True
        except Exception as e:
            print(f"删除配置失败: {e}")
        return False