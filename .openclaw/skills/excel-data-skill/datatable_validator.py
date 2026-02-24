#!/usr/bin/env python3
"""
DataTable Schema 验证器

验证 DataTable 类型 Excel 文件是否符合标准 Schema。
"""

import pandas as pd
from typing import Dict, Any
from schema_validator import (
    BaseSchemaValidator,
    SchemaType,
    ValidationLevel,
    ValidationIssue
)


class DataTableValidator(BaseSchemaValidator):
    """DataTable 验证器"""
    
    SCHEMA_TYPE = SchemaType.DATATABLE
    
    # 支持的数据类型
    SUPPORTED_TYPES = {
        'int', 'float', 'double', 'string', 'bool', 'long', 'DateTime',
        'Vector2', 'Vector3', 'Vector4', 'Vector2Int', 'Vector3Int',
        'Color', 'Color32', 'enum'
    }
    
    # 数组类型后缀
    ARRAY_SUFFIXES = ['[]', '[][]']
    
    def _validate_impl(self, df: pd.DataFrame, context: Dict[str, Any]):
        """DataTable 具体验证逻辑"""
        
        # 1. 检查基本信息
        if df.empty:
            self._add_error(
                'data',
                '数据表为空，没有数据行',
                'DT_E001',
                '请至少添加一行数据（不包括表头）'
            )
            return
        
        # 获取列名
        columns = list(df.columns)
        
        # 2. 检查 Id 列（必须存在）
        if 'Id' not in columns:
            self._add_error(
                'column:Id',
                '缺少必需的 Id 列',
                'DT_E002',
                'DataTable 必须包含 Id 列作为主键，请添加 Id 列（int 类型）'
            )
        else:
            # 3. 检查 Id 列数据类型和唯一性
            self._validate_id_column(df['Id'])
        
        # 4. 检查其他列的命名规范
        for col in columns:
            if col == 'Id':
                continue  # Id 是特殊列
            
            if not self.FIELD_NAME_PATTERN.match(col):
                self._add_error(
                    f'column:{col}',
                    f'列名 "{col}" 不符合命名规范',
                    'DT_E003',
                    '列名必须以大写字母开头，只能包含字母和数字（如 MonsterId, HpMax）'
                )
        
        # 5. 检查数据类型（如果有类型信息）
        # 注意：这里假设可以通过某种方式获取类型信息
        # 实际实现中可能需要读取 Excel 的特定行或使用上下文信息
        
        # 6. 数据完整性检查
        self._validate_data_integrity(df)
    
    def _validate_id_column(self, id_series: pd.Series):
        """验证 Id 列"""
        
        # 检查是否为空
        if id_series.isna().any():
            null_count = id_series.isna().sum()
            self._add_error(
                'column:Id',
                f'Id 列存在 {null_count} 个空值',
                'DT_E004',
                'Id 列不允许为空，所有数据行必须有唯一的 Id'
            )
        
        # 检查是否为整数
        try:
            id_int = id_series.dropna().astype(int)
            if not (id_series.dropna() == id_int).all():
                self._add_error(
                    'column:Id',
                    'Id 列包含非整数值',
                    'DT_E005',
                    'Id 列必须是整数类型（如 1, 2, 100）'
                )
        except (ValueError, TypeError):
            self._add_error(
                'column:Id',
                'Id 列无法转换为整数',
                'DT_E006',
                '请确保 Id 列只包含整数值'
            )
        
        # 检查唯一性
        if id_series.nunique() != len(id_series.dropna()):
            dupes = id_series[id_series.duplicated()].unique()
            self._add_error(
                'column:Id',
                f'Id 列存在重复值: {list(dupes)}',
                'DT_E007',
                'Id 列的值必须唯一，请检查并修改重复的 Id'
            )
        
        # 检查是否 >= 1
        if (id_series.dropna() < 1).any():
            invalid = id_series[id_series < 1].unique()
            self._add_error(
                'column:Id',
                f'Id 列包含无效值（必须 >= 1）: {list(invalid)}',
                'DT_E008',
                'Id 值必须从 1 开始，不能为 0 或负数'
            )
    
    def _validate_data_integrity(self, df: pd.DataFrame):
        """验证数据完整性"""
        
        # 检查是否有完全空行
        empty_rows = df.isna().all(axis=1).sum()
        if empty_rows > 0:
            self._add_warning(
                'data',
                f'发现 {empty_rows} 行完全为空的数据',
                'DT_W001',
                '建议删除空行以保持数据整洁'
            )
        
        # 检查是否有完全重复的行
        dupes = df.duplicated().sum()
        if dupes > 0:
            self._add_warning(
                'data',
                f'发现 {dupes} 行完全重复的数据',
                'DT_W002',
                '建议检查并删除重复行，或确认是否为有意为之'
            )
    
    def _generate_summary(self, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成 DataTable 专用摘要"""
        summary = super()._generate_summary(df, context)
        
        # DataTable 特有信息
        summary.update({
            "has_id_column": "Id" in df.columns,
            "id_range": {
                "min": int(df["Id"].min()) if "Id" in df.columns and not df["Id"].empty else None,
                "max": int(df["Id"].max()) if "Id" in df.columns and not df["Id"].empty else None
            } if "Id" in df.columns else None,
            "data_types": context.get("data_types", {}),
            "is_datatable": True
        })
        
        return summary


# 导出
__all__ = ['DataTableValidator']
