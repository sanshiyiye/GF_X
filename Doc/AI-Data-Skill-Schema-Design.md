# AI 数据编辑 Skill - Schema 分类设计方案

> 基于三类数据（DataTable/Config/Language）的不同 Schema 要求，设计输入分类处理和输出标准化机制。

---

## 一、核心设计原则

```
┌─────────────────────────────────────────────────────────────────┐
│                    Schema-Driven Processing                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   输入需求 ──→ 分类器 ──→ 匹配 Schema ──→ 标准化输出               │
│      │           │           │            │                     │
│      ▼           ▼           ▼            ▼                     │
│   "修改怪    识别为      应用        生成符合                      │
│    物血量"   DataTable   DataTable    DataTable                   │
│             类型        Schema       Schema 的                   │
│                                      Excel 数据                  │
│                                                                  │
│   核心约束:                                                       │
│   • 输出必须符合对应类型的 Schema 标准                             │
│   • 不允许跨类型混合（如 DataTable 用 Config 的格式）              │
│   • 每种类型有明确的字段要求和验证规则                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、三类数据的 Schema 标准

### 2.1 DataTable Schema

```yaml
# DataTable 标准 Schema 定义
DataTableSchema:
  type: "DataTable"
  description: "游戏数据表，支持强类型访问和代码生成"
  
  # 必须包含的系统字段
  system_fields:
    - name: "Id"
      type: "int"
      required: true
      description: "唯一标识符，主键"
      constraints:
        unique: true
        min: 1
    
    - name: "Name"
      type: "string"
      required: false
      description: "名称（可选）"
  
  # 支持的字段类型
  supported_types:
    - int
    - float
    - double
    - string
    - bool
    - long
    - DateTime
    - Vector2
    - Vector3
    - Vector4
    - Vector2Int
    - Vector3Int
    - Color
    - Color32
    - enum
    # 数组类型
    - "int[]"
    - "float[]"
    - "string[]"
    - "Vector3[]"
    # 二维数组
    - "int[][]"
    - "float[][]"
  
  # 文件命名规范
  naming:
    pattern: "^[A-Z][a-zA-Z0-9]*Table$"
    examples:
      - "MonsterTable"
      - "ItemTable"
      - "LevelTable"
    
  # 输出要求
  output:
    excel_structure:
      row_1: "表名/注释"
      row_2: "字段名（必须包含 Id）"
      row_3: "数据类型"
      row_4: "默认值（可选）"
      row_5: "字段注释（可选）"
      row_6_plus: "数据内容"
    
    generated_files:
      - "{TableName}.txt"      # Tab分隔文本
      - "{TableName}.bytes"    # 二进制数据
      - "{TableName}.cs"       # C# 代码
  
  # 验证规则
  validation:
    - "Id 列必须存在且类型为 int"
    - "Id 值必须唯一且 >= 1"
    - "字段名必须以大写字母开头"
    - "类型必须是支持的数据类型之一"
    - "数组类型使用 [] 或 [][] 后缀"
    - "枚举类型格式: EnumType.EnumValue"
```

### 2.2 Config Schema

```yaml
# Config 标准 Schema 定义
ConfigSchema:
  type: "Config"
  description: "游戏配置表，键值对形式，运行时弱类型访问"
  
  # 结构特点
  structure:
    type: "key-value pairs"
    description: "两列结构：Key 和 Value"
    
  # 必须包含的列
  required_columns:
    - name: "Key"
      type: "string"
      description: "配置键，唯一标识"
      constraints:
        unique: true
        pattern: "^[a-zA-Z][a-zA-Z0-9_]*$"
    
    - name: "Value"
      type: "string"
      description: "配置值，运行时解析"
  
  # 支持的值类型（运行时解析）
  supported_value_types:
    - int:      "整数，如 100"
    - float:    "浮点数，如 3.14"
    - string:   "字符串，如 'hello'"
    - bool:     "布尔值，true/false"
    - Vector2:  "二维向量，如 (1,2)"
    - Vector3:  "三维向量，如 (1,2,3)"
    - Color:    "颜色，如 #FF0000"
    - "string[]": "字符串数组，逗号分隔"
  
  # 文件命名规范
  naming:
    pattern: "^[A-Z][a-zA-Z0-9]*Config$"
    examples:
      - "GameConfig"
      - "ServerConfig"
      - "BalanceConfig"
    
  # 输出要求
  output:
    excel_structure:
      description: "简单两列结构"
      columns:
        - "Key: 配置键"
        - "Value: 配置值"
      rows: "键值对数据"
    
    generated_files:
      - "{ConfigName}.txt"      # Tab分隔文本
      - "{ConfigName}.bytes"    # 二进制数据
      # 注意: 不生成 .cs 代码！
  
  # 验证规则
  validation:
    - "Key 列必须存在且唯一"
    - "Key 必须符合命名规范"
    - "不允许重复的 Key"
    - "Value 可以为空（使用默认值）"
    
  # 与 DataTable 的区别
  differences_from_datatable:
    - "无 Id 列要求"
    - "无 .cs 代码生成"
    - "运行时弱类型访问 (GetString/GetInt)"
    - "适合简单键值对配置"
    - "不支持子目录"
    - "不支持复杂表结构"
