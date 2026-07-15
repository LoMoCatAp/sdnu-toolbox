# 参与贡献

感谢关注 QLU 工具箱。提交问题或代码前，请先阅读 README 中的非官方声明、使用限制和隐私说明。

## 报告 Bug

请使用 [Bug 报告模板](https://github.com/C1ouDreamW/qlu-toolbox/issues/new/choose)，并尽量提供：

- QLU 工具箱版本；
- Windows 版本；
- 问题发生前执行的步骤；
- 预期结果和实际结果；
- 已经脱敏的错误信息或截图。

不要在公开 Issue 中提交账号、密码、验证码、Cookie、成绩文件、浏览器个人资料或包含个人信息的日志。涉及安全、隐私或个人信息的问题，请发送邮件至 `cloud_aaa@163.com`。

## 建议新功能

请说明使用场景、希望解决的问题、预期交互和可能影响的数据。新增工具应遵守本地优先、手动登录、最小权限和不收集账号信息的原则。

## 本地开发

需要 [Node.js](https://nodejs.org/) 和 [uv](https://docs.astral.sh/uv/)：

```powershell
npm ci
uv sync --locked
npm run dev
```

验证：

```powershell
uv run --locked python -B -m unittest discover -s tests -v
npm run typecheck
npm run build
```

修改 Python 依赖请使用 `uv add` 或 `uv remove`，修改前端依赖请使用 `npm install`，并一并提交更新后的锁文件。

提交代码时请保持改动范围清晰，并说明验证方式。未经维护者确认，请勿提交包含学校账号、成绩数据、Cookie、日志或其他个人信息的测试材料。
