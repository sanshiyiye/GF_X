# GF_X - AI 常见错误清单

> 本文档列出了 AI 在使用 GF_X 框架时最容易犯的错误，以及正确的做法。

---

## 1. 资源加载错误

### ❌ 错误 1：使用 Resources.Load()

```csharp
// ❌ 错误：使用 Resources
void LoadPrefab()
{
    var prefab = Resources.Load<GameObject>("Prefabs/Enemy");
    Instantiate(prefab);
}
```

**问题**：
- 无法热更新
- 不能异步加载，会卡顿
- 没有依赖管理

```csharp
// ✅ 正确：使用 GF.Resource
void LoadPrefab()
{
    GF.Resource.LoadAsset<GameObject>(
        "Assets/AAAGame/Prefabs/Entity/Enemy.prefab",
        (assetName, asset, duration, userData) =>
        {
            Instantiate((GameObject)asset);
        }
    );
}
```

---

### ❌ 错误 2：直接 Instantiate GameObject

```csharp
// ❌ 错误：直接实例化
void SpawnEnemy()
{
    var enemy = Instantiate(enemyPrefab, position, rotation);
    enemy.GetComponent<EnemyLogic>().Initialize(data);
}
```

**问题**：
- 绕过 GF 实体系统
- 无法使用对象池
- 没有生命周期管理

```csharp
// ✅ 正确：使用 GF.Entity
void SpawnEnemy()
{
    var entityData = EnemyEntityData.Create(EntityId.Enemy, position, level);
    GF.Entity.ShowEntity(typeof(EnemyEntityLogic), entityData);
}
```

---

## 2. UI 系统错误

### ❌ 错误 3：直接 Instantiate UI

```csharp
// ❌ 错误：直接实例化 UI
void OpenMenu()
{
    var menu = Instantiate(menuPrefab);
    menu.transform.SetParent(canvas.transform, false);
    
    // 手动设置层级
    menu.transform.SetAsLastSibling();
}
```

**问题**：
- 没有层级管理
- 没有生命周期回调
- 无法使用 UI 组

```csharp
// ✅ 正确：使用 GF.UI
void OpenMenu()
{
    // 简单打开
    GF.UI.OpenUIForm(UIFormId.MainMenu);
    
    // 带数据打开
    var data = new MenuData { Level = 10 };
    GF.UI.OpenUIForm(UIFormId.MainMenu, data, "Main");
}
```

---

### ❌ 错误 4：使用 GameObject.Find()

```csharp
// ❌ 错误：使用 Find
void Start()
{
    var button = GameObject.Find("ConfirmButton").GetComponent<Button>();
    button.onClick.AddListener(OnClick);
}
```

**问题**：
- 性能差（遍历整个场景）
- 容易出错（名称修改后找不到）
- 依赖场景结构

```csharp
// ✅ 正确：使用序列化字段
public class MyUIFormLogic : UIFormLogic
{
    [SerializeField]
    private Button _confirmButton;
    
    protected override void OnInit(object userData)
    {
        base.OnInit(userData);
        _confirmButton.onClick.AddListener(OnClick);
    }
}
```

---

## 3. 数据管理错误

### ❌ 错误 5：硬编码配置数据

```csharp
// ❌ 错误：硬编码
void CreatePlayer()
{
    player.MaxHP = 1000;
    player.MoveSpeed = 5.0f;
    player.Attack = 50;
}

void GetItemName(int itemId)
{
    if (itemId == 1001) return "铁剑";
    if (itemId == 1002) return "钢剑";
    if (itemId == 1003) return "银剑";
    return "";
}
```

**问题**：
- 无法热更新
- 难以维护
- 容易出错

```csharp
// ✅ 正确：使用数据表
void CreatePlayer()
{
    var configTable = GF.DataTable.GetDataTable<DRPlayerConfig>();
    var config = configTable.GetDataRow(1);
    
    player.MaxHP = config.MaxHP;
    player.MoveSpeed = config.MoveSpeed;
    player.Attack = config.BaseAttack;
}

string GetItemName(int itemId)
{
    var itemTable = GF.DataTable.GetDataTable<DRItem>();
    var item = itemTable.GetDataRow(itemId);
    return item?.Name ?? "";
}
```

