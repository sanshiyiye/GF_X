# CLAUDE.md - GF_X AI 开发指南

> 本文档为 Claude Code 提供 GF_X 框架的核心规则和快速参考。
> 
> **完整文档**: `Doc/AI-Reference/`

---

## 🚨 关键规则（必须遵守！）

### ❌ 绝对禁止

| 禁止操作 | 错误示例 | 后果 |
|---------|---------|------|
| 使用 Resources.Load | `Resources.Load<GameObject>("path")` | 无法热更新 |
| 直接 Instantiate | `Instantiate(prefab)` | 绕过对象池 |
| 直接 Destroy | `Destroy(gameObject)` | 对象池失效 |
| 使用 GameObject.Find | `GameObject.Find("Name")` | 性能差、易出错 |
| 硬编码数据 | `int damage = 100;` | 无法热更新配置 |
| 忽略生命周期 | 不取消事件订阅 | 内存泄漏 |

### ✅ 必须使用

| 操作 | 正确做法 | 所在模块 |
|------|---------|---------|
| 加载资源 | `GF.Resource.LoadAsset<T>(assetName, callback)` | Resource |
| 显示实体 | `GF.Entity.ShowEntity(typeof(XXX), data)` | Entity |
| 隐藏实体 | `GF.Entity.HideEntity(entity)` | Entity |
| 打开 UI | `GF.UI.OpenUIForm(UIFormId.XXX, data)` | UI |
| 关闭 UI | `GF.UI.CloseUIForm(uiForm)` / `Close()` | UI |
| 获取数据 | `GF.DataTable.GetDataTable<DRXXX>()` | DataTable |
| 读取配置 | `GF.Config.GetString("Key", default)` | Config |
| 订阅事件 | `GF.Event.Subscribe(EventId, Handler)` | Event |
| 取消订阅 | `GF.Event.Unsubscribe(EventId, Handler)` | Event |

---

## 📂 文件组织

### 热更新代码（放在这里）

```
Assets/AAAGame/Scripts/
├── Procedure/              # 流程
│   ├── Game/
│   ├── Menu/
│   └── System/
├── UI/                     # UI 逻辑
│   ├── Menu/
│   ├── Game/
│   └── Common/
├── Entity/                 # 实体逻辑
│   ├── Player/
│   ├── Enemy/
│   └── Effect/
├── DataTable/              # 数据表行定义
├── Network/                # 网络协议
└── Extension/              # GF 扩展
    ├── GF.cs
    ├── GF.UI.cs
    ├── GF.Entity.cs
    └── ...
```

### 内置代码（不能热更新）

```
Assets/AAAGame/ScriptsBuiltin/
└── Runtime/
    └── Procedures/         # 启动流程
        ├── LaunchProcedure.cs
        ├── CheckResourcesProcedure.cs
        └── LoadHotfixDllProcedure.cs
```

### 预制体资源

```
Assets/AAAGame/Prefabs/
├── UI/                     # UI 预制体
│   ├── MainMenu.prefab
│   └── Setting.prefab
├── Entity/                 # 实体预制体
│   ├── Player.prefab
│   └── Enemy.prefab
└── Effect/                 # 特效预制体
    └── Explosion.prefab
```

---

## 🏷️ 命名规范

### 类名

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| 普通类 | 大驼峰 | `GameManager`, `PlayerController` |
| 流程类 | 大驼峰 + Procedure | `MenuProcedure`, `GameProcedure` |
| UI 类 | 大驼峰 + UIFormBase | `MainMenuUIFormBase` |
| 实体类 | 大驼峰 + EntityLogic | `PlayerEntityLogic` |
| 数据表行 | DR + 大驼峰 | `DRItem`, `DRLevel` |
| 接口 | I + 大驼峰 | `IManager`, `IPlayer` |
| 枚举 | E + 大驼峰 | `EGameState`, `EItemType` |

### 成员变量

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| 公有属性 | 大驼峰 | `public int PlayerLevel { get; set; }` |
| 常量 | 全大写下划线 | `public const int MAX_COUNT = 100;` |
| 静态只读 | 全大写下划线 | `public static readonly int MAX_SIZE = 1024;` |
| 私有字段 | 小驼峰_前缀 | `private int _playerLevel;` |
| 序列化字段 | 小驼峰_前缀 | `[SerializeField] private Button _confirmButton;` |

### ID 定义

```csharp
// UIFormId.cs
public static class UIFormId
{
    public const int MainMenu = 1001;
    public const int Setting = 1002;
    public const int GameHud = 1003;
}

// EntityId.cs
public static class EntityId
{
    public const int Player = 10001;
    public const int EnemySlime = 10011;
    public const int EnemyBoss = 10012;
}

// SoundId.cs
public static class SoundId
{
    public const int BgmMenu = 1;
    public const int BgmGame = 2;
    public const int SfxClick = 1001;
}
```

---

## 🔍 快速查找表

### GF 模块访问

```csharp
GF.UI           // UI 管理
GF.Entity       // 实体管理
GF.Procedure    // 流程管理（只读）
GF.DataTable    // 数据表管理
GF.Config       // 配置管理
GF.Resource     // 资源管理
GF.Sound        // 音频管理
GF.Network      // 网络管理
GF.Scene        // 场景管理
GF.Setting      // 本地存储
GF.WebRequest   // HTTP 请求
GF.Event        // 事件系统
GF.ObjectPool   // 对象池
GF.Fsm          // 状态机（高级）
```

### 常用生命周期顺序

```
Procedure:
  OnInit() → OnEnter() → [OnUpdate() × N] → OnLeave() → [OnDestroy()]

UIFormBase:
  OnInit() → OnOpen() → [OnUpdate() × N] → OnClose()

EntityLogic:
  OnInit() → OnShow() → [OnUpdate() × N] → OnHide()
```

### 完整文档索引

| 文档 | 内容 | 何时阅读 |
|------|------|----------|
| `Doc/AI-Reference/README.md` | 文档总览 | 首次使用 |
| `Doc/AI-Reference/AI-Framework-Overview.md` | 框架总览 | 首次使用 |
| `Doc/AI-Reference/Modules/01-Procedure.md` | 流程系统 | 创建流程时 |
| `Doc/AI-Reference/Modules/02-UI.md` | UI 系统 | 创建 UI 时 |
| `Doc/AI-Reference/Modules/03-Entity.md` | 实体系统 | 创建实体时 |
| `Doc/AI-Reference/Modules/04-DataTable.md` | 数据表 | 使用数据时 |
| `Doc/AI-Reference/Modules/05-Config.md` | 配置系统 | 读取配置时 |
| `Doc/AI-Reference/Modules/06-Resource.md` | 资源系统 | 加载资源时 |
| `Doc/AI-Reference/Templates/*.md` | 代码模板 | 创建新文件时 |
| `Doc/AI-Reference/AI-Coding-Patterns.md` | 编码模式 | 参考最佳实践 |
| `Doc/AI-Reference/AI-Common-Mistakes.md` | 常见错误 | 避免错误 |

---

**记住**：当你不确定时，查看 `Doc/AI-Reference/` 中的详细文档！
