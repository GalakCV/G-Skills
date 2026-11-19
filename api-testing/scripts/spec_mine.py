#!/usr/bin/env python3
"""Mine an OpenAPI/Swagger spec into a ranked test list. The spec is intel, not a bug.

Emits, from the spec alone (no requests):
  - endpoints declared WITHOUT auth (security: [] or missing) -> test these first
  - Bearer-protected GETs                                     -> no-token test candidates
  - path-param endpoints ({id}, {uuid})                       -> BOLA candidates
  - interesting-by-name endpoints (admin/export/token/...)
  - servers block (leaked environments/hosts)

Usage: spec_mine.py <spec.json>
"""
import sys
import json
import re

INTERESTING = re.compile(r"admin|internal|export|debug|token|key|secret|config|upload|import|bulk|download|user|account|proxy|webhook", re.I)


def op_security(op, global_sec):
    sec = op.get("security", global_sec)
    return sec if sec is not None else global_sec


def main():
    spec = json.load(open(sys.argv[1]))
    global_sec = spec.get("security")
    paths = spec.get("paths", {})
    no_auth, bearer_gets, id_params, interesting = [], [], [], []
    for path, item in paths.items():
        if INTERESTING.search(path):
            interesting.append(path)
        if re.search(r"\{[^}]+\}", path):
            id_params.append(path)
        for method, op in (item or {}).items():
            if method.lower() not in ("get", "post", "put", "patch", "delete"):
                continue
            sec = op_security(op, global_sec)
            label = f"{method.upper()} {path}"
            if sec == [] or (sec is None and not global_sec):
                no_auth.append(label)
            elif method.lower() == "get" and sec:
                bearer_gets.append(label)

    def dump(title, items):
        print(f"\n## {title} ({len(items)})")
        for x in items[:60]:
            print(f"  {x}")

    print(f"servers: {spec.get('servers')}")
    dump("declared WITHOUT auth (test first)", no_auth)
    dump("auth-protected GETs (no-token test)", bearer_gets)
    dump("path-param endpoints (BOLA candidates)", id_params)
    dump("interesting by name", interesting)
    print("\nNote: the spec tells you WHERE to test, not that anything is broken.")


if __name__ == "__main__":
    main()
