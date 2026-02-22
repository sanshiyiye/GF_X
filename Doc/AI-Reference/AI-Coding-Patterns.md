# GF_X - AI 编码模式与最佳实践

> 本文档总结了在 GF_X 框架中进行 AI 辅助编码时的最佳模式和实践。

---

## 1. 核心原则

### 1.1 框架优先原则

```csharp
// ✅ 正确：使用 GF 框架 API
GF.UI.OpenUIForm(UIFormId.MainMenu);
GF.Entity.ShowEntity(typeof(PlayerEntity), data);
GF.Resource.LoadAsset<GameObject>(assetName, callback);

// ❌ 错误：绕过框架直接使用 Unity API
Instantiate(uiPrefab);
GameObject player = new GameObject("Player");
Resources.Load<GameObject>(path);
```

### 1.2 数据驱动原则

```csharp
// ✅ 正确：从数据表/配置读取数据
var itemTable = GF.DataTable.GetDataTable<DRItem>();
var itemData = itemTable.GetDataRow(itemId);
int attack = itemData.Attack;

// ❌ 错误：硬编码数据
int attack = 100;  // 不要硬编码！
```

### 1.3 生命周期管理原则

```csharp
public class MyUIFormLogic : UIFormLogic
{
    protected override void OnInit(object userData)
    {
        base.OnInit(userData);
        // 绑定事件、初始化组件
    }
    
    protected override void OnOpen(object userData)
    {
        base.OnOpen(userData);
        // 接收数据、更新显示
    }
    
    protected override void OnClose(bool isShutdown, object userData)
    {
        base.OnClose(isShutdown, userData);
        // 清理数据
    }
}
```

---

## 2. 常用代码模式

### 2.1 单例访问模式

```csharp
// GF 模块访问（已经是单例模式）
GF.UI.OpenUIForm(...);
GF.Entity.ShowEntity(...);
GF.Resource.LoadAsset(...);

// 游戏内单例（GameEntry 扩展）
public static class GameEntry
{
    public static GameManager Game { get; private set; }
    public static PlayerManager Player { get; private set; }
    
    public static void Initialize()
    {
        Game = new GameManager();
        Player = new PlayerManager();
    }
}
```

### 2.2 事件订阅模式

```csharp
public class MyProcedure : ProcedureBase
{
    protected override void OnEnter(IFsm<IProcedureManager> procedureOwner)
    {
        base.OnEnter(procedureOwner);
        
        // 订阅事件
        GF.Event.Subscribe(OpenUIFormSuccessEventArgs.EventId, OnOpenUISuccess);
        GF.Event.Subscribe(GameOverEventArgs.EventId, OnGameOver);
    }
    
    protected override void OnLeave(IFsm<IProcedureManager> procedureOwner, bool isShutdown)
    {
        base.OnLeave(procedureOwner, isShutdown);
        
        // 取消订阅（重要！）
        GF.Event.Unsubscribe(OpenUIFormSuccessEventArgs.EventId, OnOpenUISuccess);
        GF.Event.Unsubscribe(GameOverEventArgs.EventId, OnGameOver);
    }
    
    private void OnOpenUISuccess(object sender, GameEventArgs e)
    {
        var args = (OpenUIFormSuccessEventArgs)e;
        Log.Info($"UI 打开成功: {args.UIForm.UIFormAssetName}");
    }
}
```

### 2.3 异步加载模式

