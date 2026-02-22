# CompressImageTools 图片压缩（优化）工具

<!-- markdownlint-disable MD060 -->

对应目录：**Tools/CompressImageTools**。提供 pngquant（Win/Mac）离线压缩及 TinyPNG 在线压缩，与 Unity 编辑器「资源/压缩(优化)工具」配合，用于批量压缩图片、压缩贴图、创建图集、图集变体、压缩动画等，减小包体。

---

## 使用方式

1. **入口**：Unity 顶部工具栏打开 **「资源/压缩(优化)工具」**，在左侧选择子功能：
   - **图片文件压缩**：对 jpg/png 原文件压缩，支持拖拽文件夹或图片添加列表；可先「备份图片」再「开始压缩」；不勾选「覆盖原图片」时结果输出到配置的输出目录。
   - **压缩贴图**：对 Unity 工程内贴图资源按平台压缩。
   - **创建图集**：将多张图打成 Sprite Atlas。
   - **创建图集变体**：基于已有图集生成缩放变体。
   - **压缩动画**：压缩动画片段。

2. **配置**：在 **ProjectSettings/EditorToolSettings** 中可配置（部分在面板内也可改）：
   - 备份路径（默认 `CompressImageTool\ImgBackupDir`）、输出路径（默认 `CompressImageTool\ImgCompressedDir`）。
   - 离线/在线、压缩质量、是否覆盖原图等。
   - TinyPNG Key（在线压缩时使用）。

3. **图片文件压缩流程**：添加待压缩图片 → 可选「备份图片」到备份目录 → 点击「开始压缩」；离线时使用 **Tools/CompressImageTools/pngquant_win** 或 **pngquant_mac** 下的 pngquant，输出到输出目录或覆盖原文件。

---

## 运行流程图

```mermaid
flowchart LR
    Input[待压缩图片或贴图列表]
    Panel[压缩工具面板选择子功能]
    Backup[可选备份到 ImgBackupDir]
    Compress[压缩执行 pngquant或TinyPNG]
    Output[输出到 ImgCompressedDir或覆盖原图]
    Input --> Panel
    Panel --> Backup
    Backup --> Compress
    Compress --> Output
```

---

## 输入

| 输入项 | 说明 | 必填/默认 |
|--------|------|-----------|
| 待处理资源 | 图片文件压缩：拖入的 jpg/png 或文件夹；压缩贴图/图集：在面板中选择的 Unity 贴图或图集 | 必填 |
| 备份路径 | EditorToolSettings.CompressImgToolBackupDir，如 `CompressImageTool\ImgBackupDir` | 备份时必填 |
| 输出路径 | EditorToolSettings.CompressImgToolOutputDir，不覆盖原图时使用 | 不覆盖原图时必填 |
| TinyPNG Key | 在线压缩时使用，在面板中配置 | 在线模式必填 |

---

## 产出内容的来源与后续使用

- **来源**：压缩结果由「开始压缩」触发生成。离线 PNG 压缩由 pngquant 输出；若未勾选「覆盖原图片」，则写入 **CompressImageTool/ImgCompressedDir**（或 EditorToolSettings 中配置的输出路径）；若勾选覆盖，则直接覆盖工程内原图。备份文件来自「备份图片」，写入 **CompressImageTool/ImgBackupDir** 下按时间戳命名的子目录。
- **后续使用**：
  - **不覆盖原图**：压缩后的图片在输出目录中，可手动替换回 Assets 中对应位置，或作为资源包外置使用。
  - **覆盖原图**：工程内贴图体积减小，打包时直接使用当前资源，无需额外步骤。
- **举例**：对 `Assets/AAAGame/Sprites/UI` 下 10 张 PNG 先「备份图片」到 `CompressImageTool/ImgBackupDir/2025-02-18-143000`，再勾选「覆盖原图片」并「开始压缩」，则原路径下 10 张图被压缩后体积下降，运行时 UI 仍引用同一路径；若需回滚，可用「还原备份」选择该时间戳目录还原。

---

更多目录说明见 [项目目录结构](../项目目录结构.md)。
