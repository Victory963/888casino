#!/usr/bin/env python3
"""List the lazily loaded chunks declared by a webpack 5 runtime file.

Reads the `"static/js/" + ({id: name}[e] || e) + "." + {id: hash}[e] + suffix`
expression from the runtime (parsed as text, never executed), writes one TSV
row per chunk and prints a name-family breakdown (trailing digits collapsed).

Usage: python3 -I tools/webpack_chunk_inventory.py runtime.<hash>.js [--tsv out.tsv]
"""
import argparse
import re
from collections import defaultdict


def parse_runtime(runtime):
    start = runtime.index('"static/js/"')
    segment = runtime[start:start + 40000]
    maps = re.findall(r'\{((?:\d+:"[^"]*",?)+)\}', segment)
    names = dict(re.findall(r'(\d+):"([^"]+)"', maps[0]))
    hashes = dict(re.findall(r'(\d+):"([^"]+)"', maps[1]))
    tail = re.search(r'\}\[e\]\+"([^"]+)"', segment)
    suffix = tail.group(1) if tail else ""
    rows = [(int(cid), names.get(cid, cid), digest, f"{names.get(cid, cid)}.{digest}{suffix}")
            for cid, digest in hashes.items()]
    return sorted(rows), names


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("runtime_js")
    parser.add_argument("--tsv", help="write chunk_id, name, hash, filename rows here")
    args = parser.parse_args()

    rows, names = parse_runtime(open(args.runtime_js, encoding="utf-8").read())
    if args.tsv:
        with open(args.tsv, "w", encoding="utf-8") as out:
            out.write("chunk_id\tname\thash\tfilename\n")
            for row in rows:
                out.write("\t".join(map(str, row)) + "\n")

    families = defaultdict(list)
    for name in names.values():
        families[re.sub(r"\d+$", "#", name)].append(name)
    print(f"chunks: {len(rows)}  named: {len(names)}")
    for family, members in sorted(families.items(), key=lambda item: (-len(item[1]), item[0])):
        print(f"{len(members):4d}  {family}")


if __name__ == "__main__":
    main()
