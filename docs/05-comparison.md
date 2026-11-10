# 05 横向对比：888casino / Mr Green / Unibet

## 1. 总表

| 维度 | 888casino | Mr Green | Unibet（unibet.com） |
|---|---|---|---|
| 所属集团 | 888 / evoke plc | 原属 William Hill，现运行在 888 平台上 | Kindred（现属 FDJ United） |
| 前端平台 | Orbit（React + MobX + MUI，webpack 5） | **同一份 Orbit 构建** | KWP（Kindred Web Platform）：SystemJS 微前端 |
| 证明两站同源的证据 | — | 入口包 `runtime.56d412df.js`、`main.63d22730.js` 与 888 页面里 `$orbitEntryPoints` 的哈希完全相同；`funnel-data-v5.min.js` 的 sha256 相同（`1c641eb0…`）；Orbit SDK 里有 `mrgreen_sweeden_regulation` | — |
| 内容管理 | Adobe Experience Manager 云服务 + Helix RUM | Adobe Experience Manager（`cw-prod/mrgreen-websites/aemMgr.js`） | 自建（`kwp-sites`、`kmf-cms-generic-content`） |
| 落地页大小 | 约 3.76 MB（其中 `$allConfigs` 约 3.6 MB） | 约 3.28 MB | 约 138 KB |
| 引导数据 | 内联 `$allConfigs`（含 4134 款游戏的目录） | 内联 `$allConfigs`（约 3.2 MB 的内联脚本） | SystemJS import map（427 个模块入口） |
| 静态资源托管 | `cgp-cdn.safe-iplay.com/static/js/` | 同左 | `www.unibet.com/kwp-bundle-store/<包名>/<版本>/` |
| 版本管理方式 | 整个应用一个构建，内容哈希命名 | 同左 | **每个微前端包独立发版**（如 `game-lobby 0.350.2`、`kindred-betting-client 0.983.0`） |
| 数据统计 | 第一方 GTM/GA4（`analytics.888casino.com`） | 第一方 GTM/GA4（`analytics.mrgreen.com`） | 自建 Snowplow 埋点（`kindred-snow`） |
| 体验监控 | TrackJS、web-vitals、结构化日志 | 同左 | `keum` 用 `sendBeacon` 上报到 `/eum-collector/events`；SystemJS 加载失败时也上报到这里 |
| 地理定位 | GeoComply（插件 / HTML5 / 原生） | GeoComply | 这次没有观察到 |
| 公开 source map | **有**，含完整 `sourcesContent` | 同左（同一份构建） | `keum` 声明了 source map，但请求返回 403 |
| 合规组织方式 | 单体应用内按辖区插件化（见 [04](04-orbit-compliance.md)） | 同左 | **每项责任博彩功能是一个独立的微前端** |

依据：REA 观察（`ev_f162dbd6…`、`ev_d2c7b07e…`、`ev_56422336…`、`ev_2840bbd5…`、`ev_574afece…`）+ 公开元数据。

## 2. Unibet KWP 微前端架构

### 加载方式

- 页面只直接加载 5 个脚本：`kmf-vendor-pack/2.44.0/systemjs-*.js`（SystemJS 加载器）、`keum/0.12.0`（体验监控）、`analytics-data-collection-cookieservice`、`analytics-data-collection-fe`（Snowplow）、`rg-info-snackbar-fe`（责任博彩信息条）。
- 其余功能通过 `<script type="systemjs-importmap">` 声明。import map 里有 `imports`（427 条）和 `umd`（6 条），按需加载。完整清单见 [data/unibet/importmap-imports.tsv](../data/unibet/importmap-imports.tsv) 和 [data/unibet/kwp-packages.tsv](../data/unibet/kwp-packages.tsv)。
- 命名前缀：`kmf-*`（Kindred micro frontend）、`kaf-*`（认证）、`ksp-*`（体育相关）、`kwp-*`（平台核心）、`pay-*-kmf`（支付）、`rg-*`（责任博彩）、`saplus-*`、`ts-*`（交易历史）。

依据：公开元数据（HTML import map）+ REA 观察。

### 182 个包按职能分组

分组是作者根据包名归纳的。

