# 模板：Entity（实体）

> 创建新实体时的标准模板

---

## EntityLogic 模板

```csharp
// 文件路径: Assets/AAAGame/Scripts/Entity/{Category}/{EntityName}EntityLogic.cs

using UnityGameFramework.Runtime;
using UnityEngine;

/// <summary>
/// {EntityName} 实体逻辑
/// </summary>
public class {EntityName}EntityLogic : EntityLogic
{
    #region Serialize Fields
    
    [Header("Basic")]
    [SerializeField]
    private float _moveSpeed = 5f;
    
    [SerializeField]
    private float _rotationSpeed = 10f;
    
    // 在此添加更多序列化字段
    
    #endregion
    
    #region Private Fields
    
    private {EntityName}EntityData _data;
    
    #endregion
    
    #region Lifecycle
    
    /// <summary>
    /// 初始化（仅调用一次）
    /// </summary>
    protected override void OnInit(object userData)
    {
        base.OnInit(userData);
        
        // 初始化代码
    }
    
    /// <summary>
    /// 显示时调用
    /// </summary>
    protected override void OnShow(object userData)
    {
        base.OnShow(userData);
        
        _data = userData as {EntityName}EntityData;
        if (_data == null)
        {
            Log.Error($"{EntityName}EntityLogic 无效的数据");
            return;
        }
        
        // 应用数据
        CachedTransform.position = _data.Position;
        
        // 初始化状态
        InitializeState();
    }
    
    /// <summary>
    /// 隐藏时调用
    /// </summary>
    protected override void OnHide(bool isShutdown, object userData)
    {
        base.OnHide(isShutdown, userData);
        
        // 清理
        _data = null;
    }
    
    /// <summary>
    /// 每帧更新
    /// </summary>
    protected override void OnUpdate(float elapseSeconds, float realElapseSeconds)
    {
        base.OnUpdate(elapseSeconds, realElapseSeconds);
        
        // 更新逻辑
    }
    
    #endregion
    
    #region Private Methods
    
    private void InitializeState()
    {
        // 初始化状态
    }
    
    #endregion
}

/// <summary>
/// {EntityName} 实体数据
/// </summary>
public class {EntityName}EntityData : EntityData
{
    public Vector3 Position { get; set; }
    
    // 在此添加更多字段
    
    public static {EntityName}EntityData Create(int entityId, Vector3 position)
    {
        {EntityName}EntityData data = ReferencePool.Acquire<{EntityName}EntityData>();
        data.Id = entityId;
        data.Position = position;
        return data;
    }
}
```

---

## 使用步骤

### 1. 定义 EntityId

```csharp
// 在 EntityId.cs 中添加
public static class EntityId
{
    public const int {EntityName} = {ID};
}
```

### 2. 创建文件

```bash
touch Assets/AAAGame/Scripts/Entity/{Category}/{EntityName}EntityLogic.cs
```

### 3. 替换占位符

| 占位符 | 替换为 |
|--------|--------|
| `{EntityName}` | 实体名称 |
| `{Category}` | 分类目录 |

### 4. 显示实体

```csharp
var data = {EntityName}EntityData.Create(EntityId.{EntityName}, position);
GF.Entity.ShowEntity(typeof({EntityName}EntityLogic), data);
```

---

> 💡 **提示**: 实体系统使用对象池管理，不要直接 Destroy！
