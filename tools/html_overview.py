#!/usr/bin/env python3
"""Summarize a saved landing-page HTML file without executing it.

Prints external script sources, referenced hosts, licence/responsible-gaming
text snippets, platform hints, and -- for 888 "Orbit" pages -- the top-level
*structure* (keys and sizes only, never values) of the inline `$allConfigs`
bootstrap object.

Usage: python3 -I tools/html_overview.py page.html [--json out.json]
"""
import argparse
import html
import json
import re
from collections import Counter

LICENCE_KEYWORDS = ["Gambling Commission", "Malta Gaming", "licen", "Gibraltar",
                    "18+", "BeGambleAware", "GAMSTOP"]
PLATFORM_HINTS = r'(/content/dam/[a-z0-9_-]+|/etc\.clientlibs/[a-z0-9_-]+|hlx\.(?:page|live)|' \
                 r'aem\.(?:page|live)|data-routing="[^"]*"|kwp-bundle-store/[a-z0-9-]+)'


def visible_text(page):
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    return re.sub(r"\s+", " ", text)


def all_configs_structure(page):
    match = re.search(r"var \$allConfigs = ", page)
    if not match:
        return None
    obj, _ = json.JSONDecoder().raw_decode(page[match.end():])

    def describe(value):
        size = len(json.dumps(value))
        if isinstance(value, dict):
            return {"type": "object", "keys": len(value), "json_chars": size}
        if isinstance(value, list):
            return {"type": "array", "items": len(value), "json_chars": size}
        return {"type": type(value).__name__, "json_chars": size}

    structure = {key: describe(value) for key, value in obj.items()}
    for section in ("sdk", "adminConfig"):
        inner = obj.get(section)
        if not isinstance(inner, dict):
            continue
        for key, value in inner.items():
            structure[f"{section}.{key}"] = describe(value)
            if isinstance(value, dict) and section == "sdk":
                for sub, sub_value in value.items():
                    structure[f"{section}.{key}.{sub}"] = describe(sub_value)
    return structure


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("html_file")
    parser.add_argument("--json", help="write the overview as JSON to this path")
    args = parser.parse_args()

    page = open(args.html_file, encoding="utf-8", errors="replace").read()
    text = visible_text(page)
    overview = {
        "bytes": len(page.encode("utf-8")),
        "script_srcs": re.findall(r'<script[^>]*\bsrc="([^"]+)"', page),
        "hosts": Counter(re.findall(r"https?://([a-zA-Z0-9.-]+\.[a-z]{2,})", page)).most_common(40),
        "licence_snippets": {},
        "platform_hints": sorted(set(re.findall(PLATFORM_HINTS, page))),
        "all_configs_structure": all_configs_structure(page),
    }
    for keyword in LICENCE_KEYWORDS:
        hit = re.search(re.escape(keyword), text, flags=re.I)
        if hit:
            overview["licence_snippets"][keyword] = text[max(0, hit.start() - 200):hit.end() + 200].strip()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as out:
            json.dump(overview, out, ensure_ascii=False, indent=1)
    print(f"bytes: {overview['bytes']}")
    print(f"script srcs ({len(overview['script_srcs'])}):")
    for src in overview["script_srcs"]:
        print("  ", src[:140])
    print("hosts:", overview["hosts"][:25])
    print("platform hints:", overview["platform_hints"][:15])
    for keyword, snippet in overview["licence_snippets"].items():
        print(f"[{keyword}] {snippet}")
    if overview["all_configs_structure"]:
        print("$allConfigs structure:")
        for key, info in overview["all_configs_structure"].items():
            print(f"   {key}: {info}")


if __name__ == "__main__":
    main()
