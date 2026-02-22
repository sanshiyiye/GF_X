# GF_X 模块参考：Procedure（流程系统）

> 本文档帮助 AI 理解并正确使用 GF_X 的 Procedure 状态机系统。

---

## 1. 核心概念

### 1.1 什么是 Procedure？

Procedure 是 **有限状态机 (FSM)** 的实现，用于管理游戏的不同阶段或状态。

```
游戏流程示例:

LaunchProcedure ──→ CheckResourcesProcedure ──→ LoadHotfixDllProcedure
                                                          ↓
PreloadProcedure ←── ChangeSceneProcedure ←── GameOverProcedure ←── GameProcedure ←── MenuProcedure
```

### 1.2 两种类型的 Procedure

| 类型 | 位置 | 是否可以热更新 | 用途 |
|------|------|----------------|------|
| **Builtin** | `ScriptsBuiltin/Runtime/Procedures/` | ❌ 不能热更新 | 启动、资源检查、DLL加载 |
| **Hotfix** | `Scripts/Procedure/` | ✅ 可以热更新 | 游戏逻辑（Preload、Menu、Game等）|

---

## 2. 基础使用

### 2.1 创建新的 Procedure

#### 热更新 Procedure（推荐，大部分情况用这个）

```csharp
// 文件路径: Assets/AAAGame/Scripts/Procedure/Game/MyGameProcedure.cs

using GameFramework.Fsm;
using GameFramework.Procedure;

/// <summary>
/// 我的游戏流程
/// </summary>
public class MyGameProcedure : ProcedureBase
{
    protected override void OnEnter(IFsm<IProcedureManager> procedureOwner)
    {
        base.OnEnter(procedureOwner);
        Log.Info("进入 MyGameProcedure");
        
        // 在这里初始化游戏
    }
    
    protected override void OnUpdate(IFsm<IProcedureManager> procedureOwner, float elapseSeconds, float realElapseSeconds)
    {
        base.OnUpdate(procedureOwner, elapseSeconds, realElapseSeconds);
        
        // 游戏主循环逻辑
        
        // 示例：当游戏结束时切换到结束流程
        if (IsGameOver())
        {
            ChangeState<GameOverProcedure>(procedureOwner);
        }
    }
    
    protected override void OnLeave(IFsm<IProcedureManager> procedureOwner, bool isShutdown)
    {
        base.OnLeave(procedureOwner, isShutdown);
        Log.Info("离开 MyGameProcedure");
        
        // 清理资源
    }
}
```

#### 内置 Procedure（仅在需要时创建）

```csharp
// 文件路径: Assets/AAAGame/ScriptsBuiltin/Runtime/Procedures/MyBuiltinProcedure.cs

using GameFramework.Fsm;
using GameFramework.Procedure;

/// <summary>
/// 内置流程示例（不可热更新）
/// </summary>
public class MyBuiltinProcedure : ProcedureBase
{
    protected override void OnEnter(IFsm<IProcedureManager> procedureOwner)
    {
        base.OnEnter(procedureOwner);
        
        // 内置流程逻辑
    }
}
```

### 2.2 在 Procedure 中切换状态

```csharp
// 切换到另一个流程
ChangeState<TargetProcedure>(procedureOwner);

// 示例：从 MenuProcedure 切换到 GameProcedure
ChangeState<GameProcedure>(procedureOwner);

// 示例：从 GameProcedure 切换到 GameOverProcedure
ChangeState<GameOverProcedure>(procedureOwner);
```

### 2.3 在 Procedure 中访问其他模块

```csharp
protected override void OnEnter(IFsm<IProcedureManager> procedureOwner)
{
    base.OnEnter(procedureOwner);
    
    // UI 系统
    GF.UI.OpenUIForm(UIFormId.MainMenu);
    
    // 实体系统
    GF.Entity.ShowEntity(typeof(PlayerEntity), playerData);
    
    // 数据表
    var itemTable = GF.DataTable.GetDataTable<DRItem>();
    
    // 配置
    string gameName = GF.Config.GetString("Game.Name");
    
    // 资源加载
    GF.Resource.LoadAsset<GameObject>(assetName, OnLoadSuccess);
    
    // 音效
    GF.Sound.PlaySound(SoundId.BgmMenu);
}
```

---

## 3. 标准流程参考

### 3.1 标准启动流程

```
LaunchProcedure
    ↓ 检测资源模式、初始化设置
CheckResourcesProcedure (或 UpdateResourcesProcedure)
    ↓ 检查/更新资源
LoadHotfixDllProcedure
    ↓ 加载热更新 DLL
HotfixEntry.StartHotfixLogic
    ↓ 进入热更新代码
PreloadProcedure
    ↓ 预加载数据表、配置、多语言
ChangeSceneProcedure → MenuProcedure
```

