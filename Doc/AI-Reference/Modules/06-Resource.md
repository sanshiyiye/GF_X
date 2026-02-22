# GF_X 模块参考：Resource（资源系统）

> 本文档帮助 AI 理解并正确使用 GF_X 的资源管理系统。

---

## 1. 核心概念

### 1.1 什么是资源系统？

GF_X 的资源系统基于 **GameFramework.Resource**，提供：

- 📦 **AssetBundle 管理** - 自动加载依赖
- 🔄 **对象池复用** - 减少 GC 压力
- ⚡ **异步加载** - 避免卡顿
- 📁 **资源路径管理** - 统一资源寻址

### 1.2 资源加载方式对比

| 方式 | API | 适用场景 | 特点 |
|------|-----|----------|------|
| **Resources** | `Resources.Load()` | 简单项目 | Unity 原生，无法热更新 |
| **AssetBundle** | `GF.Resource.LoadAsset()` | 生产环境 | GF 管理，支持热更新 |
| **Addressables** | `Addressables.LoadAssetAsync()` | 大型项目 | Unity 官方，需要额外配置 |

**GF_X 推荐：使用 AssetBundle 方式**（GF.Resource 模块）

### 1.3 资源路径规范

```
资源路径格式：Assets/AAAGame/{类型}/{路径}/{文件名}.{扩展名}

类型目录：
├── Prefabs/        # 预制体 (UI、实体、特效等)
├── Scene/          # 场景文件
├── Audio/          # 音频文件
├── DataTable/      # 数据表资源 (.txt/.bytes)
├── Config/         # 配置文件
├── Language/       # 多语言资源
├── Animation/      # 动画文件
├── Materials/      # 材质文件
├── Models/         # 模型文件
├── Sprites/        # 精灵图
└── Textures/       # 贴图文件
```

---

## 2. 基础使用

### 2.1 加载资源

```csharp
// ====== 基础加载（回调方式） ======

GF.Resource.LoadAsset<GameObject>(
    "Assets/AAAGame/Prefabs/Enemy/Slime.prefab",
    OnLoadSuccess,
    OnLoadFailure
);

void OnLoadSuccess(string assetName, object asset, float duration, object userData)
{
    GameObject prefab = (GameObject)asset;
    // 实例化或使用资源
}

void OnLoadFailure(string assetName, LoadResourceStatus status, string errorMessage, object userData)
{
    Log.Error($"资源加载失败: {assetName}, 错误: {errorMessage}");
}


// ====== 使用 UniTask 异步加载（推荐） ======

using Cysharp.Threading.Tasks;

async UniTask LoadAssetAsync()
{
    try
    {
        GameObject prefab = await GF.Resource.LoadAsset<GameObject>(
            "Assets/AAAGame/Prefabs/UI/MainMenu.prefab"
        ).ToUniTask();
        
        // 资源加载成功
        Instantiate(prefab);
    }
    catch (Exception e)
    {
        Log.Error($"加载失败: {e.Message}");
    }
}
```

### 2.2 实例化预制体

```csharp
// ====== 方式1：加载后手动实例化 ======

GF.Resource.LoadAsset<GameObject>(
    "Assets/AAAGame/Prefabs/Effect/Explosion.prefab",
    (assetName, asset, duration, userData) =>
    {
        GameObject prefab = (GameObject)asset;
        
        // 实例化到指定位置
        GameObject instance = Instantiate(prefab, spawnPosition, spawnRotation);
        
        // 获取并调用初始化
        var effectLogic = instance.GetComponent<EffectLogic>();
        effectLogic?.Play();
    }
);


// ====== 方式2：通过实体系统（推荐） ======

// 对于游戏对象（玩家、敌人、NPC等），使用 Entity 系统
var entityData = EnemyEntityData.Create(EntityId.EnemySlime, position, level);
GF.Entity.ShowEntity(typeof(EnemyEntityLogic), entityData);
```

### 2.3 卸载资源

```csharp
// ====== 方式1：使用 Asset 对象引用 ======

GameObject _loadedPrefab;

void UnloadAsset()
{
    if (_loadedPrefab != null)
    {
        GF.Resource.UnloadAsset(_loadedPrefab);
        _loadedPrefab = null;
    }
}


// ====== 方式2：强制卸载未使用资源（慎用） ======

// 在场景切换或内存紧张时调用
GF.Resource.ForceUnloadUnusedAssets(true);


// ====== 方式3：设置资源对象池自动释放 ======

// 在加载时设置过期时间
GF.Resource.LoadAsset<GameObject>(
    assetName,
    priority: 0,
    userData: null,
    loadCallbacks: callbacks,
    playDuration: 60f  // 60秒后自动释放
);
```

---

## 3. 资源加载策略

### 3.1 预加载策略

