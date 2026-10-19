#!/usr/bin/env python3
"""Regenerate iso/copper/pkg/index.json from the package pages.

The page files are the source of truth, not the index. The index only maps a
name to the category directory that holds its page, so it can always be
rebuilt -- and rebuilt from scratch is the only way to keep it honest, because
the failure mode of a stale index is a name with no payload behind it.

ingot reads the index as *text*, one key per line (it is a POSIX sh script
with no JSON parser -- see `category_for()`), so the output must stay
`"name": "category"` on one line each. It is also written as strict JSON
(`json.dump`) so that jq, a browser's JSON viewer, or any other client can
read it. The very first version of this generator emitted every line but the
closing brace, which is valid enough for ingot and invalid for everything
else -- hence the re-read and assert at the end.

Usage:
    python3 tools/index.py           # validate, then write index.json
    python3 tools/index.py --check   # validate, and fail if index.json is stale
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, os.pardir, "iso", "copper", "pkg"))
INDEX = os.path.join(PKG, "index.json")
SHA256 = re.compile(r"^[0-9a-f]{64}$")

problems = []
notes = []


def problem(msg):
    problems.append(msg)


def load_pages():
    """Every page, as {name: (category, page)}. Reports what it cannot read."""
    pages = {}
    for category in sorted(os.listdir(PKG)):
        catdir = os.path.join(PKG, category)
        if not os.path.isdir(catdir):
            continue
        for name in sorted(os.listdir(catdir)):
            path = os.path.join(catdir, name)
            rel = "%s/%s" % (category, name)

            try:
                with open(path, encoding="utf-8") as fh:
                    page = json.load(fh)
            except ValueError as exc:
                problem("BAD json: %s (%s)" % (rel, exc))
                continue
            if not isinstance(page, dict):
                problem("BAD json: %s is not an object" % rel)
                continue

            if page.get("name") != name:
                problem("BAD name: %s says name=%r" % (rel, page.get("name")))
            if page.get("category") != category:
                problem("BAD category: %s says category=%r" % (rel, page.get("category")))
            if not page.get("version"):
                problem("BAD version: %s" % rel)
            if not page.get("url"):
                problem("BAD url: %s" % rel)
            sha = page.get("sha256") or ""
            if not SHA256.match(sha):
                problem("BAD sha256: %s -> %r" % (rel, sha))
            if not isinstance(page.get("size"), int) or page.get("size", 0) <= 0:
                problem("BAD size: %s -> %r" % (rel, page.get("size")))
            if not isinstance(page.get("depends"), list):
                problem("BAD depends: %s -> %r" % (rel, page.get("depends")))

            if name in pages:
                problem("BAD duplicate name: %s and %s/%s" % (pages[name][0], category, name))
                continue
            pages[name] = (category, page)
    return pages


def check_depends(pages):
    for name, (category, page) in sorted(pages.items()):
        for dep in page.get("depends") or []:
            if dep not in pages:
                problem("BAD depends: %s/%s needs %r, which has no page"
                        % (category, name, dep))


def orphan_assets_not_checkable():
    notes.append(
        "assets on the release are not checked here -- tools/audit.py does that "
        "against the GitHub API")


def write(wanted):
    with open(INDEX, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(wanted, fh, indent=2, sort_keys=True)
        fh.write("\n")

    # Prove the file we just wrote is both valid JSON and what we meant.
    with open(INDEX, encoding="utf-8") as fh:
        back = json.load(fh)
    if back != wanted:
        problem("WROTE an index that does not read back the same")
    return wanted


def read_index():
    try:
        with open(INDEX, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None
    except ValueError as exc:
        problem("index.json on disk is not valid JSON: %s" % exc)
        return None


def main():
    check = "--check" in sys.argv[1:]

    pages = load_pages()
    names = {name: category for name, (category, _) in pages.items()}

    for name, (category, page) in sorted(pages.items()):
        for dep in page.get("depends") or []:
            if dep not in names:
                problem("BAD depends: %s/%s needs %r, which has no page"
                        % (category, name, dep))

    print("== pages: %d across %s" % (
        len(pages), ", ".join(sorted({c for c, _ in pages.values()}))))

    if check:
        on_disk = read_index()
        if on_disk is None:
            problem("index.json is missing or unreadable")
        elif on_disk != names:
            only_disk = sorted(set(on_disk) - set(names))
            only_pages = sorted(set(names) - set(on_disk))
            problem("index.json is stale: on disk only=%s, in pages only=%s"
                    % (only_disk or "-", only_pages or "-"))
        else:
            print("== index.json matches the pages")
    else:
        wanted = write(names)
        print("== wrote index.json: %d entries, %d bytes"
              % (len(wanted), os.path.getsize(INDEX)))

    for note in notes:
        print("== note: %s" % note)
    for p in problems:
        print("!! %s" % p)
    print("== problems: %d" % len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
