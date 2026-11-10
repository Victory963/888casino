# data/

这里只有元数据：名称、路径、版本、计数、结构和哈希。**不包含**目标站点的代码、source map、源码内容或业务数据（例如游戏目录里的具体条目）。采集时间：2026-10-26。

| 文件 | 内容 | 由谁生成 |
|---|---|---|
| `orbit/chunk-inventory.tsv` | Orbit webpack runtime 登记的 257 个按需分块：ID、名称、哈希、文件名 | `tools/webpack_chunk_inventory.py` |
| `orbit/source-paths.tsv` | 11 个 source map 中的 385 条原始源文件路径（map 文件名 + 路径） | `tools/sourcemap_inventory.py` |
| `orbit/vendor-packages.tsv` | `vendor.common` 用到的 npm 包及模块数 | `tools/sourcemap_inventory.py` |
| `orbit/allconfigs-structure.json` | 888casino 落地页 `$allConfigs` 的结构：键名、类型、条目数、JSON 字符数，**不含值** | 一次性脚本（逻辑同 `tools/html_overview.py`） |
| `unibet/kwp-packages.tsv` | Unibet import map 中的 182 个 KWP 包：名称、版本、模块入口数 | 一次性脚本 |
| `unibet/importmap-imports.tsv` | import map 的 427 个模块入口：名称、所属包、版本 | 一次性脚本 |
| `rea/888casino.web-bundle.summary.json` | REA `analyze_web_bundle` 摘要（脚本 URL、大小、sha256、分块边、接口、source map 状态） | `tools/rea_evidence_summary.py` |
| `rea/mrgreen.web-bundle.summary.json` | 同上，Mr Green。从 MCP 内联结果转录 | 手工转录 |
| `rea/unibet.web-bundle.summary.json` | 同上，Unibet。从 MCP 内联结果转录 | 手工转录 |
| `rea/orbit-app.js-application.summary.json` | REA `analyze_javascript_application` 摘要：统计、覆盖率、节点类型、385 个 source-module 路径、接口、worker | `tools/rea_evidence_summary.py` |
| `rea/unibet-kwp.js-application.summary.json` | 同上，Unibet 的 5 个包 | `tools/rea_evidence_summary.py` |

证据编号与覆盖率说明见 [../docs/06-evidence-index.md](../docs/06-evidence-index.md)。
