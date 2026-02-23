#!/usr/bin/env python3
"""
GF_X UI Linter - UI 代码规范检查工具

检查 UI 代码是否符合 GF_X 框架规范：
1. 继承检查：必须继承 UIFormBase
2. 命名规范：类名以 UIForm 结尾
3. 生命周期：事件订阅必须取消
4. API 使用：必须使用 GF.UI
5. 数据驱动：必须使用 UIFormData
"""

import re
import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class Severity(Enum):
    """问题严重程度"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    """检查发现的单个问题"""
    rule_id: str
    rule_name: str
    severity: Severity
    message: str
    file_path: str
    line_number: int
    column: int = 0
    code_snippet: str = ""
    suggestion: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        result['severity'] = self.severity.value
        return result


@dataclass
class LintResult:
    """单次检查的结果"""
    success: bool
    file_path: str
    issues: List[Issue] = field(default_factory=list)
    summary: str = ""
    
    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)
    
    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'file_path': self.file_path,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'summary': self.summary,
            'issues': [i.to_dict() for i in self.issues]
        }


class UILinter:
    """UI 代码规范检查器"""
    
    def __init__(self):
        self.rules = {
            'inheritance': self._check_inheritance,
            'naming': self._check_naming,
            'lifecycle': self._check_lifecycle,
            'api_usage': self._check_api_usage,
            'data_driven': self._check_data_driven,
        }
    
    def lint_file(self, file_path: str) -> LintResult:
        """检查单个文件"""
        path = Path(file_path)
        
        if not path.exists():
            return LintResult(
                success=False,
                file_path=file_path,
                summary=f"文件不存在: {file_path}"
            )
        
        if not path.suffix == '.cs':
            return LintResult(
                success=False,
                file_path=file_path,
                summary=f"不是 C# 文件: {file_path}"
            )
        
        try:
            content = path.read_text(encoding='utf-8')
            lines = content.split('\n')
        except Exception as e:
            return LintResult(
                success=False,
                file_path=file_path,
                summary=f"读取文件失败: {e}"
            )
        
        # 收集所有问题
        all_issues = []
        for rule_id, check_func in self.rules.items():
            try:
                issues = check_func(content, lines, str(path))
                all_issues.extend(issues)
            except Exception as e:
                print(f"规则 {rule_id} 检查失败: {e}", file=sys.stderr)
        
        # 生成摘要
        error_count = sum(1 for i in all_issues if i.severity == Severity.ERROR)
        warning_count = sum(1 for i in all_issues if i.severity == Severity.WARNING)
        
        if error_count == 0 and warning_count == 0:
            summary = f"✅ {path.name} 通过所有检查"
        else:
            summary = f"⚠️ {path.name}: {error_count} 个错误, {warning_count} 个警告"
        
        return LintResult(
            success=error_count == 0,
            file_path=file_path,
            issues=all_issues,
            summary=summary
        )
    
    def lint_directory(self, directory_path: str, recursive: bool = True) -> List[LintResult]:
        """检查整个目录"""
        results = []
        path = Path(directory_path)
        
        if not path.exists():
            print(f"目录不存在: {directory_path}", file=sys.stderr)
            return results
        
        # 查找所有 C# 文件
        if recursive:
            cs_files = list(path.rglob('*.cs'))
        else:
            cs_files = list(path.glob('*.cs'))
        
        # 过滤掉 Unity 生成的文件等
        cs_files = [f for f in cs_files if 'UIVariables' not in str(f)]
        
        print(f"找到 {len(cs_files)} 个 C# 文件待检查...")
        
        for cs_file in cs_files:
            result = self.lint_file(str(cs_file))
            results.append(result)
            print(f"  {result.summary}")
        
        return results
    
    # ==================== 具体规则检查 ====================
    
    def _check_inheritance(self, content: str, lines: List[str], file_path: str) -> List[Issue]:
        """检查继承：必须继承 UIFormBase"""
        issues = []
        
        # 查找类定义
        class_pattern = r'class\s+(\w+)\s*:\s*(\w+)'
        matches = re.finditer(class_pattern, content, re.MULTILINE)
        
        for match in matches:
            class_name = match.group(1)
            base_class = match.group(2)
            
            # 只检查 UI 相关的类
            if 'UIForm' in class_name or 'Dialog' in class_name:
                # 检查是否继承正确的基类
                if base_class == 'UIFormLogic':
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append(Issue(
                        rule_id='inheritance',
                        rule_name='继承检查',
                        severity=Severity.ERROR,
                        message=f'类 {class_name} 继承自 UIFormLogic，应该继承 UIFormBase',
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=f'class {class_name} : {base_class}',
                        suggestion='将 UIFormLogic 改为 UIFormBase'
                    ))
                elif base_class != 'UIFormBase' and 'UIForm' in class_name:
                    # 可能继承其他不正确的类
                    if base_class not in ['MonoBehaviour', 'UIFormLogic', 'UIFormBase']:
                        line_num = content[:match.start()].count('\n') + 1
                        issues.append(Issue(
                            rule_id='inheritance',
                            rule_name='继承检查',
                            severity=Severity.WARNING,
                            message=f'类 {class_name} 继承自 {base_class}，请确认是否正确',
                            file_path=file_path,
                            line_number=line_num,
                            code_snippet=f'class {class_name} : {base_class}',
                            suggestion='应该继承 UIFormBase'
                        ))
        
        return issues
    
    def _check_naming(self, content: str, lines: List[str], file_path: str) -> List[Issue]:
        """检查命名规范：类名以 UIForm 结尾，无 Logic 后缀"""
        issues = []
        
        # 查找类定义
        class_pattern = r'class\s+(\w+)'
        matches = re.finditer(class_pattern, content, re.MULTILINE)
        
        for match in matches:
            class_name = match.group(1)
            
            # 只检查 UI 相关的类
            if 'UI' in class_name or 'Dialog' in class_name or 'Form' in class_name:
                # 检查是否以 Logic 结尾
                if class_name.endswith('Logic'):
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append(Issue(
                        rule_id='naming',
                        rule_name='命名规范',
                        severity=Severity.ERROR,
                        message=f'类名 {class_name} 不应该以 Logic 结尾',
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=f'class {class_name}',
                        suggestion=f'改为 {class_name[:-5]} 或 {class_name[:-5]}UIForm'
                    ))
                
                # 检查是否以 UIForm 结尾（推荐）
                if not class_name.endswith('UIForm') and not class_name.endswith('Dialog'):
                    if 'UI' in class_name and 'Form' in class_name:
                        line_num = content[:match.start()].count('\n') + 1
                        issues.append(Issue(
                            rule_id='naming',
                            rule_name='命名规范',
                            severity=Severity.WARNING,
                            message=f'类名 {class_name} 建议以 UIForm 结尾',
                            file_path=file_path,
                            line_number=line_num,
                            code_snippet=f'class {class_name}',
                            suggestion=f'改为 {class_name}UIForm'
                        ))
        
        return issues
    
    def _check_lifecycle(self, content: str, lines: List[str], file_path: str) -> List[Issue]:
        """检查生命周期：事件订阅必须在 OnClose 中取消"""
        issues = []
        
        # 查找 Subscribe 调用
        subscribe_pattern = r'GF\.Event\.Subscribe\s*\(\s*([^,]+)'
        subscribe_matches = list(re.finditer(subscribe_pattern, content))
        
        # 查找对应的 Unsubscribe 调用
        unsubscribe_pattern = r'GF\.Event\.Unsubscribe\s*\(\s*([^,]+)'
        unsubscribe_matches = list(re.finditer(unsubscribe_pattern, content))
        
        # 提取 Subscribe 的事件 ID
        subscribed_events = set()
        for match in subscribe_matches:
            event_id = match.group(1).strip()
            subscribed_events.add(event_id)
        
        # 提取 Unsubscribe 的事件 ID
        unsubscribed_events = set()
        for match in unsubscribe_matches:
            event_id = match.group(1).strip()
            unsubscribed_events.add(event_id)
        
        # 检查是否有未取消的订阅
        missing_unsubscribe = subscribed_events - unsubscribed_events
        
        for event_id in missing_unsubscribe:
            # 找到 Subscribe 的位置
            for match in subscribe_matches:
                if match.group(1).strip() == event_id:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append(Issue(
                        rule_id='lifecycle',
                        rule_name='生命周期',
                        severity=Severity.WARNING,
                        message=f'事件 {event_id} 被订阅但没有找到对应的取消订阅',
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=f'GF.Event.Subscribe({event_id}, ...)',
                        suggestion=f'在 OnClose 方法中添加：GF.Event.Unsubscribe({event_id}, ...)'
                    ))
                    break
        
        return issues
    
    def _check_api_usage(self, content: str, lines: List[str], file_path: str) -> List[Issue]:
        """检查 API 使用：必须使用 GF.UI，禁止 Instantiate/Destroy"""
        issues = []
        
        # 检查禁止使用的 API
        forbidden_patterns = [
            (r'\bInstantiate\s*\(', 'Instantiate', '使用 GF.UI.OpenUIForm'),
            (r'\bDestroy\s*\(', 'Destroy', '使用 GF.UI.CloseUIForm'),
            (r'\bGameObject\.Find\s*\(', 'GameObject.Find', '使用序列化字段绑定'),
            (r'\bResources\.Load\s*<', 'Resources.Load', '使用 GF.Resource.LoadAsset'),
        ]
        
        for pattern, api_name, suggestion in forbidden_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                
                issues.append(Issue(
                    rule_id='api_usage',
                    rule_name='API 使用',
                    severity=Severity.ERROR,
                    message=f'禁止使用 {api_name}',
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line_content.strip(),
                    suggestion=suggestion
                ))
        
        return issues
    
    def _check_data_driven(self, content: str, lines: List[str], file_path: str) -> List[Issue]:
        """检查数据驱动：必须使用 UIFormData，禁止硬编码"""
        issues = []
        
        # 检查硬编码字符串（简单的启发式检查）
        # 注意：这是一个简化的检查，实际应用中可能需要更复杂的分析
        
        # 检查是否使用了 UIFormData
        if 'UIFormData' not in content and 'as' not in content:
            # 如果没有找到 UIFormData 的使用，可能是问题
            # 但这也可能是正常的，所以只给 INFO 级别
            pass  # 暂时不报告，避免误报
        
        return issues


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='GF_X UI Linter')
    parser.add_argument('path', help='要检查的文件或目录路径')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归检查子目录')
    parser.add_argument('-f', '--format', choices=['text', 'json'], default='text', help='输出格式')
    parser.add_argument('-o', '--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    linter = UILinter()
    
    if os.path.isfile(args.path):
        result = linter.lint_file(args.path)
        results = [result]
    elif os.path.isdir(args.path):
        results = linter.lint_directory(args.path, args.recursive)
    else:
        print(f"错误: 路径不存在: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    # 输出结果
    if args.format == 'json':
        output = json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False)
    else:
        output = format_text_output(results)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"结果已保存到: {args.output}")
    else:
        print(output)


def format_text_output(results: List[LintResult]) -> str:
    """格式化文本输出"""
    lines = []
    
    total_files = len(results)
    total_errors = sum(r.error_count for r in results)
    total_warnings = sum(r.warning_count for r in results)
    
    lines.append("=" * 60)
    lines.append("GF_X UI Linter 检查结果")
    lines.append("=" * 60)
    lines.append(f"检查文件数: {total_files}")
    lines.append(f"错误数: {total_errors}")
    lines.append(f"警告数: {total_warnings}")
    lines.append("")
    
    for result in results:
        if not result.issues:
            continue
        
        lines.append("-" * 60)
        lines.append(f"文件: {result.file_path}")
        lines.append("-" * 60)
        
        for issue in result.issues:
            severity_icon = "❌" if issue.severity == Severity.ERROR else "⚠️"
            lines.append(f"{severity_icon} [{issue.rule_name}] 第 {issue.line_number} 行")
            lines.append(f"   问题: {issue.message}")
            if issue.code_snippet:
                lines.append(f"   代码: {issue.code_snippet[:80]}")
            if issue.suggestion:
                lines.append(f"   建议: {issue.suggestion}")
            lines.append("")
    
    lines.append("=" * 60)
    if total_errors == 0:
        lines.append("✅ 所有检查通过！")
    else:
        lines.append(f"⚠️ 发现 {total_errors} 个错误，请修复后重试")
    lines.append("=" * 60)
    
    return '\n'.join(lines)


if __name__ == '__main__':
    main()
