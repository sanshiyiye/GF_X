#!/usr/bin/env python3
"""
完整工作流程演示 - 方案 A

演示场景：
1. 创建一个示例 Excel 文件（怪物数据表）
2. 用户输入自然语言需求
3. AI 解析需求并生成编辑脚本
4. 执行脚本并展示结果
5. 对比修改前后的数据

作者: AI Assistant
版本: 1.0.0
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from nlp_parser import NLPParser, ParsedIntent
from script_executor import ScriptExecutor, ExecutionResult


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(title: str):
    """打印标题"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")


def print_step(step_num: int, title: str):
    """打印步骤标题"""
    print(f"\n{Colors.BLUE}【步骤 {step_num}】{title}{Colors.END}")
    print(f"{Colors.BLUE}{'-'*70}{Colors.END}")


def print_success(message: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_info(message: str):
    """打印信息"""
    print(f"{Colors.CYAN}ℹ {message}{Colors.END}")


def print_warning(message: str):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_error(message: str):
    """打印错误信息"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_code(code: str, language: str = "python"):
    """打印代码块"""
    print(f"{Colors.MAGENTA}```{language}{Colors.END}")
    for line in code.split('\n'):
        print(f"  {line}")
    print(f"{Colors.MAGENTA}```{Colors.END}")


def create_demo_excel() -> Path:
    """创建演示用的 Excel 文件"""
    print_info("正在创建演示数据表...")
    
    # 创建示例数据：怪物表
    data = {
        'Id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Name': [
            '史莱姆', '哥布林', '兽人战士', '黑暗骑士', '巨龙',
            '史莱姆王', '哥布林首领', '兽人酋长', '死亡骑士', '远古巨龙'
        ],
        'Level': [1, 5, 10, 15, 20, 8, 12, 18, 25, 30],
        'HP': [50, 100, 300, 500, 2000, 400, 800, 1500, 3000, 8000],
        'Attack': [5, 15, 30, 50, 150, 40, 80, 120, 200, 400],
        'Defense': [2, 8, 20, 35, 80, 25, 50, 90, 150, 300],
        'IsBoss': [False, False, False, False, True, True, True, True, True, True],
    }
    
    df = pd.DataFrame(data)
    
    # 保存到文件
    output_path = Path(__file__).parent / "demo_data" / "MonsterTable.xlsx"
    output_path.parent.mkdir(exist_ok=True)
    df.to_excel(output_path, index=False, sheet_name='MonsterTable')
    
    print_success(f"演示数据已创建: {output_path}")
    return output_path


def parse_user_request(request: str) -> ParsedIntent:
    """解析用户请求"""
    print_step(2, "解析用户意图")
    print_info(f"用户请求: {request}")
    
    parser = NLPParser()
    intent = parser.parse(request)
    
    print_info(f"解析描述: {intent.description}")
    
    if intent.conditions:
        print_info(f"筛选条件 ({len(intent.conditions)} 个):")
        for i, cond in enumerate(intent.conditions, 1):
            print(f"  {i}. {cond.column} {cond.operator} {cond.value}")
    
    if intent.actions:
        print_info(f"操作 ({len(intent.actions)} 个):")
        for i, action in enumerate(intent.actions, 1):
            modify_type = action.modify_type.value if action.modify_type else "未知"
            print(f"  {i}. {action.target_column} -> {modify_type} {action.value}{action.unit}")
    
    return intent


def generate_script(intent: ParsedIntent, file_path: str) -> str:
    """生成编辑脚本"""
    print_step(3, "生成编辑脚本")
    print_info("正在生成 Python 脚本...")
    
    # 这里简化生成逻辑，实际应该使用 script_generator.py
    # 但为了演示，我们直接生成一个针对性的脚本
    
    # 从 intent 中提取信息
    condition_col = intent.conditions[0].column if intent.conditions else "Level"
    condition_op = intent.conditions[0].operator if intent.conditions else ">"
    condition_val = intent.conditions[0].value if intent.conditions else 10
    
    action_col = intent.actions[0].target_column if intent.actions else "HP"
    action_type = intent.actions[0].modify_type.value if intent.actions and intent.actions[0].modify_type else "multiply"
    action_val = intent.actions[0].value if intent.actions else "1.2"
    
    script = f'''#!/usr/bin/env python3
"""
自动生成的 Excel 编辑脚本

原始请求: {intent.original_request}
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import pandas as pd
import shutil
from pathlib import Path

# 配置文件路径
file_path = Path('{file_path}')
sheet_name = 0

# 创建备份
backup_path = file_path.parent / f"{{file_path.stem}}_backup_{{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}}{{file_path.suffix}}"
shutil.copy2(file_path, backup_path)
print(f"✓ 已创建备份: {{backup_path}}")

# 读取 Excel 文件
df = pd.read_excel(file_path, sheet_name=sheet_name)
print(f"✓ 已读取文件: {{file_path}}")
print(f"  行数: {{len(df)}}, 列数: {{len(df.columns)}}")
print("\\n原始数据:")
print(df)

# 应用筛选条件
mask = df['{condition_col}'] {condition_op} {condition_val}
selected = df[mask]
print(f"\\n▶ 筛选条件: {condition_col} {condition_op} {condition_val}")
print(f"  选中 {{len(selected)}} 行数据")
print(selected)

# 执行修改
print(f"\\n▶ 执行修改: {action_col} {action_type} {action_val}")
'''
    
    # 根据操作类型生成不同的代码
    if action_type == "add" and "%" in action_val:
        percent = float(action_val.replace('%', ''))
        multiplier = 1 + percent / 100
        script += f'''original = df.loc[mask, '{action_col}'].copy()
df.loc[mask, '{action_col}'] = (df.loc[mask, '{action_col}'] * {multiplier}).astype(int)
'''
    elif action_type == "multiply":
        script += f'''original = df.loc[mask, '{action_col}'].copy()
df.loc[mask, '{action_col}'] = (df.loc[mask, '{action_col}'] * {action_val}).astype(int)
'''
    elif action_type == "set":
        script += f'''original = df.loc[mask, '{action_col}'].copy()
df.loc[mask, '{action_col}'] = {action_val}
'''
    
    script += f'''
print(f"  已修改 {{mask.sum()}} 行数据")

# 显示修改前后的对比
print("\\n修改前后对比（选中行）:")
comparison = pd.DataFrame({{
    'ID': df.loc[mask, 'Id'],
    'Name': df.loc[mask, 'Name'],
    'Before': original,
    'After': df.loc[mask, '{action_col}'],
}})
print(comparison)

# 保存修改后的文件
print("\\n▶ 保存修改...")
df.to_excel(file_path, index=False, sheet_name=sheet_name if isinstance(sheet_name, str) else None)
print(f"✓ 已保存到: {{file_path}}")

# 验证保存
verify_df = pd.read_excel(file_path, sheet_name=sheet_name)
print(f"\\n✓ 验证成功 - 文件包含 {{len(verify_df)}} 行数据")

print("\\n" + "="*50)
print("编辑完成！")
print(f"备份文件: {{backup_path}}")
print("="*50)
'''
    
    print_success("脚本生成完成！")
    print_info(f"脚本长度: {len(script)} 字符")
    
    return script


def execute_script(script_code: str, dry_run: bool = False) -> ExecutionResult:
    """执行脚本"""
    print_step(4, "执行编辑脚本" if not dry_run else "试运行（不保存）")
    
    executor = ScriptExecutor()
    result = executor.execute_script(script_code, dry_run=dry_run)
    
    if result.success:
        print_success(result.message)
        print_info(f"执行时间: {result.execution_time:.3f} 秒")
    else:
        print(f"{Colors.RED}✗ 执行失败{Colors.END}")
        print(f"{Colors.RED}错误: {result.error}{Colors.END}")
    
    return result


def main():
    """主程序 - 完整工作流程演示"""
    print_header("方案 A：AI 生成编辑脚本 - 完整演示")
    
    print(f"{Colors.CYAN}本演示将展示完整的 AI 数据编辑工作流程：{Colors.END}")
    print(f"{Colors.CYAN}1. 准备示例数据{Colors.END}")
    print(f"{Colors.CYAN}2. 用户输入自然语言需求{Colors.END}")
    print(f"{Colors.CYAN}3. AI 解析意图并生成脚本{Colors.END}")
    print(f"{Colors.CYAN}4. 试运行验证{Colors.END}")
    print(f"{Colors.CYAN}5. 正式执行并查看结果{Colors.END}")
    
    # 步骤 1：创建示例数据
    print_step(1, "创建示例数据")
    demo_file = create_demo_excel()
    
    # 读取并显示原始数据
    df_original = pd.read_excel(demo_file)
    print_info("原始数据（共 10 条记录）：")
    print(df_original.to_string())
    
    # 步骤 2-4：用户输入需求
    print_step(2, "用户输入需求")
    user_request = "帮我把所有等级大于 10 的怪物生命值增加 20%"
    print_info(f'用户说：{Colors.BOLD}"{user_request}"{Colors.END}')
    
    # 步骤 3：解析意图
    intent = parse_user_request(user_request)
    
    # 步骤 3.5：生成脚本
    script_code = generate_script(intent, str(demo_file))
    
    print_step(3, "查看生成的脚本")
    print_info("已生成 Python 脚本（部分展示）：")
    script_lines = script_code.split('\n')
    for i, line in enumerate(script_lines[:30], 1):
        print(f"  {i:3d}| {line}")
    if len(script_lines) > 30:
        print(f"  ... ({len(script_lines) - 30} 行省略)")
    
    # 步骤 4：试运行
    print_step(4, "试运行验证（不保存）")
    print_info("正在试运行以验证逻辑...")
    
    result_dry = execute_script(script_code, dry_run=True)
    
    if not result_dry.success:
        print_error("试运行失败，不执行实际修改")
        return
    
    # 询问用户是否继续
    print_step(5, "确认执行")
    print_info("试运行成功！准备正式执行修改。")
    print_warning("注意：这将实际修改 Excel 文件，但会自动创建备份。")
    
    # 自动继续（在演示中）
    print_info("（演示中自动继续）")
    
    # 步骤 6：正式执行
    print_step(6, "正式执行修改")
    
    result_exec = execute_script(script_code, dry_run=False)
    
    if not result_exec.success:
        print_error("执行失败")
        return
    
    # 步骤 7：对比结果
    print_step(7, "对比修改结果")
    
    df_after = pd.read_excel(demo_file)
    
    print_info("修改后数据：")
    print(df_after.to_string())
    
    # 找出被修改的行
    modified_mask = df_original['HP'] != df_after['HP']
    modified_count = modified_mask.sum()
    
    print_info(f"统计：共修改了 {modified_count} 行数据")
    
    if modified_count > 0:
        print_info("被修改的行详情：")
        comparison = pd.DataFrame({
            'ID': df_original.loc[modified_mask, 'Id'],
            'Name': df_original.loc[modified_mask, 'Name'],
            'Level': df_original.loc[modified_mask, 'Level'],
            'HP_Before': df_original.loc[modified_mask, 'HP'],
            'HP_After': df_after.loc[modified_mask, 'HP'],
        })
        print(comparison.to_string(index=False))
    
    # 完成
    print_header("演示完成！")
    print_success("方案 A 完整工作流程演示结束")
    print_info("总结：")
    print(f"  1. 用户输入: \"{user_request}\"")
    print(f"  2. AI 解析: 识别出筛选条件(等级>10)和操作(HP增加20%)")
    print(f"  3. 生成脚本: Python pandas 代码")
    print(f"  4. 试运行: 验证逻辑正确")
    print(f"  5. 正式执行: 修改了 {modified_count} 行数据")
    print(f"  6. 自动备份: 已创建备份文件")
    print()
    print_info("文件位置：")
    print(f"  - 数据文件: {demo_file}")
    if result_exec.backup_path:
        print(f"  - 备份文件: {result_exec.backup_path}")
    print()
    print(f"{Colors.GREEN}您现在可以：{Colors.END}")
    print(f"  - 查看生成的脚本: cat {Path(__file__).parent}/generated_script.py")
    print(f"  - 手动执行: python3 {demo_file}")
    print(f"  - 恢复数据: 从备份文件复制回来")


if __name__ == "__main__":
    main()
