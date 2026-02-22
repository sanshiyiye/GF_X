# GF_X Unity 项目框架 - 开发辅助文档

> 基于 GameFramework + HybridCLR 的热更新 Unity 游戏开发框架

---

## 📋 目录

1. [项目概述](#1-项目概述)
2. [技术栈与架构](#2-技术栈与架构)
3. [项目结构详解](#3-项目结构详解)
4. [核心模块说明](#4-核心模块说明)
5. [开发工作流](#5-开发工作流)
6. [工具使用指南](#6-工具使用指南)
7. [常见问题与最佳实践](#7-常见问题与最佳实践)

---

## 1. 项目概述

GF_X 是一个基于 **GameFramework** 和 **HybridCLR** 的 Unity 游戏开发框架，提供完整的热更新解决方案和丰富的游戏开发基础设施。

### 主要特性

| 特性 | 说明 |
|------|------|
| 🔥 **热更新** | 基于 HybridCLR 的 C# 热更新方案 |
| 🎮 **GameFramework** | 成熟的游戏框架，包含资源、UI、网络等模块 |
| 📦 **资源管理** | 支持 AssetBundle 和 Addressables |
| 🌐 **网络层** | 内置网络模块支持 |
| 🛠️ **工具链** | 丰富的开发辅助工具 |

---

## 2. 技术栈与架构

### 2.1 核心技术栈

```
Unity 2022.3.x LTS
├── HybridCLR (C# 热更新)
├── GameFramework (游戏框架)
├── UniTask (异步编程)
├── DOTween (动画库)
├── ZString (高性能字符串)
└── Protobuf (序列化)
```

### 2.2 架构图

```
┌─────────────────────────────────────────────────────────┐
│                    Unity 运行时                          │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   Builtin   │  │   Hotfix    │  │    AAAGame      │  │
│  │   Scripts   │  │    Dlls     │  │    Scripts      │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────┤
│              GameFramework 框架层                        │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────────┐ │
│  │ Resource│ │   UI    │ │ Network │ │   Procedure   │ │
│  │ Manager │ │ Manager │ │ Manager │ │   Manager     │ │
│  └─────────┘ └─────────┘ └─────────┘ └───────────────┘ │
├─────────────────────────────────────────────────────────┤
│              HybridCLR 热更新运行时                      │
├─────────────────────────────────────────────────────────┤
│              Unity IL2CPP 运行时                         │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 项目结构详解

### 3.1 根目录结构

```
GF_X/
├── AAAGameData/           # 游戏数据配置
│   ├── Configs/           # 游戏配置
│   ├── DataTables/        # 数据表格
│   └── Languages/         # 多语言文件
├── AB/                    # AssetBundle 输出目录
├── Assets/                # Unity 主资源目录
│   ├── AAAGame/           # 游戏业务代码和资源
│   ├── GameFramework/     # 框架核心代码
│   ├── HybridCLRData/     # HybridCLR 数据
│   ├── Plugins/           # 插件目录
│   └── Resources/         # Unity Resources
├── CompressImageTool/     # 图片压缩工具
├── Packages/              # Unity Packages
├── ProjectSettings/       # Unity 项目设置
├── Tools/                 # 开发工具集合
└── UserSettings/          # 用户设置
```

### 3.2 Assets 详细结构

#### AAAGame/ (游戏业务)
```
AAAGame/
├── Animation/           # 动画文件
├── Audio/               # 音频资源
├── Config/              # 运行时配置
├── DataTable/           # 数据表资源
├── Font/                # 字体文件
├── HotfixDlls/          # 热更新 DLL
├── Language/            # 本地化资源
├── Materials/           # 材质
├── Models/              # 3D 模型
├── Prefabs/             # 预制体
├── Scene/               # 场景文件
├── ScriptableAssets/    # ScriptableObject
├── Scripts/             # 游戏脚本
├── ScriptsBuiltin/      # 内置脚本
├── Shader/              # 着色器
├── SharedMaterials/     # 共享材质
├── Sprites/             # 精灵图
└── Textures/            # 贴图
```

#### Plugins/ (插件)
```
Plugins/
├── Android/             # Android 原生插件
├── DOTween/             # 动画库
├── Protobuf/            # 序列化库
├── UniTask/             # 异步库
├── ZString/             # 高性能字符串
├── UnityGameFramework/  # 框架运行时代码
└── ForEditor/           # 编辑器插件
```

---

## 4. 核心模块说明

### 4.1 GameFramework 模块

| 模块 | 描述 | 用途 |
|------|------|------|
| **Resource** | 资源管理 | AssetBundle 加载、资源缓存、依赖管理 |
| **UI** | UI 管理 | 界面管理、层级控制、窗口管理 |
| **Network** | 网络通信 | TCP/UDP 连接、消息协议、心跳机制 |
| **Procedure** | 流程管理 | 游戏状态机、场景流程控制 |
| **Event** | 事件系统 | 全局事件分发、订阅发布 |
| **Sound** | 音频管理 | 音效、背景音乐控制 |
| **Scene** | 场景管理 | 场景加载、异步切换 |
| **WebRequest** | HTTP 请求 | REST API 通信 |
| **ObjectPool** | 对象池 | 缓存复用优化 |

### 4.2 HybridCLR 热更新系统

```
HybridCLR Data/
├── Generated/           # 自动生成的桥接代码
│   ├── AOTMonos/      # AOT 通用代码
│   └── MethodBridge/  # 方法桥接
└── HotUpdateDlls/     # 热更新 DLL 输出

Assets/AAAGame/HotfixDlls/
└── Game.Hotfix.dll    # 热更新程序集
```

### 4.3 关键程序集

| 程序集 | 类型 | 说明 |
|--------|------|------|
| Assembly-CSharp | Runtime | 游戏运行时代码 |
| Assembly-CSharp-Editor | Editor | 编辑器扩展代码 |
| GameFramework | Runtime | 框架核心代码 |
| UnityGameFramework.Runtime | Runtime | Unity 适配层 |
| UnityGameFramework.Editor | Editor | Unity 编辑器扩展 |
| Hotfix | Runtime | 热更新代码 |

---

## 5. 开发工作流

### 5.1 项目启动流程

```
┌─────────┐    ┌─────────────┐    ┌──────────────────┐
│ Unity   │ -> │ 编译 Builtin │ -> │ 生成 HybridCLR   │
│ 打开    │    │ 代码        │    │ AOT              │
└─────────┘    └─────────────┘    └──────────────────┘
                                         │
    ┌─────────────┐    ┌─────────┐      │
    │  运行测试   │ <- │ AB 打包 │ <────┘
    └─────────────┘    └─────────┘
```

### 5.2 代码编写规范

#### 目录分工

| 目录 | 用途 | 更新方式 |
|------|------|----------|
| `ScriptsBuiltin/` | 核心框架代码，不热更新 | 随包发布 |
| `Scripts/` | 业务逻辑代码，可热更新 | 热更新替换 |

#### 命名规范

```csharp
// 类名 - 大驼峰
public class GameManager : MonoBehaviour { }

// 接口 - I 前缀
public interface IGameModule { }

// 枚举 - E 前缀
public enum EGameState { Loading, Playing, Pause }

// 常量 - 全大写下划线
public const int MAX_PLAYER_COUNT = 100;

// 私有字段 - 小驼峰下划线前缀
private int _playerLevel;

// 公有属性 - 大驼峰
public int PlayerLevel { get; set; }
```

### 5.3 资源管理流程

#### AssetBundle 命名规则

```
ab_scene_{场景名}        # 场景资源
ab_ui_{界面名}           # UI 预制体
ab_model_{模型名}        # 3D 模型
ab_audio_{分类}_{文件名} # 音频资源
ab_config_{配置名}       # 配置文件
```

#### 资源打包命令

```bash
# Unity 命令行打包 AB
/Applications/Unity/Unity.app/Contents/MacOS/Unity \
    -quit \
    -batchmode \
    -projectPath /data/GF_X \
    -executeMethod GameFramework.Editor.AssetBundleBuilder.Build
```

---

## 6. 工具使用指南

### 6.1 工具总览

```
Tools/
├── CompressImageTools/       # 图片压缩工具
├── FontMinify/               # 字体精简工具
├── Jenkins/                  # 自动化构建
├── LocalizationStringScanner/ # 本地化扫描
└── PSD2UGUI/                 # PSD 转 UI 工具
```

### 6.2 图片压缩工具

**用途：** 批量压缩项目中的纹理图片，减少包体大小。

**使用方法：**

```bash
cd /data/GF_X/CompressImageTool
# 配置压缩参数
# 运行压缩脚本
```

**支持的格式：**
- PNG (使用 pngquant)
- JPEG
- TGA

### 6.3 字体精简工具

**用途：** 从完整字体文件中提取项目实际使用的字符，减小字体文件大小。

**工作流程：**
1. 扫描项目中所有文本资源
2. 收集使用的字符集合
3. 从源字体提取子集
4. 生成精简后的字体文件

### 6.4 Jenkins 自动化构建

**配置路径：** `Tools/Jenkins/jobs/`

**支持的构建任务：**
- 每日构建 (Daily Build)
- 版本发布构建 (Release Build)
- 资源打包 (Asset Bundle Build)
- 热更新包生成 (Hotfix Build)

### 6.5 本地化字符串扫描

**用途：** 自动扫描代码中的硬编码中文文本，协助国际化工作。

**扫描范围：**
- C# 脚本中的字符串字面量
- 预制体中的文本组件
- 配置文件中的描述文本

### 6.6 PSD2UGUI 工具

**用途：** 将 Photoshop 设计稿自动转换为 Unity UI 预制体。

**支持的功能：**
- 图层转 UI 组件
- 自动切图和命名
- 保留图层样式
- 生成对应的 UI 脚本

---

## 7. 常见问题与最佳实践

### 7.1 热更新相关问题

**Q: 哪些代码需要放在热更新程序集？**

A: 频繁变更的业务逻辑代码，如：
- UI 控制逻辑
- 游戏玩法逻辑
- 任务/活动系统
- 配置表解析

**Q: 哪些代码不能热更新？**

A: 基础框架代码，如：
- MonoBehaviour 生命周期相关
- 序列化类定义
- 网络协议基础结构
- 第三方插件的 C# 封装

**Q: 热更新后如何回滚？**

A: 框架会自动维护版本历史，可以通过清除热更新缓存或强制更新到指定版本来回滚。

### 7.2 资源管理最佳实践

**1. AssetBundle 粒度控制**

```
✅ 推荐粒度：
- 一个 UI 界面 = 一个 AB
- 一个角色 = 一个 AB
- 共享资源 = 独立 AB

❌ 避免：
- 单个文件过大 (>50MB)
- 大量小文件 (<10KB)
```

**2. 依赖管理**

```csharp
// 使用框架提供的资源加载接口
// 自动处理依赖关系
GameEntry.Resource.LoadAsset<GameObject>(assetName, (asset, duration) => {
    // 加载完成回调
});
```

**3. 内存管理**

```csharp
// 及时释放不再使用的资源
GameEntry.Resource.UnloadAsset(asset);
// 或统一调用垃圾回收
GameEntry.Resource.ForceUnloadUnusedAssets(true);
```

### 7.3 性能优化建议

**1. UI 优化**

```
✅ UI 层级优化：
- 使用静态批处理
- 减少 Overdraw
- 合并材质
- 使用对象池复用 UI 元素
```

**2. 代码优化**

```csharp
// 使用 UniTask 替代协程
async UniTask LoadDataAsync()
{
    await GameEntry.Resource.LoadAssetAsync<T>(assetName);
}

// 使用 ZString 替代字符串拼接
using var sb = ZString.CreateStringBuilder();
sb.Append("Hello ").Append(name);
```

**3. 资源优化**

```
✅ 纹理优化：
- 使用压缩格式 (ASTC/ETC2/BC7)
- 启用 Mipmap
- 控制纹理尺寸

✅ 音频优化：
- 根据使用场景选择格式 (Vorbis/ADPCM)
- 启用 Force To Mono
- 使用 Streaming 模式加载长音频
```

### 7.4 调试技巧

**1. 日志系统**

```csharp
// 使用框架的日志接口
GameEntry.Log.Info("普通信息");
GameEntry.Log.Warning("警告信息");
GameEntry.Log.Error("错误信息");
GameEntry.Log.Debug("调试信息"); // Debug 模式才输出
```

**2. 调试工具**

```
项目内置调试工具：
- 运行时日志查看器
- 资源加载监控
- 内存使用统计
- 性能分析器
```

**3. 常用