#!/usr/bin/env python3
"""Inventory source maps: original source paths and npm package usage.

Reports only metadata (paths, counts, whether sourcesContent is present). It
never prints or copies the embedded original source text.

Usage: python3 -I tools/sourcemap_inventory.py DIR_WITH_MAPS [--paths out.txt] [--packages out.tsv]
"""
import argparse
import json
import os
import re
from collections import Counter


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("directory")
    parser.add_argument("--paths", help="write '<map file>\\t<original source path>' rows here")
    parser.add_argument("--packages", help="write '<package>\\t<module count>' rows here")
    args = parser.parse_args()

    path_rows = []
    packages = Counter()
    for name in sorted(os.listdir(args.directory)):
        if not name.endswith(".map"):
            continue
        source_map = json.load(open(os.path.join(args.directory, name), encoding="utf-8"))
        sources = source_map.get("sources", [])
        contents = source_map.get("sourcesContent") or []
        print(f"== {name}: {len(sources)} sources, sourcesContent {sum(1 for c in contents if c)}")
        for source in sources:
            path_rows.append((name, source))
            package = re.search(r"node_modules/((?:@[^/]+/)?[^/]+)", source)
            if package:
                packages[package.group(1)] += 1

    if args.paths:
        with open(args.paths, "w", encoding="utf-8") as out:
            out.write("map_file\tsource_path\n")
            for row in path_rows:
                out.write("\t".join(row) + "\n")
    if args.packages:
        with open(args.packages, "w", encoding="utf-8") as out:
            out.write("package\tmodules\n")
            for package, count in packages.most_common():
                out.write(f"{package}\t{count}\n")
    print("npm packages:", ", ".join(f"{p}({c})" for p, c in packages.most_common(60)))


if __name__ == "__main__":
    main()