```

### 2.3 Language Schema

```yaml
# Language 标准 Schema 定义
LanguageSchema:
  type: "Language"
  description: "多语言表，键值对形式，特殊 JSON 输出格式"
  
  # 结构特点
  structure:
    type: "key-value pairs"
    description: "两列结构：Key 和对应语言的文本"
    
  # 必须包含的列
  required_columns:
    - name: "Key"
      type: "string"
      description: "多语言键，在代码中使用"
      constraints:
        unique: true
        pattern: "^[A-Z][A-Z0-9_]*$"
        examples:
          - "HELLO_WORLD"
          - "GAME_START"
          - "ERROR_NETWORK"
    
    - name: "Text"  # 列名可自定义，通常是语言名
      type: "string"
      description: "该语言对应的显示文本"
  
  # 文件命名规范
  naming:
    pattern: "^{LanguageName}$"
    examples:
      - "ChineseSimplified"
      - "ChineseTraditional"
      - "English"
      - "Japanese"
      - "Korean"
    language_codes:
      ChineseSimplified: "zh-CN"
      ChineseTraditional: "zh-TW"
      English: "en"
      Japanese: "ja"
      Korean: "ko"
  
  # 输出要求 - 特殊 JSON 格式
  output:
    description: "与其他类型完全不同，输出为 JSON"
    
    generated_files:
      - "{LanguageName}.json"  # 注意: 不是 .txt/.bytes！
    
    json_structure:
      type: "object"
      format: "key-value pairs"
      example: |
        {
          "HELLO_WORLD": "你好，世界！",
          "GAME_START": "游戏开始",
          "ERROR_NETWORK": "网络错误"
        }
    
    special_notes:
      - "输出为 JSON 格式，不是 .txt/.bytes"
      - "Key 保持原样，不进行转换"
      - "Value 为纯文本字符串"
      - "不支持复杂嵌套结构"
  
  # 运行时加载流程
  runtime_loading:
    description: "与其他类型完全不同的加载流程"
    steps:
      - "1. PreloadProcedure 从 LanguagesTable 获取当前语言"
      - "2. 根据语言获取对应的 AssetName"
      - "3. 调用 GF.Localization.LoadLanguage(assetName, ...)"
      - "4. LocalizationComponent 加载 .json 文件"
      - "5. 业务代码使用 GF.Localization.GetString(key)"
    
    dependencies:
      - "LanguagesTable (DataTable) - 必须预先加载"
      - "Language .json 文件 - 必须在 Resources 或 AssetBundle 中"
  
  # 验证规则
  validation:
    - "Key 列必须存在且唯一"
    - "Key 必须符合命名规范 (大写下划线)"
    - "不允许重复的 Key"
    - "空 Key 不允许"
    - "空 Text 允许（显示为空字符串）"
    - "特殊字符需正确转义（JSON 输出时）"
    
  # 与其他类型的对比
  differences:
    datatable:
      - "无 Id 列要求"
      - "输出为 JSON 而非 .txt/.bytes"
      - "无 .cs 代码生成"
      - "需要 LanguagesTable 协助加载"
      - "特殊的多语言运行时流程"
    
    config:
      - "Key 命名规范不同 (大写下划线 vs 驼峰)"
      - "输出为 JSON 而非 .txt/.bytes"
      - "需要 LanguagesTable 协助加载"
      - "特殊的多语言运行时流程"
```

---

## 三、AI 数据编辑 Skill 设计方案

基于上述 Schema 标准，设计 **Skill: `excel-data-editor`**

### 3.1 核心功能

```yaml
Skill: excel-data-editor
Version: 1.0.0
Description: 基于 Schema 标准的 Excel 数据编辑工具

