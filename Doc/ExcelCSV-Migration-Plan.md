# Excel/CSV 中间层迁移计划

> 将 AI 数据编辑从直接维护 .txt 升级为 CSV 中间层方案

## 背景

当前问题：
- AI 无法直接编辑 Excel 文件
- 让 AI 编辑 .txt 容易出错（格式问题）
- 需要人工介入 Excel 编辑

解决方案：引入 CSV 中间层
- AI 编辑 CSV（纯文本，AI 友好）
- 工具验证并转换为 Unity 数据
- 人工仍可使用 Excel（导出/导入 CSV）

## 实施步骤

### Phase 1: 准备（今天）

- [x] 创建 `/data/ExcelCSVAdapter/` 项目结构
- [x] 编写 README 和迁移计划文档
- [ ] 设计 CSV 格式规范
- [ ] 验证现有 Excel 导出 CSV 的可行性

**风险检查**：
- [ ] 确认现有导表工具是否支持 CSV 输入
- [ ] 测试中文编码（UTF-8 with BOM）
- [ ] 验证特殊字符（逗号、引号）处理

### Phase 2: 核心实现（明天）

- [ ] 实现 CSVValidator（验证 CSV 格式）
- [ ] 实现 ExcelConverter（双向转换）
- [ ] 实现 UnityDataBuilder（生成 Unity 数据）
- [ ] 实现 AIDataInterface（AI 友好接口）

**代码位置**：`/data/ExcelCSVAdapter/`

**核心模块**：
1. `csv_validator.py` - 验证 CSV 列数、编码、格式
2. `excel_converter.py` - CSV ↔ Excel 转换
3. `unity_builder.py` - 生成 .txt/.bytes
4. `ai_interface.py` - AI 操作接口

### Phase 3: 集成测试（后天）

- [ ] 编写单元测试
- [ ] 使用真实数据测试（Item.xlsx → CSV → Unity 数据）
- [ ] 验证数据一致性（Excel vs CSV vs Unity 数据）
- [ ] 性能测试（大批量数据）

**测试数据**：使用 `AAAGameData/Configs/Item.xlsx`

### Phase 4: 迁移上线（本周内）

- [ ] 更新现有导表工具配置
- [ ] 编写迁移脚本（Excel → CSV）
- [ ] 更新 CI/CD 流程
- [ ] 编写使用文档
- [ ] 培训团队成员

**交付物**：
1. 可运行的 `/data/ExcelCSVAdapter/` 工具
2. 更新后的 GF_X 文档
3. 迁移后的 CSV 数据文件
4. 使用手册

## 风险评估与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 中文编码问题 | 中 | 高 | 强制使用 UTF-8 with BOM |
| 特殊字符处理（逗号、引号） | 中 | 中 | 使用标准 CSV 库，充分测试 |
| 与现有工具不兼容 | 低 | 高 | 提前验证，准备回滚方案 |
| 数据格式不一致 | 中 | 高 | 严格的验证和测试 |
| AI 编辑 CSV 出错 | 中 | 中 | 验证工具 + 备份机制 |

## 回滚方案

如果迁移失败：
1. 保留原 Excel 文件不变
2. 保留原导表工具配置
3. 随时可以切回原有流程
4. CSV 文件作为备份保留

## 下一步行动

**今天**：
1. ✅ 确认此迁移计划
2. 设计 CSV 格式规范
3. 验证现有 Excel 导出 CSV 的可行性

**明天**：开始 Phase 2 核心实现

请确认此计划，或提出修改意见。
