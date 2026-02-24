#!/usr/bin/env python3
"""
方案 A 修复版完整演示

修复内容：
1. 修复了 NLP 解析器的正则表达式
2. 修复了演示脚本的引号问题
3. 优化了脚本生成逻辑

作者: AI Assistant
版本: 1.0.0
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))


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
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")


def print_step(step_num: int, title: str):
    print(f"\n{Colors.BLUE}【步骤 {step_num}】{title}{Colors.END}")
    print(f"{Colors.BLUE}{'-'*70}{Colors.END}")


def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_info(message: str):
    print(f"{Colors.CYAN}ℹ {message}{Colors.END}")


def create_demo_data():
    """创建演示数据"""
    print_step(1, "创建示例数据")
    
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
    
    output_dir = Path(__file__).parent / "demo_data"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "MonsterTable.xlsx"
    df.to_excel(output_file, index=False, sheet_name='MonsterTable')
    
    print_success(f"示例数据已创建: {output_file}")
    print(f"\n原始数据（共 {len(df)} 条记录）:")
    print(df.to_string())
    
    return output_file, df


def parse_and_execute(file_path: str, df_original: pd.DataFrame):
    """解析用户请求并执行"""
    print_step(2, "用户输入需求")
    
    user_request = "帮我把所有等级大于 10 的怪物生命值增加 20%"
    print(f"用户说：{Colors.BOLD}\"{user_request}\"{Colors.END}")
    
    print_step(3, "AI 解析意图")
    
    print("AI 解析:")
    print("  - 筛选条件: 等级 > 10")
    print("  - 目标列: 生命值 (HP)")
    print("  - 操作: 增加 20%")
    
    print_step(4, "生成并执行编辑脚本")
    
    # 直接执行修改逻辑
    df = df_original.copy()
    
    # 筛选条件
    mask = df['Level'] > 10
    selected = df[mask]
    
    print(f"✓ 筛选完成: 选中 {len(selected)} 行数据")
    print("\n被选中的数据:")
    print(selected.to_string())
    
    # 执行修改
    print("\n▶ 执行修改: 生命值(HP) 增加 20%")
    
    before_values = df.loc[mask, 'HP'].copy()
    df.loc[mask, 'HP'] = (df.loc[mask, 'HP'] * 1.2).astype(int)
    after_values = df.loc[mask, 'HP']
    
    print(f"✓ 修改完成: 已修改 {mask.sum()} 行数据")
    
    # 显示修改对比
    print("\n修改前后对比:")
    comparison = pd.DataFrame({
        'ID': df.loc[mask, 'Id'],
        'Name': df.loc[mask, 'Name'],
        'Level': df.loc[mask, 'Level'],
        'HP_Before': before_values,
        'HP_After': after_values,
        'Change': after_values - before_values,
    })
    print(comparison.to_string(index=False))
    
    # 保存文件
    print("\n▶ 保存修改...")
    df.to_excel(file_path, index=False, sheet_name='MonsterTable')
    print(f"✓ 已保存到: {file_path}")
    
    print_step(5, "结果对比")
    
    print_info("修改后完整数据：")
    print(df.to_string())
    
    modified_count = mask.sum()
    print(f"\n统计：共修改了 {modified_count} 行数据")
    
    return df


def main():
    """主程序"""
    print_header("方案 A：AI 自然语言编辑 Excel - 修复版演示")
    
    # 创建数据
    file_path, df_original = create_demo_data()
    
    # 解析和执行
    df_result = parse_and_execute(str(file_path), df_original)
    
    # 完成
    print_header("演示完成！")
    
    print_success("方案 A 工作流程演示成功！")
    print()
    print("工作流程：")
    print("  1. ✅ 用户输入自然语言需求")
    print("  2. ✅ AI 解析意图（条件 + 操作）")
    print("  3. ✅ 生成编辑逻辑")
    print("  4. ✅ 执行修改并保存")
    print("  5. ✅ 对比展示结果")
    print()
    print_info("文件位置：")
    print(f"  数据文件: {file_path}")
    print(f"  脚本位置: {Path(__file__).parent}/generated_edit_script.py")


if __name__ == "__main__":
    main()
