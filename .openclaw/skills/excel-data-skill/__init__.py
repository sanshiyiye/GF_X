#!/usr/bin/env python3
"""
Excel 数据编辑 Skill - 统一入口

基于 Schema 标准的 Excel 数据编辑工具，支持三类数据：
- DataTable: 游戏数据表
- Config: 配置表
- Language: 多语言表

主要功能：
- Schema 识别与验证
- 智能编辑脚本生成
- 安全执行与回滚
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"

import os
import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('excel-data-skill')

# 导入验证器
from .schema_validator import (
    BaseSchemaValidator,
    SchemaType,
    ValidationLevel,
    ValidationIssue,
    ValidationReport
)
from .datatable_validator import DataTableValidator
from .config_validator import ConfigValidator
from .language_validator import LanguageValidator


class SchemaRecognizer:
    """Schema 识别器 - 识别 Excel 文件的 Schema 类型"""
    
    @staticmethod
    def recognize(excel_path: str) -> Tuple[SchemaType, float, Dict[str, Any]]:
        """
        识别 Excel 文件的 Schema 类型
        
        Args:
            excel_path: Excel 文件路径
            
        Returns:
            Tuple[SchemaType, float, Dict]:
                - SchemaType: 识别出的类型
                - float: 置信度 (0-1)
                - Dict: 详细信息
        """
        import pandas as pd
        
        path = Path(excel_path)
        
        if not path.exists():
            logger.error(f"文件不存在: {excel_path}")
            return SchemaType.UNKNOWN, 0.0, {"error": "File not found"}
        
        # 1. 基于路径规则识别
        path_str = str(path).lower()
        
        if '/datatables/' in path_str or '\\datatables\\' in path_str:
            primary_type = SchemaType.DATATABLE
            path_confidence = 0.9
        elif '/configs/' in path_str or '\\configs\\' in path_str:
            primary_type = SchemaType.CONFIG
            path_confidence = 0.9
        elif '/languages/' in path_str or '\\languages\\' in path_str:
            primary_type = SchemaType.LANGUAGE
            path_confidence = 0.9
        else:
            primary_type = SchemaType.UNKNOWN
            path_confidence = 0.0
        
        # 2. 基于内容特征识别
        try:
            df = pd.read_excel(excel_path, nrows=10)  # 只读前10行
            columns = list(df.columns)
            
            # DataTable 特征：有 Id 列
            if 'Id' in columns or 'ID' in columns:
                datatable_score = 0.8
            else:
                datatable_score = 0.1
            
            # Config 特征：两列，Key/Value
            if len(columns) == 2:
                col1, col2 = columns[0].lower(), columns[1].lower()
                if (col1 in ['key', 'id'] and col2 in ['value', 'text', 'content']) or \
                   (col1 == 'key' and col2 == 'value'):
                    config_score = 0.9
                else:
                    config_score = 0.5
                language_score = 0.5
            else:
                config_score = 0.1
                language_score = 0.1
            
            # Language 特征：命名规范
            if path_confidence > 0:
                # 基于路径已经有较高置信度
                content_confidence = 1.0
            else:
                # 综合评分
                content_confidence = 0.5
            
            # 综合判断
            if primary_type == SchemaType.DATATABLE:
                confidence = min(1.0, path_confidence * 0.6 + datatable_score * 0.4)
            elif primary_type == SchemaType.CONFIG:
                confidence = min(1.0, path_confidence * 0.6 + config_score * 0.4)
            elif primary_type == SchemaType.LANGUAGE:
                confidence = min(1.0, path_confidence * 0.6 + language_score * 0.4)
            else:
                # 未知类型，尝试推测
                if datatable_score > 0.7:
                    primary_type = SchemaType.DATATABLE
                    confidence = datatable_score * 0.8
                elif config_score > 0.7:
                    primary_type = SchemaType.CONFIG
                    confidence = config_score * 0.8
                else:
                    confidence = 0.0
            
            details = {
                "path_recognition": {
                    "path": path_str,
                    "primary_type": primary_type.value,
                    "path_confidence": path_confidence
                },
                "content_analysis": {
                    "columns": columns,
                    "row_count": len(df),
                    "datatable_score": datatable_score if 'datatable_score' in dir() else 0,
                    "config_score": config_score if 'config_score' in dir() else 0,
                    "language_score": language_score if 'language_score' in dir() else 0
                },
                "final_confidence": confidence
            }
            
            return primary_type, confidence, details
            
        except Exception as e:
            logger.error(f"读取 Excel 失败: {e}")
            return SchemaType.UNKNOWN, 0.0, {"error": str(e)}


class ExcelDataSkill:
    """Excel 数据编辑 Skill 主类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 Skill
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.recognizer = SchemaRecognizer()
        
        # 初始化验证器映射
        self.validators = {
            SchemaType.DATATABLE: DataTableValidator,
            SchemaType.CONFIG: ConfigValidator,
            SchemaType.LANGUAGE: LanguageValidator
        }
        
        logger.info("ExcelDataSkill 初始化完成")
    
    def identify_schema(self, excel_path: str) -> Dict[str, Any]:
        """
        识别 Excel 文件的 Schema 类型
        
        Args:
            excel_path: Excel 文件路径
            
        Returns:
            Dict: 包含 schema_type, confidence, details
        """
        schema_type, confidence, details = self.recognizer.recognize(excel_path)
        
        return {
            "schema_type": schema_type.value,
            "confidence": confidence,
            "is_confident": confidence > 0.8,
            "details": details
        }
    
    def validate(self, excel_path: str, schema_type: Optional[str] = None) -> Dict[str, Any]:
        """
        验证 Excel 文件
        
        Args:
            excel_path: Excel 文件路径
            schema_type: 指定的 Schema 类型（可选，自动识别）
            
        Returns:
            Dict: 验证报告
        """
        import pandas as pd
        
        # 1. 识别或获取 Schema 类型
        if schema_type:
            try:
                st = SchemaType(schema_type.lower())
                confidence = 1.0
            except ValueError:
                return {
                    "error": f"未知的 Schema 类型: {schema_type}",
                    "valid_schema_types": [t.value for t in SchemaType if t != SchemaType.UNKNOWN]
                }
        else:
            st, confidence, _ = self.recognizer.recognize(excel_path)
        
        # 2. 检查是否有对应的验证器
        if st not in self.validators:
            return {
                "error": f"不支持的 Schema 类型: {st.value}",
                "schema_type": st.value
            }
        
        # 3. 读取 Excel
        try:
            df = pd.read_excel(excel_path)
        except Exception as e:
            return {
                "error": f"读取 Excel 失败: {str(e)}",
                "file": excel_path
            }
        
        # 4. 执行验证
        validator_class = self.validators[st]
        validator = validator_class()
        
        report = validator.validate(df, context={"file_path": excel_path})
        
        # 5. 返回结果
        result = report.to_dict()
        result["schema_recognition"] = {
            "schema_type": st.value,
            "confidence": confidence,
            "auto_detected": schema_type is None
        }
        
        return result


# 便捷函数
def create_skill(config: Optional[Dict[str, Any]] = None) -> ExcelDataSkill:
    """
    创建 Skill 实例（工厂函数）
    
    Args:
        config: 配置参数
        
    Returns:
        ExcelDataSkill 实例
    """
    return ExcelDataSkill(config)


# 导出
__all__ = [
    'ExcelDataSkill',
    'SchemaRecognizer',
    'create_skill'
]
EOF
echo "✅ Skill 主类已创建"
