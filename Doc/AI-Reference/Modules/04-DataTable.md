# GF_X 模块参考：DataTable（数据表系统）

> 本文档帮助 AI 理解并正确使用 GF_X 的数据表系统。

---

## 1. 核心概念

### 1.1 什么是数据表？

数据表是**游戏配置数据**的管理方式，使用 Excel 编辑，运行时加载：

```
Excel (设计时) → 自动导表 → 运行时读取
```

### 1.2 数据表 vs 配置表

| 特性 | 数据表 (DataTable) | 配置表 (Config) |
|------|-------------------|----------------|
| **数据结构** | 多行数据（类似数据库表） | 键值对（类似字典） |
| **典型用途** | 物品列表、关卡数据、怪物属性 | 游戏设置、开关、常量 |
| **Excel 格式** | 多行数据 | 两列（Key/Value） |
| **代码访问** | `GetDataRow(id)` / `GetAllDataRows()` | `GetString(key)` / `GetInt(key)` |

---

## 2. 数据表工作流程

### 2.1 完整流程

```
┌─────────────────────────────────────────────────────────────┐
│  1. Excel 设计阶段                                             │
│  AAAGameData/DataTables/Item.xlsx                            │
│  ├── 第一行：字段名 (Id, Name, Type, Attack, Price)           │
│  ├── 第二行：数据类型 (int, string, int, int, int)           │
│  └── 数据行：具体数据                                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. 自动导表                                                  │
│  点击 Unity 菜单：GameFramework → DataTable → Generate       │
│  或执行：GameDataGenerator.RefreshAllDataTable()              │
│                                                              │
│  输出：                                                      │
│  - Assets/AAAGame/DataTable/Item.txt (.bytes)              │
│  - Assets/AAAGame/Scripts/DataTable/DRItem.cs               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. 运行时加载                                                │
│  PreloadProcedure 中调用：                                    │
│  GF.DataTable.GetDataTable<DRItem>();                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 代码中使用                                                │
│  var itemTable = GF.DataTable.GetDataTable<DRItem>();        │
│  var item = itemTable.GetDataRow(1001);                      │
│  int attack = item.Attack;                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 代码中使用

### 3.1 基础使用

```csharp
// ====== 获取数据表 ======
IDataTable<DRItem> itemTable = GF.DataTable.GetDataTable<DRItem>();

// ====== 获取单行数据 ======
DRItem item = itemTable.GetDataRow(1001);  // 根据 ID 获取
if (item != null)
{
    string name = item.Name;
    int attack = item.Attack;
    int price = item.Price;
}

// ====== 获取所有数据 ======
DRItem[] allItems = itemTable.GetAllDataRows();
foreach (DRItem item in allItems)
{
    // 处理每个物品
}

// ====== 条件查询 ======
// 获取所有武器
DRItem[] weapons = itemTable.GetAllDataRows(item => item.Type == 1);

// 获取价格小于 100 的物品
DRItem[] cheapItems = itemTable.GetAllDataRows(item => item.Price < 100);

// 获取排序后的数据
DRItem[] sortedItems = itemTable.GetAllDataRows()
    .OrderBy(item => item.Price)
    .ToArray();
```

### 3.2 数据表行类示例

```csharp
// 文件：Assets/AAAGame/Scripts/DataTable/DRItem.cs
// 注意：此文件通常由导表工具自动生成

using GameFramework.DataTable;

/// <summary>
/// 物品数据表行
/// </summary>
public class DRItem : IDataRow
{
    // ========== 数据字段 ==========
    
    /// <summary>
    /// 物品 ID
    /// </summary>
    public int Id { get; private set; }
    
    /// <summary>
    /// 物品名称
    /// </summary>
    public string Name { get; private set; }
    
    /// <summary>
    /// 物品类型 (1=武器, 2=防具, 3=消耗品)
    /// </summary>
    public int Type { get; private set; }
    
    /// <summary>
    /// 攻击力
    /// </summary>
    public int Attack { get; private set; }
    
    /// <summary>
    /// 防御力
    /// </summary>
    public int Defense { get; private set; }
    
    /// <summary>
    /// 价格
    /// </summary>
    public int Price { get; private set; }
    
    /// <summary>
    /// 图标资源路径
    /// </summary>
    public string IconPath { get; private set; }
    
    /// <summary>
    /// 描述
    /// </summary>
    public string Description { get; private set; }
    
    // ========== IDataRow 接口实现 ==========
    
    /// <summary>
    /// 数据表行 ID
    /// </summary>
    public int Id2 => Id;
    
    /// <summary>
    /// 解析数据
    /// </summary>
    public bool ParseDataRow(string dataRow)
    {
        // 此部分通常由导表工具自动生成
        // 根据 Excel 列顺序解析数据
        string[] columns = dataRow.Split('\t');
        
        int index = 0;
        Id = int.Parse(columns[index++]);
        Name = columns[index++];
        Type = int.Parse(columns[index++]);
        Attack = int.Parse(columns[index++]);
        Defense = int.Parse(columns[index++]);
        Price = int.Parse(columns[index++]);
        IconPath = columns[index++];
        Description = columns[index++];
        
        return true;
    }
}
```

---

## 4. 常见错误与纠正

### 4.1 错误：硬编码数据

```csharp
// ❌ 错误：在代码中硬编码配置
void CreateItem()
{
    item.Name = "铁剑";
    item.Attack = 10;
    item.Price = 100;
}

// ✅ 正确：使用数据表
void CreateItem(int itemId)
{
    var itemTable = GF.DataTable.GetDataTable<DRItem>();
    var itemData = itemTable.GetDataRow(itemId);
    
    item.Name = itemData.Name;
    item.Attack = itemData.Attack;
    item.Price = itemData.Price;
}
```

### 4.2 错误：频繁查询数据表

```csharp
// ❌ 错误：每帧查询数据表
void Update()
{
    var table = GF.DataTable.GetDataTable<DRItem>();  // 不要每帧调用！
    var item = table.GetDataRow(currentItemId);
    UpdateUI(item);
}

// ✅ 正确：缓存数据表引用
private IDataTable<DRItem> _itemTable;

void Start()
{
    _itemTable = GF.DataTable.GetDataTable<DRItem>();  // 只获取一次
}

void Update()
{
    var item = _itemTable.GetDataRow(currentItemId);
    UpdateUI(item);
}
```

---

## 5. 快速参考

### 5.1 常用方法

```csharp
// 获取数据表 (通常在 OnEnter 或 Start 中缓存)
var table = GF.DataTable.GetDataTable<DRItem>();

// 获取单行
var row = table.GetDataRow(id);

// 获取所有数据
var all = table.GetAllDataRows();

// 条件查询
var filtered = table.GetAllDataRows(r => r.Type == 1);

// 遍历
foreach (var row in table.GetAllDataRows())
{
    // 处理
}
```

---

> 💡 **AI 提示**: 使用数据表时，记住三步骤：
> 1. **设计时**：在 Excel 中编辑数据
> 2. **构建时**：运行导表工具生成代码和资源
> 3. **运行时**：使用 `GF.DataTable.GetDataTable<>()` 读取数据
> 
> **绝对不要**在代码中硬编码配置数据！
