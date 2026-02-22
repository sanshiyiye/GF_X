# GF_X 模块参考：Entity（实体系统）

> 本文档帮助 AI 理解并正确使用 GF_X 的实体管理系统。

---

## 1. 核心概念

### 1.1 什么是 Entity？

Entity（实体）是游戏中可见或不可见的**游戏对象**，包括：

- 🎭 **角色** - 玩家、NPC、敌人
- 🏠 **场景物体** - 建筑、道具、障碍物
- ✨ **特效** - 粒子效果、动画
- 🎯 **逻辑对象** - 触发器、区域

### 1.2 Entity vs Unity GameObject

| 对比 | Unity GameObject | GF Entity |
|------|------------------|-----------|
| **创建方式** | `Instantiate()` | `GF.Entity.ShowEntity()` |
| **销毁方式** | `Destroy()` | `GF.Entity.HideEntity()` |
| **内存管理** | 手动管理 | 自动对象池复用 |
| **性能** | 频繁创建/销毁 GC 压力大 | 对象池优化，零 GC |
| **生命周期** | 简单 | 完整的生命周期回调 |

### 1.3 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    EntityManager                         │
├─────────────────────────────────────────────────────────┤
│  EntityGroup (实体组)                                     │
│  ├── Player (玩家组)                                     │
│  ├── Enemy (敌人组)                                      │
│  ├── Item (道具组)                                       │
│  └── Effect (特效组)                                     │
├─────────────────────────────────────────────────────────┤
│  ObjectPool (实体对象池)                                  │
│  ├── EntityInstanceObject_1 ← 复用                       │
│  ├── EntityInstanceObject_2 ← 复用                       │
│  └── EntityInstanceObject_3 ← 新建                       │
├─────────────────────────────────────────────────────────┤
│  EntityLogic (实体逻辑脚本)                               │
│  ├── OnInit() → OnShow() → OnUpdate() → OnHide()        │
│  └── 业务逻辑：移动、攻击、状态管理等                      │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 基础使用

### 2.1 显示/隐藏实体

```csharp
// ====== 显示实体 ======

// 方式1：直接指定 EntityLogic 类型
GF.Entity.ShowEntity(typeof(PlayerEntityLogic), playerData);

// 方式2：指定实体 ID（推荐，使用常量定义）
GF.Entity.ShowEntity(EntityId.Player, playerData);

// 方式3：完整参数
GF.Entity.ShowEntity(
    entityLogicType: typeof(PlayerEntityLogic),
    entityData: playerData,
    entityGroupName: "Player"  // 实体组
);


// ====== 隐藏实体 ======

// 方式1：通过 EntityLogic 实例
GF.Entity.HideEntity(playerEntityLogic);

// 方式2：通过实体 ID
GF.Entity.HideEntity(entityId);

// 方式3：隐藏指定组的所有实体
GF.Entity.HideAllLoadedEntities("Enemy");

// 方式4：隐藏所有实体
GF.Entity.HideAllLoadedEntities();
```

### 2.2 创建新实体（完整流程）

#### 步骤 1: 定义实体 ID

```csharp
// 文件：Assets/AAAGame/Scripts/Definition/EntityId.cs

/// <summary>
/// 实体 ID 定义
/// </summary>
public static class EntityId
{
    // 玩家实体
    public const int Player = 10001;
    
    // 敌人实体 (10011-10100)
    public const int EnemySlime = 10011;
    public const int EnemyGoblin = 10012;
    public const int EnemyBoss = 10013;
    
    // 道具实体 (10101-10200)
    public const int ItemCoin = 10101;
    public const int ItemPotion = 10102;
    public const int ItemWeapon = 10103;
    
    // 特效实体 (10301-10400)
    public const int EffectExplosion = 10301;
    public const int EffectHeal = 10302;
}
```

#### 步骤 2: 创建 EntityLogic 脚本