### 3.2 标准游戏循环流程

```
MenuProcedure (主菜单)
    ↓ 点击开始游戏
ChangeSceneProcedure
    ↓ 切换场景
GameProcedure (游戏玩法)
    ↓ 游戏结束(胜利/失败)
GameOverProcedure (结算)
    ↓ 点击下一关/重玩/返回
ChangeSceneProcedure → GameProcedure 或 MenuProcedure
```

---

## 4. 最佳实践

### 4.1 Do's and Don'ts

#### ✅ 应该做的

```csharp
// 1. 在 OnEnter 中初始化，在 OnLeave 中清理
protected override void OnEnter(IFsm<IProcedureManager> procedureOwner)
{
    base.OnEnter(procedureOwner);
    GF.Event.Subscribe(OpenUIFormSuccessEventArgs.EventId, OnOpenUISuccess);
}

protected override void OnLeave(IFsm<IProcedureManager> procedureOwner, bool isShutdown)
{
    base.OnLeave(procedureOwner, isShutdown);
    GF.Event.Unsubscribe(OpenUIFormSuccessEventArgs.EventId, OnOpenUISuccess);
}

// 2. 使用 ChangeState 切换流程
if (IsGameCompleted())
{
    ChangeState<GameOverProcedure>(procedureOwner);
}

// 3. 在 OnUpdate 中处理游戏主循环
protected override void OnUpdate(IFsm<IProcedureManager> procedureOwner, float elapseSeconds, float realElapseSeconds)
{
    base.OnUpdate(procedureOwner, elapseSeconds, realElapseSeconds);
    
    // 更新游戏世界
    GameWorld.Instance.Update(elapseSeconds);
}
```

#### ❌ 不应该做的

```csharp
// 1. 不要在 OnEnter 中执行长时间阻塞操作
protected override void OnEnter(IFsm<IProcedureManager> procedureOwner)
{
    // ❌ 错误：会阻塞主线程
    var data = LoadHugeDataSync();
    
    // ✅ 正确：使用异步加载
    GF.Resource.LoadAsset(assetName, OnLoadComplete);
}

// 2. 不要手动管理流程状态
protected override void OnUpdate(IFsm<IProcedureManager> procedureOwner, float elapseSeconds, float realElapseSeconds)
{
    // ❌ 错误：不要手动切换
    if (shouldChange)
    {
        var nextProcedure = new NextProcedure(); // ❌
        nextProcedure.OnEnter(procedureOwner); // ❌
    }
    
    // ✅ 正确：使用框架提供的 ChangeState
    if (shouldChange)
    {
        ChangeState<NextProcedure>(procedureOwner);
    }
}

// 3. 不要忽略生命周期管理
protected override void OnLeave(IFsm<IProcedureManager> procedureOwner, bool isShutdown)
{
    // ❌ 错误：不清理会导致内存泄漏
    // 没有取消事件订阅
    // 没有释放资源
    
    // ✅ 正确：清理所有资源
    GF.Event.Unsubscribe(...);
    GF.UI.CloseAllLoadedUIForms();
}
```

---

## 5. 调试与故障排除

### 5.1 常见问题

#### Q: 流程不切换？

```csharp
// 检查是否正确调用了 ChangeState
ChangeState<TargetProcedure>(procedureOwner);

// 确保 TargetProcedure 已注册
// 检查日志是否有错误
```

#### Q: OnEnter 没有执行？

```csharp
// 检查流程是否通过 ChangeState 正确切换
// 检查是否有异常抛出
// 检查是否进入了错误的流程分支
```

#### Q: 内存泄漏？

```csharp
// 确保在 OnLeave 中：
// 1. 取消所有事件订阅
// 2. 关闭所有打开的UI
// 3. 停止所有协程和定时器
// 4. 释放引用池对象
```

---

## 6. 参考链接

- [GameFramework 官方文档](https://gameframework.cn/)
- [HybridCLR 文档](https://focus-creative-games.github.io/hybridclr/)
- [GF_X DeepWiki](https://deepwiki.com/sunsvip/GF_X)

---

> 💡 **AI 提示**: 当生成 Procedure 代码时，请确保：
> 1. 继承 `ProcedureBase`
> 2. 正确实现 `OnEnter`、`OnUpdate`、`OnLeave`
> 3. 使用 `ChangeState<>()` 切换流程
> 4. 在 `OnLeave` 中清理资源
