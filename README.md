# copper-ingot-repo

the package repos

Default repo URL (used by ingot unless `INGOT_REPO` or `/etc/ingot.conf`
overrides it):

    https://12hrformat.github.io/copper-ingot-repo

## Layout

    iso/copper/pkg/index.json              name -> category, one entry per line
    iso/copper/pkg/<category>/<name>       one JSON page per package (no extension)

What ingot fetches, exactly:

1. `<repo-url>/iso/copper/pkg/index.json`
   — maps a package name to its category
2. `<repo-url>/iso/copper/pkg/<category>/<name>`
   — the package's JSON page

`.nojekyll` sits at the repo root so Pages serves every file verbatim,
including the extensionless package pages.

## index.json format

One `name -> category` entry per line. ingot finds an entry with a sed line
matcher, so each entry must **start the line** (after optional whitespace) and
its `: "value"` must be on the **same line**:

```json
{
  "libpcap": "libs",
  "nmap": "hacking",
  "tcpdump": "network",
  "tree": "tools"
}
```

The category is also the directory the page lives in: `"tcpdump": "network"`
means the page is at `iso/copper/pkg/network/tcpdump`.

## Package page format

One key per line, values on the same line as the key. Strings are
double-quoted; `size` is the one unquoted integer (`"size": 533377`).
`depends` is the ONLY array and must be on a single line. Pretty-print — a
minified one-line file will break ingot, whose parser is a sed line-matcher,
not a JSON parser.

```json
{
  "name": "tcpdump",
  "version": "4.99.7-1",
  "category": "network",
  "url": "https://github.com/12hrformat/copper-ingot-repo/releases/download/payloads-v1/tcpdump-4.99.7-1.tar.gz",
  "size": 533377,
  "sha256": "6ae1d621c17e1931747ad6fdb31e67e8f7299437b589ed66ec580cc2d2b0e8a2",
  "depends": ["libpcap"]
}
```

Field rules:

| field | required | shape |
| --- | --- | --- |
| `name` | yes | string, same line as the key |
| `version` | yes | string |
| `category` | yes | string, must match `index.json` and the directory |
| `url` | yes | string — the REAL payload tarball (a Release asset) |
| `sha256` | yes | string — 64-char hex of that exact tarball |
| `size` | no | unquoted integer, the payload's byte count — ingot draws a live download bar only when this is present |
| `depends` | no | single-line array `["a","b"]`, empty `[]`, or omit the line |

If `url` or `sha256` is missing, ingot refuses to install — by design. Key
order does not matter; field **names** must match exactly.

## The payload (`url` + `sha256`)

- `url` points at a `.tar.gz` attached to a **GitHub Release** of this repo
  (Pages never holds binaries) and must be reachable with no auth:
  `https://github.com/12hrformat/copper-ingot-repo/releases/download/<tag>/<asset>`
- `sha256` is the SHA-256 of that exact tarball's bytes:

      sha256sum <file> | awk '{print $1}'

  If you replace the asset, the bytes (and the hash) change — recompute it.

- The tarball's contents are extracted **relative to `/`** on the target
  system, so it must contain real filesystem paths only:

      usr/bin/tcpdump
      usr/lib/libpcap.so.1
      usr/share/man/man1/tcpdump.1

- It MUST NOT contain absolute paths (leading `/`) or any `..` path segment;
  ingot scans `tar -tzf` output and refuses the payload outright if it does.
  Build it that way from the start:

      tar -czf hello-1.0-1.tar.gz -C staging usr

## Packages

