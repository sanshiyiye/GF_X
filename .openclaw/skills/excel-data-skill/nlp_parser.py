#!/usr/bin/env python3
"""
NLP Parser - 自然语言解析器

将用户的自然语言描述解析为结构化的编辑操作

支持的语义：
- 筛选："等级大于 10 的", "生命值小于 100 的"
- 修改："增加 20%", "设置为 100", "乘以 1.5"
- 条件："所有...", "满足...的"

作者: AI Assistant
版本: 1.0.0
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class OperationType(Enum):
    """操作类型"""
    FILTER = "filter"           # 筛选
    MODIFY = "modify"           # 修改
    CALCULATE = "calculate"     # 计算
    DELETE = "delete"           # 删除
    ADD = "add"                 # 添加


class ModifyType(Enum):
    """修改类型"""
    ADD = "add"                 # 增加
    SUBTRACT = "subtract"       # 减少
    MULTIPLY = "multiply"       # 乘以
    DIVIDE = "divide"           # 除以
    SET = "set"                 # 设置为


@dataclass
class ParsedCondition:
    """解析后的条件"""
    column: str                 # 列名
    operator: str               # 操作符: >, >=, <, <=, ==, !=
    value: Any                  # 值
    original_text: str          # 原始文本


@dataclass
class ParsedAction:
    """解析后的操作"""
    operation_type: OperationType
    modify_type: Optional[ModifyType]
    target_column: str          # 目标列
    value: Any                  # 值或表达式
    unit: str                   # 单位: '', '%', '倍'
    original_text: str          # 原始文本


@dataclass
class ParsedIntent:
    """解析后的完整意图"""
    original_request: str
    conditions: List[ParsedCondition]
    actions: List[ParsedAction]
    target_file: Optional[str] = None
    description: str = ""


class NLPParser:
    """
    自然语言解析器
    
    将用户输入解析为结构化的编辑操作
    """
    
    # 列名别名映射（用于智能识别）
    COLUMN_ALIASES = {
        'id': ['id', 'ID', 'Id', '编号', '序号', '标识符'],
        'name': ['name', 'Name', '名称', '名字', '标题'],
        'level': ['level', 'Level', '等级', '级别', 'lv'],
        'hp': ['hp', 'HP', 'Hp', '生命值', '生命', '血量', 'health'],
        'attack': ['attack', 'Attack', '攻击力', '攻击', 'atk', '伤害'],
        'defense': ['defense', 'Defense', '防御力', '防御', 'def', '护甲'],
        'gold': ['gold', 'Gold', '金币', '金钱', '货币'],
        'exp': ['exp', 'EXP', '经验', '经验值', 'xp', '熟练度'],
    }
    
    # 条件匹配模式
    CONDITION_PATTERNS = [
        # "等级大于 10" -> column=等级, operator=>, value=10
        # 改进: 使用更精确的模式，避免捕获不必要的词
        r'(?:所有|把|将|找出|选择|筛选)?\s*([\u4e00-\u9fa5]{2,4}|[a-zA-Z_]+?)\s*(大于|>|超过|高于)\s*(\d+)',
        r'(?:所有|把|将|找出|选择|筛选)?\s*([\u4e00-\u9fa5]{2,4}|[a-zA-Z_]+)\s*(大于等于|>=|至少)\s*(\d+)',
        r'(?:所有|把|将|找出|选择|筛选)?\s*([\u4e00-\u9fa5]{2,4}|[a-zA-Z_]+)\s*(小于|<|低于|少于)\s*(\d+)',
        r'(?:所有|把|将|找出|选择|筛选)?\s*([\u4e00-\u9fa5]{2,4}|[a-zA-Z_]+)\s*(小于等于|<=|至多)\s*(\d+)',
        r'(?:所有|把|将|找出|选择|筛选)?\s*([\u4e00-\u9fa5]{2,4}|[a-zA-Z_]+)\s*(等于|=|是|为)\s*(\d+)',
    ]
    
    # 操作匹配模式
    ACTION_PATTERNS = {
        'increase_by_percent': [
            r'(?:把|将|让|使)?\s*([\u4e00-\u9fa5]{2,4}|[a-zA-Z_]+)\s*(?:增加|提升|上涨|上升|add|increase|raise)\s*(\d+(?:\.\d+)?)\s*%',
        ],
        'increase_by_value': [
            r'(?:把|将|让|使)?\s*([\u4e00-\u9fa5]{2,4}|[a-zA-Z_]+)\s*(?:增加|提升|上涨|上升|add|increase|raise)\s*(\d+(?:\.\d+)?)(?!\s*%)',
        ],
        'decrease_by_percent': [
            r'(?:把|将|让|使)?\s*([\u4e00-\u9fa5]{2,4}|[a-zA-Z_]+)\s*(?:减少|降低|下降|削弱|decrease|reduce|lower)\s*(\d+(?:\.\d+)?)\s*%',
        ],
        'decrease_by_value': [
            r'(?:把|将|让|使)?\s*([\u4e00-\u9fa5]{2,4}|[a-zA-Z_]+)\s*(?:减少|降低|下降|削弱|decrease|reduce|lower)\s*(\d+(?:\.\d+)?)(?!\s*%)',
        ],
        'multiply': [
            r'(?:把|将|让|使)?\s*([\u4e00-\u9fa5]{2,4}|[a-zA-Z_]+)\s*(?:乘以|放大|multiply|times)\s*(\d+(?:\.\d+)?)\s*(?:倍|times)?',
        ],
        'divide': [
            r'(?:把|将|让|使)?\s*([\u4e00-\u9fa5]{2,4}|[a-zA-Z_]+)\s*(?:除以|缩小|divide|divided by)\s*(\d+(?:\.\d+)?)',
        ],
        'set_to': [
            r'(?:把|将)?\s*([\u4e00-\u9fa5]{2,4}|[a-zA-Z_]+)\s*(?:设置|设为|设置为|=|set to|set as)\s*(\d+)',
        ],
    }
    
    def __init__(self):
        self.setup_patterns()
    
    def setup_patterns(self):
        """初始化匹配模式"""
        # 编译正则表达式以提高性能
        self.compiled_condition_patterns = []
        for pattern in self.CONDITION_PATTERNS:
            try:
                self.compiled_condition_patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error as e:
                print(f"警告: 正则表达式编译失败: {pattern}, 错误: {e}")
        
        self.compiled_action_patterns = {}
        for action_type, patterns in self.ACTION_PATTERNS.items():
            compiled_list = []
            for pattern in patterns:
                try:
                    compiled_list.append(re.compile(pattern, re.IGNORECASE))
                except re.error as e:
                    print(f"警告: 正则表达式编译失败: {pattern}, 错误: {e}")
            if compiled_list:
                self.compiled_action_patterns[action_type] = compiled_list
    
    def parse(self, request: str) -> ParsedIntent:
        """
        解析用户的自然语言请求
        
        Args:
            request: 用户的自然语言描述
            
        Returns:
            ParsedIntent: 解析后的意图
        """
        # 提取文件路径（如果有）
        target_file = self._extract_file_path(request)
        
        # 解析条件
        conditions = self._parse_conditions(request)
        
        # 解析操作
        actions = self._parse_actions(request)
        
        return ParsedIntent(
            original_request=request,
            conditions=conditions,
            actions=actions,
            target_file=target_file,
            description=self._generate_description(conditions, actions)
        )
    
    def _extract_file_path(self, text: str) -> Optional[str]:
        """从文本中提取文件路径"""
        # 匹配常见的 Excel 文件路径模式
        patterns = [
            r'([\w/\\]+(?:DataTables|Configs|Languages)[\w/\\]*\.xlsx)',
            r'([\w/\\]+\.xlsx)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _parse_conditions(self, text: str) -> List[ParsedCondition]:
        """解析条件"""
        conditions = []
        
        for pattern in self.compiled_condition_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 3:
                    column = self._normalize_column_name(groups[0].strip())
                    operator = self._normalize_operator(groups[1])
                    value = self._parse_value(groups[2])
                    
                    conditions.append(ParsedCondition(
                        column=column,
                        operator=operator,
                        value=value,
                        original_text=match.group(0)
                    ))
        
        return conditions
    
    def _parse_actions(self, text: str) -> List[ParsedAction]:
        """解析操作"""
        actions = []
        
        for action_type, patterns in self.compiled_action_patterns.items():
            for pattern in patterns:
                matches = pattern.finditer(text)
                for match in matches:
                    groups = match.groups()
                    if len(groups) >= 2:
                        target = self._normalize_column_name(groups[0].strip())
                        value = groups[1]
                        
                        # 解析修改类型
                        modify_type = self._get_modify_type(action_type)
                        unit = self._get_unit(text, action_type)
                        
                        actions.append(ParsedAction(
                            operation_type=OperationType.MODIFY,
                            modify_type=modify_type,
                            target_column=target,
                            value=value,
                            unit=unit,
                            original_text=match.group(0)
                        ))
        
        return actions
    
    def _normalize_column_name(self, name: str) -> str:
        """标准化列名"""
        # 查找别名映射
        for standard, aliases in self.COLUMN_ALIASES.items():
            if name.lower() in [a.lower() for a in aliases]:
                return standard
        return name
    
    def _normalize_operator(self, op: str) -> str:
        """标准化操作符"""
        op_mapping = {
            '大于': '>', '超过': '>', '高于': '>', 'above': '>', 'greater than': '>',
            '大于等于': '>=', '至少': '>=', 'minimum': '>=',
            '小于': '<', '低于': '<', '少于': '<', 'below': '<', 'less than': '<',
            '小于等于': '<=', '至多': '<=', 'maximum': '<=',
            '等于': '==', '是': '==', '为': '==', '=': '==', 'equal': '==', 'equals': '==',
        }
        return op_mapping.get(op.lower().strip(), op)
    
    def _parse_value(self, value_str: str) -> Any:
        """解析值"""
        # 尝试转换为数字
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            # 去除引号
            value_str = value_str.strip('"\'')
            return value_str
    
    def _get_modify_type(self, action_type: str) -> Optional[ModifyType]:
        """获取修改类型"""
        mapping = {
            'increase_by_percent': ModifyType.ADD,
            'increase_by_value': ModifyType.ADD,
            'decrease_by_percent': ModifyType.SUBTRACT,
            'decrease_by_value': ModifyType.SUBTRACT,
            'multiply': ModifyType.MULTIPLY,
            'divide': ModifyType.DIVIDE,
            'set_to': ModifyType.SET,
        }
        return mapping.get(action_type)
    
    def _get_unit(self, text: str, action_type: str) -> str:
        """获取单位"""
        if 'percent' in action_type or '%' in text:
            return '%'
        elif 'multiply' in action_type or 'divide' in action_type:
            return '倍'
        return ''
    
    def _generate_description(self, conditions: List[ParsedCondition], 
                              actions: List[ParsedAction]) -> str:
        """生成描述"""
        parts = []
        
        if conditions:
            cond_strs = [f"{c.column} {c.operator} {c.value}" for c in conditions]
            parts.append(f"筛选条件: {', '.join(cond_strs)}")
        
        if actions:
            action_strs = []
            for a in actions:
                if a.modify_type:
                    type_name = {
                        ModifyType.ADD: "增加",
                        ModifyType.SUBTRACT: "减少",
                        ModifyType.MULTIPLY: "乘以",
                        ModifyType.DIVIDE: "除以",
                        ModifyType.SET: "设置为",
                    }.get(a.modify_type, "修改")
                    action_strs.append(f"{a.target_column} {type_name} {a.value}{a.unit}")
            parts.append(f"操作: {', '.join(action_strs)}")
        
        return "; ".join(parts) if parts else "未识别具体操作"


# ==================== 便捷使用函数 ====================

def parse_request(request: str) -> ParsedIntent:
    """
    便捷函数：解析用户请求
    
    Args:
        request: 用户的自然语言请求
        
    Returns:
        ParsedIntent: 解析后的意图
    """
    parser = NLPParser()
    return parser.parse(request)


def main():
    """示例用法"""
    # 测试用例
    test_requests = [
        "帮我把所有等级大于 10 的怪物生命值增加 20%",
        "把初始金币设置为 5000",
        "找出所有攻击力小于 50 的怪物并删除",
        "将所有 Boss 的防御力乘以 1.5 倍",
    ]
    
    print("="*70)
    print("NLP Parser 测试")
    print("="*70)
    
    for request in test_requests:
        print(f"\n📢 用户请求: {request}")
        print("-"*70)
        
        intent = parse_request(request)
        
        print(f"📋 描述: {intent.description}")
        print(f"📁 目标文件: {intent.target_file or '未指定'}")
        
        if intent.conditions:
            print(f"\n🔍 条件 ({len(intent.conditions)} 个):")
            for i, cond in enumerate(intent.conditions, 1):
                print(f"  {i}. {cond.column} {cond.operator} {cond.value}")
        
        if intent.actions:
            print(f"\n✏️ 操作 ({len(intent.actions)} 个):")
            for i, action in enumerate(intent.actions, 1):
                modify_type = action.modify_type.value if action.modify_type else "未知"
                print(f"  {i}. 目标: {action.target_column}")
                print(f"      类型: {modify_type}")
                print(f"      值: {action.value}{action.unit}")
        
        print("="*70)


if __name__ == "__main__":
    main()