```csharp
// 在 PreloadProcedure 中预加载常用资源

public class PreloadProcedure : ProcedureBase
{
    private List<string> _preloadAssets = new List<string>
    {
        "Assets/AAAGame/Prefabs/UI/MainMenu.prefab",
        "Assets/AAAGame/Prefabs/UI/Setting.prefab",
        "Assets/AAAGame/Prefabs/Effect/CommonHit.prefab",
        "Assets/AAAGame/Audio/Music/MainBgm.ogg",
    };
    
    private int _loadedCount = 0;
    
    protected override void OnEnter(IFsm<IProcedureManager> procedureOwner)
    {
        base.OnEnter(procedureOwner);
        
        // 显示加载界面
        GF.UI.OpenUIForm(UIFormId.Loading);
        
        // 开始预加载
        PreloadAssets();
    }
    
    private void PreloadAssets()
    {
        foreach (string assetName in _preloadAssets)
        {
            GF.Resource.LoadAsset<Object>(
                assetName,
                OnPreloadSuccess,
                OnPreloadFailure
            );
        }
    }
    
    private void OnPreloadSuccess(string assetName, object asset, float duration, object userData)
    {
        _loadedCount++;
        
        // 更新加载进度
        float progress = (float)_loadedCount / _preloadAssets.Count;
        GF.Event.Fire(this, ReferencePool.Acquire<LoadingProgressEventArgs>().Fill(progress));
        
        // 检查是否全部加载完成
        if (_loadedCount >= _preloadAssets.Count)
        {
            OnPreloadComplete();
        }
    }
    
    private void OnPreloadFailure(string assetName, LoadResourceStatus status, string errorMessage, object userData)
    {
        Log.Error($"预加载失败: {assetName}, {errorMessage}");
        
        // 失败也算完成，继续后续逻辑
        _loadedCount++;
        if (_loadedCount >= _preloadAssets.Count)
        {
            OnPreloadComplete();
        }
    }
    
    private void OnPreloadComplete()
    {
        // 关闭加载界面
        GF.UI.CloseAllLoadedUIForms(UIFormId.Loading);
        
        // 切换到菜单流程
        ChangeState<MenuProcedure>(procedureOwner);
    }
}
```

### 3.2 按需加载策略

```csharp
// 对于不常用的资源，按需加载，用完即释放

public class ShopUIFormBase : UIFormBase
{
    private GameObject _shopItemPrefab;
    private List<GameObject> _itemInstances = new List<GameObject>();
    
    protected override void OnOpen(object userData)
    {
        base.OnOpen(userData);
        
        // 按需加载商店物品预制体
        GF.Resource.LoadAsset<GameObject>(
            "Assets/AAAGame/Prefabs/UI/ShopItem.prefab",
            OnShopItemPrefabLoaded
        );
    }
    
    private void OnShopItemPrefabLoaded(string assetName, object asset, float duration, object userData)
    {
        _shopItemPrefab = (GameObject)asset;
        
        // 创建商店物品列表
        CreateShopItems();
    }
    
    private void CreateShopItems()
    {
        var itemTable = GF.DataTable.GetDataTable<DRItem>();
        var items = itemTable.GetAllDataRows(item => item.Type == (int)ItemType.Shop);
        
        foreach (var item in items)
        {
            GameObject instance = Instantiate(_shopItemPrefab, contentParent);
            var itemLogic = instance.GetComponent<ShopItemLogic>();
            itemLogic.Setup(item);
            _itemInstances.Add(instance);
        }
    }
    
    protected override void OnClose(bool isShutdown, object userData)
    {
        base.OnClose(isShutdown, userData);
        
        // 清理实例
        foreach (var instance in _itemInstances)
        {
            Destroy(instance);
        }
        _itemInstances.Clear();
        
        // 释放预制体资源
        if (_shopItemPrefab != null)
        {
            GF.Resource.UnloadAsset(_shopItemPrefab);
            _shopItemPrefab = null;
        }
    }
}
```

---

## 4. 快速参考

### 4.1 常用方法速查

```csharp
// 加载资源
GF.Resource.LoadAsset<T>(
    assetName,      // 资源路径
    loadCallbacks,  // 成功/失败回调
    priority,       // 优先级
    userData        // 用户数据
);

// 卸载资源
GF.Resource.UnloadAsset(asset);

// 强制卸载未使用资源
GF.Resource.ForceUnloadUnusedAssets(performGCCollect);

// 设置对象池容量
GF.Resource.SetObjectPoolCapacity(objectType, capacity);

// 设置对象池过期时间
GF.Resource.SetObjectPoolExpireTime(objectType, expireTime);
```

### 4.2 资源路径示例

```
// 预制体
Assets/AAAGame/Prefabs/UI/MainMenu.prefab
Assets/AAAGame/Prefabs/Entity/Player.prefab
Assets/AAAGame/Prefabs/Effect/Explosion.prefab

// 场景
Assets/AAAGame/Scene/Menu.unity
Assets/AAAGame/Scene/Level01.unity

// 音频
Assets/AAAGame/Audio/Music/MainBgm.ogg
Assets/AAAGame/Audio/SFX/Click.wav

// 数据表
Assets/AAAGame/DataTable/Item.txt
Assets/AAAGame/DataTable/Level.txt

// 材质、贴图等
Assets/AAAGame/Materials/Character.mat
Assets/AAAGame/Textures/UI/Atlas.png
```

---

> 💡 **AI 提示**: 使用资源系统时，记住三原则：
> 1. **使用 GF.Resource** 代替 Resources.Load 和 Instantiate
> 2. **异步加载** 避免阻塞主线程
> 3. **及时卸载** 不用的资源，避免内存泄漏