| package | category | version | depends |
| --- | --- | --- | --- |
| hypr-configs | desktop | 9c2e40f | — |
| nmap | hacking | 7.95-1 | libpcap |
| liblzma5 | libs | 5.6.1+really5.4.5-1ubuntu0.3 | — |
| libncurses6 | libs | 6.4+20240113-1ubuntu2.2 | — |
| libpcap | libs | 1.11.0-1 | — |
| libpcre2-8-0 | libs | 10.42-4ubuntu2.1 | — |
| libpng16-16t64 | libs | 1.6.43-5ubuntu0.7 | — |
| libreadline8t64 | libs | 8.2-4build1 | ncurses-base |
| libsqlite3-0 | libs | 3.45.1-1ubuntu2.8 | — |
| libssl3t64 | libs | 3.0.13-0ubuntu3.16 | — |
| libxml2 | libs | 2.9.14+dfsg-1.3ubuntu3.10 | — |
| libzstd1 | libs | 1.5.5+dfsg2-2build1.1 | — |
| ncurses-base | libs | 6.4+20240113-1ubuntu2.2 | — |
| zlib1g | libs | 1:1.3.dfsg-3.1ubuntu2.2 | — |
| discord | network | 1.0.161 | — |
| tcpdump | network | 4.99.7-1 | libpcap |
| 7zip | tools | 23.01+dfsg-11 | — |
| bat | tools | 0.24.0-1build1 | — |
| btop | tools | 1.3.0-1 | — |
| curl | tools | 8.5.0-2ubuntu10.15 | — |
| duf | tools | 0.8.1-1ubuntu0.24.04.3 | — |
| fastfetch | tools | 2.69.0 | — |
| fd-find | tools | 9.0.0-1 | — |
| file | tools | 1:5.45-3build1 | — |
| firefox | tools | 157.0.1-1 | — |
| fzf | tools | 0.44.1-1ubuntu0.3 | — |
| git | tools | 1:2.43.0-1ubuntu7.3 | — |
| htop | tools | 3.3.0-4build1 | ncurses-base |
| jq | tools | 1.7.1-3ubuntu0.24.04.2 | — |
| less | tools | 590-2ubuntu2.1 | ncurses-base |
| lsof | tools | 4.95.0-1build3 | — |
| mousepad | tools | 0.6.1-1build2 | — |
| nano | tools | 7.2-2ubuntu0.2 | ncurses-base |
| ncdu | tools | 1.19-0.1 | ncurses-base |
| ripgrep | tools | 14.1.0-1 | — |
| ristretto | tools | 0.13.1-1build2 | — |
| rsync | tools | 3.2.7-1ubuntu1.5 | — |
| strace | tools | 6.8-0ubuntu2 | — |
| tmux | tools | 3.4-1ubuntu0.1 | ncurses-base |
| tree | tools | 2.3.2-1 | — |
| unzip | tools | 6.0-28ubuntu4.1 | — |
| vim-tiny | tools | 2:9.1.0016-1ubuntu7.20 | ncurses-base |
| wget | tools | 1.21.4-1ubuntu4.5 | — |
| xarchiver | tools | 1:0.5.4.22-1build2 | — |
| xfce4-taskmanager | tools | 1.5.7-1build1 | — |
| zip | tools | 3.0-13ubuntu0.2 | — |
| zsh | tools | 5.9-6ubuntu2 | ncurses-base |

All payloads are x86_64 Linux (glibc). They come from two build styles:

