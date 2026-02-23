# GF_X UI Linter Skill

> 自动检查 UI 代码是否符合 GF_X 框架规范

## 功能

- ✅ 继承检查：确保继承 UIFormBase
- ✅ 命名规范：类名以 UIForm 结尾
- ✅ 生命周期：检查事件订阅取消
- ✅ API 使用：禁止使用 Instantiate/Destroy
- ✅ 数据驱动：检查硬编码数据

## 安装

```bash
# 确保虚拟环境已激活
cd /data/GF_X
source venv/bin/activate

# Skill 已包含在项目内，无需额外安装
```

## 使用

### 检查单个文件

```bash
# 使用 Python 直接运行
./venv/bin/python .openclaw/skills/ui-linter/skill.py \
  Assets/AAAGame/Scripts/UI/Menu/ShopUIForm.cs
```

### 检查整个目录

```bash
# 递归检查所有 UI 文件
./venv/bin/python .openclaw/skills/ui-linter/skill.py \
  Assets/AAAGame/Scripts/UI/ \
  --recursive
```

### JSON 输出（用于自动化）

```bash
./venv/bin/python .openclaw/skills/ui-linter/skill.py \
  Assets/AAAGame/Scripts/UI/Menu/ShopUIForm.cs \
  --format json \
  --output result.json
```

## OpenClaw Skill 调用

```yaml
skill: gf-x-ui-linter
action: lint_file
parameters:
  file_path: "Assets/AAAGame/Scripts/UI/Menu/ShopUIForm.cs"
```

## 规则说明

| 规则 | 严重级别 | 说明 |
|------|----------|------|
| `inheritance` | Error | 必须继承 UIFormBase |
| `naming` | Error | 类名以 UIForm 结尾，无 Logic 后缀 |
| `lifecycle` | Warning | 事件订阅必须在 OnClose 中取消 |
| `api_usage` | Error | 必须使用 GF.UI，禁止 Instantiate/Destroy |
| `data_driven` | Warning | 必须使用 UIFormData，禁止硬编码 |

## 集成到 CI/CD

```yaml
# .github/workflows/ui-lint.yml
name: UI Lint Check

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      
      - name: Run UI Linter
        run: |
          python .openclaw/skills/ui-linter/skill.py \
            Assets/AAAGame/Scripts/UI/ \
            --recursive \
            --format json \
            --output ui-lint-result.json
      
      - name: Check Results
        run: |
          if grep -q '"error_count": 0' ui-lint-result.json; then
            echo "✅ 所有检查通过"
            exit 0
          else
            echo "❌ 发现错误"
            cat ui-lint-result.json
            exit 1
          fi
```

## 贡献

欢迎提交 Issue 和 PR！

## 许可证

MIT License - 与 GF_X 项目一致
