# GF_X 框架 - AI 可读概述

> 本文档专为 AI 模型设计，帮助 AI 理解并正确使用 GF_X 框架进行 Unity 游戏开发。

---

## 1. 框架核心概念

### 1.1 架构分层

```
┌─────────────────────────────────────────────────────────┐
│  [热更新层]  C# Hotfix Scripts (Scripts/)               │  ← 可热更新
│  - 业务逻辑、UI、游戏流程、网络协议                      │
├─────────────────────────────────────────────────────────┤
│  [内置层]  Builtin Scripts (ScriptsBuiltin/)           │  ← 随包发布
│  - 启动流程、资源更新、DLL加载、框架初始化               │
├─────────────────────────────────────────────────────────┤
│  [框架层]  GameFramework + GF_X Extensions              │
│  - 资源、UI、实体、网络、数据表、配置等核心模块          │
├─────────────────────────────────────────────────────────┤
│  [运行时]  HybridCLR + Unity IL2CPP                     │
└─────────────────────────────────────────────────────────┘
```

### 1.2 核心设计原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **流程驱动** | 游戏逻辑通过 Procedure 状态机管理 | Launch → Preload → Menu → Game |
| **数据驱动** | 配置、数据表通过 Excel 管理，运行时加载 | DataTable, Config, Localization |
| **模块化** | 功能通过 GF 模块解耦，通过 GF.Module 访问 | GF.UI, GF.Entity, GF.Procedure |
| **自动化** | 工具链自动化重复工作 | 导表、打包、多语言扫描 |

---

## 2. 核心模块速查

### 2.1 模块调用方式

```csharp
// 所有模块通过 GF 静态类访问
GF.UI        // UI 管理
GF.Entity    // 实体管理
GF.Procedure // 流程管理
GF.DataTable // 数据表管理
GF.Config    // 配置管理
GF.Resource  // 资源管理
GF.Sound     // 音频管理
GF.Network   // 网络管理
GF.Scene     // 场景管理
GF.Setting   // 本地存储
GF.WebRequest // HTTP 请求
GF.Event     // 事件系统
GF.ObjectPool // 对象池
```

### 2.2 关键接口说明

| 模块 | 核心方法 | 用途 |
|------|----------|------|
| **UI** | `GF.UI.OpenUIForm(uiFormId)` | 打开界面 |
| | `GF.UI.CloseUIForm(uiForm)` | 关闭界面 |
| **Entity** | `GF.Entity.ShowEntity(entityId)` | 显示实体 |
| | `GF.Entity.HideEntity(entityLogic)` | 隐藏实体 |
| **Procedure** | `ChangeState<NextProcedure>()` | 切换流程 |
| **DataTable** | `GF.DataTable.GetDataTable<DRXXX>()` | 获取数据表 |
| **Resource** | `GF.Resource.LoadAsset<T>(assetName)` | 加载资源 |

---

## 3. 代码组织规范

### 3.1 目录结构约定

```
Assets/AAAGame/
├── Scripts/                    # 【热更新】业务逻辑代码
│   ├── Extension/              # GF 框架扩展
│   │   ├── GF.cs               # 框架主入口静态类
│   │   ├── GF.UI.cs            # UI 扩展
│   │   ├── GF.Entity.cs        # 实体扩展
│   │   └── ...
│   ├── HotfixEntry.cs          # 热更新入口
│   ├── DataTable/              # 数据表结构代码
│   ├── Network/                # 网络协议
│   ├── Procedure/              # 游戏流程 (热更新部分)
│   ├── UI/                     # UI 逻辑
│   ├── Entity/                 # 实体逻辑
│   └── Game/                   # 游戏核心逻辑
├── ScriptsBuiltin/             # 【内置】非热更新代码
│   ├── Runtime/
│   │   └── Procedures/         # 启动流程
│   └── Editor/                 # 编辑器工具
├── Scene/                      # 场景文件
├── Prefabs/                    # 预制体
└── Resources/                  # 运行时配置
```

### 3.2 命名规范