Capabilities:
  1. Schema-Aware Editing:
     - 识别 Excel 类型 (DataTable/Config/Language)
     - 应用对应 Schema 标准
     - 生成符合 Schema 的输出
  
  2. Intelligent Script Generation:
     - 解析自然语言需求
     - 生成 Python 编辑脚本
     - 包含 Schema 验证和备份机制
  
  3. Safe Execution:
     - 自动备份原始文件
     - 变更预览和确认
     - 失败回滚机制

Schema Support:
  - DataTable: ✅ 完全支持
  - Config: ✅ 完全支持
  - Language: ✅ 完全支持
```

### 3.2 接口设计

```python
# Skill 核心接口

class ExcelDataEditorSkill:
    """Excel 数据编辑 Skill"""
    
    def identify_schema(self, excel_path: str) -> SchemaType:
        """
        识别 Excel 文件类型和 Schema
        
        通过分析文件路径和内容，自动识别：
        - DataTable: 路径包含 DataTables/, 有 Id 列
        - Config: 路径包含 Configs/, 两列结构 (Key/Value)
        - Language: 路径包含 Languages/, 命名匹配语言名
        
        Returns:
            SchemaType: DATATABLE | CONFIG | LANGUAGE
        """
        pass
    
    def generate_edit_script(
        self,
        excel_path: str,
        requirements: str,
        schema_type: SchemaType = None
    ) -> EditScript:
        """
        生成编辑脚本
        
        基于自然语言需求，生成符合 Schema 标准的 Python 脚本。
        脚本包含：
        - 数据读取（使用 pandas/openpyxl）
        - 业务逻辑处理
        - Schema 验证
        - 备份和回滚机制
        - 数据保存
        
        Args:
            excel_path: Excel 文件路径
            requirements: 自然语言描述的需求
            schema_type: Schema 类型（可选，自动识别）
        
        Returns:
            EditScript: 包含脚本内容、变更预览、验证信息
        """
        pass
    
    def execute_script(
        self,
        script: EditScript,
        dry_run: bool = True
    ) -> ExecutionResult:
        """
        执行编辑脚本
        
        支持预览模式（dry_run）和实际执行。
        自动处理：
        - 备份原始文件
        - 执行脚本
        - 验证结果（Schema 合规性）
        - 成功：提交变更
        - 失败：回滚到备份
        
        Args:
            script: 编辑脚本
            dry_run: 是否为预览模式
        
        Returns:
            ExecutionResult: 执行结果、变更详情、验证报告
        """
        pass


class SchemaValidator:
    """Schema 验证器"""
    
    def validate_datatable(self, df: pd.DataFrame) -> ValidationReport:
        """验证 DataTable Schema"""
        checks = [
            "检查 Id 列存在",
            "检查 Id 列类型为 int",
            "检查 Id 值唯一性",
            "检查字段名命名规范",
            "检查数据类型有效性",
        ]
        pass
    
    def validate_config(self, df: pd.DataFrame) -> ValidationReport:
        """验证 Config Schema"""
        checks = [
            "检查 Key 列存在",
            "检查 Value 列存在",
            "检查 Key 唯一性",
            "检查 Key 命名规范",
        ]
        pass
    
    def validate_language(self, df: pd.DataFrame) -> ValidationReport:
        """验证 Language Schema"""
        checks = [
            "检查 Key 列存在",
            "检查 Text 列存在",
            "检查 Key 唯一性",
            "检查 Key 命名规范（大写下划线）",
            "检查 JSON 特殊字符转义",
        ]
        pass
```

### 3.3 使用示例

```python
# 示例 1: DataTable 编辑
skill = ExcelDataEditorSkill()

# 识别 Schema
schema = skill.identify_schema("AAAGameData/DataTables/MonsterTable.xlsx")
# 返回: SchemaType.DATATABLE

# 生成编辑脚本
script = skill.generate_edit_script(
    excel_path="AAAGameData/DataTables/MonsterTable.xlsx",
    requirements="将所有等级大于 10 的怪物生命值增加 20%",
    schema_type=SchemaType.DATATABLE
)

# 脚本内容预览
print(script.preview)
# 输出:
# 变更预览:
# - MonsterTable.xlsx
#   修改行: 15, 23, 31, ...
#   字段: HP
#   变更: 1000→1200, 1500→1800, ...

# 执行（预览模式）
result = skill.execute_script(script, dry_run=True)
print(result.validation_report)
# 验证通过: Schema 合规 (DataTable)