```csharp
// 文件：Assets/AAAGame/Scripts/Entity/PlayerEntityLogic.cs

using UnityGameFramework.Runtime;
using UnityEngine;
using UnityEngine.AI;

/// <summary>
/// 玩家实体逻辑
/// </summary>
public class PlayerEntityLogic : EntityLogic
{
    // ========== 序列化字段 (在 Inspector 中绑定) ==========
    
    [Header("移动")]
    [SerializeField]
    private float _moveSpeed = 5f;
    
    [SerializeField]
    private float _rotationSpeed = 10f;
    
    [Header("组件引用")]
    [SerializeField]
    private NavMeshAgent _agent;
    
    [SerializeField]
    private Animator _animator;
    
    [SerializeField]
    private Collider _collider;
    
    // ========== 私有字段 ==========
    
    private PlayerEntityData _data;
    private Vector3 _targetPosition;
    private bool _isMoving;
    private int _animMoveId;
    
    // ========== 生命周期方法 ==========
    
    /// <summary>
    /// 实体初始化（仅调用一次）
    /// </summary>
    protected override void OnInit(object userData)
    {
        base.OnInit(userData);
        
        // 缓存 Animator 参数 ID
        _animMoveId = Animator.StringToHash("IsMoving");
        
        // 确保组件引用
        if (_agent == null)
            _agent = GetComponent<NavMeshAgent>();
        if (_animator == null)
            _animator = GetComponent<Animator>();
        
        // 设置导航代理
        if (_agent != null)
        {
            _agent.speed = _moveSpeed;
            _agent.angularSpeed = _rotationSpeed * 100;
            _agent.acceleration = _moveSpeed * 2;
        }
    }
    
    /// <summary>
    /// 实体显示时调用
    /// </summary>
    protected override void OnShow(object userData)
    {
        base.OnShow(userData);
        
        _data = userData as PlayerEntityData;
        if (_data == null)
        {
            Log.Error("PlayerEntityLogic 无效的数据");
            return;
        }
        
        // 应用数据
        CachedTransform.position = _data.SpawnPosition;
        CachedTransform.rotation = _data.SpawnRotation;
        
        // 启用组件
        if (_agent != null)
            _agent.enabled = true;
        if (_collider != null)
            _collider.enabled = true;
        
        // 订阅输入事件
        InputManager.Instance.OnMoveInput += OnMoveInput;
        InputManager.Instance.OnAttackInput += OnAttackInput;
    }
    
    /// <summary>
    /// 实体隐藏时调用
    /// </summary>
    protected override void OnHide(bool isShutdown, object userData)
    {
        base.OnHide(isShutdown, userData);
        
        // 取消输入事件订阅
        if (InputManager.Instance != null)
        {
            InputManager.Instance.OnMoveInput -= OnMoveInput;
            InputManager.Instance.OnAttackInput -= OnAttackInput;
        }
        
        // 停止移动
        if (_agent != null && _agent.enabled)
        {
            _agent.ResetPath();
            _agent.enabled = false;
        }
        
        // 禁用组件
        if (_collider != null)
            _collider.enabled = false;
        
        // 清理数据引用
        _data = null;
    }
    
    /// <summary>
    /// 每帧更新
    /// </summary>
    protected override void OnUpdate(float elapseSeconds, float realElapseSeconds)
    {
        base.OnUpdate(elapseSeconds, realElapseSeconds);
        
        // 更新移动状态
        UpdateMovement();
        
        // 更新动画
        UpdateAnimation();
    }
    
    // ========== 私有方法 ==========
    
    /// <summary>
    /// 移动输入处理
    /// </summary>
    private void OnMoveInput(Vector3 direction)
    {
        if (direction.sqrMagnitude > 0.01f)
        {
            _targetPosition = CachedTransform.position + direction * 10f;
            _isMoving = true;
            
            if (_agent != null && _agent.enabled)
            {
                _agent.SetDestination(_targetPosition);
            }
        }
        else
        {
            _isMoving = false;
            
            if (_agent != null && _agent.enabled)
            {
                _agent.ResetPath();
            }
        }
    }
    
    /// <summary>
    /// 攻击输入处理
    /// </summary>
    private void OnAttackInput()
    {
        // 触发攻击动画
        if (_animator != null)
        {
            _animator.SetTrigger("Attack");
        }
        
        // 播放音效
        GF.Sound.PlaySound(SoundId.PlayerAttack);
    }
    
    /// <summary>
    /// 更新移动
    /// </summary>
    private void UpdateMovement()
    {
        if (_agent != null && _agent.enabled && _agent.hasPath)
        {
            // 检查是否到达目标
            if (_agent.remainingDistance < 0.1f)
            {
                _isMoving = false;
                _agent.ResetPath();
            }
        }
    }
    
    /// <summary>
    /// 更新动画
    /// </summary>
    private void UpdateAnimation()
    {
        if (_animator != null)
        {
            _animator.SetBool(_animMoveId, _isMoving);
        }
    }
}

/// <summary>
/// 玩家实体数据
/// </summary>
public class PlayerEntityData : EntityData
{
    public Vector3 SpawnPosition { get; set; }
    public Quaternion SpawnRotation { get; set; }
    public int Level { get; set; }
    public int Health { get; set; }
    public int MaxHealth { get; set; }
    
    public static PlayerEntityData Create(
        int entityId, 
        Vector3 position, 
        Quaternion rotation,
        int level = 1)
    {
        PlayerEntityData data = ReferencePool.Acquire<PlayerEntityData>();
        data.Id = entityId;
        data.SpawnPosition = position;
        data.SpawnRotation = rotation;
        data.Level = level;
        data.Health = 100;
        data.MaxHealth = 100;
        return data;
    }
    
    public override void Clear()
    {
        base.Clear();
        SpawnPosition = Vector3.zero;
        SpawnRotation = Quaternion.identity;
        Level = 0;
        Health = 0;
        MaxHealth = 0;
    }
}
```