---

### ❌ 错误 6：在 Update 中查询数据表

```csharp
// ❌ 错误：每帧查询
void Update()
{
    var table = GF.DataTable.GetDataTable<DRItem>();  // 不要每帧调用！
    var item = table.GetDataRow(currentItemId);
    UpdateUI(item);
}
```

**问题**：
- 性能浪费
- 重复获取相同数据

```csharp
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

## 4. 生命周期管理错误

### ❌ 错误 7：忘记取消事件订阅

```csharp
// ❌ 错误：不取消订阅
protected override void OnLeave(IFsm<IProcedureManager> procedureOwner, bool isShutdown)
{
    base.OnLeave(procedureOwner, isShutdown);
    // 没有取消事件订阅！
}
```

**问题**：
- 内存泄漏
- 事件重复触发
- 空引用异常

```csharp
// ✅ 正确：取消订阅
private void OnGameOver(object sender, GameEventArgs e)
{
    ChangeState<GameOverProcedure>(procedureOwner);
}

protected override void OnEnter(IFsm<IProcedureManager> procedureOwner)
{
    base.OnEnter(procedureOwner);
    GF.Event.Subscribe(GameOverEventArgs.EventId, OnGameOver);
}

protected override void OnLeave(IFsm<IProcedureManager> procedureOwner, bool isShutdown)
{
    base.OnLeave(procedureOwner, isShutdown);
    GF.Event.Unsubscribe(GameOverEventArgs.EventId, OnGameOver);
}
```

---

### ❌ 错误 8：在生命周期外操作对象

```csharp
// ❌ 错误：在 OnLeave 后访问对象
protected override void OnLeave(IFsm<IProcedureManager> procedureOwner, bool isShutdown)
{
    base.OnLeave(procedureOwner, isShutdown);
    
    _player.transform.position = Vector3.zero;  // 错误！对象可能已销毁
}
```

```csharp
// ✅ 正确：在生命周期内完成操作
protected override void OnLeave(IFsm<IProcedureManager> procedureOwner, bool isShutdown)
{
    // 先完成所有操作
    if (_player != null)
    {
        _player.transform.position = Vector3.zero;
    }
    
    // 最后调用基类
    base.OnLeave(procedureOwner, isShutdown);
}
```

---

## 5. 内存管理错误

### ❌ 错误 9：不使用引用池

```csharp
// ❌ 错误：直接 new
void FireEvent()
{
    var args = new DamageEventArgs();  // GC 分配
    args.Damage = 100;
    GF.Event.Fire(this, args);
}
```

```csharp
// ✅ 正确：使用引用池
void FireEvent()
{
    var args = ReferencePool.Acquire<DamageEventArgs>();  // 从池中获取
    args.Damage = 100;
    GF.Event.Fire(this, args);
    // 事件处理完成后自动归还池中
}
```

---

## 6. 快速检查清单

### 编码前检查

- [ ] 确定使用哪个 GF 模块 (UI/Entity/Resource/...)
- [ ] 确认文件放在正确的目录 (Scripts/ vs ScriptsBuiltin/)
- [ ] 确认继承正确的基类 (ProcedureBase/UIFormLogic/EntityLogic)

### 编码中检查

- [ ] 使用 GF.XXX 而不是 Unity API
- [ ] 从数据表/配置读取数据，不硬编码
- [ ] 使用异步加载，不阻塞主线程
- [ ] 使用引用池，不直接 new

### 编码后检查

- [ ] 在 OnLeave/OnClose 中取消事件订阅
- [ ] 释放不用的资源
- [ ] 清理数据引用

---

> 💡 **核心口诀**:
> - **用 GF，不用 Unity** - 框架优先
> - **查数据，不硬编码** - 数据驱动  
> - **走异步，不阻塞** - 性能优化
> - **记清理，不泄露** - 生命周期