- **Upstream source** (the original set): `libpcap`/`tcpdump` from tcpdump.org
  releases, `nmap` from nmap.org 7.95, `tree` from
  [Old-Man-Programmer/tree](https://github.com/Old-Man-Programmer/tree),
  stripped, and staged with `tar -czf out.tar.gz -C <staging> usr`.
- **Ubuntu 24.04 (noble) debs** (the larger set added later — `firefox`,
  `discord`, the desktop apps, the CLI tools and the `libs/*` packages):
  unpacked from noble `.deb`s and bundled with each package's **full dependency
  closure**, so a single payload already carries everything it needs. `discord`
  and `fastfetch` are packaged from the vendor `.deb`, since neither is in any
  apt repo.

Because the deb-based payloads bundle their closure, `depends` is mostly empty
for them — the libraries are already inside the tarball. There are two
exceptions:

- `tcpdump` and `nmap` keep the older split style: both binaries have
  `libpcap.so.1` as a dynamic `NEEDED` entry, and their pages carry
  `"depends": ["libpcap"]`, so `ingot install tcpdump` (or `nmap`) installs
  `libpcap` first.
- The ncurses programs (`nano`, `less`, `vim-tiny`, `htop`, `ncdu`, `tmux`,
  `zsh`) and the `libreadline8t64` library depend on `ncurses-base`. ncurses
  reads the terminfo database at runtime, and terminfo ships in `ncurses-base` —
  an `Essential: yes` package that a closure walk against an empty dpkg status
  never pulls in. Without it any full-screen program dies with
  `Error opening terminal: linux.` on the VGA console.

`hypr-configs` is the one **non-deb, non-binary** payload: it is Copper's own
Hyprland configuration tree (the ML4W-derived dotfiles from
`12hrformat/copper-hyprland-configs`), staged at
`usr/share/copper/hyprland-skel/`. It ships no ELF, so it has no dependency
closure and declares none. It exists so the first Hyprland login can refresh
the config the ISO baked in: `starthyprland` offers it
(`would you like your hyprland config files?`) and installs it with
`ingot install hypr-configs`. It is data for the session, not the compositor —
see "Deliberately not packaged" for why the compositor itself is not a package.

`neofetch` was dropped in favour of `fastfetch`: it is a bash script and the
image has no `bash`, so it installed but could not run at all. `fastfetch` is a
compiled binary and runs as-is.

These payloads are verified locally (sha256 matches the page, tar has no
absolute or `..` paths) but have **not** been boot-tested on a running Copper
image. `hypr-configs` is verified the same way: the published `9c2e40f` asset
hashes to the `sha256` in its page, the tar carries only `usr/...` paths, and
its scripts keep their `+x` bit.

## Deliberately not packaged

`hyprland` is a Wayland compositor, not an application: it needs a running
Wayland session plus a seat manager (`seatd`/`logind`) to take the seat, while
Copper's live image boots under busybox init. Nothing installable would make it
start, so it is a v1.2 project, not a package. Shipping it would only add a
payload that cannot run. (The compositor is instead baked into the ISO by the
`hypr` build stage, behind the first-boot wizard's Desktop question. The
*config* for that session **is** packaged — `hypr-configs` above — because it
is plain files with no runtime to satisfy.)

## Adding a package

1. **Stage and build the tarball.** Contents extract relative to `/`; use
   `usr/...` paths only — no absolute paths, no `..`:

       mkdir -p staging/usr/bin
       cp hello staging/usr/bin/
       tar -czf hello-1.0-1.tar.gz -C staging usr
       tar -tzf hello-1.0-1.tar.gz     # inspect: usr/... only

2. **Upload it to a Release** (Pages is not for binaries):

       gh release create payloads-v1 hello-1.0-1.tar.gz
       # or, if the release already exists:
       gh release upload payloads-v1 hello-1.0-1.tar.gz

3. **Compute the sha256 of the exact asset bytes** (the file you just
   uploaded — hash it locally, don't rebuild after hashing):

       sha256sum hello-1.0-1.tar.gz | awk '{print $1}'

4. **Write the page** at `iso/copper/pkg/<category>/<name>` (one file per
   package, no extension), pretty-printed, one key per line:

       {
         "name": "hello",
         "version": "1.0-1",
         "category": "tools",
         "url": "https://github.com/12hrformat/copper-ingot-repo/releases/download/payloads-v1/hello-1.0-1.tar.gz",
         "size": <payload bytes>,
         "sha256": "<64-char hex of the payload tarball>",
         "depends": []
       }

5. **Add the name to `index.json`**, on its own line:

       "hello": "tools",

6. **Commit and push.** GitHub Pages republishes from `main` (root) within a
   minute or so.

## Verifying

Point ingot at the site and install into a scratch root — it never touches
your real filesystem this way (`ingot` is
`iso/rootfs-overlay/usr/bin/ingot` in `12hrformat/copper`):

    INGOT_REPO="https://12hrformat.github.io/copper-ingot-repo" \
    INGOT_ROOT="$PWD/scratch" \
    sh ingot install tcpdump

Success prints:

    ingot: installed libpcap
    ingot: installed tcpdump

and the files appear under `scratch/` (`scratch/usr/bin/tcpdump`,
`scratch/usr/lib/libpcap.so.1`, ...). ingot also records an installed
manifest under `<root>/var/lib/ingot/`, verifies the payload sha256 before
unpacking, and deletes the package JSON from `/tmp` when it is done.