```csharp
// 类名 - 大驼峰
public class GameManager : MonoBehaviour { }
public class MenuProcedure : ProcedureBase { }
public class MainUIForm : UIFormLogic { }

// 接口 - I 前缀
public interface IGameModule { }

// 枚举 - E 前缀
public enum EGameState { Loading, Playing, Pause }

// 数据表行 - DR 前缀 (Data Row)
public class DRItem : IDataRow { }

// 常量 - 全大写下划线
public const int MAX_PLAYER_COUNT = 100;

// 私有字段 - 小驼峰下划线前缀
private int _playerLevel;
private UIForm _mainForm;

// 公有属性 - 大驼峰
public int PlayerLevel { get; set; }

// GF 模块访问 - 全大写静态类
GF.UI.OpenUIForm(uiFormId);
```

### 3.3 代码分层原则

```csharp
// ✅ 好的分层：Procedure 协调多个模块
public class GameProcedure : ProcedureBase
{
    protected override void OnEnter(ProcedureBase lastProcedure)
    {
        base.OnEnter(lastProcedure);
        
        // 加载数据表
        var levelTable = GF.DataTable.GetDataTable<DRLevel>();
        var levelData = levelTable.GetDataRow(LevelId);
        
        // 显示实体
        GF.Entity.ShowEntity(typeof(PlayerEntity), playerId);
        
        // 打开UI
        GF.UI.OpenUIForm(UIFormId.GameHud);
        
        // 播放音效
        GF.Sound.PlaySound(SoundId.BgmGame);
    }
}

// ❌ 避免：模块间直接依赖
public class PlayerEntity : EntityLogic
{
    // 不要这样：直接访问其他实体的内部
    private void OnCollisionEnter(Collision other)
    {
        var enemy = other.gameObject.GetComponent<EnemyEntity>();
        enemy.TakeDamage(100); // ❌ 直接调用
    }
}
```

---

## 4. AI 编码模式

### 4.1 创建新流程 (Procedure)

```csharp
// 文件路径: Assets/AAAGame/Scripts/Procedure/Game/MyNewProcedure.cs

using GameFramework.Fsm;
using GameFramework.Procedure;
using UnityGameFramework.Runtime;

/// <summary>
/// 新流程示例
/// </summary>
public class MyNewProcedure : ProcedureBase
{
    // 流程内数据
    private int _currentStep = 0;
    
    /// <summary>
    /// 进入流程时调用
    /// </summary>
    protected override void OnEnter(IFsm<IProcedureManager> procedureOwner)
    {
        base.OnEnter(procedureOwner);
        
        Log.Info("进入 MyNewProcedure");
        
        // 在这里初始化
        _currentStep = 0;
        
        // 示例：加载资源
        GF.Resource.LoadAsset<GameObject>("Assets/AAAGame/Prefabs/MyPrefab.prefab", OnLoadSuccess, OnLoadFailure);
        
        // 示例：打开UI
        GF.UI.OpenUIForm(UIFormId.MyUIForm);
    }
    
    /// <summary>
    /// 每帧更新时调用
    /// </summary>
    protected override void OnUpdate(IFsm<IProcedureManager> procedureOwner, float elapseSeconds, float realElapseSeconds)
    {
        base.OnUpdate(procedureOwner, elapseSeconds, realElapseSeconds);
        
        // 在这里处理每帧逻辑
        // 例如：检查条件，满足后切换状态
        if (_currentStep >= 100)
        {
            ChangeState<MyNextProcedure>(procedureOwner);
        }
    }
    
    /// <summary>
    /// 离开流程时调用
    /// </summary>
    protected override void OnLeave(IFsm<IProcedureManager> procedureOwner, bool isShutdown)
    {
        base.OnLeave(procedureOwner, isShutdown);
        
        Log.Info("离开 MyNewProcedure");
        
        // 在这里清理资源
        GF.UI.CloseAllLoadedUIForms();
    }
    
    /// <summary>
    /// 资源加载成功回调
    /// </summary>
    private void OnLoadSuccess(string assetName, object asset, float duration, object userData)
    {
        Log.Info($"资源加载成功: {assetName}");
        // 实例化或使用资源
    }
    
    /// <summary>
    /// 资源加载失败回调
    /// </summary>
    private void OnLoadFailure(string assetName, LoadResourceStatus status, string errorMessage, object userData)
    {
        Log.Error($"资源加载失败: {assetName}, 错误: {errorMessage}");
    }
}
```

