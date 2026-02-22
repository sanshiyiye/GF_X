# 模板：Procedure（流程）

> 创建新流程时的标准模板

---

## 热更新 Procedure 模板

```csharp
// 文件路径: Assets/AAAGame/Scripts/Procedure/{Category}/{ProcedureName}Procedure.cs

using GameFramework.Fsm;
using GameFramework.Procedure;
using UnityGameFramework.Runtime;

/// <summary>
/// {ProcedureName} 流程
/// </summary>
public class {ProcedureName}Procedure : ProcedureBase
{
    #region Fields
    
    // 在此添加流程私有字段
    
    #endregion
    
    #region Lifecycle
    
    /// <summary>
    /// 初始化（仅调用一次）
    /// </summary>
    protected override void OnInit(IFsm<IProcedureManager> procedureOwner)
    {
        base.OnInit(procedureOwner);
        
        // 初始化代码
    }
    
    /// <summary>
    /// 进入流程
    /// </summary>
    protected override void OnEnter(IFsm<IProcedureManager> procedureOwner)
    {
        base.OnEnter(procedureOwner);
        
        Log.Info("进入 {ProcedureName}Procedure");
        
        // 订阅事件
        // GF.Event.Subscribe(...);
        
        // 加载资源
        // GF.Resource.LoadAsset(...);
        
        // 显示UI
        // GF.UI.OpenUIForm(...);
    }
    
    /// <summary>
    /// 每帧更新
    /// </summary>
    protected override void OnUpdate(IFsm<IProcedureManager> procedureOwner, float elapseSeconds, float realElapseSeconds)
    {
        base.OnUpdate(procedureOwner, elapseSeconds, realElapseSeconds);
        
        // 游戏主循环逻辑
        
        // 示例：条件满足时切换流程
        // if (ShouldChangeState())
        // {
        //     ChangeState<NextProcedure>(procedureOwner);
        // }
    }
    
    /// <summary>
    /// 离开流程
    /// </summary>
    protected override void OnLeave(IFsm<IProcedureManager> procedureOwner, bool isShutdown)
    {
        base.OnLeave(procedureOwner, isShutdown);
        
        Log.Info("离开 {ProcedureName}Procedure");
        
        // 取消事件订阅
        // GF.Event.Unsubscribe(...);
        
        // 关闭UI
        // GF.UI.CloseAllLoadedUIForms();
        
        // 清理资源
    }
    
    /// <summary>
    /// 销毁（很少使用）
    /// </summary>
    protected override void OnDestroy(IFsm<IProcedureManager> procedureOwner)
    {
        base.OnDestroy(procedureOwner);
    }
    
    #endregion
    
    #region Private Methods
    
    // 在此添加私有方法
    
    #endregion
}
```

---

## 内置 Procedure 模板

```csharp
// 文件路径: Assets/AAAGame/ScriptsBuiltin/Runtime/Procedures/{ProcedureName}Procedure.cs

using GameFramework.Fsm;
using GameFramework.Procedure;
using UnityGameFramework.Runtime;

/// <summary>
/// {ProcedureName} 内置流程
/// </summary>
public class {ProcedureName}Procedure : ProcedureBase
{
    protected override void OnEnter(IFsm<IProcedureManager> procedureOwner)
    {
        base.OnEnter(procedureOwner);
        
        // 内置流程逻辑
    }
}
```

---

## 使用步骤

### 1. 创建文件

```bash
# 热更新流程
touch Assets/AAAGame/Scripts/Procedure/{Category}/{ProcedureName}Procedure.cs

# 内置流程
touch Assets/AAAGame/ScriptsBuiltin/Runtime/Procedures/{ProcedureName}Procedure.cs
```

### 2. 复制模板代码

将上面的模板代码复制到新建的文件中

### 3. 替换占位符

| 占位符 | 替换为 | 示例 |
|--------|--------|------|
| `{ProcedureName}` | 流程名 | `Game`, `Menu`, `Shop` |
| `{Category}` | 分类目录 | `Game`, `System` |
| `{Author}` | 作者名 | 你的名字 |

### 4. 实现业务逻辑

在 `OnEnter`、`OnUpdate`、`OnLeave` 中添加具体逻辑

### 5. 状态切换

使用 `ChangeState<NextProcedure>(procedureOwner)` 切换到其他流程

---

> 💡 **提示**: 记住热更新流程放在 `Scripts/Procedure/`，内置流程放在 `ScriptsBuiltin/Runtime/Procedures/`
