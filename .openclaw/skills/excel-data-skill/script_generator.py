#!/usr/bin/env python3
"""
Script Generator - 根据自然语言生成 Excel 编辑脚本

方案 A.1 快速实现：
- 基于模板和关键词匹配生成脚本
- 支持常见的数据筛选和修改操作
- 生成的脚本可以直接执行或人工审核

作者: AI Assistant
版本: 1.0.0
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EditOperation:
    """编辑操作描述"""
    operation_type: str  # 'filter', 'modify', 'calculate', 'delete'
    target_column: str
    condition: Optional[str] = None
    new_value: Optional[str] = None
    description: str = ""


@dataclass
class GeneratedScript:
    """生成的脚本"""
    script_code: str
    description: str
    safety_level: str  # 'safe', 'medium', 'dangerous'
    backup_recommended: bool
    operations: List[EditOperation]


class ScriptGenerator:
    """
    脚本生成器 - 将自然语言转换为 Python 编辑脚本
    """
    
    def __init__(self):
        self.column_mapping: Dict[str, List[str]] = {}
        self.setup_patterns()
    
    def setup_patterns(self):
        """设置匹配模式"""
        # 常见列名映射（用于智能匹配）
        self.column_aliases = {
            'id': ['id', 'ID', 'Id', '编号', '序号'],
            'name': ['name', 'Name', '名称', '名字'],
            'level': ['level', 'Level', '等级', '级别'],
            'hp': ['hp', 'HP', 'Hp', '生命值', '生命', '血量'],
            'attack': ['attack', 'Attack', '攻击力', '攻击'],
            'defense': ['defense', 'Defense', '防御力', '防御'],
            'gold': ['gold', 'Gold', '金币', '金钱'],
            'exp': ['exp', 'EXP', '经验', '经验值'],
        }
        
        # 操作关键词
        self.operation_patterns = {
            'filter': [
                r'(?:把|将|选择|筛选|找出|找到)(?:所有)?(.+?)(?:中|里|大于|小于|等于|>=|<=|>|<|=)(.+?)(?:的)?',
                r'(.+?)(?:>|>=|<|<=|=)(.+?)(?:时|的时候)?',
                r'(?:where|when|if)(.+?)(?:>|>=|<|<=|=)(.+)',
            ],
            'modify': [
                r'(?:把|将|让|使)(.+?)(?:增加|减少|乘以|除以|设置为|变成|改为)(.+?)(?:倍|%|倍)?',
                r'(.+?)(?:\*|x|X|×)(\d+(?:\.\d+)?)',
                r'(.+?)(?:增加|提升|上涨|上升)(\d+)(?:%|％)?',
                r'(.+?)(?:减少|降低|下降)(\d+)(?:%|％)?',
            ],
        }
    
    def generate(self, user_request: str, file_path: str, 
                 sheet_name: Optional[str] = None) -> GeneratedScript:
        """
        根据用户请求生成编辑脚本
        
        Args:
            user_request: 用户的自然语言请求
            file_path: Excel 文件路径
            sheet_name: 工作表名称（可选）
            
        Returns:
            GeneratedScript: 生成的脚本信息
        """
        # 解析用户请求
        operations = self._parse_request(user_request)
        
        # 生成脚本代码
        script_code = self._generate_script_code(
            operations, file_path, sheet_name, user_request
        )
        
        # 评估安全性
        safety_level = self._assess_safety(operations)
        
        return GeneratedScript(
            script_code=script_code,
            description=f"根据请求 '{user_request}' 生成的编辑脚本",
            safety_level=safety_level,
            backup_recommended=safety_level != 'safe',
            operations=operations
        )
    
    def _parse_request(self, request: str) -> List[EditOperation]:
        """解析用户请求，提取操作"""
        operations = []
        request_lower = request.lower()
        
        # 解析筛选条件（如：等级大于 10 的）
        filter_match = self._match_pattern(request_lower, 'filter')
        if filter_match:
            column, operator, value = filter_match
            operations.append(EditOperation(
                operation_type='filter',
                target_column=column,
                condition=f"{column} {operator} {value}",
                description=f"筛选 {column} {operator} {value} 的数据"
            ))
        
        # 解析修改操作（如：生命值增加 20%）
        modify_match = self._match_pattern(request_lower, 'modify')
        if modify_match:
            column, operation, value = modify_match
            operations.append(EditOperation(
                operation_type='modify',
                target_column=column,
                new_value=f"{operation} {value}",
                description=f"将 {column} {operation} {value}"
            ))
        
        # 如果没有匹配到任何操作，添加一个通用的描述
        if not operations:
            operations.append(EditOperation(
                operation_type='unknown',
                target_column='unknown',
                description=f"无法完全解析请求: {request}"
            ))
        
        return operations
    
    def _match_pattern(self, text: str, pattern_type: str) -> Optional[Tuple[str, str, str]]:
        """匹配模式并提取信息"""
        patterns = self.operation_patterns.get(pattern_type, [])
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    # 尝试解析操作符
                    column = groups[0].strip()
                    value_str = groups[1].strip()
                    
                    # 确定操作符
                    if '>' in text and '>=' not in text:
                        operator = '>'
                    elif '>=' in text:
                        operator = '>='
                    elif '<' in text and '<=' not in text:
                        operator = '<'
                    elif '<=' in text:
                        operator = '<='
                    elif '=' in text:
                        operator = '=='
                    else:
                        operator = '=='
                    
                    return (column, operator, value_str)
        
        return None
    
    def _generate_script_code(self, operations: List[EditOperation], 
                              file_path: str, sheet_name: Optional[str],
                              original_request: str) -> str:
        """生成 Python 脚本代码"""
        
        # 构建脚本
        lines = [
            "#!/usr/bin/env python3",
            "\"\"\"",
            f"自动生成的 Excel 编辑脚本",
            f"",
            f"原始请求: {original_request}",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\"\"\"",
            "",
            "import pandas as pd",
            "import shutil",
            "from pathlib import Path",
            "",
            f"# 配置文件路径",
            f"file_path = Path('{file_path}')",
        ]
        
        if sheet_name:
            lines.append(f"sheet_name = '{sheet_name}'")
        else:
            lines.append("sheet_name = 0  # 默认第一个工作表")
        
        lines.extend([
            "",
            "# 创建备份",
            "backup_path = file_path.parent / f\"{file_path.stem}_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}{file_path.suffix}\"",
            "shutil.copy2(file_path, backup_path)",
            "print(f\"✓ 已创建备份: {backup_path}\")",
            "",
            "# 读取 Excel 文件",
            f"df = pd.read_excel(file_path, sheet_name=sheet_name)",
            "print(f\"✓ 已读取文件: {file_path}\")",
            "print(f\"  行数: {len(df)}, 列数: {len(df.columns)}\")",
            "",
        ])
        
        # 根据操作生成编辑代码
        for i, op in enumerate(operations, 1):
            lines.append(f"# 操作 {i}: {op.description}")
            
            if op.operation_type == 'filter':
                # 筛选操作
                lines.extend([
                    f"print(f\"\\n▶ 执行: {op.description}\")",
                    f"filtered_df = df[{op.condition}]",
                    f"print(f\"  筛选后行数: {{len(filtered_df)}}\")",
                ])
                
            elif op.operation_type == 'modify':
                # 修改操作
                if '增加' in op.description or '+' in op.description:
                    lines.extend([
                        f"print(f\"\\n▶ 执行: {op.description}\")",
                        f"mask = {operations[0].condition if operations else 'True'}",  # 使用之前的筛选条件
                        f"original_values = df.loc[mask, '{op.target_column}'].copy()",
                        f"df.loc[mask, '{op.target_column}'] = (df.loc[mask, '{op.target_column}'] * 1.2).astype(int)",
                        f"print(f\"  已修改 {{mask.sum()}} 行的 {op.target_column}\")",
                    ])
            
            lines.append("")
        
        # 保存部分
        lines.extend([
            "# 保存修改后的文件",
            "print(\"\\n▶ 保存修改...\")",
            "df.to_excel(file_path, index=False, sheet_name=sheet_name if isinstance(sheet_name, str) else None)",
            "print(f\"✓ 已保存到: {file_path}\")",
            "",
            "# 验证保存",
            "verify_df = pd.read_excel(file_path, sheet_name=sheet_name)",
            "print(f\"\\n✓ 验证成功 - 文件包含 {len(verify_df)} 行数据\")",
            "",
            "print(\"\\n" + "="*50 + "\")",
            "print(\"编辑完成！\")",
            "print(f\"备份文件: {backup_path}\")",
        ])
        
        return "\n".join(lines)
    
    def _assess_safety(self, operations: List[EditOperation]) -> str:
        """评估操作安全性"""
        if not operations:
            return 'safe'
        
        for op in operations:
            if op.operation_type == 'unknown':
                return 'dangerous'
            if op.operation_type == 'delete':
                return 'dangerous'
            if op.operation_type == 'modify' and '所有' in op.description:
                return 'medium'
        
        return 'safe'


# ==================== 便捷使用函数 ====================

def generate_edit_script(user_request: str, file_path: str, 
                         sheet_name: Optional[str] = None) -> str:
    """
    便捷函数：根据用户请求生成编辑脚本
    
    Args:
        user_request: 用户的自然语言请求
        file_path: Excel 文件路径
        sheet_name: 工作表名称（可选）
        
    Returns:
        str: 生成的 Python 脚本代码
    """
    generator = ScriptGenerator()
    result = generator.generate(user_request, file_path, sheet_name)
    return result.script_code


def main():
    """示例用法"""
    # 示例 1：修改怪物数据
    request1 = "帮我把所有等级大于 10 的怪物生命值增加 20%"
    script1 = generate_edit_script(
        request1,
        "DataTables/MonsterTable.xlsx"
    )
    print("="*60)
    print(f"请求: {request1}")
    print("="*60)
    print(script1)
    
    # 示例 2：修改配置
    request2 = "把初始金币设置为 5000"
    script2 = generate_edit_script(
        request2,
        "Configs/GameConfig.xlsx"
    )
    print("\n" + "="*60)
    print(f"请求: {request2}")
    print("="*60)
    print(script2)


if __name__ == "__main__":
    main()
