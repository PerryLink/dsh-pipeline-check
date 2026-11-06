#!/usr/bin/env python3
"""Generate README image assets for dsh-pipeline-check (docs/assets/).

dsh-pipeline-check is a no-UI checker plugin, so the hero is a hand-written
SVG flow diagram (vector — never rasterized to webp):

  dsh-pipeline-check-flow-light.svg / dsh-pipeline-check-flow-dark.svg
      material → parseMaterial → rulesFile → runCheck → report.
      Text inside is command-surface tokens only (tool name, config keys,
      rule ids, report fields), so all five README languages share one pair.

There is no benchmark directory in this repository, so no evidence chart is
emitted. The PerryLink palette and the CJK font probe are kept identical to
the family skeleton: the probe aborts loudly instead of ever rendering a CJK
label as tofu boxes, and future raster assets (webp, quality 90) must reuse
it.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow (pip install pillow)
"""
from __future__ import annotations

import os
import sys

from PIL import ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

# --- palette: PerryLink family (accent) + GitHub page backgrounds ----------
FAMILY = "#4B67B4"   # family accent (badges use labelColor #2B3245)
SKIN = {
    "light": dict(bg="#ffffff", box="#f6f8fa", border="#d0d7de",
                  text="#1f2328", sub="#57606a", track="#eaeef2"),
    "dark": dict(bg="#0d1117", box="#161b22", border="#30363d",
                 text="#f0f6fc", sub="#8b949e", track="#21262d"),
}

# --- CJK font probe: Chinese must never render as tofu boxes ----------------
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",      # Microsoft YaHei
    r"C:\Windows\Fonts\simhei.ttf",    # SimHei
    r"C:\Windows\Fonts\Deng.ttf",      # DengXian
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if FONT_PATH is None:
    sys.exit("FATAL: no CJK font found (looked for msyh.ttc, simhei.ttf, "
             "Deng.ttf, Noto Sans CJK, PingFang). Refusing to render Chinese "
             "as tofu boxes; install one of the probed fonts and re-run.")


def probe_font() -> None:
    """Load the CJK face once so a corrupt font fails here, not at draw time."""
    ImageFont.truetype(FONT_PATH, 24)


# ---------------------------------------------------------------------------
# Hero flow SVG (light + dark)
# ---------------------------------------------------------------------------
# (label, sub line 1, sub line 2 or None). Every string is a command token:
# tool/function names, config keys, rule ids, or report field names.
FLOW_NODES = [
    ("material", "file | material", None),
    ("parseMaterial", "stage · document · docNo", None),
    ("rulesFile", "rules/pipeline-check.yaml", "PC-001 … PC-008"),
    ("runCheck", "order · terms", "notBeforeField"),
    ("report", "findings · skipped", None),
]


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    w, h = 1200, 400
    nw, nh, gap = 180, 104, 45
    y0 = 150
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="dsh-pipeline-check workflow">',
        '<title>dsh-pipeline-check workflow</title>',
        f'<rect width="{w}" height="{h}" rx="18" fill="{s["bg"]}"/>',
        f'<text x="60" y="62" fill="{s["text"]}" font-family="ui-sans-serif,'
        f'system-ui,sans-serif" font-size="30" font-weight="700">'
        f'dsh-pipeline-check</text>',
        f'<text x="60" y="94" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="16">pipeline_check · JSON · YAML · '
        f'rules/pipeline-check.yaml</text>',
        f'<line x1="60" y1="116" x2="1140" y2="116" stroke="{s["border"]}"/>',
    ]
    for i, (label, sub1, sub2) in enumerate(FLOW_NODES):
        x = 60 + i * (nw + gap)
        accent = FAMILY if i in (2, 4) else s["border"]
        parts.append(
            f'<rect x="{x}" y="{y0}" width="{nw}" height="{nh}" rx="14" '
            f'fill="{s["box"]}" stroke="{accent}" stroke-width="2"/>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 38}" fill="{s["text"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="15" font-weight="700">{label}</text>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 64}" fill="{s["sub"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="11">{sub1}</text>')
        if sub2 is not None:
            parts.append(
                f'<text x="{x + nw // 2}" y="{y0 + 84}" fill="{s["sub"]}" '
                f'text-anchor="middle" font-family="ui-monospace,monospace" '
                f'font-size="11">{sub2}</text>')
        if i < len(FLOW_NODES) - 1:
            ax = x + nw + 6
            ay = y0 + nh // 2
            parts.append(
                f'<path d="M{ax} {ay}h{gap - 12}" stroke="{s["sub"]}" '
                f'stroke-width="3"/>')
            parts.append(
                f'<path d="M{ax + gap - 14} {ay - 7}l10 7-10 7" fill="none" '
                f'stroke="{s["sub"]}" stroke-width="3" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')
    # Report-shape bar under nodes 2..4 (same composition as the family hero).
    bx, bw, by, bh = 285, 630, 300, 50
    for cx in (375, 825):
        parts.append(
            f'<path d="M{cx} {y0 + nh}v{by - y0 - nh}" '
            f'stroke="{FAMILY}" stroke-width="2" stroke-dasharray="5 5"/>')
    parts.append(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="12" '
        f'fill="{s["box"]}" stroke="{FAMILY}" stroke-width="2"/>')
    parts.append(
        f'<text x="{bx + bw // 2}" y="{by + 31}" fill="{s["text"]}" '
        f'text-anchor="middle" font-family="ui-monospace,monospace" '
        f'font-size="12">report · id · ruleId · severity · locator · '
        f'found · expected · fix</text>')
    parts.append(
        f'<text x="60" y="382" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="13">checkedAt · rulesetVersion · '
        f'issueCount · skippedCount · target</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> None:
    probe_font()
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        name = f"dsh-pipeline-check-flow-{skin}.svg"
        with open(os.path.join(OUT, name), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(flow_svg(skin))
    print("wrote 2 SVG assets to docs/assets/ "
          "(no benchmark data: no evidence chart)")


if __name__ == "__main__":
    main()
