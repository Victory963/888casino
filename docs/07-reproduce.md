# 07 复现步骤

> 复现前请先确认当地法律、目标网站的服务条款，以及你所在网络环境的适用规则。本流程只读取公开资源：不登录，不调用业务接口，不绕过任何访问控制。下载的目标文件只用于本地分析，请不要再分发。

## 0. 准备

- Node.js、npm，以及 REA：`npm install -g rea-agents`（版本 6.8.0）。如果 npm 的全局前缀不可写，可以用 `npm install -g --prefix ~/.local rea-agents@latest`。
- Chromium 或 Chrome，Python 3。
- 在仓库外新建一个空的工作目录存放下载物，例如 `~/rea-work`。本仓库的 `.gitignore` 也排除了 `work/`。

```bash
WORK=~/rea-work
mkdir -p "$WORK"/{html,orbit-app/static/js,unibet-kwp,evidence}
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
```

## 1. 落地页概览

```bash
curl -sS --compressed -A "$UA" https://www.888casino.com/ -o "$WORK/html/888casino.html"
curl -sS --compressed -A "$UA" https://www.mrgreen.com/   -o "$WORK/html/mrgreen.html"
curl -sS --compressed -A "$UA" https://www.unibet.com/    -o "$WORK/html/unibet.html"

python3 -I tools/html_overview.py "$WORK/html/888casino.html" --json "$WORK/888casino.overview.json"
```

## 2. 浏览器侧被动观察（REA MCP）

```bash
tools/launch_cdp_browser.sh https://www.888casino.com/ https://www.mrgreen.com/ https://www.unibet.com/
# 输出每个标签页的 target id 和 CDP 地址 http://127.0.0.1:9333
```

然后在接入了 REA MCP 的智能体里依次调用：

1. `inspect_web_page`：传 `cdp_endpoint`、`target_id`，`include_accessibility_text: true`。
2. `capture_web_screenshot`
3. `analyze_web_bundle`：`allowed_origins` 填从 HTML 概览里得到的相关域名（888 的情况是主站、`cgp-cdn.safe-iplay.com`、`analytics.<品牌域名>`、CloudFront、`storage.googleapis.com`、`cdn.geocomply.com` 等），`fetch_source_maps: true`。

结果很大时，MCP 客户端可能把它存成文件。用 `tools/rea_evidence_summary.py` 汇总：

```bash
python3 -I tools/rea_evidence_summary.py saved-web-bundle-result.json --json summary.json
```

## 3. Orbit 静态重建

入口包的地址来自 REA 在 Mr Green 页面上的观察，哈希来自 888 页面里的 `$orbitEntryPoints`：

```bash
cd "$WORK/orbit-app/static/js"
for f in runtime.56d412df.js main.63d22730.js vendor.common.959660fa.js; do
  curl -sS --compressed -A "$UA" -O "https://cgp-cdn.safe-iplay.com/static/js/$f"
  curl -sS --compressed -A "$UA" -O "https://cgp-cdn.safe-iplay.com/static/js/$f.map"
done
cd -

# 分块清单（文件名 = 名称.哈希.chunk.js）
python3 -I tools/webpack_chunk_inventory.py "$WORK/orbit-app/static/js/runtime.56d412df.js" --tsv "$WORK/chunks.tsv"

# 按需下载感兴趣的分块及其 .map，例如：
#   grep -P '\tservices\.compliance\t' "$WORK/chunks.tsv"

python3 -I tools/sourcemap_inventory.py "$WORK/orbit-app/static/js" --paths "$WORK/source-paths.tsv" --packages "$WORK/packages.tsv"

tools/run_rea_js_analysis.sh "$WORK/orbit-app" "$WORK/evidence/orbit-app"
python3 -I tools/rea_evidence_summary.py "$WORK/evidence/orbit-app.json" --json "$WORK/evidence/orbit-app.digest.json"
```

本项目的 Orbit 分析在一台普通开发机上约需 5 分钟，生成的证据文件约 95 MB。

## 4. Unibet KWP

```bash
grep -oE 'src="https://www.unibet.com/kwp-bundle-store/[^"]+\.js"' "$WORK/html/unibet.html" \
  | sed -E 's/^src="//; s/"$//' \
  | while read -r url; do
      p="${url#https://www.unibet.com/}"
      mkdir -p "$WORK/unibet-kwp/$(dirname "$p")"
      curl -sS --compressed -A "$UA" -o "$WORK/unibet-kwp/$p" "$url"
    done
tools/run_rea_js_analysis.sh "$WORK/unibet-kwp" "$WORK/evidence/unibet-kwp"
```

import map 的提取方法见 [05-comparison.md](05-comparison.md)：解析 `<script type="systemjs-importmap">` 里的 JSON。

## 5. 牌照

在 <https://www.gamblingcommission.gov.uk/public-register> 按公司名或账号查询，本项目用到的账号是 39028、39264、45322。

## 注意事项

- 如果你在会话中途升级了 REA，正在运行的 MCP 服务需要重启，否则 `analyze_javascript_application` 可能报 `unknown_budget`。在那之前可以改用 CLI（`tools/run_rea_js_analysis.sh`）。
- 结果受访问地区影响，请记录你的出口地区。
- 资源哈希会随目标站点发版而变化；本仓库记录的是 2026-10-26 的状态。