### 4.2 创建新UI界面

```csharp
// 文件路径: Assets/AAAGame/Scripts/UI/MyUIFormLogic.cs

using UnityGameFramework.Runtime;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// 我的UI界面逻辑
/// </summary>
public class MyUIFormLogic : UIFormLogic
{
    // UI 组件引用
    [SerializeField]
    private Button _confirmButton;
    
    [SerializeField]
    private Button _closeButton;
    
    [SerializeField]
    private Text _titleText;
    
    [SerializeField]
    private Text _contentText;
    
    // 数据
    private MyUIFormData _data;
    
    /// <summary>
    /// 界面初始化时调用（仅一次）
    /// </summary>
    protected override void OnInit(object userData)
    {
        base.OnInit(userData);
        
        // 绑定按钮事件
        if (_confirmButton != null)
        {
            _confirmButton.onClick.AddListener(OnConfirmClicked);
        }
        
        if (_closeButton != null)
        {
            _closeButton.onClick.AddListener(OnCloseClicked);
        }
    }
    
    /// <summary>
    /// 界面打开时调用
    /// </summary>
    protected override void OnOpen(object userData)
    {
        base.OnOpen(userData);
        
        // 接收数据
        _data = userData as MyUIFormData;
        if (_data == null)
        {
            Log.Warning($"UI {gameObject.name} 没有接收到有效数据");
            return;
        }
        
        // 更新UI显示
        UpdateUI();
    }
    
    /// <summary>
    /// 界面关闭时调用
    /// </summary>
    protected override void OnClose(bool isShutdown, object userData)
    {
        base.OnClose(isShutdown, userData);
        
        // 清理数据
        _data = null;
    }
    
    /// <summary>
    /// 界面轮询时调用
    /// </summary>
    protected override void OnUpdate(float elapseSeconds, float realElapseSeconds)
    {
        base.OnUpdate(elapseSeconds, realElapseSeconds);
        
        // 处理需要每帧更新的逻辑
    }
    
    /// <summary>
    /// 界面深度改变时调用
    /// </summary>
    protected override void OnDepthChanged(int uiGroupDepth, int depthInUIGroup)
    {
        base.OnDepthChanged(uiGroupDepth, depthInUIGroup);
    }
    
    /// <summary>
    /// 更新UI显示
    /// </summary>
    private void UpdateUI()
    {
        if (_titleText != null && _data.Title != null)
        {
            _titleText.text = _data.Title;
        }
        
        if (_contentText != null && _data.Content != null)
        {
            _contentText.text = _data.Content;
        }
    }
    
    /// <summary>
    /// 确认按钮点击
    /// </summary>
    private void OnConfirmClicked()
    {
        // 触发确认事件
        GF.Event.Fire(this, ReferencePool.Acquire<ConfirmUIEventArgs>().Fill(_data));
        
        // 关闭界面
        Close();
    }
    
    /// <summary>
    /// 关闭按钮点击
    /// </summary>
    private void OnCloseClicked()
    {
        Close();
    }
}

/// <summary>
/// UI 数据类
/// </summary>
public class MyUIFormData
{
    public string Title { get; set; }
    public string Content { get; set; }
    public int ConfirmId { get; set; }
}

/// <summary>
/// 确认事件参数
/// </summary>
public class ConfirmUIEventArgs : GameEventArgs
{
    public static readonly int EventId = typeof(ConfirmUIEventArgs).GetHashCode();
    
    public override int Id => EventId;
    
    public MyUIFormData Data { get; private set; }
    
    public ConfirmUIEventArgs Fill(MyUIFormData data)
    {
        Data = data;
        return this;
    }
    
    public override void Clear()
    {
        Data = null;
    }
}
```

### 4.3 创建新实体 (Entity)

