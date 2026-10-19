#!/usr/bin/env python3
"""Check every package page against the release asset it points at.

A page is a promise: a URL, a size and a sha256. This walks the pages and
checks that promise against the release the URL names -- the asset must exist,
with the same size and the same sha256 (GitHub reports the digest on each
asset now). It also reports assets that no page names, which is how a payload
gets published and either never offered, or removed from the pages and left
behind.

    python3 tools/audit.py            # uses GITHUB_TOKEN/GH_TOKEN if present

Unauthenticated works too -- the API is public and this needs one or two
requests per release -- but a token is kinder to the rate limit.
"""

import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, os.pardir, "iso", "copper", "pkg"))
PAGE = re.compile(
    r"^https://github\.com/([^/]+)/([^/]+)/releases/download/([^/]+)/(.+)$")


def api(url, token):
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "copper-ingot-repo-tools"}
    if token:
        headers["Authorization"] = "Bearer " + token
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as resp:
        return json.load(resp)


def pages():
    for category in sorted(os.listdir(PKG)):
        catdir = os.path.join(PKG, category)
        if not os.path.isdir(catdir):
            continue
        for name in sorted(os.listdir(catdir)):
            with open(os.path.join(catdir, name), encoding="utf-8") as fh:
                yield category, name, json.load(fh)


def assets_for(owner, repo, tag, token, cache):
    key = (owner, repo, tag)
    if key in cache:
        return cache[key]
    # Resolve the tag to a release id first: the assets route is keyed on the
    # release, and /releases/tags/<tag>/assets is not a route GitHub serves.
    release = api("https://api.github.com/repos/%s/%s/releases/tags/%s"
                  % (owner, repo, tag), token)
    rid = release["id"]
    found, page = {}, 1
    while True:
        url = ("https://api.github.com/repos/%s/%s/releases/%s/assets?per_page=100&page=%d"
               % (owner, repo, rid, page))
        batch = api(url, token)
        if not batch:
            break
        for asset in batch:
            found[asset["name"]] = asset
        if len(batch) < 100:
            break
        page += 1
    cache[key] = found
    return found


def main():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    cache, problems, wanted = {}, [], {}

    for category, name, page in pages():
        match = PAGE.match(page.get("url", ""))
        if not match:
            problems.append("%s: url is not a release download: %r"
                            % (name, page.get("url")))
            continue
        owner, repo, tag, asset = match.groups()
        wanted[(owner, repo, tag, asset)] = name

        try:
            found = assets_for(owner, repo, tag, token, cache)
        except Exception as exc:  # network, auth, missing release
            problems.append("%s: cannot list %s/%s %s: %s"
                            % (name, owner, repo, tag, exc))
            continue

        got = found.get(asset)
        if got is None:
            problems.append("%s: no asset named %s on %s" % (name, asset, tag))
            continue
        if got["size"] != page.get("size"):
            problems.append("%s: size page=%s asset=%s"
                            % (name, page.get("size"), got["size"]))
        digest = got.get("digest") or ""
        if digest.startswith("sha256:"):
            if digest.split(":", 1)[1].lower() != (page.get("sha256") or "").lower():
                problems.append("%s: sha256 page=%s asset=%s"
                                % (name, page.get("sha256"), digest))
        else:
            problems.append("%s: asset reports no digest, cannot verify sha256" % name)

    orphans = []
    for (owner, repo, tag), found in cache.items():
        for asset in sorted(found):
            if (owner, repo, tag, asset) not in wanted:
                orphans.append("%s/%s %s %s" % (owner, repo, tag, asset))

    print("== pages: %d, releases: %d" % (len({(o, r, t) for o, r, t, _ in wanted}),
                                          len(cache)))
    for o in orphans:
        print("== asset with no page: %s" % o)
    for p in problems:
        print("!! %s" % p)
    print("== problems: %d" % len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
