# 888casino 前端架构与合规实现分析

对持牌在线赌场公开前端的**被动、只读**逆向分析，主角是 888 集团自研的前端平台 **Orbit**（888casino 与 Mr Green 共用），并与 Kindred/Unibet 的微前端平台做横向对比。分析主要使用 [REA](https://github.com/morluto/rea)（Reverse Engineer Anything）。

> **免责声明**：本项目是独立的技术研究，与 888 Holdings / evoke plc、Mr Green、Kindred / FDJ United 均无任何关联，也未获其授权或认可。仓库**不包含**任何目标站点的专有代码、source map、源码内容或业务数据，只包含作者自己编写的分析脚本、分析文档，以及从公开页面提取的元数据（文件路径、分块名、包名与版本、配置结构等）。本仓库不提供任何绕过地区限制、风控、合规控制或博彩结果的方法。

## 核心结论

1. **888casino 与 Mr Green 运行同一份 Orbit 构建。** 两站加载的入口包 `runtime.56d412df.js` / `main.63d22730.js` 哈希完全一致，均托管在 `cgp-cdn.safe-iplay.com`；Orbit SDK 里还有 Mr Green 专用的瑞典监管类。Mr Green Limited 的英国牌照已于 2024-10-28 交回（UKGC 公开名录），Orbit 中存在 `player-migration` 服务——两者时间线吻合，但因果关系属推断。
2. **Orbit 是 React + MobX + MUI 的单页应用**，由页面内联的 `$allConfigs`（约 3.6 MB，含 86 个 SDK 配置模块和 4134 款游戏的目录）引导，按需加载 257 个 webpack 分块。
3. **合规按辖区插件化**：英国、德国、意大利、西班牙、葡萄牙、罗马尼亚、瑞典、丹麦、马耳他、直布罗陀、加拿大安大略/阿尔伯塔、美国新泽西各有独立的 regulation 类；现实检查（reality check）、德国强制冷却、地理定位（GeoComply）、资金来源核查、限制规则等以独立服务实现。
4. **执行在服务器端，前端只负责展示。** 冷却限制由服务器接口下发，地理踢出和奖金滥用拒绝由服务器经 Firebase 推送，前端存储的倒计时等状态仅用于显示。
5. **Unibet 采用完全不同的路线**：SystemJS 微前端，import map 中有 182 个独立版本化的包、427 个模块入口；责任博彩功能（各类限额、自我排除、自我评估、现实检查、冷静期等）每项都是独立的微前端。

## 文档

| 文档 | 内容 |
|---|---|
| [docs/01-scope-and-method.md](docs/01-scope-and-method.md) | 范围、方法、工具、边界、环境限制 |
| [docs/02-licensing.md](docs/02-licensing.md) | 三个品牌的牌照核实（UKGC 公开名录） |
| [docs/03-orbit-architecture.md](docs/03-orbit-architecture.md) | Orbit 平台架构：托管、引导流程、分块、SDK 模块、技术栈、游戏接入、数据统计 |
| [docs/04-orbit-compliance.md](docs/04-orbit-compliance.md) | Orbit 合规架构：辖区规则、现实检查、冷却、地理定位、限制、资金来源 |
| [docs/05-comparison.md](docs/05-comparison.md) | 888casino / Mr Green / Unibet 横向对比，以及 Unibet KWP 微前端架构 |
| [docs/06-evidence-index.md](docs/06-evidence-index.md) | REA 证据编号、覆盖率、已知未知与局限 |
| [docs/07-reproduce.md](docs/07-reproduce.md) | 复现步骤 |
| [docs/appendix-my-article.md](docs/appendix-my-article.md) | 附录：本项目起点——对一个赌博 SEO 垃圾站仓库的评估（未复刻） |

## 仓库结构

```
tools/                         作者编写的分析脚本（不含任何目标代码）
  launch_cdp_browser.sh        启动只监听本机的无头 Chromium，供 REA 网页工具连接
  html_overview.py             汇总落地页 HTML：脚本、域名、牌照文字、$allConfigs 结构（只取键和大小）
  webpack_chunk_inventory.py   从 webpack runtime 解析按需分块清单
  sourcemap_inventory.py       source map 元数据清单：原始路径、npm 包统计（不输出源码）
  run_rea_js_analysis.sh       调用 rea CLI 做 JS 应用静态重建
  rea_evidence_summary.py      汇总 REA 证据文件
data/                          提取出的元数据，说明见 data/README.md
docs/                          分析文档
```

## 环境

- REA 6.8.0（`rea-agents`），Chromium 149（无头，CDP 仅监听 127.0.0.1）
- 分析时间：2026-10-26
- 出口 IP 位于日本，目标站点按日本访客下发内容（`country: "jpn"`），与英国用户看到的配置不同，详见 [docs/01-scope-and-method.md](docs/01-scope-and-method.md)。
