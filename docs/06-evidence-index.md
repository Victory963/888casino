# 06 证据索引、覆盖率与局限

## REA 证据记录

REA 证据编号是它对一次观察生成的内容寻址 ID。完整的证据文件里嵌有目标代码的语法树和表达式，所以**不放进本仓库**，只提供摘要（见 [data/rea/](../data/rea/)）。

| # | 操作 | 目标 | 证据编号 | 覆盖情况 | 摘要文件 |
|---|---|---|---|---|---|
| 1 | `inspect_web_page` | www.888casino.com | `ev_8aa0d5d2e3e60978ff2c2b3418175053da25b6ebabff3c27f4111a787810dc1f` | DOM 159 个节点，无障碍树 6 个节点（`busy`），同源脚本 10 个；第三方部分按策略过滤 | — |
| 2 | `capture_web_screenshot` | www.888casino.com | `ev_d238d30fc750229f2099e762b066adf51815b46fd7271a222fbe6ff7ff2d6ad2` | 1366×757 视口，PNG 27 KB（页面停在启动画面） | — |
| 3 | `analyze_web_bundle` | www.888casino.com | `ev_f162dbd6105016993e15310c644460319ae2100300c1998f24ff221fc13b0583` | 11/11 个脚本解析成功，访问 439,841 个语法树节点；1 个 source map（`funnel-data-v5.min.js.map`）已获取 | [888casino.web-bundle.summary.json](../data/rea/888casino.web-bundle.summary.json) |
| 4 | `analyze_web_bundle` | www.mrgreen.com | `ev_d2c7b07ea47a6b3d73f2dd7a09a57b074ee5c1edf790c0e21e0016c493fa005d` | 23/23 个脚本解析成功，访问 1,045,301 个节点；观察到 Orbit 的 runtime 和 main 从 `cgp-cdn.safe-iplay.com` 加载 | [mrgreen.web-bundle.summary.json](../data/rea/mrgreen.web-bundle.summary.json) |
| 5 | `analyze_web_bundle` | www.unibet.com | `ev_56422336313752a411dd66f4883ebc6755a3daed9aba407aa306d4fb62ba9390` | 6 个内联脚本；**结果为 partial**，5 个外部 KWP 包没有被抓到；source map 不可用 | [unibet.web-bundle.summary.json](../data/rea/unibet.web-bundle.summary.json) |
| 6 | `analyze_javascript_application`（CLI） | 下载的 Unibet 包（5 个文件） | 父证据 `ev_2840bbd56e4e2838abf809c9d7b7d58c41c3d22e99cad8b2d1b90d3cff63baaf`，摘要视图 `ev_680288ac73ac25430ab06e85f641584d2504812dbabb14e0cb8e09ce4fc44b80` | 5/5 个文件解析成功，27,541 个语法树节点，43 条发现；语义图有 20,133 个节点、31,627 条关系、6,548 个未知项 | [unibet-kwp.js-application.summary.json](../data/rea/unibet-kwp.js-application.summary.json) |
| 7 | `analyze_javascript_application`（CLI） | 下载的 Orbit 包（11 个 JS + 11 个 source map） | 父证据 `ev_574afecebc36c444fb9625ddbace5be0c7ee39f0dc36d980dee177e726e28fa7`，摘要视图 `ev_4e0b3e2ebc6a9887bc6a2268b704cbd25ef82172c378e1b3f8c4f1152de7d798` | 11/11 个 JS 解析成功，读取 3.7 MB 文本，191,089 个语法树节点，590 条发现，187 个模块；385 个原始源文件精确映射；30,688 个语义未知项 | [orbit-app.js-application.summary.json](../data/rea/orbit-app.js-application.summary.json) |

另有两次失败的 MCP 调用：`analyze_javascript_application` 对两个目录各调用一次，原因是 REA 原地升级后 MCP 服务进程和分析子进程版本不一致（`unknown_budget`）。失败时留下了不完整的证据 `ev_01cea4ba…` 和 `ev_be3d5336…`，不作为结论依据。

## 其他数据来源

| 来源 | 内容 | 本仓库中的产物 |
|---|---|---|
| curl 拿到的 888casino.com 落地页（3,761,495 字节） | `$allConfigs`、内联脚本、外部脚本、域名 | [data/orbit/allconfigs-structure.json](../data/orbit/allconfigs-structure.json)（只有结构） |
| curl 拿到的 mrgreen.com、unibet.com 落地页 | 脚本、域名、import map | [data/unibet/](../data/unibet/) |
| `cgp-cdn.safe-iplay.com/static/js/runtime.56d412df.js` | webpack 分块表 | [data/orbit/chunk-inventory.tsv](../data/orbit/chunk-inventory.tsv) |
| 11 个公开 source map | 原始路径、npm 包 | [data/orbit/source-paths.tsv](../data/orbit/source-paths.tsv)、[data/orbit/vendor-packages.tsv](../data/orbit/vendor-packages.tsv) |
| UKGC 公开名录 | 牌照状态 | [02-licensing.md](02-licensing.md) |

## 覆盖率与已知未知

| 问题 | 状态 | 说明 |
|---|---|---|
| Orbit 的整体结构和分块清单 | 已回答 | 257 个分块全部列出 |
| Orbit 的合规架构 | **部分回答** | 只下载了 8 个按需分块加入口三件套。其余 249 个按需分块未分析，包括 37 个"辖区 × 厂商"分块中的 36 个 |
| Orbit 的真实后端接口 | **未回答** | 网络请求通过 SDK 封装（`services.api.<controller>.<method>`），REA 只找到 3 个低置信度的接口候选。没有为此去探测接口 |
| 888casino 在无头浏览器中为何停在启动画面 | **未回答** | 可能和地区（`jpn`）或无头环境检测有关，没有深究 |
| Unibet 的原始源码 | **未回答** | source map 返回 403 |
| Unibet 本地站点（如 unibet.co.uk）的结构 | 未分析 | 只看了 .com 引导页 |
| 英国用户实际看到的配置 | **未回答** | 出口在日本 |
| Mr Green 国际站的马耳他、丹麦、瑞典牌照 | 未核实 | 没有查询 MGA、DGA、SGA 的名录 |
| Mr Green 英国玩家迁移到 888 UK | **推断** | 依据是时间线吻合和代码里有迁移服务，没有直接证据 |

## REA 自述的局限（摘录）

- 静态分析只是观察或有界推断；REA 不执行抓取到的 JavaScript。
- 接口候选里，未绑定的 HTTP 方法名调用的裸字符串参数属于低置信度；表单、翻译、存储等 API 会用相同语法。
- 用字符串拼出来的路由和接口、加密的配置、服务器端行为，都可能仍然未知。
- 语义图的覆盖率是 partial 或 unknown；无法获得的事实会显式标出，不能当作"不存在"。
