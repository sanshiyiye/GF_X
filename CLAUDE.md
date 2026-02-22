# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GF_X is a comprehensive Unity game development framework built on top of **GameFramework** and **HybridCLR** that provides a complete C# hot-update solution and extensive game development infrastructure. It's designed for industrial-grade workflows with a focus on extreme performance and development efficiency.

**Key Technologies:**
- Unity 2022.x LTS (supports up to Unity 6000)
- HybridCLR for C# hot updates
- GameFramework for game infrastructure
- UniTask for zero-allocation async/await
- ZString for zero-allocation string operations
- DOTween for animations

## Project Structure

```
GF_X/
├── AAAGameData/              # External game data sources (Excel files)
│   ├── Configs/             # Configuration tables (Excel)
│   ├── DataTables/          # Data tables (Excel)
│   └── Languages/           # Multi-language tables (Excel)
├── Assets/                   # Unity main resources and code
│   ├── AAAGame/             # Game development directory
│   │   ├── Scripts/         # Hot update scripts (Hotfix assembly)
│   │   ├── ScriptsBuiltin/  # Built-in assembly (not hot-updateable)
│   │   ├── Scene/           # Game scenes (Launch is entry point)
│   │   ├── Prefabs/         # UI and Entity prefabs
│   │   ├── DataTable/       # Generated data table resources
│   │   ├── Config/          # Generated config resources
│   │   ├── Language/        # Generated multi-language resources
│   │   └── HotfixDlls/      # Hot update DLL output/reference
│   ├── HybridCLRData/       # HybridCLR hot update related data
│   ├── Plugins/             # Third-party and framework plugins
│   └── Resources/           # Unity Resources folder (AppSettings, configs)
├── Tools/                    # Editor and batch processing tools
│   ├── CompressImageTools/  # Image compression tools
│   ├── FontMinify/          # Font minification tool
│   ├── Jenkins/             # Jenkins automation build scripts
│   ├── LocalizationStringScanner/ # Multi-language string scanner
│   └── PSD2UGUI/            # PSD to UGUI converter
└── AB/                       # AssetBundle output directory
```

## Development Workflow

### Game Launch Flow

1. **LaunchProcedure** (Builtin) - Initialize settings, detect resource mode
2. **UpdateResourcesProcedure** (Builtin) - Check/Update resources, AssetBundle management
3. **LoadHotfixDllProcedure** (Builtin) - Load hot fix DLLs, AOT metadata
4. **HotfixEntry.StartHotfixLogic** - Enter hot update code, create hotfix procedure state machine
5. **PreloadProcedure** (Hotfix) - Preload game data, configs, data tables, language
6. **ChangeSceneProcedure** (Hotfix) - Switch scene
7. **MenuProcedure** (Hotfix) - Main menu
8. **GameProcedure** (Hotfix) - Gameplay
9. **GameOverProcedure** (Hotfix) - Game end

### Key Entry Points

- **Builtin Entry:** `Assets/AAAGame/ScriptsBuiltin/Runtime/Procedures/LaunchProcedure.cs`
- **Hotfix Entry:** `Assets/AAAGame/Scripts/HotfixEntry.cs`

### Code Locations

- **Hot Update Scripts:** `Assets/AAAGame/Scripts/` - Compiled to Hotfix.dll (can be hot updated)
- **Built-in Scripts:** `Assets/AAAGame/ScriptsBuiltin/` - Not hot-updateable
- **Entry Scene:** `Assets/AAAGame/Scene/Launch`

## Data Management System

### Configuration Tables (Config)
- **Source:** `AAAGameData/Configs/` (Excel files)
- **Generation:** GameDataGenerator.RefreshAllConfig
- **Output:** `Assets/AAAGame/Config/` (txt + bytes)
- **Access:** `GF.Config.GetString(key)`

### Data Tables (DataTable)
- **Source:** `AAAGameData/DataTables/` (Excel files)
- **Generation:** DataTableGenerator.GenerateCodeFile
- **Output:** `Assets/AAAGame/DataTable/` (txt + bytes) and `Scripts/DataTable/` (C# classes)
- **Access:** `GF.DataTable.GetDataTable<T>()`

### Multi-language Support (Language)
- **Source:** `AAAGameData/Languages/` (Excel files per language)
- **Generation:** GameDataGenerator.RefreshAllLanguage
- **Output:** `Assets/AAAGame/Language/` (JSON files)
- **Languages:** Chinese (Simplified/Traditional), English, Japanese, Korean
- **Runtime Change:** `GF.Localization.LoadLanguage()`

### A/B Testing
- **Naming Convention:** `[MainTable]#[TestGroup].xlsx` (e.g., `GameConfig#GroupA.xlsx`)
- **Code API:** `GF.Setting.SetABTestGroup("GroupName")`

## Build & Development Commands

### Initial Setup
1. Install HybridCLR: Unity top menu → **HybridCLR->Installer**
2. Open Build window: Unity toolbar → **Build App/Hotfix** button
3. First build: Click dropdown → **Full Build**

### Build Commands (Unity Editor)
- **Build App:** Produce installable package
- **Build Resource:** Generate hot update package

### Jenkins Automation
Location: `Tools/Jenkins/`
- Build App, Build Resource, hot update scripts available

## Core Framework APIs

### UI Management
```csharp
GF.UI.OpenUIForm(uiFormId);      // Open UI form
GF.UI.CloseUIForm(uiForm);        // Close UI form
```

### Entity Management
```csharp
GF.Entity.ShowEntity(entityId);   // Show entity (auto object pool)
GF.Entity.HideEntity(entity);     // Hide entity
```

### Procedure Management
```csharp
procedure.ChangeState<NextProcedure>();  // Switch to another procedure
```

## Key Files

- `Assets/AAAGame/Scripts/HotfixEntry.cs` - Hotfix entry point
- `Assets/AAAGame/Scripts/Extension/GF.cs` - Main framework interface
- `Assets/AAAGame/ScriptsBuiltin/Editor/GameDataGenerator.cs` - Data generation
- `Assets/AAAGame/ScriptsBuiltin/Editor/EditorTools/AppBuildEditor.cs` - Build window
- `Assets/Resources/AppSettings.asset` - Global config (ScriptableObject)

## Documentation

- **README.md** - Project overview and basic usage
- **GF_X开发辅助文档.md** - Comprehensive development guide
- **项目目录结构.md** - Detailed directory structure
- **AAAGameData-Excel使用说明.md** - Excel data table guide
- **DeepWiki:** https://deepwiki.com/sunsvip/GF_X
- **Video Tutorials:** Bilibili video series (Chinese)
