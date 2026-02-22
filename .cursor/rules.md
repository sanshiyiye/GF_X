# Cursor Rules for GF_X Development

> This file provides guidance to Cursor AI when working with the GF_X Unity game development framework.

---

## 🚨 Critical Rules (MUST FOLLOW)

### ❌ Absolutely Forbidden

| Operation | Wrong Way | Why |
|-----------|-----------|-----|
| **Resource Loading** | `Resources.Load<T>("path")` | Cannot hot update |
| **GameObject Creation** | `Instantiate(prefab)` | Bypasses object pool |
| **GameObject Destruction** | `Destroy(gameObject)` | Object pool breaks |
| **Finding Objects** | `GameObject.Find("Name")` | Slow and fragile |
| **Hard-coded Data** | `int damage = 100;` | Not configurable |
| **Unity UI Instantiation** | `new GameObject("UI")` | No lifecycle management |

### ✅ Always Use

| Operation | Correct Way | Module |
|-----------|-------------|--------|
| **Load Asset** | `GF.Resource.LoadAsset<T>(assetName, callback)` | Resource |
| **Show Entity** | `GF.Entity.ShowEntity(typeof(XXXEntity), data)` | Entity |
| **Hide Entity** | `GF.Entity.HideEntity(entityLogic)` | Entity |
| **Open UI** | `GF.UI.OpenUIForm(UIFormId.XXX, data)` | UI |
| **Close UI** | `GF.UI.CloseUIForm(uiForm)` / `Close()` | UI |
| **Read Data** | `GF.DataTable.GetDataTable<DRXXX>().GetDataRow(id)` | DataTable |
| **Read Config** | `GF.Config.GetString("Key", default)` | Config |
| **Subscribe Event** | `GF.Event.Subscribe(EventId, Handler)` | Event |
| **Unsubscribe Event** | `GF.Event.Unsubscribe(EventId, Handler)` | Event |

---

## 📂 File Organization

### Hot-Update Code (Scripts/)

```
Assets/AAAGame/Scripts/
├── Procedure/              # Procedures (hot-update)
│   ├── Game/
│   ├── Menu/
│   └── System/
├── UI/                     # UI Logic (hot-update)
│   ├── Menu/
│   ├── Game/
│   └── Common/
├── Entity/                 # Entity Logic (hot-update)
│   ├── Player/
│   ├── Enemy/
│   └── Effect/
├── DataTable/              # Data Table Row Definitions (hot-update)
├── Network/                # Network Protocols (hot-update)
└── Extension/              # GF Extensions (hot-update)
    ├── GF.cs
    ├── GF.UI.cs
    ├── GF.Entity.cs
    └── ...
```

### Built-in Code (Cannot Hot-Update)

```
Assets/AAAGame/ScriptsBuiltin/
└── Runtime/
    └── Procedures/         # Boot Procedures (NOT hot-updateable)
        ├── LaunchProcedure.cs
        ├── CheckResourcesProcedure.cs
        └── LoadHotfixDllProcedure.cs
```

### Prefab Assets

```
Assets/AAAGame/Prefabs/
├── UI/                     # UI Prefabs
│   ├── MainMenu.prefab
│   └── Setting.prefab
├── Entity/                 # Entity Prefabs
│   ├── Player.prefab
│   └── Enemy.prefab
└── Effect/                 # Effect Prefabs
    └── Explosion.prefab
```

---

## 🏷️ Naming Conventions

### Classes

| Type | Rule | Example |
|------|------|---------|
| Regular Class | PascalCase | `GameManager`, `PlayerController` |
| Procedure Class | PascalCase + Procedure | `MenuProcedure`, `GameProcedure` |
| UI Class | PascalCase + UIFormLogic | `MainMenuUIFormLogic` |
| Entity Class | PascalCase + EntityLogic | `PlayerEntityLogic` |
| Data Row Class | DR + PascalCase | `DRItem`, `DRLevel` |
| Interface | I + PascalCase | `IManager`, `IPlayer` |
| Enum | E + PascalCase | `EGameState`, `EItemType` |

### Members

| Type | Rule | Example |
|------|------|---------|
| Public Property | PascalCase | `public int PlayerLevel { get; set; }` |
| Constant | UPPER_SNAKE_CASE | `public const int MAX_COUNT = 100;` |
| Static Readonly | UPPER_SNAKE_CASE | `public static readonly int MAX_SIZE = 1024;` |
| Private Field | _camelCase | `private int _playerLevel;` |
| Serialized Field | _camelCase | `[SerializeField] private Button _confirmButton;` |

### ID Definitions

