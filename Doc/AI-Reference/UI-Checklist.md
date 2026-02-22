# UI 代码自查清单

> 用于检查 UI 代码是否符合 GF_X 框架规范和最佳实践。

---

## 📋 基础结构检查

### 类定义
- [ ] UI ID 已在 `UIFormId.cs` 中定义
- [ ] 类继承自 `UIFormBase`（**不是** `UIFormLogic`）
- [ ] 类使用 `partial` 关键字（如果需要工具生成变量）
- [ ] 命名符合规范：`XXXUIForm`（**无 Logic 后缀**）
- [ ] 文件路径正确：`Assets/AAAGame/Scripts/UI/{Category}/`

**正确示例**：
```csharp
// 文件：Assets/AAAGame/Scripts/UI/Menu/ShopUIForm.cs
public partial class ShopUIForm : UIFormBase
{
    // UI 逻辑
}

// ID 定义
public static class UIFormId
{
    public const int Shop = 2001;
}
```

**常见错误**：
```csharp
// ❌ 错误：继承 UIFormLogic
public class ShopUIForm : UIFormLogic  // 应该是 UIFormBase

// ❌ 错误：命名带 Logic 后缀
public class ShopUIFormLogic : UIFormBase  // 应该是 ShopUIForm

// ❌ 错误：没定义 ID
// UIFormId.cs 中没有 Shop = 2001
```

---

## 📁 文件组织检查

- [ ] 文件路径：`Assets/AAAGame/Scripts/UI/{Category}/`
- [ ] Prefab 路径：`Assets/AAAGame/Prefabs/UI/`
- [ ] Prefab 命名与类名一致（如 `ShopUIForm.prefab`）
- [ ] 工具生成代码在 `UIVariables/` 子目录
- [ ] 变量代码文件：`{UIFormName}.Variables.cs`

**文件结构示例**：
```
Assets/AAAGame/
├── Scripts/
│   └── UI/
│       ├── Menu/
│       │   ├── ShopUIForm.cs          # 主逻辑文件
│       │   └── MenuUIForm.cs
│       └── UIVariables/               # 工具生成变量
│           ├── ShopUIForm.Variables.cs
│           └── MenuUIForm.Variables.cs
└── Prefabs/
    └── UI/
        ├── ShopUIForm.prefab          # Prefab
        └── MenuUIForm.prefab
```

---

## ⏱️ 生命周期检查

### OnInit（初始化，只调用一次）
- [ ] 绑定按钮点击事件
- [ ] 获取组件引用（GetComponent）
- [ ] 初始化本地数据

**正确示例**：
```csharp
protected override void OnInit(object userData)
{
    base.OnInit(userData);
    
    // ✅ 绑定事件
    _confirmButton.onClick.AddListener(OnConfirmClicked);
    _closeButton.onClick.AddListener(OnCloseClicked);
    
    // ✅ 获取组件
    _animator = GetComponent<Animator>();
}
```

### OnOpen（打开时调用，每次打开都调用）
- [ ] 接收并存储数据（转换为 UIFormData）
- [ ] 更新 UI 显示
- [ ] 播放打开动画
- [ ] 订阅需要的事件

**正确示例**：
```csharp
protected override void OnOpen(object userData)
{
    base.OnOpen(userData);
    
    // ✅ 接收数据
    _data = userData as ShopUIFormData;
    if (_data == null)
    {
        Log.Warning("ShopUIForm 没有接收到有效数据");
        return;
    }
    
    // ✅ 更新显示
    UpdateUI();
    
    // ✅ 播放动画
    PlayOpenAnimation();
    
    // ✅ 订阅事件
    GF.Event.Subscribe(BuyItemSuccessEventArgs.EventId, OnBuySuccess);
}
```

### OnClose（关闭时调用）
- [ ] 取消订阅所有事件（**必须！**）
- [ ] 播放关闭动画
- [ ] 清理数据引用（设为 null）
- [ ] 停止协程/定时器

**正确示例**：
```csharp
protected override void OnClose(bool isShutdown, object userData)
{
    base.OnClose(isShutdown, userData);
    
    // ✅ 取消订阅（必须！）
    GF.Event.Unsubscribe(BuyItemSuccessEventArgs.EventId, OnBuySuccess);
    
    // ✅ 播放关闭动画
    PlayCloseAnimation();
    
    // ✅ 清理数据
    _data = null;
}
```

**⚠️ 常见错误**：忘记取消订阅导致内存泄漏！

