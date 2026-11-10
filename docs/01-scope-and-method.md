# 01 范围与方法

## 研究问题

1. 持牌在线赌场的 Web 前端是怎样构建和交付的？
2. 多辖区的监管要求（现实检查、冷却、地理限制、限额、资金来源核查等）在前端是怎样组织的？
3. 同一集团的不同品牌是否共享平台？不同集团之间的架构路线有何差异？

## 目标选择

起点是监管机构的公开名录，而不是"持牌赌场排行榜"之类的推广站：

- 英国博彩委员会（UKGC）公开名录：<https://www.gamblingcommission.gov.uk/public-register>（每日更新，可下载 CSV）
- 候选站点从分析主机能否正常打开（未被反爬拦截、未被地区屏蔽）来筛选：

| 站点 | 从分析主机访问的结果 | 处理 |
|---|---|---|
| casino.bet365.com | Cloudflare 人机验证页 | 未绕过，放弃 |
| www.casumo.com | Cloudflare "Just a moment..." | 未绕过，放弃 |
| www.leovegas.com、www.paddypower.com/casino | HTTP 403 | 放弃 |
| betway.com | 跳转到"日本市场已关闭"维护页 | 放弃 |
| www.betfair.com、www.williamhill.com | 跳转到日文页 | 未分析 |
| **www.888casino.com** | 正常 | **主分析对象** |
| **www.mrgreen.com** | 正常 | 对比对象 |
| **www.unibet.com** | 正常（全球引导页） | 对比对象 |

## 边界

本项目只做被动、只读的分析：

- **只接触公开资源**：落地页 HTML，以及页面自身会加载的脚本、样式和公开 source map。
- **不登录、不注册、不充值、不进入游戏**，不调用任何业务 API。
- **不探测接口路径**：888 主站上猜测入口包路径得到 404 后即停止，未去请求 `cgpapi/orbit/config/appEntryPoints` 这类接口。后来是 REA 观察到 Mr Green 页面实际从 `cgp-cdn.safe-iplay.com` 加载 Orbit，才拿到入口包。
- **不绕过任何防护**：Cloudflare 验证、403、地区屏蔽均未尝试绕过。
- **不再分发目标的专有内容**：下载的包、source map 和其中的源码只在本地分析，不进入本仓库。文档里只引用标识符级别的短片段（类名、文件路径、常量名）来说明结构。

## 工具链

| 工具 | 用途 |
|---|---|
| REA `inspect_web_page` | 被动检查页面：DOM、无障碍树、脚本清单、资源、存储清单（值被脱敏） |
| REA `capture_web_screenshot` | 截取当前视口 |
| REA `analyze_web_bundle` | 从浏览器抓取页面的 JS，静态解析出分块图、路由与接口候选、source map（JS 只解析、不执行） |
| REA `analyze_javascript_application`（CLI） | 对下载到本地的包做应用级静态重建：模块、webpack 分块、source map 原始模块映射、存储/接口/worker、语义图 |
| `tools/*.py` | 作者编写的元数据提取脚本（HTML 概览、webpack 分块清单、source map 路径清单、证据汇总） |
| Chromium 149 无头模式 | 提供只监听 127.0.0.1 的 CDP 端点，配置目录用临时目录隔离 |

### REA 使用中遇到的问题

在同一会话里原地把 REA 从 6.5.0 升级到 6.8.0 之后，仍在运行的 MCP 服务进程是旧版，它调用新版分析子进程时，`analyze_javascript_application` 报错 `unknown_budget: expected number`。解决办法是改用同版本的 `rea` CLI（见 `tools/run_rea_js_analysis.sh`），或重启 MCP 客户端。

## 分析环境的影响

- 出口 IP 位于日本，服务器在 HTML 里写入了 `country: "jpn"`。日本不是这些运营商的持牌市场，所以看到的配置、游戏可用性、页面流程与英国用户不同。
- 在无头浏览器里，888casino 页面一直停在启动画面（无障碍树 `busy`），Orbit 主程序没有加载；Mr Green 页面则加载了 Orbit 的 runtime 和 main。
- 同一 URL 在 curl 和浏览器中拿到的 `$allConfigs` 大小不同（约 3.6 MB 对比约 57 KB 的内联脚本），说明服务器会按请求特征下发不同内容。本项目的配置结构数据来自 curl 拿到的完整版本。

## 证据分级

文档里每条结论都标明依据来自哪一类：

- **REA 观察**：REA 证据记录里的直接观察，证据编号见 [06-evidence-index.md](06-evidence-index.md)。
- **公开元数据**：从公开 HTML、webpack runtime、source map 的路径和名称中直接读出的事实。
- **源码阅读**：阅读公开 source map 中原始源码得到的结论，只引用标识符。
- **推断**：作者的推测，会明确写出。
