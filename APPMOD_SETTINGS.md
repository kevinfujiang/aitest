说明：已在工作区创建一个建议的 VS Code 设置文件 `./.vscode/settings.json`，用于为 `appmod` 系列工具提供默认参数，避免模型输出占位符 JSON 调用。

包含的示例键（可能需要根据你安装的扩展/插件调整键名）：

- `appmod.defaultWorkspacePath`：工作区路径，示例 `/Users/xuxiaorong/Code/demo/ai/test1`
- `appmod.defaultSessionId`：会话 ID，示例 `session-20260210-01`
- `appmod.defaultLanguage`：目标语言，示例 `python` 或 `java`
- `appmod.kbIds`：知识库 ID 列表
- `appmod.autoInvokeTools`：是否允许模型在参数不完整时自动调用工具（`false` 可禁止）

如何使用：

1. 打开 VS Code，按 `Cmd+Shift+P`，运行 `Preferences: Open Settings (JSON)`。
2. 如果你知道所用扩展的真实设置键名（例如扩展名中包含 `appmod` 或 `migration`），把上面对应值移动到该扩展的配置项下（替换键名）。
3. 如果不确定键名：打开左侧扩展栏 → 找到相关扩展 → 查看“设置”页，找到用于指定 `workspacePath` / `sessionId` / `language` 的设置项并填入相应值。

我可以继续：
- 直接把这些键替换为你安装的扩展的真实设置名（请告诉我扩展 ID 或截图设置页）。
- 或在你允许的情况下，帮你在 `settings.json` 中写入扩展的真实键名。