---

## 6. 实体组管理

### 6.1 创建实体组

```csharp
// 在 Procedure 或初始化代码中创建实体组
GF.Entity.AddEntityGroup("Player", 10, 60f, 30);
GF.Entity.AddEntityGroup("Enemy", 50, 60f, 30);
GF.Entity.AddEntityGroup("Effect", 100, 30f, 50);
```

### 6.2 参数说明

```csharp
void AddEntityGroup(
    string name,           // 实体组名称
    int instanceAutoReleaseInterval,  // 实例自动释放间隔（秒）
    float instanceExpireTime,         // 实例过期时间（秒）
    int instancePriority              // 实例优先级
);
```

---

## 7. 常见错误与纠正

### 7.1 错误：直接 Instantiate

```csharp
// ❌ 错误：直接实例化
void SpawnEnemy()
{
    var enemy = Instantiate(enemyPrefab);
    enemy.transform.position = spawnPoint.position;
}

// ✅ 正确：使用 GF 实体系统
void SpawnEnemy()
{
    var data = EnemyEntityData.Create(EntityId.EnemySlime, position, level);
    GF.Entity.ShowEntity(typeof(EnemyEntityLogic), data);
}
```

### 7.2 错误：手动管理生命周期

```csharp
// ❌ 错误：手动管理
void OnEnemyDeath()
{
    Destroy(enemyGameObject);  // 不要这样做！
}

// ✅ 正确：使用 GF 隐藏
void OnEnemyDeath()
{
    GF.Entity.HideEntity(this);  // 正确！
}
```

---

> 💡 **AI 提示**: 使用 Entity 系统时，记住三点：
> 1. 用 `ShowEntity` 代替 `Instantiate`
> 2. 用 `HideEntity` 代替 `Destroy`
> 3. 通过 `EntityData` 传递初始化数据
