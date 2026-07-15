<p align="center">
  <img src="assets/qlu-toolbox.png" width="128" alt="QLU 工具箱 Logo">
</p>

# QLU 工具箱

<p align="center">
  <img src="https://img.shields.io/badge/Vue-3.5-42B883?logo=vuedotjs&logoColor=white" alt="Vue 3">
  <img src="https://img.shields.io/badge/Electron-37-47848F?logo=electron&logoColor=white" alt="Electron">
  <img src="https://img.shields.io/badge/TypeScript-5.8-3178C6?logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Playwright-1.55-2EAD33?logo=playwright&logoColor=white" alt="Playwright">
  <img src="https://img.shields.io/badge/Vite-7-646CFF?logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/license-non--commercial-red" alt="license">
</p>

QLU 工具箱是一款面向齐鲁工业大学学生的本地校园效率桌面软件。v1.0.1 使用 Vue 3、TypeScript 与 Electron 提供全新桌面界面，Python 与 Playwright 负责可靠的本地自动化。首个内置工具是“分项成绩导出”，后续工具将通过统一模块规范逐步加入。

分项成绩导出会打开本机 Edge、Chrome 或兼容 Chromium。用户在浏览器中手动登录教务系统后，工具自动查询指定学期，并将经过校验的分项成绩保存为 Excel 文件。

工具箱不会要求用户在客户端填写或复制账号、密码、验证码、Cookie，也不会把成绩发送到开发者服务器。

浏览器登录状态、任务记录和设置默认保存在当前 Windows 用户的本地应用数据目录中，**程序完全本地运行**。

## 使用

1. 前往 [Releases](https://github.com/C1ouDreamW/qlu-toolbox/releases) 下载最新版本 `QLUToolbox_v*.zip`
2. 若无法访问 GitHub，可从蓝奏云下载：[wwavy.lanzouq.com/b00b5q2orc](https://wwavy.lanzouq.com/b00b5q2orc)（密码 `d7os`）
3. 解压到任意目录
4. 双击 `QLU 工具箱.exe` 启动

> 程序为免安装绿色版，更新时直接覆盖目录即可，不会删除本地数据。

## 作者与反馈

- 联系邮箱：[cloud_aaa@163.com](mailto:cloud_aaa@163.com)
- Bug 与功能建议：[GitHub Issues](https://github.com/C1ouDreamW/qlu-toolbox/issues/new/choose)
- 版本发布：[GitHub Releases](https://github.com/C1ouDreamW/qlu-toolbox/releases)

提交 Bug 时请注明软件版本、Windows 版本、复现步骤、预期结果和实际结果。请勿在公开 Issue 中上传账号、密码、验证码、Cookie、成绩文件或未经脱敏的日志；涉及安全、隐私或个人信息的问题请通过邮箱私下联系作者。

## 使用说明与免责声明

本项目仅供个人学习、交流和非商业用途。未经开发者明确书面许可，禁止将本项目或其修改版本用于收费服务、商业产品、商业推广、代运营或其他营利活动。

本项目不是齐鲁工业大学官方软件，与齐鲁工业大学及其教务系统服务商不存在隶属、授权、合作或担保关系。本项目不代表学校官方立场，学校系统变更可能导致部分功能暂时不可用。

本软件按相应接口现状提供，**不保证功能持续可用**，也不保证导出结果绝对完整或准确。

使用者应仅处理本人有权访问的数据，遵守学校规定、目标系统规则及适用法律法规，**并自行承担使用、误用或无法使用本软件产生的风险和后果**。在适用法律允许的范围内，开发者不承担由此造成的账号、数据、学业、设备或其他损失。

## v1.0.1 当前模块

- 首页：工具入口和最近任务。
- 全部工具：搜索和打开内置工具。
- 分项成绩导出：选择学年、学期和保存目录，完成登录后自动导出。
- 任务记录：查看成功、失败、取消和异常中断记录。
- 设置：默认目录、浏览器、主题和登录状态管理。
- 更新提醒：启动时检查 GitHub Release，也可在设置中手动检查；不会自动下载安装。
- 关于：版本、非商业说明和非官方免责声明。

完整需求见 [`docs/PRD.md`](docs/PRD.md)。

## 源码运行

1. 安装 [Node.js](https://nodejs.org/) 和 [uv](https://docs.astral.sh/uv/getting-started/installation/)；uv 会按 `.python-version` 准备 Python 3.12。
2. 克隆本仓库，进入项目目录。
3. 运行：
    ```powershell
    uv sync --locked
    npm ci
    npm run dev
    ```

前端与桌面依赖声明在 `package.json`，Python 依赖声明在 `pyproject.toml`。Vue 渲染进程通过 Electron 安全预加载层与本地 Python Bridge 通信，不直接访问文件系统或数据库。

## 浏览器顺序

默认依次尝试：

1. Microsoft Edge
2. Google Chrome
3. 兼容 Chromium

可在“设置”中调整首选浏览器。浏览器登录数据使用工具箱专用档案，不读取日常浏览器个人资料。

## 本地数据位置

软件的“设置 → 数据管理”会显示以下完整路径，并可直接打开对应位置：

- 设置文件：`%APPDATA%\QLUToolbox\settings.json`
- 任务记录：`%LOCALAPPDATA%\QLUToolbox\tasks.sqlite3`
- 运行日志：`%LOCALAPPDATA%\QLUToolbox\logs`
- 浏览器登录状态：`%LOCALAPPDATA%\QLUToolbox\profiles`
- 导出文件：默认为当前用户的“下载”目录，也可在设置中修改

更新或替换程序目录不会删除这些数据。浏览器登录状态目录可能包含 Cookie 等敏感信息，请勿上传或分享。

## 当前限制

- 仅针对 `https://jw.qlu.edu.cn/` 当前使用的正方教务系统页面。
- 登录等待时间为 15 分钟。
- 当前版本提供 Windows 64 位免安装目录式构建；安装包尚未进行数字签名，Windows 可能显示来源未知提示。
- 更新提醒依赖访问 GitHub；网络异常不会影响工具使用。

## 项目结构

```text
src/                                Vue 3 页面、组件、状态与设计系统
electron/                           Electron 主进程、安全预加载层和 Python IPC
main.py                             Python Bridge 和 Worker 统一入口
qlu_toolbox/bridge.py               设置、任务和后台任务通信桥
qlu_toolbox/core/                   设置、路径、任务数据库、工具注册
qlu_toolbox/modules/grade_export/   分项成绩导出业务核心
tests/                              Python 核心与 Bridge 自动化测试
package.json                        Electron/Vue 依赖与联合构建配置
pyproject.toml                      Python 项目元数据与依赖声明
```

## 开发验证

```powershell
uv run --locked python -B -m unittest discover -s tests -v
npm run typecheck
npm run build
```

生成 Windows 发布目录：

```powershell
build.bat
```
