# Excel 数据编辑 Skill

基于 Schema 标准的 Excel 数据编辑工具，支持 GF_X 框架的三类数据：
- **DataTable**: 游戏数据表
- **Config**: 配置表  
- **Language**: 多语言表

## 核心功能

### 1. Schema 识别
自动识别 Excel 文件的 Schema 类型：
```python
skill = create_skill()
result = skill.identify_schema("MonsterTable.xlsx")
# {
#   "schema_type": "datatable",
#   "confidence": 0.95,
#   "details": {...}
# }
```

### 2. Schema 验证
根据 Schema 标准验证数据合规性：
```python
report = skill.validate("MonsterTable.xlsx")
# {
#   "valid": true,
#   "errors": [],
#   "warnings": [...],
#   "summary": {...}
# }
```

## Schema 标准

### DataTable Schema
- **输入**: `.xlsx` 文件
- **结构**: Id 列 + 数据列
- **输出**: `.txt` + `.bytes` + `.cs`
- **运行时**: `GF.DataTable.GetDataTable<T>()`

**验证规则**:
- 必须包含 Id 列（int 类型，唯一，>= 1）
- 字段名大驼峰命名（如 MonsterId, HpMax）
- 支持类型：int, float, string, Vector3, 数组等

### Config Schema
- **输入**: `.xlsx` 文件
- **结构**: Key/Value 两列
- **输出**: `.txt` + `.bytes`
- **运行时**: `GF.Config.GetString()`

**验证规则**:
- Key 小驼峰命名（如 initialGold, maxLevel）
- Key 唯一，不能为空
- Value 运行时解析为对应类型

### Language Schema
- **输入**: `.xlsx` 文件
- **结构**: Key/Text 两列
- **输出**: `.json`
- **运行时**: `GF.Localization.GetString()`

**验证规则**:
- Key 全大写下划线（如 HELLO_WORLD, ERROR_NETWORK）
- Key 唯一，不能为空
- 特殊字符自动转义（JSON 输出时）

## 文件结构

```
excel-data-skill/
├── skill.yaml              # Skill 定义
├── README.md               # 本文件
├── __init__.py             # 主入口
├── schema_validator.py     # 基础框架
├── datatable_validator.py  # DataTable 验证
├── config_validator.py     # Config 验证
└── language_validator.py   # Language 验证
```

## 安装

```bash
# 依赖
pip install pandas openpyxl xlsxwriter pyyaml
```

## 使用

```python
from excel_data_skill import create_skill

# 创建 Skill
skill = create_skill()

# 1. 识别 Schema
result = skill.identify_schema("DataTables/MonsterTable.xlsx")
print(f"类型: {result['schema_type']}, 置信度: {result['confidence']}")

# 2. 验证数据
report = skill.validate("DataTables/MonsterTable.xlsx")
if report['valid']:
    print("✅ 验证通过")
else:
    print(f"❌ 发现 {len(report['errors'])} 个错误")
    for error in report['errors']:
        print(f"  - [{error['code']}] {error['field']}: {error['message']}")
```

## 开发

### 添加新的验证规则

在对应的验证器中添加：

```python
def _validate_impl(self, df: pd.DataFrame, context: Dict[str, Any]):
    # 你的验证逻辑
    if 某种条件:
        self._add_error(
            field="字段名",
            message="错误信息",
            code="ERROR_CODE",
            suggestion="修复建议"
        )
```

## 许可证

MIT
