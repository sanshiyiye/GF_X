# 方案 A 完整演示指南

## 🎯 演示目标

展示 **AI 自然语言编辑 Excel** 的完整工作流程：

```
用户自然语言 → AI 解析 → 生成脚本 → 执行修改 → 查看结果
```

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `demo_full_workflow.py` | 完整自动化演示 |
| `demo_quick.py` | 简化快速演示 |
| `demo_data/` | 演示数据目录 |
| `generated_edit_script.py` | 生成的编辑脚本 |

## 🚀 快速开始

### 方式 1：运行完整演示（推荐）

```bash
cd /data/GF_X/.openclaw/skills/excel-data-skill
source venv/bin/activate
python3 demo_full_workflow.py
```

**预期输出：**
```
======================================================================
  方案 A：AI 生成编辑脚本 - 完整演示
======================================================================

【步骤 1】创建示例数据
...
【步骤 2】用户输入需求
用户说："帮我把所有等级大于 10 的怪物生命值增加 20%"
...
【步骤 3】AI 解析意图
...
【步骤 4】生成编辑脚本
...
【步骤 5】试运行验证
...
【步骤 6】正式执行
...
【步骤 7】对比结果
...
```

### 方式 2：分步手动测试

#### 步骤 1：准备环境

```bash
# 进入目录
cd /data/GF_X/.openclaw/skills/excel-data-skill

# 激活虚拟环境
source venv/bin/activate

# 检查文件
ls -la
```

#### 步骤 2：创建测试数据

```python
# 运行 Python 交互式环境
python3

# 执行以下代码
import pandas as pd
from pathlib import Path

# 创建测试数据
data = {
    'Id': [1, 2, 3, 4, 5],
    'Name': ['史莱姆', '哥布林', '兽人', '骑士', '巨龙'],
    'Level': [1, 5, 10, 15, 20],
    'HP': [50, 100, 300, 500, 2000],
    'Attack': [5, 15, 30, 50, 150],
    'Defense': [2, 8, 20, 35, 80],
    'IsBoss': [False, False, False, False, True],
}

df = pd.DataFrame(data)
print("原始数据:")
print(df)

# 保存
output_path = Path("demo_data/ManualTest.xlsx")
output_path.parent.mkdir(exist_ok=True)
df.to_excel(output_path, index=False)
print(f"\n已保存到: {output_path}")

# 退出
exit()
```

#### 步骤 3：测试 NLP 解析

```python
# 运行 NLP 解析测试
python3 nlp_parser.py

# 查看输出，应该看到类似：
# ====================================================================
# NLP Parser 测试
# ====================================================================
# 
# 📢 用户请求: 帮我把所有等级大于 10 的怪物生命值增加 20%
# --------------------------------------------------------------------
# 📋 描述: 筛选条件: 等级 > 10; 操作: 生命值 增加 20%
# ...
```

#### 步骤 4：运行集成测试

```bash
# 运行单元测试
python3 test_validator.py

# 运行集成测试
python3 test_integration.py
```

#### 步骤 5：执行完整演示

```bash
# 运行完整演示
python3 demo_full_workflow.py
```

## 📊 预期结果

### 成功标志

1. **创建数据** ✅
   - 生成 `demo_data/MonsterTable.xlsx`
   - 包含 10 条怪物记录

2. **解析意图** ✅
   - 识别筛选条件: 等级 > 10
   - 识别操作: 生命值增加 20%

3. **生成脚本** ✅
   - 创建 `generated_edit_script.py`
   - 包含完整 pandas 操作代码

4. **执行修改** ✅
   - 修改 6 行数据（Id: 4,5,7,8,9,10）
   - HP 值增加 20%
   - 创建备份文件

5. **结果验证** ✅
   - 对比显示修改前后差异
   - 确认修改正确

## 🔧 故障排除

### 问题 1：ModuleNotFoundError

**症状：**
```
ModuleNotFoundError: No module named 'pandas'
```

**解决：**
```bash
source venv/bin/activate
pip install pandas openpyxl
```

### 问题 2：Permission Denied

**症状：**
```
PermissionError: [Errno 13] Permission denied: 'demo_data'
```

**解决：**
```bash
# 检查目录权限
ls -la

# 如果需要，修改权限
chmod 755 demo_data
```

### 问题 3：NLP 解析不准确

**症状：**
解析结果不符合预期

**解决：**
```python
# 尝试更明确的表达
# 原句: "帮我把所有等级大于 10 的怪物生命值增加 20%"
# 改为: "将 Level > 10 的 HP 增加 20%"
```

## 📝 后续步骤

1. **完善 NLP 解析** 🎯
   - 支持更多表达方式
   - 提高解析准确率

2. **增加操作类型** 🎯
   - 支持删除行
   - 支持添加列
   - 支持批量替换

3. **优化用户体验** 🎯
   - 添加交互式界面
   - 支持撤销/重做
   - 可视化对比

## 📞 支持

如有问题，请检查：
1. 是否已激活虚拟环境
2. 依赖包是否已安装
3. 文件路径是否正确

---

**文档版本**: 1.0.0  
**最后更新**: 2026-02-24
