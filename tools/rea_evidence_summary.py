#!/usr/bin/env python3
"""Summarize REA Evidence produced by this project.

Handles two shapes:
  * an `analyze_javascript_application` evidence bundle written by
    `rea analyze-javascript-application ... --evidence_output FILE`
  * an `analyze_web_bundle` Evidence record saved as JSON

Prints counts, coverage, recovered chunks/endpoints/storage/workers, and
(for web bundles) the captured script inventory. Script text is never printed.

Usage: python3 -I tools/rea_evidence_summary.py EVIDENCE.json [--json out.json]
"""
import argparse
import json
from collections import Counter


def summarize_application(record):
    result = record["normalized_result"]
    graph = result["graph"]
    semantic = result["semantic_graph"]
    by_kind = Counter(node.get("kind") for node in graph["nodes"])

    def keys(kind):
        return sorted({node["identity"].get("key", "") for node in graph["nodes"] if node.get("kind") == kind})

    return {
        "evidence_id": record["evidence_id"],
        "operation": record["operation"],
        "statistics": result["statistics"],
        "graph_coverage": graph["coverage"],
        "graph_node_kinds": dict(by_kind),
        "module_namespaces": dict(Counter(node["identity"].get("namespace") for node in graph["nodes"]
                                          if node.get("kind") == "javascript-module")),
        "source_modules": sorted(node["identity"].get("original_source", "") for node in graph["nodes"]
                                 if node.get("kind") == "source-module"),
        "endpoints": keys("endpoint"),
        "storage": keys("storage"),
        "workers": keys("worker"),
        "semantic_node_kinds": dict(Counter(node.get("kind") for node in semantic["nodes"]).most_common()),
        "semantic_relations": len(semantic["relations"]),
        "semantic_unknowns": len(semantic["unknowns"]),
        "limitations": result["limitations"],
    }


def summarize_web_bundle(record):
    result = record["normalized_result"]
    observations = result["observations"]
    return {
        "evidence_id": record["evidence_id"],
        "operation": record["operation"],
        "target_url": result["capture"]["target_url"],
        "allowed_origins": record["parameters"].get("allowed_origins"),
        "completeness": result["completeness"],
        "scripts": [{"url": node["url"], "bytes": node["bytes"], "sha256": node["artifact_sha256"]}
                    for node in observations["chunks"]["nodes"]],
        "chunk_edges": [{"specifier": edge["specifier"], "resolved_url": edge["resolved_url"]}
                        for edge in observations["chunks"]["edges"]],
        "routes": [route["value"] for route in observations["routes"]],
        "endpoints": [endpoint["value"] for endpoint in observations["endpoints"]],
        "source_maps": [{"declared_url": item["declared_url"], "status": item["status"]}
                        for item in observations["source_maps"].get("items", [])],
        "low_confidence_inferences": len(result["inferences"]),
        "limitations": result["limitations"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("evidence_json")
    parser.add_argument("--json", help="write the summary as JSON to this path")
    args = parser.parse_args()

    data = json.load(open(args.evidence_json, encoding="utf-8"))
    if "records" in data:
        summary = [summarize_application(record) for record in data["records"]
                   if record["operation"] == "analyze_javascript_application"]
    else:
        summary = [summarize_web_bundle(data)]

    if args.json:
        with open(args.json, "w", encoding="utf-8") as out:
            json.dump(summary, out, ensure_ascii=False, indent=1)
    for item in summary:
        print(json.dumps({k: v for k, v in item.items()
                          if k not in ("source_modules", "limitations", "scripts")}, ensure_ascii=False, indent=1))
        if "scripts" in item:
            for script in item["scripts"]:
                print(f"   {script['bytes']:>9}  {script['url'][:110]}")


if __name__ == "__main__":
    main()
