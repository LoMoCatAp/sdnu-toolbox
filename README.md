<p align="center">
  <img src="assets/qlu-toolbox.png" width="128" alt="SDNU 工具箱 Logo">
</p>

# SDNU 工具箱

<p align="center">
  <img src="https://img.shields.io/badge/Vue-3.5-42B883?logo=vuedotjs&logoColor=white" alt="Vue 3">
  <img src="https://img.shields.io/badge/Electron-37-47848F?logo=electron&logoColor=white" alt="Electron">
  <img src="https://img.shields.io/badge/TypeScript-5.8-3178C6?logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Playwright-1.55-2EAD33?logo=playwright&logoColor=white" alt="Playwright">
  <img src="https://img.shields.io/badge/Vite-7-646CFF?logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white" alt="Windows">
</p>

SDNU 工具箱是一款面向**山东师范大学**学生的本地校园效率桌面软件，基于 [QLU 工具箱](https://github.com/C1ouDreamW/qlu-toolbox) 改造而来。使用 Vue 3、TypeScript 与 Electron 提供桌面界面，Python 与 Playwright 负责本地自动化。当前内置「分项成绩导出」和「绩点计算器」两个教务工具。

分项成绩导出会打开本机 Edge、Chrome 或兼容 Chromium。用户在校外需通过 WebVPN 登录，在校内可直接访问教务系统。工具会自动查询指定学期并将成绩保存为 Excel 文件。

绩点计算器支持**多文件导入**，可同时导入多个学期的成绩文件，自动计算累计加权平均 GPA。

工具箱不会要求用户在客户端填写或复制账号、密码、验证码、Cookie，也不会把成绩发送到开发者服务器。

浏览器登录状态、任务记录和设置默认保存在当前用户的系统应用数据目录中，**程序完全本地运行**。

## 致谢与授权

本项目基于 [C1ouDreamW/qlu-toolbox](https://github.com/C1ouDreamW/qlu-toolbox) 改造，经原作者授权作为非商业衍生版本发布。

**维护边界**：本项目由 [LoMoCatAp](https://github.com/LoMoCatAp) 独立维护。山东师范大学适配、版本发布及问题反馈均由本仓库维护者负责。如需贡献或报告问题，请使用本仓库的 [Issues](https://github.com/LoMoCatAp/sdnu-toolbox/issues)，不要提交到原项目。

**致谢**：感谢原作者 [C1ouDreamW](https://github.com/C1ouDreamW) 的开源贡献。

主要改动：
- 教务系统地址适配山东师范大学（含 WebVPN 校外访问）
- 绩点公式改为 SDNU 标准：`(分数 - 50) / 10`
- 成绩导出改为页面抓取方式（SDNU 未开放导出接口）
- 绩点计算器支持多文件导入、累计绩点计算

## 使用

1. 前往 [Releases](https://github.com/LoMoCatAp/sdnu-toolbox/releases) 下载最新版本（Windows x64 安装包或免安装 ZIP）。
2. **校外访问**：启动后会自动打开 WebVPN 门户页面，依次完成：
   - WebVPN 统一身份认证登录
   - 在 VPN 门户中找到并进入「教务系统」
   - 在教务登录页输入学号密码
3. **校内访问**：直接连接校园网即可使用。

## 使用说明与免责声明

本项目仅供个人学习、交流和非商业用途。

本项目不是山东师范大学官方软件，与山东师范大学及其教务系统服务商不存在隶属、授权、合作或担保关系。本项目不代表学校官方立场。

本软件按相应接口现状提供，**不保证功能持续可用**，也不保证导出结果绝对完整或准确。

使用者应仅处理本人有权访问的数据，遵守学校规定、目标系统规则及适用法律法规，**并自行承担使用、误用或无法使用本软件产生的风险和后果**。

## 当前模块

- **首页**：工具入口和最近任务。
- **分项成绩导出**：选择学年、学期和保存目录，完成登录后自动抓取成绩并生成 Excel。
- **绩点计算器**：导入多个学期的分项成绩 XLSX，查看成绩明细，自由勾选课程，实时计算累计 GPA。
- **任务记录**：查看成功、失败、取消和异常中断记录。
- **设置**：默认目录、浏览器、主题和登录状态管理。
- **关于**：版本、非商业说明和非官方免责声明。

## 源码运行

1. 安装 [Node.js](https://nodejs.org/) 和 [uv](https://docs.astral.sh/uv/getting-started/installation/)；uv 会按 `.python-version` 准备 Python 3.12。
2. 克隆本仓库，进入项目目录。
3. 运行：
    ```powershell
    uv sync --locked
    npm ci
    npm run dev
    ```

前端与桌面依赖声明在 `package.json`，Python 依赖声明在 `pyproject.toml`。

## 构建

```powershell
# 免安装版
.\build.bat

# 安装程序版
.\build-installer.bat
```

## 浏览器顺序

默认依次尝试：

1. Microsoft Edge
2. Google Chrome
3. 备用 Chromium

可在「设置」中调整首选浏览器。若 Edge 和 Chrome 均无法启动且尚未安装备用 Chromium，软件会先征求用户同意再按需下载。

## 本地数据位置

- Windows 设置文件：`%APPDATA%\SDNUToolbox\settings.json`
- Windows 任务记录、日志、浏览器登录状态：`%LOCALAPPDATA%\SDNUToolbox`
- 导出文件：默认为当前用户的「下载」目录，也可在设置中修改

## 当前限制

- 仅针对山东师范大学正方教务系统（`jwxt.sdnu.edu.cn`）。
- SDNU 教务系统无分项成绩导出接口，成绩通过页面抓取获取。
- 更新提醒依赖访问 GitHub。

## 项目结构

```text
src/                                Vue 3 页面、组件、状态与设计系统
electron/                           Electron 主进程、安全预加载层和 Python IPC
main.py                             Python Bridge 和 Worker 统一入口
qlu_toolbox/bridge.py               设置、任务和后台任务通信桥
qlu_toolbox/core/                   设置、路径、任务数据库、工具注册
qlu_toolbox/modules/grade_export/   分项成绩导出业务核心
qlu_toolbox/modules/gpa_calculator/ 绩点解析与计算核心
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

## 作者与反馈

- 维护者：[LoMoCatAp](https://github.com/LoMoCatAp)
- 原作者：[C1ouDreamW/qlu-toolbox](https://github.com/C1ouDreamW/qlu-toolbox)
- Bug 与功能建议：[GitHub Issues](https://github.com/LoMoCatAp/sdnu-toolbox/issues)