# 实际执行
result = skill.execute_script(script, dry_run=False)
```

```python
# 示例 2: Config 编辑
script = skill.generate_edit_script(
    excel_path="AAAGameData/Configs/GameConfig.xlsx",
    requirements="将初始金币设置为 1000",
    schema_type=SchemaType.CONFIG
)

# Config 只有 Key/Value 两列
# 生成的脚本会检查 Key="InitialGold"，修改 Value="1000"
```

```python
# 示例 3: Language 编辑
script = skill.generate_edit_script(
    excel_path="AAAGameData/Languages/ChineseSimplified.xlsx",
    requirements="将所有'敌人'改为'怪物'",
    schema_type=SchemaType.LANGUAGE
)

# Language 需要检查 Key 命名规范（大写下划线）
# 需要处理 JSON 特殊字符转义
```

---

## 四、Schema 分类处理流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    Schema 分类处理流程                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. 输入分类 (Input Classification)                               │
│      ┌─────────────────────────────────────────────────────┐   │
│      │ 输入: 自然语言需求 + Excel 文件路径                   │   │
│      │                                                      │   │
│      │ 分类器分析:                                          │   │
│      │ 1. 文件路径分析                                      │   │
│      │    - DataTables/* → DataTable                       │   │
│      │    - Configs/* → Config                             │   │
│      │    - Languages/* → Language                         │   │
│      │                                                      │   │
│      │ 2. 文件内容验证                                      │   │
│      │    - 检查列结构是否符合 Schema                        │   │
│      │    - DataTable: 必须有 Id 列                          │   │
│      │    - Config: 必须有 Key/Value 列                      │   │
│      │    - Language: 必须有 Key/Text 列                       │   │
│      │                                                      │   │
│      │ 3. 需求语义分析                                      │   │
│      │    - 提取操作对象（表名、字段、行）                     │   │
│      │    - 识别操作类型（增删改查）                         │   │
│      │    - 提取条件（筛选逻辑）                             │   │
│      │                                                      │   │
│      │ 输出: SchemaType + 结构化需求描述                      │   │
│      └─────────────────────────────────────────────────────┘   │
│                                                                  │
│   2. Schema 路由 (Schema Routing)                                │
│      ┌─────────────────────────────────────────────────────┐   │
│      │ 根据 SchemaType 路由到对应的处理器                     │   │
│      │                                                      │   │
│      │ DataTable Handler:                                   │   │
│      │ - 使用 DataTableSchema 验证                          │   │
│      │ - 生成 DataTable 专用编辑脚本                          │   │
│      │ - 检查 Id 唯一性、字段类型等                           │   │
│      │ - 生成 .cs 代码预览（可选）                           │   │
│      │                                                      │   │
│      │ Config Handler:                                      │   │
│      │ - 使用 ConfigSchema 验证                               │   │
│      │ - 生成 Config 专用编辑脚本                             │   │
│      │ - 检查 Key 唯一性、命名规范                            │   │
│      │ - 简单键值对处理                                      │   │
│      │                                                      │   │
│      │ Language Handler:                                  │   │
│      │ - 使用 LanguageSchema 验证                             │   │
│      │ - 生成 Language 专用编辑脚本                           │   │
│      │ - 检查 Key 命名规范（大写下划线）                       │   │
│      │ - 检查 JSON 特殊字符转义                               │   │
│      │ - 特殊的多语言处理逻辑                                │   │
│      │                                                      │   │
│      └─────────────────────────────────────────────────────┘   │
│                                                                  │
│   3. 标准化输出 (Standardized Output)                            │
│      ┌─────────────────────────────────────────────────────┐   │
│      │ 输出必须符合对应 Schema 的标准                         │   │
│      │                                                      │   │
│      │ DataTable 输出要求:                                  │   │
│      │ - Excel 文件结构:                                     │   │
│      │   Row 1: 表名/注释                                    │   │
│      │   Row 2: 字段名 (必须有 Id)                             │   │
│      │   Row 3: 数据类型                                      │   │
│      │   Row 4: 默认值                                        │   │
│      │   Row 5: 字段注释                                      │   │
│      │   Row 6+: 数据内容                                     │   │
│      │ - 字段名: 大驼峰命名 (e.g., MonsterId, HpMax)           │   │
│      │ - 类型: 必须是支持的数据类型之一                        │   │
│      │ - Id: int, 唯一, >= 1                                   │   │
│      │                                                      │   │
│      │ Config 输出要求:                                       │   │
│      │ - Excel 文件结构:                                     │   │
│      │   只有两列: Key, Value                                │   │
│      │   Row 1: 列名                                          │   │
│      │   Row 2+: 键值对数据                                   │   │
│      │ - Key: 小驼峰命名 (e.g., initialGold, maxLevel)        │   │
│      │ - Value: 字符串，运行时解析                               │   │
│      │ - 必须唯一                                               │   │
│      │                                                      │   │
│      │ Language 输出要求:                                       │   │
│      │ - Excel 文件结构:                                       │   │
│      │   只有两列: Key, Text                                   │   │
│      │   Row 1: 列名                                            │   │
│      │   Row 2+: 键值对数据                                     │   │
│      │ - Key: 全大写下划线 (e.g., HELLO_WORLD, ERROR_NETWORK)  │   │
│      │ - Text: 显示文本，支持特殊字符                           │   │
│      │ - 必须唯一                                               │   │
│      │ - 注意: 输出为 JSON 而非 .txt/.bytes!                    │   │
│      └─────────────────────────────────────────────────────┘   │
│                                                                  │
│   4. 验证与执行 (Validation & Execution)                         │
│      ┌─────────────────────────────────────────────────────┐   │
│      │ 最终输出前必须通过 Schema 验证                       │   │
│      │                                                      │   │
│      │ 验证步骤:                                            │   │
│      │ 1. Schema 合规性检查                                 │   │
│      │    - 检查必须字段存在                                │   │
│      │    - 检查数据类型匹配                                │   │
│      │    - 检查命名规范                                    │   │
│      │    - 检查唯一性约束                                  │   │
│      │                                                      │   │
│      │ 2. 数据完整性检查                                    │   │
│      │    - 检查空值和缺失值                                │   │
│      │    - 检查数据范围                                    │   │
│      │    - 检查关联一致性                                  │   │
│      │                                                      │   │
│      │ 3. 业务规则检查                                      │   │
│      │    - 检查业务逻辑合规性                              │   │
│      │    - 检查数值计算正确性                              │   │
│      │                                                      │   │
│      │ 执行步骤:                                            │   │
│      │ 1. 备份原始文件                                      │   │
│      │ 2. 执行编辑脚本（预览或实际）                         │   │
│      │ 3. 验证输出 Schema 合规性                             │   │
│      │ 4. 生成变更报告                                      │   │
│      │ 5. 人工确认（如果是实际执行）                         │   │
│      │                                                      │   │
│      │ 失败处理:                                            │   │
│      │ - 验证失败: 拒绝执行，返回错误报告                    │   │
│      │ - 执行失败: 自动回滚到备份                            │   │
│      │ - 部分失败: 回滚并返回详细错误信息                      │   │
│      └─────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 五、实施建议

### 5.1 立即可实施（今天）

基于今天的设计，可以立即实施以下内容：

```yaml
Immediate Actions:
  1. 确认 Schema 标准:
     - 确认 DataTable/Config/Language 的 Schema 定义
     - 确认字段类型、命名规范、验证规则
     
  2. 编写 Schema 验证器:
     - 实现三类数据的 Schema 验证逻辑
     - 提供清晰的错误报告
     
  3. 改造 ExcelCSVAdapter:
     - 保留: Schema 验证器、Excel 操作工具
     - 废弃: CSV 相关功能
     - 改造: AI 接口为 Skill 基础
     
  4. 创建 Skill 框架:
     - 创建 skill.yaml 定义
     - 实现基础接口（identify_schema, generate_script）
     - 提供示例脚本模板
```

### 5.2 待你确认的问题

在继续实施前，需要你确认：

```yaml
Confirmation Required:
  1. Schema 标准确认:
     Q: 上述 DataTable/Config/Language 的 Schema 定义是否准确？
     Options:
       - A: 准确，直接实施
       - B: 需要微调（请指出）
       - C: 需要大幅修改（请说明）
  
  2. Skill 化方案确认:
     Q: 是否同意将方案 A 改造为 Skill？
     Options:
       - A: 同意，立即实施
       - B: 同意，但需要调整设计（请指出）
       - C: 不同意，改用其他方案（请说明）
  
  3. ExcelCSVAdapter 处理:
     Q: 如何处理现有的 ExcelCSVAdapter？
     Options:
       - A: 保留改造为 Skill 基础（推荐）
       - B: 废弃，重新开发
       - C: 保留作为独立工具，不 Skill 化
  
  4. 实施优先级:
     Q: 接下来优先实施哪个？
     Options:
       - A: Schema 验证器
       - B: Skill 基础框架
       - C: AI 接口改造
       - D: 示例脚本模板
```

请回答上述问题，我立即根据你的确认继续实施！