```csharp
// ❌ 错误：只订阅，不取消订阅
protected override void OnOpen(object userData)
{
    GF.Event.Subscribe(EventId, OnEvent);  // 订阅
}

protected override void OnClose(bool isShutdown, object userData)
{
    // ❌ 错误：没有取消订阅！
}

// ✅ 正确：订阅和取消订阅成对出现
protected override void OnOpen(object userData)
{
    GF.Event.Subscribe(EventId, OnEvent);
}

protected override void OnClose(bool isShutdown, object userData)
{
    GF.Event.Unsubscribe(EventId, OnEvent);  // ✅ 取消订阅
}
```

---

## 🎨 编码规范检查

### 必须使用 GF API
- [ ] 使用 `GF.UI.OpenUIForm()` 打开 UI
- [ ] 使用 `GF.UI.CloseUIForm()` 或 `Close()` 关闭 UI
- [ ] 使用 `GF.Entity.ShowEntity()` 显示实体（如果 UI 包含 3D 内容）
- [ ] 使用 `GF.Resource.LoadAsset()` 加载资源
- [ ] 使用 `GF.Event.Subscribe/Unsubscribe()` 订阅/取消订阅事件
- [ ] 使用 `GF.DataTable.GetDataTable<>()` 获取数据表
- [ ] 使用 `GF.Config.GetString/Int/Bool()` 读取配置

### 禁止使用 Unity API
- [ ] ❌ 禁止使用 `Instantiate()` 创建 UI
- [ ] ❌ 禁止使用 `Destroy()` 销毁 UI
- [ ] ❌ 禁止使用 `GameObject.Find()` 查找对象
- [ ] ❌ 禁止使用 `Resources.Load()` 加载资源
- [ ] ❌ 禁止使用 `GameObject.Instantiate()` 创建游戏对象

### 数据驱动
- [ ] 使用 `UIFormData` 传递数据，无硬编码
- [ ] 从 `DataTable` 读取配置数据
- [ ] 从 `Config` 读取游戏设置
- [ ] 字符串使用多语言系统，不硬编码

### 引用池
- [ ] 使用 `ReferencePool.Acquire<>()` 获取对象
- [ ] 使用 `ReferencePool.Release<>()` 释放对象
- [ ] 事件参数使用引用池创建

---

## ⚡ 性能检查

- [ ] 不使用每帧更新（`Update`）除非必要
- [ ] 及时释放资源引用（设为 `null`）
- [ ] 动画使用 DOTween 或 Animator，避免代码逐帧修改
- [ ] 不在 `OnUpdate` 中做耗时操作
- [ ] 使用对象池复用对象，减少 GC

---

## 🔍 常见错误检查

- [ ] 没有使用 `Instantiate` 创建 UI
- [ ] 没有使用 `Destroy` 销毁 UI
- [ ] 没有使用 `GameObject.Find` 查找组件
- [ ] 没有使用 `Resources.Load` 加载资源
- [ ] 没有在 `OnLeave`/`OnClose` 中取消事件订阅
- [ ] 没有硬编码数据（字符串、数值）
- [ ] 没有每帧更新除非必要
- [ ] 没有在生命周期外访问对象

---

## 📝 使用示例

### 完整的 UI 代码检查流程

```bash
# 1. 创建 UI 后，对照此清单检查
# 2. 使用 lint 工具自动检查
python ui_linter.py Assets/AAAGame/Scripts/UI/Menu/ShopUIForm.cs

# 3. 修复发现的问题
# 4. 提交代码
```

### AI 生成代码时的自检提示

当 AI 生成 UI 代码时，提示词中应包含：

```
生成 UI 代码后，请自检以下项目：
✅ 1. 类继承自 UIFormBase（不是 UIFormLogic）
✅ 2. 类名以 UIForm 结尾，无 Logic 后缀
✅ 3. 在 OnClose 中取消所有事件订阅
✅ 4. 使用 GF.UI.Open/Close，不使用 Instantiate/Destroy
✅ 5. 数据通过 UIFormData 传递，无硬编码

如果任何一项不符合，请修改后再输出。
```

---

## 🎯 总结

此清单包含三个使用场景：

1. **人工检查**：开发完成后，逐项检查
2. **AI 自检**：在 AI 的 prompt 中包含关键检查项
3. **自动检查**：使用 lint 工具自动扫描代码

**核心原则**：
- 继承 `UIFormBase`，不是 `UIFormLogic`
- 命名 `XXXUIForm`，无 `Logic` 后缀
- 生命周期中成对出现：订阅/取消订阅
- 使用 GF API，不使用 Unity API
- 数据驱动，无硬编码

---

*最后更新：2024-02-23*
*版本：v1.0*
