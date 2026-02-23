#!/usr/bin/env python3
"""
GF_X UI Linter - 检查 UI 代码规范
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    line: int
    severity: Severity
    code: str
    message: str
    suggestion: str = ""


@dataclass
class LintResult:
    file_path: str
    passed: bool = False
    issues: List[Issue] = field(default_factory=list)
    score: int = 100


class UIRules:
    """UI 代码规范检查规则"""
    
    REQUIRED_BASE_CLASS = "UIFormBase"
    WRONG_BASE_CLASS = "UIFormLogic"
    
    FORBIDDEN_APIS = [
        (r'Resources\.Load', "使用 Resources.Load"),
        (r'Instantiate\s*\(', "使用 Instantiate"),
        (r'Destroy\s*\(', "使用 Destroy"),
        (r'GameObject\.Find', "使用 GameObject.Find"),
    ]
    
    @classmethod
    def check_naming(cls, content: str, line_num: int, line: str) -> Optional[Issue]:
        """检查命名规范"""
        class_match = re.search(r'class\s+(\w+)', line)
        if class_match:
            class_name = class_match.group(1)
            if class_name.endswith('UIFormLogic'):
                return Issue(
                    line=line_num,
                    severity=Severity.ERROR,
                    code="NAM001",
                    message=f"类名 '{class_name}' 应该以 UIForm 结尾，而不是 UIFormLogic",
                    suggestion=f"将 {class_name} 重命名为 {class_name.replace('Logic', '')}"
                )
        return None
    
    @classmethod
    def check_inheritance(cls, content: str, line_num: int, line: str) -> Optional[Issue]:
        """检查继承关系"""
        if 'class' in line and ':' in line:
            if cls.WRONG_BASE_CLASS in line:
                return Issue(
                    line=line_num,
                    severity=Severity.ERROR,
                    code="INH001",
                    message=f"类继承自 {cls.WRONG_BASE_CLASS}，应该继承自 {cls.REQUIRED_BASE_CLASS}",
                    suggestion=f"将继承关系改为 : {cls.REQUIRED_BASE_CLASS}"
                )
        return None
    
    @classmethod
    def check_forbidden_apis(cls, content: str, line_num: int, line: str) -> List[Issue]:
        """检查禁止使用的 API"""
        issues = []
        for pattern, description in cls.FORBIDDEN_APIS:
            if re.search(pattern, line):
                issues.append(Issue(
                    line=line_num,
                    severity=Severity.ERROR,
                    code="API001",
                    message=f"使用了禁止的 API: {description}",
                    suggestion="使用 GF 框架提供的对应 API"
                ))
        return issues
    
    @classmethod
    def check_lifecycle(cls, content: str) -> List[Issue]:
        """检查生命周期方法"""
        issues = []
        
        subscribe_pattern = r'GF\.Event\.Subscribe\s*\('
        unsubscribe_pattern = r'GF\.Event\.Unsubscribe\s*\('
        
        subscribe_count = len(re.findall(subscribe_pattern, content))
        unsubscribe_count = len(re.findall(unsubscribe_pattern, content))
        
        if subscribe_count > unsubscribe_count:
            issues.append(Issue(
                line=0,
                severity=Severity.ERROR,
                code="LIF001",
                message=f"有 {subscribe_count} 个 Subscribe 但只有 {unsubscribe_count} 个 Unsubscribe，可能导致内存泄漏",
                suggestion="在 OnClose 或 OnLeave 中添加对应的 Unsubscribe"
            ))
        
        return issues


def lint_ui_file(file_path: str) -> LintResult:
    """检查单个 UI 文件"""
    result = LintResult(file_path=file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        result.issues.append(Issue(
            line=0,
            severity=Severity.ERROR,
            code="FILE001",
            message=f"无法读取文件: {str(e)}"
        ))
        return result
    
    # 逐行检查
    for line_num, line in enumerate(lines, start=1):
        issue = UIRules.check_naming(content, line_num, line)
        if issue:
            result.issues.append(issue)
        
        issue = UIRules.check_inheritance(content, line_num, line)
        if issue:
            result.issues.append(issue)
        
        issues = UIRules.check_forbidden_apis(content, line_num, line)
        result.issues.extend(issues)
    
    # 生命周期检查
    issues = UIRules.check_lifecycle(content)
    result.issues.extend(issues)
    
    # 计算得分
    error_count = sum(1 for i in result.issues if i.severity == Severity.ERROR)
    warning_count = sum(1 for i in result.issues if i.severity == Severity.WARNING)
    
    result.score = max(0, 100 - error_count * 10 - warning_count * 3)
    result.passed = error_count == 0 and result.score >= 80
    
    return result


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GF_X UI Linter')
    parser.add_argument('file', help='UI 代码文件路径')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    parser.add_argument('--fix', action='store_true', help='尝试自动修复')
    
    args = parser.parse_args()
    
    result = lint_ui_file(args.file)
    
    if args.json:
        import json
        print(json.dumps({
            'file_path': result.file_path,
            'passed': result.passed,
            'score': result.score,
            'issues': [{'line': i.line, 'severity': i.severity.value, 'code': i.code, 
                       'message': i.message, 'suggestion': i.suggestion} for i in result.issues]
        }, indent=2, ensure_ascii=False))
    else:
        print(f"\n📄 文件: {result.file_path}")
        print(f"📊 得分: {result.score}/100")
        print(f"✅ 结果: {'通过' if result.passed else '未通过'}")
        
        if result.issues:
            print(f"\n🔍 发现 {len(result.issues)} 个问题:\n")
            
            errors = [i for i in result.issues if i.severity == Severity.ERROR]
            warnings = [i for i in result.issues if i.severity == Severity.WARNING]
            
            for issue in errors:
                print(f"  ❌ [错误] 第 {issue.line} 行 ({issue.code})")
                print(f"     {issue.message}")
                if issue.suggestion:
                    print(f"     💡 建议: {issue.suggestion}")
                print()
            
            for issue in warnings:
                print(f"  ⚠️  [警告] 第 {issue.line} 行 ({issue.code})")
                print(f"     {issue.message}")
                if issue.suggestion:
                    print(f"     💡 建议: {issue.suggestion}")
                print()
        else:
            print("\n✨ 没有发现问题！代码符合规范。\n")
    
    sys.exit(0 if result.passed else 1)


if __name__ == '__main__':
    main()
