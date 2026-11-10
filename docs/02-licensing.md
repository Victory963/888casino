# 02 牌照核实

核实以监管机构公开名录为准；第三方页面只作线索。

| 品牌 | 持牌主体 | 监管机构 / 账号 | 状态 | 依据 |
|---|---|---|---|---|
| 888casino（英国） | 888 UK Limited | UKGC 39028 | 有效。Bingo、Casino、General Betting（Real Event / Virtual Event）四类远程牌照 | [UKGC 名录 39028](https://www.gamblingcommission.gov.uk/public-register/business/detail/39028) |
| Mr Green（英国） | Mr Green Limited | UKGC 39264 | **已交回**：Casino、Bingo 远程牌照均于 2024-10-28 截止 | [UKGC 名录 39264](https://www.gamblingcommission.gov.uk/public-register/business/detail/39264) |
| Unibet（英国） | Platinum Gaming Limited | UKGC 45322 | 有效；名录列出 www.unibet.co.uk 等域名；有 2023 年和 2025 年的监管处罚记录 | [UKGC 名录 45322](https://www.gamblingcommission.gov.uk/public-register/business/detail/45322)、[域名列表](https://www.gamblingcommission.gov.uk/public-register/business/detail/domain-names/45322) |

## 说明与未核实项

- **888 UK Limited 登记了 90 个域名**，名录页没有展开显示，所以 888casino.com 是否在其中没有逐条核对。
- **Mr Green 国际站（mrgreen.com）** 页面自称持有马耳他（MGA）、丹麦（DGA）、瑞典（SGA）的牌照。本项目没有查询 MGA 名录，这一点未核实。2015–2016 年的新闻稿显示，Mr Green Limited（马耳他公司号 C43260）当时持有多张 MGA Class 1 牌照（[Cision PDF](https://mb.cision.com/Main/13935/2272512/678937.pdf)），但那是历史信息。
- **unibet.com** 本身是一个引导页（"Visit your local Unibet site"），把访客引到各国本地持牌站点（.co.uk、.se、.dk、.nl、.ie、.ro、.fr、.be、.it、.com.au、.mt 等）。页面路由里有 `general-info/closure-faq`。
- **Trannel International Limited** 曾是 Unibet 的马耳他运营主体，据报道已与 Unibet 分离，见 [Vixio](https://www.vixio.com/insights/gc-dutch-gambler-wins-player-refund-case-against-unibet)。
- Unibet 母公司的英国处罚报道：[Mondaq](https://www.mondaq.com/unibet's-owner-fined-%C2%A310-million-for-money-laundering-and-customer-welfare-shortcomings/1701866)。

## 与架构发现的关联（推断）

Mr Green Limited 的英国牌照交回时间（2024-10-28），与以下几点相互吻合：

- Mr Green 前端已经跑在 888 的 Orbit 平台上。
- Orbit 有 `services.player-migration` 分块，SDK 配置里有 `PlayerMigration`、`MigratedHistory`、`WinnerMigration` 模块。
- Orbit SDK 里有品牌专用的 `mrgreen_sweeden_regulation`。

由此推测英国 Mr Green 玩家被迁移到了 888 UK 的牌照下。这是推断，本项目没有直接证据。