```csharp
// 文件路径: Assets/AAAGame/Scripts/Entity/MyEntityLogic.cs

using UnityGameFramework.Runtime;
using UnityEngine;

/// <summary>
/// 我的实体逻辑
/// </summary>
public class MyEntityLogic : EntityLogic
{
    [SerializeField]
    private float _moveSpeed = 5f;
    
    private MyEntityData _data;
    private Vector3 _targetPosition;
    
    /// <summary>
    /// 实体初始化（仅一次）
    /// </summary>
    protected override void OnInit(object userData)
    {
        base.OnInit(userData);
        // 初始化组件引用
    }
    
    /// <summary>
    /// 实体显示时调用
    /// </summary>
    protected override void OnShow(object userData)
    {
        base.OnShow(userData);
        
        _data = userData as MyEntityData;
        if (_data == null)
        {
            Log.Error("实体数据无效");
            return;
        }
        
        // 应用数据
        CachedTransform.position = _data.Position;
        _targetPosition = _data.TargetPosition;
    }
    
    /// <summary>
    /// 实体隐藏时调用
    /// </summary>
    protected override void OnHide(bool isShutdown, object userData)
    {
        base.OnHide(isShutdown, userData);
        _data = null;
    }
    
    /// <summary>
    /// 每帧更新
    /// </summary>
    protected override void OnUpdate(float elapseSeconds, float realElapseSeconds)
    {
        base.OnUpdate(elapseSeconds, realElapseSeconds);
        
        // 移动逻辑
        if (_targetPosition != Vector3.zero)
        {
            CachedTransform.position = Vector3.MoveTowards(
                CachedTransform.position,
                _targetPosition,
                _moveSpeed * elapseSeconds
            );
        }
    }
}

/// <summary>
/// 实体数据
/// </summary>
public class MyEntityData : EntityData
{
    public Vector3 Position { get; set; }
    public Vector3 TargetPosition { get; set; }
    public int Level { get; set; }
    
    public static MyEntityData Create(int entityId, Vector3 pos, int level)
    {
        MyEntityData data = ReferencePool.Acquire<MyEntityData>();
        data.Position = pos;
        data.Level = level;
        return data;
    }
}
```

### 4.4 使用数据表 (DataTable)

```csharp
// 数据表访问示例

// 1. 获取数据表
IDataTable<DRItem> itemTable = GF.DataTable.GetDataTable<DRItem>();

// 2. 获取单行数据
DRItem itemData = itemTable.GetDataRow(1001);
if (itemData != null)
{
    string itemName = itemData.Name;
    int itemPrice = itemData.Price;
}

// 3. 遍历所有数据
foreach (DRItem item in itemTable.GetAllDataRows())
{
    // 处理每一行数据
}

// 4. 条件查询
DRItem[] result = itemTable.GetAllDataRows(item => item.Type == 1 && item.Price > 100);
```

### 4.5 使用配置 (Config)

```csharp
// 配置系统使用示例

// 获取字符串配置
string gameName = GF.Config.GetString("Game.Name", "DefaultName");

// 获取整型配置
int maxLevel = GF.Config.GetInt("Player.MaxLevel", 100);

// 获取浮点配置
float moveSpeed = GF.Config.GetFloat("Player.MoveSpeed", 5.0f);

// 获取布尔配置
bool enableVibration = GF.Config.GetBool("Setting.Vibration", true);
```

---

## 5. 常见 AI 编码错误与避免方法

### 5.1 错误清单

| # | 错误类型 | 错误示例 | 正确做法 |
|---|----------|----------|----------|
| 1 | **直接实例化** | `var obj = new GameObject("Enemy")` | 使用 `GF.Entity.ShowEntity()` |
| 2 | **直接加载资源** | `Resources.Load<GameObject>("Prefab")` | 使用 `GF.Resource.LoadAsset()` |
| 3 | **忽略数据表** | 在代码中硬编码配置 | 使用 `GF.DataTable.GetDataTable<>()` |
| 4 | **直接 Instantiate UI** | `Instantiate(uiPrefab)` | 使用 `GF.UI.OpenUIForm()` |
| 5 | **手动管理状态** | 用 bool 标记游戏状态 | 使用 `Procedure` 状态机 |
| 6 | **直接 Play 音效** | `AudioSource.Play()` | 使用 `GF.Sound.PlaySound()` |
| 7 | **手动缓存对象** | 用 List 缓存 GameObject | 使用 `GF.ObjectPool` |
| 8 | **忽略引用池** | 直接 `new` 数据对象 | 使用 `ReferencePool.Acquire<>()` |
| 9 | **直接改场景** | `SceneManager.LoadScene()` | 使用 `GF.Scene.LoadScene()` |
| 10 | **混用命名空间** | 忽略 `GameFramework` 命名空间 | 始终使用正确命名空间 |

