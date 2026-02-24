#!/usr/bin/env python3
"""
Config Schema 验证器

验证 Config 类型 Excel 文件是否符合标准 Schema。
Config 特点：
- 键值对结构（Key/Value）
- 简单配置，无 .cs 代码生成
- 运行时弱类型访问
"""

import re
import pandas as pd
from typing import Dict, Any
from schema_validator import (
    BaseSchemaValidator,
    SchemaType,
    ValidationLevel
)


class ConfigValidator(BaseSchemaValidator):
    """Config 验证器"""
    
    SCHEMA_TYPE = SchemaType.CONFIG
    
    # Config 命名规范：小驼峰
    CONFIG_KEY_PATTERN = re.compile(r'^[a-z][a-zA-Z0-9]*$')
    
    def _validate_impl(self, df: pd.DataFrame, context: Dict[str, Any]):
        """Config 具体验证逻辑"""
        
        # 1. 检查基本信息
        if df.empty:
            self._add_error(
                'data',
                '配置表为空，没有数据行',
                'CFG_E001',
                '请至少添加一行配置数据'
            )
            return
        
        # 2. 检查列结构（Config 必须只有 Key/Value 两列）
        columns = list(df.columns)
        
        if len(columns) != 2:
            self._add_error(
                'structure',
                f'Config 表必须有且只有 2 列，当前有 {len(columns)} 列',
                'CFG_E002',
                'Config 表必须是简单的两列结构：Key 和 Value。请删除多余的列或合并为两列结构。'
            )
            return
        
        # 检查列名
        col1, col2 = columns[0], columns[1]
        
        if col1.lower() != 'key' or col2.lower() != 'value':
            self._add_warning(
                'structure',
                f'建议将列名改为 "Key" 和 "Value"，当前为 "{col1}" 和 "{col2}"',
                'CFG_W001',
                '虽然不是强制的，但使用标准列名可以提高可读性和兼容性'
            )
        
        # 3. 验证 Key 列
        key_series = df.iloc[:, 0]  # 第一列是 Key
        self._validate_key_column(key_series)
        
        # 4. 验证 Value 列（Config 的 Value 可以是任意字符串）
        # 只需要检查是否有异常值
        value_series = df.iloc[:, 1]
        self._validate_value_column(value_series)
        
        # 5. 数据完整性检查
        self._validate_data_integrity(df)
    
    def _validate_key_column(self, key_series: pd.Series):
        """验证 Key 列"""
        
        # 检查空值
        if key_series.isna().any():
            null_count = key_series.isna().sum()
            self._add_error(
                'column:Key',
                f'Key 列存在 {null_count} 个空值',
                'CFG_E003',
                'Config 的 Key 不能为空，每个配置项必须有唯一的 Key'
            )
        
        # 检查空字符串
        empty_keys = key_series[key_series == ''].index.tolist()
        if empty_keys:
            self._add_error(
                'column:Key',
                f'Key 列存在空字符串（行 {empty_keys}）',
                'CFG_E004',
                'Key 不能为空字符串'
            )
        
        # 检查唯一性
        if key_series.nunique() != len(key_series.dropna()):
            dupes = key_series[key_series.duplicated()].unique()
            self._add_error(
                'column:Key',
                f'Key 列存在重复值: {list(dupes)}',
                'CFG_E005',
                'Config 的 Key 必须唯一，请检查并修改重复的 Key'
            )
        
        # 检查命名规范（小驼峰）
        for idx, key in key_series.dropna().items():
            if not self.CONFIG_KEY_PATTERN.match(str(key)):
                self._add_warning(
                    f'column:Key:row_{idx}',
                    f'Key "{key}" 不符合小驼峰命名规范',
                    'CFG_W002',
                    '建议使用小驼峰命名（如 initialGold, maxLevel）以提高一致性'
                )
    
    def _validate_value_column(self, value_series: pd.Series):
        """验证 Value 列"""
        
        # Config 的 Value 可以是任意字符串，但我们可以给出一些警告
        
        # 检查空值比例
        null_ratio = value_series.isna().sum() / len(value_series)
        if null_ratio > 0.5:
            self._add_warning(
                'column:Value',
                f'Value 列有超过 50% 的值为空 ({null_ratio:.1%})',
                'CFG_W003',
                '大量空值可能表示数据不完整，请检查是否遗漏了配置值'
            )
    
    def _validate_data_integrity(self, df: pd.DataFrame):
        """验证数据完整性"""
        
        # 检查完全空行
        empty_rows = df.isna().all(axis=1).sum()
        if empty_rows > 0:
            self._add_warning(
                'data',
                f'发现 {empty_rows} 行完全为空的数据',
                'CFG_W004',
                '建议删除空行以保持数据整洁'
            )
    
    def _generate_summary(self, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成 Config 专用摘要"""
        summary = super()._generate_summary(df, context)
        
        key_series = df.iloc[:, 0] if len(df.columns) > 0 else pd.Series()
        value_series = df.iloc[:, 1] if len(df.columns) > 1 else pd.Series()
        
        summary.update({
            "schema_type": "Config",
            "key_column": df.columns[0] if len(df.columns) > 0 else None,
            "value_column": df.columns[1] if len(df.columns) > 1 else None,
            "unique_keys": key_series.nunique() if not key_series.empty else 0,
            "empty_values": value_series.isna().sum() if not value_series.empty else 0,
            "is_config": True
        })
        
        return summary


# 导出
__all__ = ['ConfigValidator']