```csharp
using Cysharp.Threading.Tasks;

public class PreloadProcedure : ProcedureBase
{
    protected override async void OnEnter(IFsm<IProcedureManager> procedureOwner)
    {
        base.OnEnter(procedureOwner);
        
        try
        {
            // 并行加载多个资源
            var (playerPrefab, enemyPrefab, uiPrefab) = await UniTask.WhenAll(
                LoadAsset<GameObject>("Assets/AAAGame/Prefabs/Entity/Player.prefab"),
                LoadAsset<GameObject>("Assets/AAAGame/Prefabs/Entity/Enemy.prefab"),
                LoadAsset<GameObject>("Assets/AAAGame/Prefabs/UI/MainMenu.prefab")
            );
            
            // 继续后续逻辑
            ChangeState<MenuProcedure>(procedureOwner);
        }
        catch (Exception e)
        {
            Log.Error($"预加载失败: {e.Message}");
        }
    }
    
    private async UniTask<T> LoadAsset<T>(string assetName) where T : UnityEngine.Object
    {
        var tcs = new UniTaskCompletionSource<T>();
        
        GF.Resource.LoadAsset<T>(
            assetName,
            (name, asset, duration, userData) =>
            {
                tcs.TrySetResult((T)asset);
            },
            (name, status, error, userData) =>
            {
                tcs.TrySetException(new Exception($"加载失败: {name}, {error}"));
            }
        );
        
        return await tcs.Task;
    }
}
```

---

## 3. 常见场景解决方案

### 3.1 场景切换

```csharp
public class ChangeSceneProcedure : ProcedureBase
{
    private int _targetSceneId;
    private bool _sceneLoaded = false;
    
    protected override void OnEnter(IFsm<IProcedureManager> procedureOwner)
    {
        base.OnEnter(procedureOwner);
        
        // 显示加载界面
        GF.UI.OpenUIForm(UIFormId.Loading);
        
        // 获取目标场景ID（从 Procedure Owner 获取）
        _targetSceneId = procedureOwner.GetData<VarInt32>("TargetSceneId").Value;
        
        // 订阅场景加载事件
        GF.Event.Subscribe(LoadSceneSuccessEventArgs.EventId, OnLoadSceneSuccess);
        GF.Event.Subscribe(LoadSceneFailureEventArgs.EventId, OnLoadSceneFailure);
        
        // 开始加载场景
        var sceneTable = GF.DataTable.GetDataTable<DRScene>();
        var sceneData = sceneTable.GetDataRow(_targetSceneId);
        GF.Scene.LoadScene(sceneData.AssetName, Constants.SceneLoadPriority, this);
    }
    
    private void OnLoadSceneSuccess(object sender, GameEventArgs e)
    {
        var args = (LoadSceneSuccessEventArgs)e;
        if (args.UserData != this) return;
        
        _sceneLoaded = true;
        
        // 关闭加载界面
        GF.UI.CloseAllLoadedUIForms(UIFormId.Loading);
        
        // 切换到游戏流程
        ChangeState<GameProcedure>(procedureOwner);
    }
    
    protected override void OnLeave(IFsm<IProcedureManager> procedureOwner, bool isShutdown)
    {
        base.OnLeave(procedureOwner, isShutdown);
        
        // 取消订阅事件
        GF.Event.Unsubscribe(LoadSceneSuccessEventArgs.EventId, OnLoadSceneSuccess);
        GF.Event.Unsubscribe(LoadSceneFailureEventArgs.EventId, OnLoadSceneFailure);
    }
}
```

### 3.2 网络请求

```csharp
public class NetworkManager
{
    public void SendLoginRequest(string username, string password, Action<LoginResponse> callback)
    {
        // 构造请求数据
        var requestData = new LoginRequest
        {
            Username = username,
            Password = password,
            DeviceId = SystemInfo.deviceUniqueIdentifier
        };
        
        // 序列化为 JSON
        string json = JsonUtility.ToJson(requestData);
        byte[] postData = System.Text.Encoding.UTF8.GetBytes(json);
        
        // 发送 HTTP 请求
        GF.WebRequest.AddWebRequest(
            "https://api.game.com/login",
            postData,
            (sender, e) =>
            {
                if (e.IsError)
                {
                    Log.Error($"登录请求失败: {e.ErrorMessage}");
                    callback?.Invoke(null);
                    return;
                }
                
                // 解析响应
                string responseJson = System.Text.Encoding.UTF8.GetString(e.GetWebResponseBytes());
                var response = JsonUtility.FromJson<LoginResponse>(responseJson);
                
                callback?.Invoke(response);
            }
        );
    }
}

[Serializable]
public class LoginRequest
{
    public string Username;
    public string Password;
    public string DeviceId;
}

[Serializable]
public class LoginResponse
{
    public int Code;
    public string Message;
    public string Token;
    public PlayerInfo Player;
}

[Serializable]
public class PlayerInfo
{
    public int Id;
    public string Nickname;
    public int Level;
    public long Gold;
}
```