### 5.2 正确 vs 错误对比

```csharp
// ❌ 错误：直接实例化 GameObject
void SpawnEnemy()
{
    var enemy = Instantiate(enemyPrefab);
    enemy.transform.position = spawnPoint.position;
    enemy.GetComponent<EnemyLogic>().Initialize(data);
}

// ✅ 正确：使用 GF 实体系统
void SpawnEnemy()
{
    var entityData = EnemyEntityData.Create(enemyId, spawnPoint.position, level);
    GF.Entity.ShowEntity(typeof(EnemyEntityLogic), entityData);
}
```

```csharp
// ❌ 错误：直接加载资源
void LoadConfig()
{
    var textAsset = Resources.Load<TextAsset>("Config/GameConfig");
    var json = textAsset.text;
    config = JsonUtility.FromJson<GameConfig>(json);
}

// ✅ 正确：使用 GF 资源系统 + 数据表
void LoadConfig()
{
    // 数据表已在 PreloadProcedure 加载
    var configTable = GF.DataTable.GetDataTable<DRGameConfig>();
    var row = configTable.GetDataRow(configId);
    // 或者使用 Config 系统
    var gameName = GF.Config.GetString("Game.Name");
}
```

---

## 6. 快速参考

### 6.1 常用命名空间

```csharp
using GameFramework;                    // 框架核心
using GameFramework.DataTable;            // 数据表
using GameFramework.Event;                // 事件
using GameFramework.Fsm;                    // 状态机
using GameFramework.Network;                // 网络
using GameFramework.ObjectPool;             // 对象池
using GameFramework.Procedure;              // 流程
using GameFramework.Resource;               // 资源
using GameFramework.Sound;                  // 音频
using GameFramework.UI;                     // UI
using UnityGameFramework.Runtime;           // Unity 运行时
```

### 6.2 常用生命周期顺序

```
Procedure:
  OnInit() -> OnEnter() -> [OnUpdate()...] -> OnLeave() -> [OnDestroy()]

UIFormLogic:
  OnInit() -> OnOpen() -> [OnUpdate()...] -> OnClose()

EntityLogic:
  OnInit() -> OnShow() -> [OnUpdate()...] -> OnHide()
```

### 6.3 文件模板快速链接

- [Procedure 模板](Templates/NewProcedure-Template.md)
- [UIForm 模板](Templates/NewUIForm-Template.md)
- [Entity 模板](Templates/NewEntity-Template.md)
- [完整功能实现模板](Templates/Feature-Implementation-Template.md)

---

## 7. 参考资料

### 7.1 框架文档

- [GF_X GitHub](https://github.com/sunsvip/GF_X)
- [GameFramework 官方文档](https://gameframework.cn/)
- [HybridCLR 文档](https://focus-creative-games.github.io/hybridclr/)
- [DeepWiki 详细文档](https://deepwiki.com/sunsvip/GF_X)

### 7.2 视频教程

- [Bilibili 教程合集](https://space.bilibili.com/xxxx/channel/series)
- [半小时极速入门](https://www.bilibili.com/video/BV1AT2rYVE3V)

### 7.3 社区交流

- QQ 交流群: 1035236947
- GitHub Issues: [GF_X Issues](https://github.com/sunsvip/GF_X/issues)

---

> 💡 **给 AI 的提示**: 当使用本框架生成代码时，请始终：
> 1. 优先使用 GF 模块而非直接 Unity API
> 2. 检查数据表和配置系统是否可用
> 3. 遵循命名规范和文件组织
> 4. 使用对象池和引用池减少 GC
> 5. 参考模板代码确保正确性