```csharp
// UIFormId.cs
public static class UIFormId
{
    public const int MainMenu = 1001;
    public const int Setting = 1002;
    public const int GameHud = 1003;
}

// EntityId.cs
public static class EntityId
{
    public const int Player = 10001;
    public const int EnemySlime = 10011;
    public const int EnemyBoss = 10012;
}

// SoundId.cs
public static class SoundId
{
    public const int BgmMenu = 1;
    public const int BgmGame = 2;
    public const int SfxClick = 1001;
}
```

---

## 🔍 Quick Reference

### GF Module Access

```csharp
GF.UI           // UI Management
GF.Entity       // Entity Management
GF.Procedure    // Procedure Management (read-only)
GF.DataTable    // Data Table Management
GF.Config       // Config Management
GF.Resource     // Resource Management
GF.Sound        // Audio Management
GF.Network      // Network Management
GF.Scene        // Scene Management
GF.Setting      // Local Storage
GF.WebRequest   // HTTP Requests
GF.Event        // Event System
GF.ObjectPool   // Object Pool
GF.Fsm          // State Machine (advanced)
```

### Common Lifecycle Order

```
Procedure:
  OnInit() → OnEnter() → [OnUpdate() × N] → OnLeave() → [OnDestroy()]

UIFormLogic:
  OnInit() → OnOpen() → [OnUpdate() × N] → OnClose()

EntityLogic:
  OnInit() → OnShow() → [OnUpdate() × N] → OnHide()
```

### Resource Path Format

```
Assets/AAAGame/{Type}/{Path}/{FileName}.{Ext}

Types:
├── Prefabs/        # Prefabs (UI, Entity, Effects)
├── Scene/          # Scene files
├── Audio/          # Audio files
├── DataTable/      # Data table resources (.txt/.bytes)
├── Config/         # Config files
├── Language/       # Localization resources
├── Animation/      # Animation files
├── Materials/      # Material files
├── Models/         # Model files
├── Sprites/        # Sprite files
└── Textures/       # Texture files
```

---

## 📚 Full Documentation Index

| Document | Content | When to Read |
|----------|---------|--------------|
| `.cursor/rules.md` | This file - Quick rules reference | Daily use |
| `Doc/AI-Reference/README.md` | Documentation overview | First time |
| `Doc/AI-Reference/AI-Framework-Overview.md` | Framework overview | First time |
| `Doc/AI-Reference/Modules/01-Procedure.md` | Procedure system | Creating procedures |
| `Doc/AI-Reference/Modules/02-UI.md` | UI system | Creating UI |
| `Doc/AI-Reference/Modules/03-Entity.md` | Entity system | Creating entities |
| `Doc/AI-Reference/Modules/04-DataTable.md` | Data table system | Using data |
| `Doc/AI-Reference/Modules/05-Config.md` | Config system | Reading config |
| `Doc/AI-Reference/Modules/06-Resource.md` | Resource system | Loading assets |
| `Doc/AI-Reference/Templates/*.md` | Code templates | Creating new files |
| `Doc/AI-Reference/AI-Coding-Patterns.md` | Coding patterns | Best practices |
| `Doc/AI-Reference/AI-Common-Mistakes.md` | Common mistakes | Avoiding errors |

---

## ⚡ Quick Checklist

Before submitting code, confirm:

- [ ] Using GF.XXX instead of Unity API
- [ ] Reading data from DataTable/Config, no hard-coding
- [ ] Using async loading, not blocking
- [ ] Subscribing and unsubscribing events in lifecycle methods
- [ ] Releasing resources properly
- [ ] Following naming conventions
- [ ] Code in correct directory (Scripts/ vs ScriptsBuiltin/)

---

## 🐛 Common Issues & Solutions

### Issue: "Cannot find GF class"
**Solution**: Check you're using `GF.` namespace, not direct Unity API

### Issue: "UI doesn't show up"
**Solution**: Use `GF.UI.OpenUIForm()` not `Instantiate()`

### Issue: "Entity not spawning"
**Solution**: Use `GF.Entity.ShowEntity()` not `Instantiate()`

### Issue: "Memory leak warnings"
**Solution**: Check you're unsubscribing events in `OnLeave()`/`OnClose()`

### Issue: "Cannot hot update"
**Solution**: Check code is in `Scripts/` not `ScriptsBuiltin/`

---

**Remember**: When in doubt, check `Doc/AI-Reference/` for detailed documentation!

**Core Mantra**:
- **Use GF, not Unity** - Framework first
- **Read data, don't hardcode** - Data-driven  
- **Go async, don't block** - Performance
- **Remember cleanup, don't leak** - Lifecycle