| 分组 | 数量 | 代表包 |
|---|---|---|
| 支付 | 47 | `pay-*-kmf` 43 个（名称含 deposit 的 20 个、含 withdrawal 的 16 个，其余是收银台、支付方式选择、兼容层、Trustly Pay N Play 等），覆盖 Adyen、Apple Pay、Google Pay、PayPal、Skrill、Neteller、Trustly、Swish、MobilePay、TrueLayer、Brite、Revolut Pay、Paysafecard、Mollie、Payconiq、Nuvei、Worldpay 等；另有 `payment-kit`、`payment-ui-kit`、`payment-utils`、`payment-logos` |
| 责任博彩与监管 | 27 | 存款限额（`deposit-limit-fe`、`deposit-limit-modal-fe`、`kmf-net-deposit-limit-modal`、`ndlim-fe`）、`loss-limit-fe`、`time-limit-fe`、`session-limit-fe`、`single-bet-limit-fe`、`balance-limit-fe`、`reality-check-fe`、`cool-off-fe`、`self-exclusion-fe`、`self-assessment-fe`、`self-declaration-fe`、`rg-360view-fe`、`rg-activity-tool-fe`、`rg-limit-history-fe`、`rg-registration-fe`、`rg-user-communication-fe`、`rg-info-snackbar-fe`、`responsible-gaming-bo`、`regulatory-top-bar-fe`、`session-info-fe`、`kmf-dangers-of-gambling-modal`、`reminder-settings-fe`、`account-closure-fe` |
| 身份与验证 | 约 10 | `kaf-kmf-client`、`kaf-kmf-login`、`mfa-fe`、`otp-fe`、`kyc-ui`、`verification`、`verification-notifications`、`channel-verification-fe`、`personal-details`、`registration-fe` |
| 游戏与产品 | 约 20 | `game-lobby`、`game-play`、`game-banner`、`last-played`、`kindred-betting-client`、`sportsbook-ui-kit`、`poker-lobby`、`poker-tournaments`、`tournament-widget`、`tournament-buy-in`、`virtualsports-mini-app`、`major-events-jackpot-fe`、`ksp-livestream-player`、`ksp-betshare-app` |
| 奖金、促销与留存 | 约 25 | `available-bonuses`、`bonus-progression`、`bonus-preferences`、`cashback-fe`、`welcome-bonus-offer`、`promotions-fe`、`missions-fe`、`loyalty-fe`、`refer-a-friend`、`raf-fe`、`seasonal-calendar`、`saplus-*`、`optimove-modals` |
| 平台壳 | 约 15 | `kwp-core`、`kwp-sites`、`kwp-layouts`、`kwp-serviceworker`、`pwa-shell`、`global-navigation`、`kindred-ui-kit`、`kmf-i18n`、`kmf-sitedefinition`、`kmf-vendor-pack`、`flight-control` |
| 其余 | — | 消息通知、帮助中心、SEO 与页脚、交易历史导出、联盟商自助（`affiliate-self-service`）、测试账户门户（`test-account-portal-fe`）等 |

### REA 对 5 个直接加载脚本的分析结果

来自 `ev_2840bbd5…`：5 个文件全部解析成功，共 43 条发现，3 个接口节点，4 个存储节点。

- **`kindred-snow` 是 Snowplow 埋点 SDK**：调用里有 `track` 页面浏览（`e: "pv"`）和页面停留心跳（`e: "pp"`），以及 `setAppId`、`setPlatform`、`setTrackerNamespace`、`setTrackerVersion`、`addPlugin`；上报字段包括 `cs`、`cookie`、`tz`、`lang`、`res`、`cd`。它会读写 localStorage 和 sessionStorage。
- **`keum`** 上报接口是 `/eum-collector/events`，优先用 `navigator.sendBeacon`，不支持时退回 `fetch`；上报前把路由里的数字 ID 归一化成 `/:id`。
- **`systemjs` 加载器**被定制过：模块解析失败时，也会把 `moduleId`、`moduleParentUrl` 上报到 `/eum-collector/events`。
- 页面内联脚本里的路由：`betting`、`blog`、`general-info/closure-faq`、`poker/client/login`、`:appId(pwaapp|casinoapp|unibetpro)/(.*)`、`browser-notification`、`not-found`（来自 `ev_56422336…`）。

## 3. 两种路线的取舍（作者观点）

| | Orbit（单体 + 插件化） | KWP（微前端） |
|---|---|---|
| 发版粒度 | 整个应用一起发，靠分块按需加载控制体积 | 每个功能独立发版，团队可以各自迭代 |
| 合规改动 | 新增辖区等于新增几个规则类和展示器，评审集中 | 新增一项责任博彩功能等于新增一个微前端包，可以单独上线或回滚 |
| 首屏成本 | 内联巨大的引导配置（游戏目录约 2 MB） | 首屏 HTML 小，配置分散在各包里 |
| 多品牌复用 | 同一份构建靠 `skin`、`brandId` 切换品牌，例如 888casino 与 Mr Green | 一套平台，引导页加各国本地站点 |
| 公开暴露面 | 公开的 source map 暴露了完整的源码结构 | import map 暴露了完整的功能清单和版本号 |
