# GF_X 模块参考：Config（配置系统）

> 本文档帮助 AI 理解并正确使用 GF_X 的配置系统。

---

## 1. 核心概念

### 1.1 什么是配置系统？

配置系统用于存储**全局游戏设置**和**常量数据**，以 **Key-Value** 形式管理：

```
Game.Name = "我的游戏"
Player.MaxLevel = 100
Game.StartGold = 5000
Feature.EnablePVP = true
```

### 1.2 配置 vs 数据表

| 特性 | 配置 (Config) | 数据表 (DataTable) |
|------|---------------|-------------------|
| **数据结构** | Key-Value 键值对 | 多行数据表 |
| **用途** | 全局设置、常量 | 物品、关卡、角色等数据 |
| **典型数据** | 游戏名称、版本号、开关 | 物品属性、怪物数值 |
| **Excel 格式** | 两列 (Key, Value) | 多列表格 |

### 1.3 配置来源

```
配置读取优先级 (从高到低):

1. 运行时动态设置 (代码中调用 SetXXX)
2. 本地配置文件 (Device.json, 用户设置)
3. 全局配置文件 (Global.json)
4. 默认配置 (Config 表中的默认值)
```

---

## 2. 基础使用

### 2.1 读取配置

```csharp
// ====== 读取字符串 ======
string gameName = GF.Config.GetString("Game.Name", "DefaultGame");
// 参数说明：key, defaultValue(可选，当key不存在时返回默认值)

// ====== 读取整数 ======
int maxLevel = GF.Config.GetInt("Player.MaxLevel", 100);
int startGold = GF.Config.GetInt("Game.StartGold", 0);

// ====== 读取浮点数 ======
float moveSpeed = GF.Config.GetFloat("Player.MoveSpeed", 5.0f);
float gravity = GF.Config.GetFloat("Physics.Gravity", 9.8f);

// ====== 读取布尔值 ======
bool enablePVP = GF.Config.GetBool("Feature.EnablePVP", false);
bool enableLog = GF.Config.GetBool("Debug.EnableLog", true);

// ====== 检查配置是否存在 ======
bool hasKey = GF.Config.HasKey("Game.Name");
```

### 2.2 设置配置（运行时）

```csharp
// ====== 设置字符串 ======
GF.Config.SetString("Game.Name", "MyGame");

// ====== 设置整数 ======
GF.Config.SetInt("Player.Level", 50);

// ====== 设置浮点数 ======
GF.Config.SetFloat("Player.HP", 85.5f);

// ====== 设置布尔值 ======
GF.Config.SetBool("Game.IsPaused", true);

// ====== 保存配置到本地 ======
GF.Config.Save();  // 将当前配置保存到本地文件

// ====== 删除配置 ======
GF.Config.RemoveKey("Temp.Value");
```

### 2.3 完整使用示例

```csharp
// ====== 游戏设置管理器 ======

public static class GameSettings
{
    // 游戏名称
    public static string GameName
    {
        get => GF.Config.GetString("Game.Name", "MyGame");
        set => GF.Config.SetString("Game.Name", value);
    }
    
    // 游戏版本
    public static string GameVersion
    {
        get => GF.Config.GetString("Game.Version", "1.0.0");
        set => GF.Config.SetString("Game.Version", value);
    }
    
    // 最大等级
    public static int MaxLevel
    {
        get => GF.Config.GetInt("Player.MaxLevel", 100);
        set => GF.Config.SetInt("Player.MaxLevel", value);
    }
    
    // 初始金币
    public static int StartGold
    {
        get => GF.Config.GetInt("Game.StartGold", 1000);
        set => GF.Config.SetInt("Game.StartGold", value);
    }
    
    // 音效开关
    public static bool SoundEnabled
    {
        get => GF.Config.GetBool("Setting.SoundEnabled", true);
        set 
        { 
            GF.Config.SetBool("Setting.SoundEnabled", value);
            GF.Config.Save();  // 用户设置立即保存
        }
    }
    
    // 音乐开关
    public static bool MusicEnabled
    {
        get => GF.Config.GetBool("Setting.MusicEnabled", true);
        set 
        { 
            GF.Config.SetBool("Setting.MusicEnabled", value);
            GF.Config.Save();
        }
    }
    
    // 振动开关
    public static bool VibrationEnabled
    {
        get => GF.Config.GetBool("Setting.VibrationEnabled", true);
        set 
        { 
            GF.Config.SetBool("Setting.VibrationEnabled", value);
            GF.Config.Save();
        }
    }
}
```

---

## 3. 配置文件格式

### 3.1 Excel 配置表格式

```
文件：AAAGameData/Configs/Global.xlsx

| Key                    | Value      | Description        |
|------------------------|------------|--------------------|
| Game.Name              | MyGame     | 游戏名称            |
| Game.Version           | 1.0.0      | 游戏版本            |
| Player.MaxLevel        | 100        | 最大等级            |
| Game.StartGold         | 5000       | 初始金币            |
| Feature.EnablePVP      | true       | 开启PVP            |
| Feature.EnableGuild    | false      | 开启公会            |
```

### 3.2 JSON 配置文件格式

```json
// 全局配置 (Global.json)
{
  "Game.Name": "MyGame",
  "Game.Version": "1.0.0",
  "Player.MaxLevel": 100,
  "Player.StartHP": 1000,
  "Game.StartGold": 5000,
  "Feature.EnablePVP": true,
  "Feature.EnableGuild": false,
  "Debug.EnableLog": false
}

// 用户设置 (Device.json) - 本地保存
{
  "Setting.SoundEnabled": true,
  "Setting.MusicEnabled": true,
  "Setting.VibrationEnabled": false,
  "Setting.Language": "zh-CN",
  "Setting.GraphicsQuality": "High"
}
```

---

## 4. 快速参考

### 4.1 常用方法速查

```csharp
// ====== 读取配置 ======
string strValue = GF.Config.GetString(key, defaultValue);
int intValue = GF.Config.GetInt(key, defaultValue);
float floatValue = GF.Config.GetFloat(key, defaultValue);
bool boolValue = GF.Config.GetBool(key, defaultValue);

// ====== 设置配置 ======
GF.Config.SetString(key, value);
GF.Config.SetInt(key, value);
GF.Config.SetFloat(key, value);
GF.Config.SetBool(key, value);

// ====== 其他操作 ======
bool exists = GF.Config.HasKey(key);
GF.Config.RemoveKey(key);
GF.Config.Save();  // 保存到本地
GF.Config.Load();  // 重新加载
```

---

> 💡 **AI 提示**: 使用配置系统时，遵循以下原则：
> 1. **全局常量** → 使用 Config (如：MaxLevel, StartGold)
> 2. **多行数据** → 使用 DataTable (如：物品列表、关卡数据)
> 3. **用户设置** → 使用 Config + Save() (如：音效开关、语言)
> 4. **运行时配置** → 使用 SetXXX 动态修改
