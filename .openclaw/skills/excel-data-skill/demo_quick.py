#!/usr/bin/env python3
"""
方案 A 快速演示 - 自然语言编辑 Excel

使用方式:
1. 运行脚本: python3 demo_quick.py
2. 查看生成的编辑脚本
3. 手动执行脚本或修改后执行

作者: AI Assistant
版本: 1.0.0
"""

import sys
import pandas as pd
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def create_sample_data():
    """创建示例怪物数据表"""
    print("="*60)
    print("【步骤 1】创建示例数据")
    print("="*60)
    
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
    output_dir = Path(__file__).parent / "demo_data"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "MonsterTable.xlsx"
    df.to_excel(output_file, index=False, sheet_name='MonsterTable')
    
    print(f"✓ 示例数据已创建: {output_file}")
    print(f"\n原始数据（共 {len(df)} 条记录）:")
    print(df.to_string())
    
    return output_file, df


def generate_edit_script(user_request: str, file_path: str, df_original: pd.DataFrame) -> str:
    """根据用户请求生成编辑脚本"""
    print("\n" + "="*60)
    print("【步骤 2】AI 分析用户意图")
    print("="*60)
    
    print(f"用户请求: \"{user_request}\"")
    
    # 简单解析（实际应该用 NLPParser）
    # 解析："帮我把所有等级大于 10 的怪物生命值增加 20%"
    print("\nAI 解析:")
    print("  - 筛选条件: 等级 > 10")
    print("  - 目标列: 生命值 (HP)")
    print("  - 操作: 增加 20%")
    
    # 生成脚本
    print("\n" + "="*60)
    print("【步骤 3】生成编辑脚本")
    print("="*60)
    
    script = f'''#!/usr/bin/env python3
"""
自动生成的 Excel 编辑脚本

原始请求: {user_request}
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import pandas as pd
import shutil
from pathlib import Path
from datetime import datetime

# 文件路径
file_path = Path('{file_path}')
sheet_name = 'MonsterTable'

print("="*60)
print("Excel 数据编辑器")
print("="*60)

# 1. 创建备份
backup_path = file_path.parent / f"{{file_path.stem}}_backup_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}{{file_path.suffix}}"
shutil.copy2(file_path, backup_path)
print(f"✓ 已创建备份: {{backup_path}}")

# 2. 读取数据
df = pd.read_excel(file_path, sheet_name=sheet_name)
print(f"✓ 已读取数据: {{len(df)}} 行, {{len(df.columns)}} 列")

# 3. 显示原始数据
print("\\n原始数据:")
print(df.to_string())

# 4. 应用筛选条件
print("\\n" + "="*60)
print("应用筛选: 等级 > 10")
print("="*60)

mask = df['Level'] > 10
selected = df[mask].copy()
print(f"✓ 筛选完成: 选中 {{len(selected)}} 行数据")
print("\\n被选中的数据:")
print(selected.to_string())

# 5. 执行修改
print("\\n" + "="*60)
print("执行修改: 生命值(HP) 增加 20%")
print("="*60)

# 记录修改前的值
before_values = df.loc[mask, 'HP'].copy()

# 执行修改: HP = HP * 1.2
df.loc[mask, 'HP'] = (df.loc[mask, 'HP'] * 1.2).astype(int)

# 记录修改后的值
after_values = df.loc[mask, 'HP']

print(f"✓ 修改完成: 已修改 {{mask.sum()}} 行数据")

# 显示修改对比
print("\\n修改前后对比:")
comparison = pd.DataFrame({{
    'ID': df.loc[mask, 'Id'],
    'Name': df.loc[mask, 'Name'],
    'Level': df.loc[mask, 'Level'],
    'HP_Before': before_values,
    'HP_After': after_values,
    'Change': after_values - before_values,
}})
print(comparison.to_string(index=False))

# 6. 保存文件
print("\\n" + "="*60)
print("保存修改")
print("="*60)

print("▶ 正在保存...")
df.to_excel(file_path, index=False, sheet_name=sheet_name)
print(f"✓ 已保存到: {{file_path}}")

# 7. 验证保存
verify_df = pd.read_excel(file_path, sheet_name=sheet_name)
print(f"✓ 验证成功: 文件包含 {{len(verify_df)}} 行数据")

# 8. 显示最终数据
print("\\n" + "="*60)
print("最终数据")
print("="*60)
print(df.to_string())

# 完成
print("\\n" + "="*60)
print("✓ 编辑完成！")
print("="*60)
print(f"备份文件: {{backup_path}}")
print(f"数据文件: {{file_path}}")
print("="*60)
'''
    
    print_info("已生成编辑脚本")
    print_info(f"脚本长度: {len(script)} 字符")
    
    # 保存脚本到文件
    script_path = Path(file_path).parent / "generated_edit_script.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script)
    print_info(f"脚本已保存: {script_path}")
    
    return script


def main():
    """主程序"""
    print("\n" + "="*70)
    print("  Excel 数据编辑 Skill - 方案 A 完整演示")
    print("  功能：AI 理解自然语言 → 生成编辑脚本 → 执行修改")
    print("="*70)
    
    # 步骤 1：创建示例数据
    file_path, df_original = create_sample_data()
    
    # 步骤 2-3：用户输入需求并生成脚本
    user_request = "帮我把所有等级大于 10 的怪物生命值增加 20%"
    script = generate_edit_script(user_request, str(file_path), df_original)
    
    # 显示完整的脚本
    print("\n" + "="*60)
    print("【生成的完整脚本】")
    print("="*60)
    print(script)
    
    # 步骤 4：提示用户如何执行
    print("\n" + "="*70)
    print("【演示完成】")
    print("="*70)
    print("\n✅ 已成功生成编辑脚本！")
    print(f"\n脚本文件位置:")
    script_path = Path(file_path).parent / "generated_edit_script.py"
    print(f"  {script_path}")
    
    print(f"\n数据文件位置:")
    print(f"  {file_path}")
    
    print(f"\n你可以手动执行脚本:")
    print(f"  cd {Path(file_path).parent}")
    print(f"  python3 generated_edit_script.py")
    
    print(f"\n或者直接运行完整演示:")
    print(f"  python3 demo_full_workflow.py")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
