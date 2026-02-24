#!/usr/bin/env python3
"""
Schema 验证器 - 基于三类数据的标准 Schema 进行验证

支持:
- DataTable Schema 验证
- Config Schema 验证  
- Language Schema 验证
"""

import re
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class SchemaType(Enum):
    """Schema 类型"""
    DATATABLE = "datatable"
    CONFIG = "config"
    LANGUAGE = "language"
    UNKNOWN = "unknown"


class ValidationLevel(Enum):
    """验证级别"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """验证问题"""
    field: str
    message: str
    level: ValidationLevel
    code: str = ""
    suggestion: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "message": self.message,
            "level": self.level.value,
            "code": self.code,
            "suggestion": self.suggestion
        }


@dataclass
class ValidationReport:
    """验证报告"""
    schema_type: SchemaType
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.level == ValidationLevel.ERROR]
    
    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.level == ValidationLevel.WARNING]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_type": self.schema_type.value,
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "issues": [i.to_dict() for i in self.issues],
            "summary": self.summary
        }


class BaseSchemaValidator:
    """基础 Schema 验证器"""
    
    SCHEMA_TYPE: SchemaType = SchemaType.UNKNOWN
    
    # 命名规范正则
    FIELD_NAME_PATTERN = re.compile(r'^[A-Z][a-zA-Z0-9]*$')  # 大驼峰
    CONFIG_KEY_PATTERN = re.compile(r'^[a-z][a-zA-Z0-9]*$')   # 小驼峰
    LANGUAGE_KEY_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*$') # 全大写下划线
    
    def __init__(self):
        self.issues: List[ValidationIssue] = []
    
    def validate(self, df: pd.DataFrame, context: Dict[str, Any] = None) -> ValidationReport:
        """验证入口"""
        self.issues = []
        context = context or {}
        
        # 执行具体验证逻辑（子类实现）
        self._validate_impl(df, context)
        
        # 生成报告
        is_valid = len([i for i in self.issues if i.level == ValidationLevel.ERROR]) == 0
        
        return ValidationReport(
            schema_type=self.SCHEMA_TYPE,
            is_valid=is_valid,
            issues=self.issues,
            summary=self._generate_summary(df, context)
        )
    
    def _validate_impl(self, df: pd.DataFrame, context: Dict[str, Any]):
        """具体验证逻辑，子类必须实现"""
        raise NotImplementedError
    
    def _generate_summary(self, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成验证摘要"""
        return {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns)
        }
    
    def _add_error(self, field: str, message: str, code: str = "", suggestion: str = ""):
        """添加错误"""
        self.issues.append(ValidationIssue(
            field=field,
            message=message,
            level=ValidationLevel.ERROR,
            code=code,
            suggestion=suggestion
        ))
    
    def _add_warning(self, field: str, message: str, code: str = "", suggestion: str = ""):
        """添加警告"""
        self.issues.append(ValidationIssue(
            field=field,
            message=message,
            level=ValidationLevel.WARNING,
            code=code,
            suggestion=suggestion
        ))


# 导出验证器类
__all__ = [
    'SchemaType',
    'ValidationLevel', 
    'ValidationIssue',
    'ValidationReport',
    'BaseSchemaValidator'
]
