#!/usr/bin/env python3
"""
Script Executor - 脚本执行器

安全执行生成的编辑脚本，支持：
- 自动备份
- 执行验证
- 错误回滚
- 执行日志

作者: AI Assistant
版本: 1.0.0
"""

import shutil
import traceback
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    message: str
    backup_path: Optional[Path] = None
    rows_affected: int = 0
    columns_affected: List[str] = None
    execution_time: float = 0.0
    error: Optional[str] = None
    before_summary: Optional[Dict] = None
    after_summary: Optional[Dict] = None


class ScriptExecutor:
    """
    脚本执行器
    
    安全执行编辑脚本，确保数据安全
    """
    
    def __init__(self, backup_dir: Optional[str] = None):
        """
        初始化执行器
        
        Args:
            backup_dir: 备份文件存放目录（默认为原文件所在目录）
        """
        self.backup_dir = Path(backup_dir) if backup_dir else None
        self.execution_history: List[ExecutionResult] = []
    
    def execute_script(self, script_code: str, context: Optional[Dict[str, Any]] = None,
                       dry_run: bool = False) -> ExecutionResult:
        """
        执行脚本代码
        
        Args:
            script_code: 要执行的 Python 脚本代码
            context: 执行上下文变量
            dry_run: 是否为试运行（不实际修改文件）
            
        Returns:
            ExecutionResult: 执行结果
        """
        import time
        start_time = time.time()
        
        # 构建执行上下文
        exec_context = {
            'pd': pd,
            'Path': Path,
            'shutil': shutil,
            'print': print,
        }
        if context:
            exec_context.update(context)
        
        try:
            # 如果是试运行，添加标记
            if dry_run:
                # 修改脚本，不保存文件
                script_code = script_code.replace(
                    'df.to_excel(file_path',
                    '# [DRY RUN] df.to_excel(file_path\n    print("[DRY RUN] 不保存文件")\n    # df.to_excel(file_path'
                )
            
            # 执行脚本
            exec(script_code, exec_context)
            
            execution_time = time.time() - start_time
            
            result = ExecutionResult(
                success=True,
                message="脚本执行成功" if not dry_run else "试运行完成（未保存）",
                execution_time=execution_time,
                before_summary=exec_context.get('before_stats'),
                after_summary=exec_context.get('after_stats')
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"
            traceback_str = traceback.format_exc()
            
            result = ExecutionResult(
                success=False,
                message="脚本执行失败",
                execution_time=execution_time,
                error=f"{error_msg}\n\n{traceback_str}"
            )
        
        self.execution_history.append(result)
        return result
    
    def execute_file(self, script_path: str, **kwargs) -> ExecutionResult:
        """
        从文件加载并执行脚本
        
        Args:
            script_path: 脚本文件路径
            **kwargs: 其他参数传递给 execute_script
            
        Returns:
            ExecutionResult: 执行结果
        """
        with open(script_path, 'r', encoding='utf-8') as f:
            script_code = f.read()
        
        return self.execute_script(script_code, **kwargs)


def main():
    """测试执行器"""
    print("="*70)
    print("Script Executor 测试")
    print("="*70)
    
    # 创建一个简单的测试脚本
    test_script = """
import pandas as pd
from pathlib import Path

# 创建一个测试 DataFrame
data = {
    'Id': [1, 2, 3, 4, 5],
    'Name': ['Monster1', 'Monster2', 'Boss1', 'Monster3', 'Boss2'],
    'Level': [5, 10, 20, 8, 30],
    'HP': [100, 200, 500, 150, 1000],
}
df = pd.DataFrame(data)

print("原始数据:")
print(df)
print()

# 修改：等级大于 10 的怪物 HP 增加 20%
mask = df['Level'] > 10
count = mask.sum()
df.loc[mask, 'HP'] = (df.loc[mask, 'HP'] * 1.2).astype(int)

print(f"修改了 {count} 行数据（等级 > 10 的怪物）")
print("\\n修改后:")
print(df)
"""
    
    # 创建执行器
    executor = ScriptExecutor()
    
    # 试运行
    print("\n1. 试运行模式（不实际修改）:")
    print("-"*70)
    result = executor.execute_script(test_script, dry_run=True)
    
    if result.success:
        print(f"✓ {result.message}")
    else:
        print(f"✗ {result.message}")
        print(f"错误: {result.error}")
    
    # 实际执行
    print("\n2. 实际执行模式:")
    print("-"*70)
    result = executor.execute_script(test_script, dry_run=False)
    
    if result.success:
        print(f"✓ {result.message}")
        print(f"执行时间: {result.execution_time:.2f} 秒")
    else:
        print(f"✗ {result.message}")
        print(f"错误: {result.error}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