---

## 4. 性能优化指南

### 4.1 资源加载优化

```csharp
// ✅ 批量加载，减少 IO 次数
var assetNames = new List<string>
{
    "Assets/AAAGame/Prefabs/UI/Button.prefab",
    "Assets/AAAGame/Prefabs/UI/Panel.prefab",
    "Assets/AAAGame/Prefabs/UI/Text.prefab"
};

foreach (var assetName in assetNames)
{
    GF.Resource.LoadAsset<GameObject>(assetName, callback);
}

// ✅ 预加载常用资源，避免运行时加载
public class PreloadProcedure : ProcedureBase
{
    protected override void OnEnter(IFsm<IProcedureManager> procedureOwner)
    {
        // 预加载 UI 预制体
        GF.Resource.LoadAsset<GameObject>("Assets/AAAGame/Prefabs/UI/MainMenu.prefab", null);
        GF.Resource.LoadAsset<GameObject>("Assets/AAAGame/Prefabs/UI/Setting.prefab", null);
        
        // 预加载通用音效
        GF.Sound.PreloadSound(SoundId.Click);
        GF.Sound.PreloadSound(SoundId.Confirm);
    }
}

// ✅ 及时释放不用的资源
public class ShopUIFormLogic : UIFormLogic
{
    private GameObject _shopItemPrefab;
    
    protected override void OnClose(bool isShutdown, object userData)
    {
        base.OnClose(isShutdown, userData);
        
        // 释放资源
        if (_shopItemPrefab != null)
        {
            GF.Resource.UnloadAsset(_shopItemPrefab);
            _shopItemPrefab = null;
        }
    }
}
```

### 4.2 UI 优化

```csharp
// ✅ 对象池复用 UI 元素
public class BagUIFormLogic : UIFormLogic
{
    private IObjectPool<UIItemLogic> _itemPool;
    private List<UIItemLogic> _activeItems = new List<UIItemLogic>();
    
    protected override void OnInit(object userData)
    {
        base.OnInit(userData);
        
        // 创建对象池
        _itemPool = GF.ObjectPool.CreateSingleSpawnObjectPool<UIItemLogic>("UIItem", 50);
    }
    
    private void CreateItem(DRItem itemData)
    {
        UIItemLogic item = _itemPool.Spawn();
        if (item == null)
        {
            // 创建新的
            GameObject instance = Instantiate(_itemPrefab, _contentParent);
            item = instance.GetComponent<UIItemLogic>();
        }
        
        item.Setup(itemData);
        _activeItems.Add(item);
    }
    
    private void ClearItems()
    {
        foreach (var item in _activeItems)
        {
            _itemPool.Unspawn(item);
        }
        _activeItems.Clear();
    }
}

// ✅ 减少 UI 层级和 Overdraw
public class GameHudUIFormLogic : UIFormLogic
{
    protected override void OnOpen(object userData)
    {
        base.OnOpen(userData);
        
        // 合并材质，使用图集
        // 减少 Mask 和透明层级
        // 使用 RectMask2D 替代 Mask
    }
}
```

---

> 💡 **AI 提示**: 性能优化记住三句话：
> 1. **预加载**常用资源，避免运行时卡顿
> 2. **及时释放**不用的资源，防止内存泄漏
> 3. **使用对象池**复用对象，减少 GC
