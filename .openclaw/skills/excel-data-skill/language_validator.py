#!/usr/bin/env python3
"""
Language Schema 验证器

验证 Language 类型 Excel 文件是否符合标准 Schema。
Language 特点：
- 键值对结构（Key/Text）
- Key 命名规范：全大写下划线
- 输出为 JSON（由框架工具生成）
- 运行时通过 LocalizationComponent 加载
"""

import pandas as pd
import re
from typing import Dict, Any
from schema_validator import (
    BaseSchemaValidator,
    SchemaType,
    ValidationLevel
)


class LanguageValidator(BaseSchemaValidator):
    """Language 验证器"""
    
    SCHEMA_TYPE = SchemaType.LANGUAGE
    
    # Language Key 命名规范：全大写下划线
    # 示例: HELLO_WORLD, ERROR_NETWORK, GAME_START
    LANGUAGE_KEY_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*$')
    
    # 禁止的 Key 模式（容易混淆）
    FORBIDDEN_KEY_PATTERNS = [
        re.compile(r'^_'),           # 以下划线开头
        re.compile(r'_$'),           # 以下划线结尾
        re.compile(r'__+'),          # 连续多个下划线
        re.compile(r'^[0-9]'),       # 以数字开头
    ]
    
    def _validate_impl(self, df: pd.DataFrame, context: Dict[str, Any]):
        """Language 具体验证逻辑"""
        
        # 1. 检查基本信息
        if df.empty:
            self._add_error(
                'data',
                '多语言表为空，没有数据行',
                'LANG_E001',
                '请至少添加一行多语言数据'
            )
            return
        
        # 2. 检查列结构（Language 必须只有 Key/Text 两列）
        columns = list(df.columns)
        
        if len(columns) != 2:
            self._add_error(
                'structure',
                f'多语言表必须有且只有 2 列，当前有 {len(columns)} 列',
                'LANG_E002',
                '多语言表必须是简单的两列结构：Key 和 Text。请删除多余的列。'
            )
            return
        
        # 检查列名
        col1, col2 = columns[0], columns[1]
        
        # 列名建议（不强制）
        if col1.lower() not in ['key', 'id'] or col2.lower() not in ['text', 'value', 'content']:
            self._add_warning(
                'structure',
                f'建议将列名改为 "Key" 和 "Text"，当前为 "{col1}" 和 "{col2}"',
                'LANG_W001',
                '虽然不是强制的，但使用标准列名可以提高可读性和维护性'
            )
        
        # 3. 验证 Key 列
        key_series = df.iloc[:, 0]
        self._validate_key_column(key_series)
        
        # 4. 验证 Text 列
        text_series = df.iloc[:, 1]
        self._validate_text_column(text_series)
        
        # 5. 数据完整性检查
        self._validate_data_integrity(df)
    
    def _validate_key_column(self, key_series: pd.Series):
        """验证 Language Key 列"""
        
        # 检查空值
        if key_series.isna().any():
            null_count = key_series.isna().sum()
            self._add_error(
                'column:Key',
                f'Key 列存在 {null_count} 个空值',
                'LANG_E003',
                '多语言 Key 不能为空，每个文本必须有唯一的 Key'
            )
        
        # 检查空字符串
        empty_keys = key_series[key_series == ''].index.tolist()
        if empty_keys:
            self._add_error(
                'column:Key',
                f'Key 列存在空字符串（行 {empty_keys}）',
                'LANG_E004',
                'Key 不能为空字符串'
            )
        
        # 检查唯一性
        if key_series.nunique() != len(key_series.dropna()):
            dupes = key_series[key_series.duplicated()].unique()
            self._add_error(
                'column:Key',
                f'Key 列存在重复值: {list(dupes)}',
                'LANG_E005',
                '多语言 Key 必须唯一，请检查并修改重复的 Key'
            )
        
        # 检查命名规范（全大写下划线）
        for idx, key in key_series.dropna().items():
            key_str = str(key).strip()
            
            # 检查是否全大写下划线
            if not self.LANGUAGE_KEY_PATTERN.match(key_str):
                self._add_error(
                    f'column:Key:row_{idx}',
                    f'Key "{key_str}" 不符合命名规范',
                    'LANG_E006',
                    '多语言 Key 必须使用全大写下划线格式（如 HELLO_WORLD, ERROR_NETWORK）'
                )
            
            # 检查禁止的模式
            for pattern in self.FORBIDDEN_KEY_PATTERNS:
                if pattern.search(key_str):
                    if pattern.pattern == r'^_':
                        self._add_error(
                            f'column:Key:row_{idx}',
                            f'Key "{key_str}" 以下划线开头',
                            'LANG_E007',
                            'Key 不能以下划线开头'
                        )
                    elif pattern.pattern == r'_$':
                        self._add_error(
                            f'column:Key:row_{idx}',
                            f'Key "{key_str}" 以下划线结尾',
                            'LANG_E008',
                            'Key 不能以下划线结尾'
                        )
                    elif pattern.pattern == r'__+':
                        self._add_error(
                            f'column:Key:row_{idx}',
                            f'Key "{key_str}" 包含连续多个下划线',
                            'LANG_E009',
                            'Key 中不能使用连续多个下划线'
                        )
                    elif pattern.pattern == r'^[0-9]':
                        self._add_error(
                            f'column:Key:row_{idx}',
                            f'Key "{key_str}" 以数字开头',
                            'LANG_E010',
                            'Key 不能以数字开头'
                        )
    
    def _validate_text_column(self, text_series: pd.Series):
        """验证 Text 列"""
        
        # 多语言的 Text 可以为空（表示空字符串）
        # 但我们可以给出一些警告
        
        # 检查空值比例
        null_ratio = text_series.isna().sum() / len(text_series)
        if null_ratio > 0.3:
            self._add_warning(
                'column:Text',
                f'Text 列有超过 30% 的值为空 ({null_ratio:.1%})',
                'LANG_W002',
                '大量空值可能表示数据不完整，请检查是否遗漏了文本内容'
            )
        
        # 检查特殊字符（可能影响 JSON 输出）
        special_chars = ['\\', '"', '\n', '\r', '\t']
        for idx, text in text_series.dropna().items():
            text_str = str(text)
            for char in special_chars:
                if char in text_str:
                    # 这是一个警告，不是错误，因为框架会处理转义
                    self._add_warning(
                        f'column:Text:row_{idx}',
                        f'Text 包含特殊字符 "{repr(char)}"，可能影响 JSON 输出',
                        'LANG_W003',
                        f'特殊字符 {repr(char)} 在输出为 JSON 时需要转义，框架会自动处理，但建议确认文本内容正确'
                    )
                    break  # 每行只报告一次
    
    def _validate_data_integrity(self, df: pd.DataFrame):
        """验证数据完整性"""
        
        # 检查完全空行
        empty_rows = df.isna().all(axis=1).sum()
        if empty_rows > 0:
            self._add_warning(
                'data',
                f'发现 {empty_rows} 行完全为空的数据',
                'LANG_W004',
                '建议删除空行以保持数据整洁'
            )
        
        # 检查是否有 Key 或 Text 都相同的重复行
        dupes = df.duplicated().sum()
        if dupes > 0:
            self._add_warning(
                'data',
                f'发现 {dupes} 行完全重复的数据（Key 和 Text 都相同）',
                'LANG_W005',
                '重复的数据行可能是输入错误，建议检查并删除重复项'
            )
    
    def _generate_summary(self, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成 Language 专用摘要"""
        summary = super()._generate_summary(df, context)
        
        key_series = df.iloc[:, 0] if len(df.columns) > 0 else pd.Series()
        text_series = df.iloc[:, 1] if len(df.columns) > 1 else pd.Series()
        
        # 统计 Key 命名规范
        valid_key_count = 0
        invalid_key_examples = []
        for key in key_series.dropna():
            if self.LANGUAGE_KEY_PATTERN.match(str(key)):
                valid_key_count += 1
            else:
                if len(invalid_key_examples) < 3:
                    invalid_key_examples.append(str(key))
        
        summary.update({
            "schema_type": "Language",
            "key_column": df.columns[0] if len(df.columns) > 0 else None,
            "text_column": df.columns[1] if len(df.columns) > 1 else None,
            "unique_keys": key_series.nunique() if not key_series.empty else 0,
            "valid_key_naming": valid_key_count,
            "invalid_key_examples": invalid_key_examples if invalid_key_examples else None,
            "empty_text_count": text_series.isna().sum() if not text_series.empty else 0,
            "is_language": True
        })
        
        return summary


# 导入 re 模块
import re

# 导出
__all__ = ['ConfigValidator', 'LanguageValidator']
