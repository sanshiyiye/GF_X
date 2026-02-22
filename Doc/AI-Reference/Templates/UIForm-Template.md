# 模板：UIForm（UI界面）

> 创建新 UI 界面时的标准模板

---

## UIFormLogic 模板

```csharp
// 文件路径: Assets/AAAGame/Scripts/UI/{Category}/{UIFormName}UIFormLogic.cs

using UnityGameFramework.Runtime;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// {UIFormName} UI 界面逻辑
/// </summary>
public class {UIFormName}UIFormLogic : UIFormLogic
{
    #region Serialize Fields
    
    [Header("UI Components")]
    [SerializeField]
    private Text _titleText;
    
    [SerializeField]
    private Button _confirmButton;
    
    [SerializeField]
    private Button _closeButton;
    
    // 在此添加更多 UI 组件引用
    
    #endregion
    
    #region Private Fields
    
    private {UIFormName}UIFormData _data;
    
    #endregion
    
    #region Lifecycle
    
    /// <summary>
    /// 初始化（仅调用一次）
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
        
        // 接收并存储数据
        _data = userData as {UIFormName}UIFormData;
        if (_data == null)
        {
            Log.Warning($"UI {gameObject.name} 没有接收到有效数据");
            return;
        }
        
        // 更新 UI 显示
        UpdateUI();
        
        // 播放打开动画
        PlayOpenAnimation();
    }
    
    /// <summary>
    /// 界面关闭时调用
    /// </summary>
    protected override void OnClose(bool isShutdown, object userData)
    {
        base.OnClose(isShutdown, userData);
        
        // 播放关闭动画
        PlayCloseAnimation();
        
        // 清理数据引用
        _data = null;
    }
    
    /// <summary>
    /// 界面深度改变时调用
    /// </summary>
    protected override void OnDepthChanged(int uiGroupDepth, int depthInUIGroup)
    {
        base.OnDepthChanged(uiGroupDepth, depthInUIGroup);
        
        // 处理深度变化（如调整层级相关的显示）
    }
    
    /// <summary>
    /// 轮询时调用
    /// </summary>
    protected override void OnUpdate(float elapseSeconds, float realElapseSeconds)
    {
        base.OnUpdate(elapseSeconds, realElapseSeconds);
        
        // 处理需要每帧更新的逻辑
    }
    
    #endregion
    
    #region Private Methods
    
    /// <summary>
    /// 更新 UI 显示
    /// </summary>
    private void UpdateUI()
    {
        if (_titleText != null && _data != null && !string.IsNullOrEmpty(_data.Title))
        {
            _titleText.text = _data.Title;
        }
        
        // 更新其他 UI 元素
    }
    
    /// <summary>
    /// 播放打开动画
    /// </summary>
    private void PlayOpenAnimation()
    {
        // 实现打开动画
        // 例如：淡入、缩放、滑入等
        // 可以使用 DOTween、Animator 或自定义动画
    }
    
    /// <summary>
    /// 播放关闭动画
    /// </summary>
    private void PlayCloseAnimation()
    {
        // 实现关闭动画
    }
    
    /// <summary>
    /// 确认按钮点击处理
    /// </summary>
    private void OnConfirmClicked()
    {
        // 触发确认事件
        var eventArgs = ReferencePool.Acquire<{UIFormName}ConfirmEventArgs>();
        eventArgs.Fill(_data);
        GF.Event.Fire(this, eventArgs);
        
        // 关闭界面
        Close();
    }
    
    /// <summary>
    /// 关闭按钮点击处理
    /// </summary>
    private void OnCloseClicked()
    {
        // 触发取消事件（如果需要）
        
        // 关闭界面
        Close();
    }
    
    #endregion
}

/// <summary>
/// {UIFormName} UI 数据类
/// </summary>
public class {UIFormName}UIFormData
{
    public string Title { get; set; }
    public string Content { get; set; }
    public int ConfirmId { get; set; }
    public System.Action OnConfirm { get; set; }
    public System.Action OnCancel { get; set; }
}

/// <summary>
/// {UIFormName} 确认事件参数
/// </summary>
public class {UIFormName}ConfirmEventArgs : GameEventArgs
{
    public static readonly int EventId = typeof({UIFormName}ConfirmEventArgs).GetHashCode();
    
    public override int Id => EventId;
    
    public {UIFormName}UIFormData Data { get; private set; }
    
    public {UIFormName}ConfirmEventArgs Fill({UIFormName}UIFormData data)
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

---

## 使用步骤

### 1. 创建文件

```bash
# UI 逻辑脚本
touch Assets/AAAGame/Scripts/UI/{Category}/{UIFormName}UIFormLogic.cs

# UI 预制体（在 Unity 中创建）
# Assets/AAAGame/Prefabs/UI/{UIFormName}.prefab
```

### 2. 复制模板

将上面的模板代码复制到新建的文件中

### 3. 替换占位符

| 占位符 | 替换为 | 示例 |
|--------|--------|------|
| `{UIFormName}` | UI 名称 | `MainMenu`, `Shop`, `Dialog` |
| `{Category}` | 分类目录 | `Menu`, `Game`, `System` |

### 4. 实现业务逻辑

在 `UpdateUI`, `OnConfirmClicked`, `OnCloseClicked` 等方法中添加具体逻辑

### 5. 配置 UI Form

```csharp
// 在 UIFormId.cs 中添加 ID
public static class UIFormId
{
    public const int {UIFormName} = {ID};
}
```

---

> 💡 **提示**: UI 界面遵循 "数据驱动" 原则，通过 `UIFormData` 传递数据，不要硬编码！
