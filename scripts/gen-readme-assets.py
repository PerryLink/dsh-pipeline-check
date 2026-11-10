#!/usr/bin/env python3
"""README visuals for dsh-pipeline-check — derived from the plugin's real pipeline.

Two figures, both read off the shipped material rather than a generic template:

  hero 1440×576 (Pillow, 4 files: zh/en × light/dark)
      The material the plugin actually reads: one project whole-process file-chain
      ledger (project header + one row per stage file). The right card is the
      stage chain itself — each link carries its document number, amount and the
      approval→signing date pair. Three links carry the differences the rule pack
      reports (PC-005 repeated document number, PC-004 signing before approval,
      PC-006/PC-007 unparsable amount and template placeholder); below sit the two
      most characteristic findings and the report line that keeps the verdict with
      the reviewer. The left column carries the plugin name, its value lines and
      the rule-pack facts.

  flow 1100×660 (hand-written SVG, 2 files: light/dark)
      A three-column checking bench, not a left-to-right node chain: the material
      and the rule pack feed one pure core (`parseMaterial → runCheck`), which
      reads the stage chain under four comparison scopes — 台账级 (header, PC-001),
      行内 (one row: PC-002/004/006/007), 跨行 (two rows: PC-005/008) and 全链 (the
      whole chain against the configured order: PC-003). The chain panel marks the
      scopes in place; the right column carries the four scopes, the two output
      channels (`issues[]`, `skipped[]`) and the reviewer, and the footer states
      the evidence/severity caps and the read-only boundary.

Text values come from the repository's own fixtures, not from imagination:
  tests/fixtures/PC-002/PC-002-unsafe.json      (blank stage + document row)
  tests/fixtures/PC-004/PC-004-unsafe.json      (approved 2026-02-10, signed 2026-01-15)
  tests/fixtures/PC-005/PC-005-unsafe.json      (docNo `LX-2026- 001` repeats `LX-2026-001`)
  tests/fixtures/PC-006/PC-006-unsafe.json      (amount `待定`)
  tests/fixtures/PC-007/PC-007-unsafe.json      (document `【填写文件名称】`)
  rules/pipeline-check.yaml                     (PC-001..PC-008, order[] ships empty)
The five-row composite ledger below was run through the real core
(`parseMaterial` + `runCheck`) with checkedAt=2026-11-06: 5 issues, 1 skipped
(PC-003: 规则库未配置 order). That is the count the figures state.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow + Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf.
"""
from __future__ import annotations

import os
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

FONT_CJK = r"C:\Windows\Fonts\msyh.ttc"
FONT_CJK_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"
FONT_MONO_BOLD = r"C:\Windows\Fonts\consolab.ttf"
for _p in (FONT_CJK, FONT_CJK_BOLD, FONT_MONO, FONT_MONO_BOLD):
    if not os.path.exists(_p):
        raise SystemExit(f"FATAL: font missing: {_p}")

RADIUS = 22
SHADOW = 26

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", card_edge="#e6e2ef",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", accent2="#16a34a",
        pill="#ece7f9", band="#f5f2fb", grid="#e7e4f0",
        mark="#b45309", mark_bg="#fdf3e9",
        shadow=(32, 26, 64), glow2="#7a68c9",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", card_edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", accent2="#3fb950",
        pill="#242d42", band="#202839", grid="#262f42",
        mark="#d9a441", mark_bg="#2a2216",
        shadow=(0, 0, 0), glow2="#8496f5",
    ),
}

FONT_FILES = {"cjk": FONT_CJK, "cjk_bold": FONT_CJK_BOLD,
              "mono": FONT_MONO, "mono_bold": FONT_MONO_BOLD}


def font(size: int, kind: str = "cjk_bold") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], size)


def hx(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w: int, h: int, c1: str, c2: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(base)
    a, b = hx(c1), hx(c2)
    for y in range(h):
        t = 0.15 * (y / h) + 0.85 * (y / h) ** 1.35
        d.line([(0, y), (w, y)],
               fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base


def glow(img: Image.Image, cx: int, cy: int, r: int, color: tuple,
         alpha: int = 40) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(9, 0, -1):
        rr = r * i / 9
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=color + (int(alpha * (1 - i / 10)),))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def card(img: Image.Image, box: tuple, s: dict, radius: int = RADIUS,
         shadow: int = SHADOW, fill: str | None = None) -> Image.Image:
    """A soft-shadowed rounded card on the gradient background."""
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(shadow, 0, -3):
        sd.rounded_rectangle([x0 - i // 5, y0 + i // 2, x1 + i // 5, y1 + i],
                             radius=radius + i // 5,
                             fill=s["shadow"] + (int(9 * (1 - i / shadow)),))
    base = Image.alpha_composite(img.convert("RGBA"),
                                 sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill or s["card"]),
                        outline=hx(s["card_edge"]), width=2)
    return base.convert("RGB")


_SCRATCH = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def measure(text: str, size: int, kind: str) -> float:
    return _SCRATCH.textlength(text, font=font(size, kind))


def require_w(text: str, size: int, kind: str, max_w: float, what: str) -> None:
    """Fail loudly instead of shipping a clipped label."""
    w = measure(text, size, kind)
    if w > max_w + 0.4:
        raise SystemExit(f"FATAL: {what} overflows: {text!r} needs {w:.1f}px > {max_w}px")


def fit(text: str, kind: str, max_w: float, start: int, minimum: int) -> int:
    size = start
    while size > minimum:
        if measure(text, size, kind) <= max_w:
            return size
        size -= 1
    raise SystemExit(f"FATAL: text does not fit {max_w}px at >= {minimum}px: {text!r}")


def fit_lines(lines: list[str], kind: str, max_w: float, start: int,
              minimum: int) -> int:
    return min(fit(t, kind, max_w, start, minimum) for t in lines)


def pill(img: Image.Image, xy: tuple[int, int], text: str, s: dict,
         size: int = 16, fg: str | None = None, bg: str | None = None,
         kind: str = "cjk_bold") -> tuple[int, int]:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(text, font=f)
    x, y = xy
    h = size + 20
    d.rounded_rectangle([x, y, x + w + 30, y + h], radius=h // 2,
                        fill=hx(bg or s["pill"]))
    d.text((x + 15, y + h / 2), text, font=f, fill=hx(fg or s["accent"]),
           anchor="lm")
    return int(x + w + 30), int(y + h)


def chip(img: Image.Image, xy: tuple[int, int], text: str, fg: str, bg: str,
         size: int = 11, kind: str = "cjk_bold", padx: int = 9,
         height: int = 20) -> int:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(text, font=f)
    x, y = xy
    d.rounded_rectangle([x, y, x + w + padx * 2, y + height],
                        radius=height // 2, fill=hx(bg))
    d.text((x + padx, y + height / 2), text, font=f, fill=hx(fg), anchor="lm")
    return int(w + padx * 2)


# --------------------------------------------------------------------------- hero
# Every value below comes from the repository's own fixtures; see the module
# docstring for the row-by-row mapping.
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 项目全流程核对",
        value=["在台账进入评审之前完成核对", "哪一行、哪一栏、差什么，逐条指认"],
        sub=["核对台账自身的齐备与自洽：环节、日期、金额、编号",
             "只列差异，不判合规——结论留给审核人。"],
        meta="PC-001..PC-008 · 规则包即数据 · skipped 逐条说明",
        foot="Apache-2.0 · PerryLink DSH plugin family",
        card_title="项目全流程文件链条台账 · rows[]",
        card_chip="只读原件",
        project="某某技改项目 · XM-2026-018 · 建设单位 某某公司",
        nodes=[
            ("1", "立项 · 项目立项批复",
             "LX-2026-001 · 1200万元 · 批复 01-10 · 签署 01-15", None),
            ("2", "招标 · 项目立项批复",
             "LX-2026- 001 · 1200万元 · 批复 01-10 · 签署 01-15",
             "编号与上一环相同 → PC-005"),
            ("3", "合同 · 合同文本",
             "HT-2026-004 · 380万元 · 批复 02-10 · 签署 01-15",
             "签署早于批复 26 天 → PC-004"),
            ("4", "变更 · 【填写文件名称】",
             "BG-2026-001 · 待定 · 批复 03-02 · 签署 03-06",
             "金额不可解析 · 残留模板 → PC-006 · PC-007"),
        ],
        issue_a=dict(rule="PC-004", sev="warn",
                     d1="批复 2026-02-10", d2="签署 2026-01-15",
                     note="签署早 26 天 · 同一天视为不晚于"),
        issue_b=dict(rule="PC-005", sev="warn",
                     d1="LX-2026-001", d2="LX-2026- 001",
                     note="去空白后同号 · 命中需人工确认"),
        strip=("issues[] 差异清单 · skipped[] 未执行说明", "结论留给审核人"),
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · project chain checker",
        value=["Check the ledger before review", "each gap on a row and a column"],
        sub=["The register's own completeness and consistency:",
             "differences only — the reviewer decides."],
        meta="PC-001..PC-008 · rules are data · skipped always explained",
        foot="Apache-2.0 · PerryLink DSH plugin family",
        card_title="Project file-chain ledger · rows[]",
        card_chip="read-only",
        project="Some technical upgrade · XM-2026-018 · owner Some Co.",
        nodes=[
            ("1", "Initiation · project approval",
             "LX-2026-001 · 1200万元 · approved 01-10 · signed 01-15", None),
            ("2", "Tendering · project approval",
             "LX-2026- 001 · 1200万元 · approved 01-10 · signed 01-15",
             "same ID as link 1 → PC-005"),
            ("3", "Contract · contract text",
             "HT-2026-004 · 380万元 · approved 02-10 · signed 01-15",
             "signed 26 days early → PC-004"),
            ("4", "Change · 【file name】",
             "BG-2026-001 · TBD · approved 03-02 · signed 03-06",
             "amount unparsable · placeholder → PC-006 · PC-007"),
        ],
        issue_a=dict(rule="PC-004", sev="warn",
                     d1="approved 2026-02-10", d2="signed 2026-01-15",
                     note="26 days early · same day counts as not earlier"),
        issue_b=dict(rule="PC-005", sev="warn",
                     d1="LX-2026-001", d2="LX-2026- 001",
                     note="equal after dropping spaces · confirm by hand"),
        strip=("issues[] differences · skipped[] not executed", "verdict stays human"),
    ),
}


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    H = HERO[lang]
    W, HT = 1440, 576
    img = gradient(W, HT, s["bg_from"], s["bg_to"])
    img = glow(img, 1180, 30, 420, hx(s["accent"]),
               24 if skin == "light" else 38)
    img = glow(img, 90, 580, 300, hx(s["glow2"]),
               10 if skin == "light" else 16)

    d = ImageDraw.Draw(img)
    m = 64
    col_w = 580

    # ---- left column: kicker / title / value / sub / meta / footer -----------
    pill(img, (m, 52), H["kicker"], s, size=17)
    d = ImageDraw.Draw(img)

    title_size = fit("dsh-pipeline-check", "mono_bold", col_w, 58, 48)
    d.text((m - 2, 112), "dsh-pipeline-check",
           font=font(title_size, "mono_bold"), fill=hx(s["text"]))

    vf = fit_lines(H["value"], "cjk_bold", col_w, 42, 32)
    for i, line in enumerate(H["value"]):
        require_w(line, vf, "cjk_bold", col_w, "hero value")
        d.text((m, 200 + i * 56), line, font=font(vf, "cjk_bold"),
               fill=hx(s["text"]))

    sf = font(22, "cjk")
    for i, line in enumerate(H["sub"]):
        require_w(line, 22, "cjk", col_w, "hero sub")
        d.text((m + 1, 326 + i * 34), line, font=sf, fill=hx(s["sub"]))

    require_w(H["meta"], 19, "cjk", col_w, "hero meta")
    require_w(H["foot"], 16, "cjk", col_w, "hero footer")
    d.text((m + 1, 420), H["meta"], font=font(19, "cjk"), fill=hx(s["faint"]))
    d.line([m + 1, 462, m + col_w - 4, 462], fill=hx(s["grid"]), width=2)
    d.text((m + 1, 476), H["foot"], font=font(16, "cjk"), fill=hx(s["faint"]))

    # ---- right: the ledger chain --------------------------------------------
    img = card(img, (664, 36, 1376, 396), s, radius=RADIUS, shadow=SHADOW)
    d = ImageDraw.Draw(img)
    d.text((688, 58), H["card_title"], font=font(17, "cjk_bold"),
           fill=hx(s["accent"]))
    cw = measure(H["card_chip"], 11, "cjk")
    chip(img, (1352 - int(cw) - 18, 54), H["card_chip"], s["accent"], s["pill"],
         size=11)
    d = ImageDraw.Draw(img)
    d.text((688, 88), H["project"], font=font(13, "cjk"), fill=hx(s["sub"]))
    require_w(H["project"], 13, "cjk", 632, "project header")

    # the chain spine: order of registration, one link per stage file
    d.line([704, 116, 704, 342], fill=hx(s["grid"]), width=2)
    for i, (no, head, meta, flag) in enumerate(H["nodes"]):
        y = 126 + i * 70
        dot = hx(s["mark"]) if flag else hx(s["accent"])
        d.ellipse([698, y - 6, 710, y + 6], fill=dot)
        d.ellipse([696, y - 8, 712, y + 8], outline=dot, width=1)
        d.text((724, y - 9), no, font=font(14, "mono_bold"), fill=hx(s["accent"]))
        d.text((742, y - 10), head, font=font(15, "cjk_bold"),
               fill=hx(s["text"]))
        d.text((724, y + 11), meta, font=font(12, "cjk"), fill=hx(s["sub"]))
        require_w(no + " " + head, 15, "cjk_bold", 592, "node head")
        require_w(meta, 12, "cjk", 610, "node meta")
        if flag:
            d.text((724, y + 31), flag, font=font(11.5, "cjk"),
                   fill=hx(s["mark"]))
            require_w(flag, 11.5, "cjk", 610, "node flag")

    # ---- right: the two most characteristic findings -------------------------
    img = card(img, (664, 408, 1012, 508), s, radius=18, shadow=20)
    d = ImageDraw.Draw(img)
    A = H["issue_a"]
    d.text((682, 422), A["rule"], font=font(13, "mono_bold"),
           fill=hx(s["accent"]))
    w = measure(A["rule"], 13, "mono_bold")
    chip(img, (682 + int(w) + 8, 420), A["sev"], s["accent"], s["pill"], size=10)
    d = ImageDraw.Draw(img)
    d.text((682, 446), A["d1"], font=font(12, "cjk"), fill=hx(s["text"]))
    d.text((682, 468), A["d2"], font=font(12, "cjk"), fill=hx(s["text"]))
    d.text((682, 490), A["note"], font=font(11, "cjk"), fill=hx(s["mark"]))
    require_w(A["d1"], 12, "cjk", 310, "issue A date 1")
    require_w(A["d2"], 12, "cjk", 310, "issue A date 2")
    require_w(A["note"], 11, "cjk", 310, "issue A note")

    img = card(img, (1024, 408, 1376, 508), s, radius=18, shadow=20)
    d = ImageDraw.Draw(img)
    B = H["issue_b"]
    d.text((1042, 422), B["rule"], font=font(13, "mono_bold"),
           fill=hx(s["accent"]))
    w = measure(B["rule"], 13, "mono_bold")
    chip(img, (1042 + int(w) + 8, 420), B["sev"], s["accent"], s["pill"], size=10)
    d = ImageDraw.Draw(img)
    d.text((1042, 446), B["d1"], font=font(11.5, "mono"), fill=hx(s["text"]))
    d.text((1042, 468), B["d2"], font=font(11.5, "mono"), fill=hx(s["text"]))
    d.text((1042, 490), B["note"], font=font(11, "cjk"), fill=hx(s["mark"]))
    require_w(B["d1"], 11.5, "mono", 310, "issue B docNo 1")
    require_w(B["d2"], 11.5, "mono", 310, "issue B docNo 2")
    require_w(B["note"], 11, "cjk", 310, "issue B note")

    # ---- right: the report strip --------------------------------------------
    img = card(img, (664, 520, 1376, 562), s, radius=18, shadow=16)
    d = ImageDraw.Draw(img)
    d.text((684, 532), H["strip"][0], font=font(13, "cjk"),
           fill=hx(s["text"]))
    rw = measure(H["strip"][1], 13, "cjk_bold")
    d.text((1352 - rw, 532), H["strip"][1], font=font(13, "cjk_bold"),
           fill=hx(s["accent2"]))
    strip_w = measure(H["strip"][0], 13, "cjk") + rw + 40
    if strip_w > 668:
        raise SystemExit(f"FATAL: hero report strip overflows ({strip_w:.1f}px)")

    name = f"dsh-pipeline-check-hero-{lang}-{skin}.webp"
    img.save(os.path.join(OUT, name), "WEBP", quality=92, method=6)
    print(f"wrote {name} ({W}×{HT})")


# --------------------------------------------------------------------------- flow
FLOW = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        panel="#ffffff", edge="#e6e2ef", band="#f5f2fb", band_alt="#faf8fe",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", accent2="#16a34a", rule="#dcd8ea",
        mark="#b45309", mark_bg="#fdf3e9",
        card="#ffffff", shadow="0.10",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        panel="#1b2231", edge="#2e374b", band="#202839", band_alt="#1e2534",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", accent2="#3fb950", rule="#2b3348",
        mark="#d9a441", mark_bg="#2a2216",
        card="#1b2231", shadow="0.45",
    ),
}

FONT_CSS_CJK = ("'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',"
                "'Source Han Sans SC',sans-serif")
FONT_CSS_MONO = ("'Consolas','SFMono-Regular','Menlo',ui-monospace,monospace")

# One row per stage file, in registration order. The defects are the ones the
# real run reported on this composite ledger (5 issues, 1 skipped).
ROWS = [
    dict(no="1",
         head=[("立项", "text", True), ("\u00a0·\u00a0项目立项批复", "sub", False)],
         meta=[("LX-2026-001", "accent", "mono"),
               ("\u00a0·\u00a01200万元 · 批 01-10 · 签 01-15", "sub", False)],
         chips=[]),
    dict(no="2",
         head=[("招标", "text", True), ("\u00a0·\u00a0项目立项批复", "sub", False)],
         meta=[("LX-2026- 001", "mark", "mono"),
               ("\u00a0·\u00a01200万元 · 批 01-10 · 签 01-15", "sub", False)],
         chips=["PC-005"]),
    dict(no="3",
         head=[("合同", "text", True), ("\u00a0·\u00a0合同文本", "sub", False)],
         meta=[("HT-2026-004 · 380万元", "sub", False),
               ("\u00a0·\u00a0批 02-10 · 签 01-15", "mark", False)],
         chips=["PC-004"]),
    dict(no="4",
         head=[("变更", "text", True), ("\u00a0·\u00a0", "sub", False),
               ("【填写文件名称】", "mark", False)],
         meta=[("BG-2026-001", "sub", False), ("\u00a0·\u00a0", "sub", False),
               ("待定", "mark", False),
               ("\u00a0·\u00a0批 03-02 · 签 03-06", "sub", False)],
         chips=["PC-006", "PC-007"]),
    dict(no="5",
         head=[("环节空", "mark", False), ("\u00a0·\u00a0", "sub", False),
               ("文件名称空", "mark", False)],
         meta=[("JS-2026-002 · 860万元 · 批 04-08 · 签 04-12", "sub", False)],
         chips=["PC-002"]),
]

SCOPES = [
    ("台账级", "PC-001", "1"),
    ("行内", "PC-002 004 006 007", "4"),
    ("跨行", "PC-005 008", "2"),
    ("全链", "PC-003", "1"),
]


class Svg:
    """Tiny SVG writer that measures every label before it is emitted."""

    def __init__(self, palette: dict) -> None:
        self.palette = palette
        self.parts: list[str] = []
        self.overflows: list[str] = []

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def text(self, x: float, y: float, content: str, size: float, fill: str, *,
             anchor: str = "start", weight: int | None = None,
             mono: bool = False, max_w: float | None = None,
             opacity: float | None = None) -> None:
        fill = self.palette.get(fill, fill)
        kind = "mono" if mono else "cjk"
        if weight:
            kind += "_bold"
        if max_w is not None:
            w = measure(content, size, kind)
            if w > max_w + 0.4:
                self.overflows.append(
                    f"{content!r} needs {w:.1f}px > {max_w}px")
        family = FONT_CSS_MONO if mono else FONT_CSS_CJK
        attrs = [f'x="{x}"', f'y="{y}"', f'fill="{fill}"',
                 f'font-family="{family}"', f'font-size="{size}"']
        if anchor != "start":
            attrs.append(f'text-anchor="{anchor}"')
        if weight:
            attrs.append(f'font-weight="{weight}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<text {" ".join(attrs)} xml:space="preserve">'
                 f'{escape(content)}</text>')

    def run(self, x: float, y: float, parts: list[tuple[str, str, object]],
            right: float, *, size: float = 11) -> None:
        """Emit one line as one <text> of coloured <tspan>s.

        Chrome lays the whole line out itself, so a fill boundary can never
        shift a run: only the line's total width is checked against `right`.
        """
        tspans: list[str] = []
        total = 0.0
        for content, fill, kind in parts:
            colour = self.palette.get(fill, fill)
            attrs = [f'fill="{colour}"']
            if kind == "mono":
                attrs.append(f'font-family="{FONT_CSS_MONO}"')
                total += measure(content, size, "mono")
            elif kind is True:
                attrs.append('font-weight="700"')
                total += measure(content, size, "cjk_bold")
            else:
                total += measure(content, size, "cjk")
            tspans.append(f'<tspan {" ".join(attrs)}>{escape(content)}</tspan>')
        self.add(f'<text x="{x}" y="{y}" font-family="{FONT_CSS_CJK}" '
                 f'font-size="{size}" xml:space="preserve">'
                 + "".join(tspans) + "</text>")
        if x + total > right + 0.4:
            self.overflows.append(
                f"run at y={y} ends {x + total:.1f}px > {right}px")

    def rect(self, x: float, y: float, w: float, h: float, *, fill: str,
             rx: float = 0, stroke: str | None = None, sw: float = 1.5,
             shadow: bool = False, dash: str | None = None,
             opacity: float | None = None) -> None:
        attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"']
        if rx:
            attrs.append(f'rx="{rx}"')
        attrs.append(f'fill="{fill}"')
        if stroke:
            attrs.append(f'stroke="{stroke}"')
            attrs.append(f'stroke-width="{sw}"')
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        if shadow:
            attrs.append('filter="url(#soft)"')
        self.add(f'<rect {" ".join(attrs)}/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, *, stroke: str,
             sw: float = 1.5, dash: str | None = None,
             marker: str | None = None, opacity: float | None = None) -> None:
        attrs = [f'x1="{x1}"', f'y1="{y1}"', f'x2="{x2}"', f'y2="{y2}"',
                 f'stroke="{stroke}"', f'stroke-width="{sw}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker:
            attrs.append(f'marker-end="url(#{marker})"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<line {" ".join(attrs)}/>')

    def path(self, d: str, *, stroke: str, sw: float = 1.5,
             marker: str | None = None, dash: str | None = None,
             fill: str = "none") -> None:
        attrs = [f'd="{d}"', f'fill="{fill}"', f'stroke="{stroke}"',
                 f'stroke-width="{sw}"', 'stroke-linecap="round"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker:
            attrs.append(f'marker-end="url(#{marker})"')
        self.add(f'<path {" ".join(attrs)}/>')

    def chip(self, x_right: float, y: float, label: str, fg: str, bg: str,
             *, size: float = 11, pad: float = 9, height: float = 20,
             mono: bool = False, weight: int | None = None) -> float:
        """A pill anchored on its right edge; returns its left edge."""
        kind = "mono" if mono else "cjk"
        if weight:
            kind += "_bold"
        w = measure(label, size, kind) + pad * 2
        x = x_right - w
        self.rect(x, y, w, height, fill=bg, rx=height / 2)
        self.text(x + pad, y + height / 2 + size * 0.34, label, size, fg,
                  weight=weight, mono=mono)
        return x

    def tag(self, x: float, y: float, label: str, fg: str, bg: str,
            *, size: float = 11, pad: float = 9, height: float = 20) -> float:
        """A pill anchored on its left edge; returns its right edge."""
        w = measure(label, size, "cjk") + pad * 2
        self.rect(x, y, w, height, fill=bg, rx=height / 2)
        self.text(x + pad, y + height / 2 + size * 0.34, label, size, fg)
        return x + w

    def svg(self, w: int, h: int, label: str) -> str:
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
                f'height="{h}" viewBox="0 0 {w} {h}" role="img" '
                f'aria-label="{escape(label)}">')
        return "\n".join([head, *self.parts, "</svg>"]) + "\n"


def flow_svg(skin: str) -> str:
    s = FLOW[skin]
    W, H = 1100, 660
    v = Svg(s)

    v.add("<defs>")
    v.add(f'<linearGradient id="bg" x1="0" y1="0" x2="0.3" y2="1">'
          f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
          f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    v.add(f'<filter id="soft" x="-30%" y="-30%" width="160%" height="170%">'
          f'<feDropShadow dx="0" dy="7" stdDeviation="9" '
          f'flood-color="#16122c" flood-opacity="{s["shadow"]}"/></filter>')
    v.add('<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
          'markerWidth="6.4" markerHeight="6.4" orient="auto-start-reverse">'
          f'<path d="M0 0 L10 5 L0 10 z" fill="{s["accent"]}"/></marker>')
    v.add('<marker id="arr2" viewBox="0 0 10 10" refX="9" refY="5" '
          'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
          f'<path d="M0 0 L10 5 L0 10 z" fill="{s["faint"]}"/></marker>')
    v.add("</defs>")
    v.add(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

    # ---- header -------------------------------------------------------------
    v.text(44, 56, "dsh-pipeline-check", 26, s["text"], weight=700, mono=True,
           max_w=560)
    v.text(44, 84,
           "一份项目全流程文件链条台账（表头 + 每个环节一行）× 规则包："
           "按四层比较范围核对台账自洽，差异回到行与栏。",
           14.5, s["sub"], max_w=840)
    v.chip(1056, 34, "规则包 2026.1 · 8 条", s["accent"], s["band"],
           size=12, pad=12, height=26)

    # ---- left column: material and rule pack feed the pure core --------------
    v.rect(44, 100, 286, 92, fill=s["card"], rx=18, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(62, 124, "材料", 13.5, s["accent"], weight=700, max_w=90)
    v.chip(310, 112, "JSON / YAML", s["sub"], s["band"], size=10, pad=7,
           height=18)
    v.text(62, 147, "file | material", 11, s["sub"], mono=True, max_w=200)
    v.text(62, 165, "project · projectNo · rows[]", 11, s["sub"], mono=True,
           max_w=232)
    v.text(62, 183, "列名别名归一 · 原件不改", 11, s["faint"], max_w=232)

    v.rect(44, 204, 286, 92, fill=s["card"], rx=18, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(62, 228, "规则包", 13.5, s["accent"], weight=700, max_w=90)
    v.chip(310, 216, "8 条", s["accent"], s["band"], size=10, pad=7, height=18)
    v.text(62, 251, "rules/pipeline-check.yaml", 11, s["sub"], mono=True,
           max_w=232)
    v.text(62, 269, "order[] 出厂为空 · terms 可调", 11, s["sub"], max_w=232)
    v.text(62, 287, "excerpt 必为逐字引文", 11, s["faint"], max_w=232)

    v.line(187, 192, 187, 202, stroke=s["faint"], sw=1.6, marker="arr2")
    v.line(187, 296, 187, 306, stroke=s["faint"], sw=1.6, marker="arr2")

    v.rect(44, 308, 286, 92, fill=s["card"], rx=18, stroke=s["accent"],
           sw=1.6, shadow=True)
    v.text(62, 332, "parseMaterial → runCheck", 12.5, s["text"], mono=True,
           weight=700, max_w=232)
    v.text(62, 355, "列名归一 → 8 条规则 → 结果", 11, s["sub"], max_w=232)
    v.text(62, 373, "纯函数 · 无网络 · 不读时钟", 11, s["sub"], max_w=232)
    v.text(62, 391, "只读材料 · 不写原件", 11, s["faint"], max_w=232)

    v.line(330, 354, 346, 354, stroke=s["accent"], sw=1.8, marker="arr")

    v.rect(44, 412, 286, 88, fill=s["band"], rx=18, stroke=s["edge"],
           sw=1.5)
    v.text(62, 436, "边界", 13, s["sub"], weight=700, max_w=80)
    v.chip(310, 424, "只读", s["faint"], s["card"], size=10, pad=7, height=18)
    v.text(62, 459, "只列差异，不判合规——结论留给复核人", 11, s["sub"],
           max_w=250)
    v.text(62, 477, "空 issues ≠ 没问题：skipped 逐条写原因", 11, s["sub"],
           max_w=250)
    v.text(62, 494, "locator · found · expected · fix", 11, s["faint"],
           mono=True, max_w=250)

    # ---- centre: the stage chain under four scopes ---------------------------
    v.rect(348, 100, 452, 400, fill=s["panel"], rx=20, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(368, 128, "台账 · 环节链（登记顺序）", 12.5, s["text"],
           weight=700, max_w=280)
    v.chip(788, 116, "只读原件", s["faint"], s["band"], size=10, pad=8,
           height=18)

    # ledger header: project + projectNo, checked at the ledger level (PC-001)
    v.rect(360, 138, 428, 36, fill=s["band"], rx=10)
    v.text(376, 162, "某某技改项目 · XM-2026-018", 14, s["text"],
           weight=700, max_w=300)
    v.chip(780, 147, "PC-001 已执行", s["accent"], s["card"], size=10,
           pad=8, height=18)

    # the chain: five links, one per stage file
    row_top = 184
    step = 45
    for i, row in enumerate(ROWS):
        y = row_top + i * step
        v.rect(382, y, 322, 40, fill=s["band_alt"] if i % 2 else s["band"],
               rx=10)
        v.text(398, y + 25, row["no"], 13, s["accent"], weight=700, mono=True)
        v.run(418, y + 15, row["head"], 696, size=13)
        v.run(418, y + 31, row["meta"], 696, size=11)
        chips = row["chips"]
        for k, rule in enumerate(chips):
            cy = y + 12 if len(chips) == 1 else y + 4 + k * 18
            v.chip(786, cy, rule, s["mark"], s["mark_bg"], size=11, pad=7,
                   height=16, mono=True, weight=700)

        # the spine: a link is only a link while the chain is in registration order
    v.line(370, 176, 370, 410, stroke=s["rule"], sw=2)
    for i in range(len(ROWS)):
        v.add(f'<circle cx="370" cy="{row_top + i * step + 20}" r="4.5" '
              f'fill="{s["accent"]}"/>')

    # PC-003 reads the whole chain against the configured order; it ships empty,
    # so the scope is drawn dashed and the rule reports itself as skipped.
    v.line(356, 184, 356, 404, stroke=s["mark"], sw=1.6, dash="5 4")
    v.line(352, 184, 360, 184, stroke=s["mark"], sw=1.6)
    v.line(352, 404, 360, 404, stroke=s["mark"], sw=1.6)
    v.tag(368, 414, "PC-003 全链 · order[] 未配置 → skipped", s["mark"],
          s["mark_bg"], size=11, pad=9, height=19)
    v.text(368, 452,
           "顺序表 order[] 由本机构配置，出厂为空；这一条因此进入 skipped。",
           11, s["sub"], max_w=400)
    v.text(368, 470, "差异回到 locator（行 · 栏），每条带 found 与 expected。",
           11, s["faint"], max_w=400)

    # ---- right column: scopes, two output channels, the reviewer ------------
    v.rect(820, 100, 236, 148, fill=s["panel"], rx=18, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(838, 124, "核对范围", 12.5, s["text"], weight=700, max_w=120)
    v.text(838, 144, "按读取对象的比较范围分四层", 11, s["faint"],
           max_w=200)
    for k, (label, rules, count) in enumerate(SCOPES):
        ry = 168 + k * 20
        v.text(838, ry, label, 11.5, s["text"], weight=700, max_w=62)
        v.text(896, ry, rules, 11, s["sub"], mono=True, max_w=130)
        v.text(1038, ry, count, 11, s["faint"], anchor="end", max_w=18)

    v.rect(820, 260, 236, 132, fill=s["card"], rx=18, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(838, 284, "issues[]", 14, s["accent"], weight=700, mono=True,
           max_w=100)
    v.chip(1042, 272, "5 条", s["accent"], s["band"], size=11, pad=8,
           height=18)
    v.text(838, 308, "PC-005 · 第 2 行 · docNo", 11, s["text"], mono=True,
           max_w=200)
    v.text(838, 324, "与第 1 行重复（去空白后同号）", 11, s["sub"],
           max_w=200)
    v.text(838, 344, "PC-004 · 第 3 行 · signedAt", 11, s["text"],
           mono=True, max_w=200)
    v.text(838, 360, "签署 01-15 早于批复 02-10", 11, s["sub"], max_w=200)
    v.text(838, 380, "+ PC-002 · PC-006 · PC-007 另 3 条", 11,
           s["faint"], max_w=200)

    v.rect(820, 404, 236, 64, fill=s["card"], rx=18, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(838, 426, "skipped[]", 13, s["sub"], weight=700, mono=True,
           max_w=100)
    v.chip(1042, 414, "1 条", s["sub"], s["band"], size=11, pad=8,
           height=18)
    v.text(838, 448, "PC-003 · order[] 未配置", 11, s["text"], max_w=200)
    v.text(838, 464, "空 issues ≠ 没问题", 11, s["faint"], max_w=200)

    v.rect(820, 476, 236, 24, fill=s["band"], rx=12, stroke=s["accent"],
           sw=1.4)
    v.text(938, 493, "复核人 · 结论不在报告里", 11, s["accent"],
           weight=700, anchor="middle", max_w=200)

    # manifold: the chain feeds both channels; the reviewer reads both of them
    v.path("M800 330 H810 V436", stroke=s["accent"], sw=1.6)
    v.line(810, 330, 818, 330, stroke=s["accent"], sw=1.6, marker="arr")
    v.line(810, 436, 818, 436, stroke=s["accent"], sw=1.6, marker="arr")

    # ---- footer -------------------------------------------------------------
    v.line(44, 520, 1056, 520, stroke=s["rule"], sw=1)
    v.text(44, 544,
           "严重级跟着证据走：derived-from-principle ≤ warn · "
           "institutional-configuration ≤ info；excerpt 必须是逐字引文。",
           11.5, s["sub"], max_w=1012)
    v.text(44, 568,
           "config：rulesFile · disabledRules · onlyRules · skipNotes · "
           "timeoutMs ｜ 只读材料 · 无网络 · 不调用模型",
           11.5, s["faint"], max_w=1012)
    v.text(44, 592,
           "输出：pipeline_check → markdown + reportJson（issueCount · "
           "skippedCount · summary）；8 条规则全部来自规则包。",
           11.5, s["faint"], max_w=1012)

    if v.overflows:
        raise SystemExit("FATAL: SVG label overflow:\n  " + "\n  ".join(v.overflows))
    return v.svg(W, H, "dsh-pipeline-check 结构图：材料与规则包进入共同的纯函数核对；"
                       "台账环节链按台账级、行内、跨行、全链四层范围被读取，"
                       "差异与未执行进入 issues[] 与 skipped[] 两条通道，结论留给复核人")


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        for lang in ("zh", "en"):
            hero(lang, skin)
        name = f"dsh-pipeline-check-flow-v5-{skin}.svg"
        with open(os.path.join(OUT, name), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(flow_svg(skin))
        print(f"wrote {name} (1100×660)")


if __name__ == "__main__":
    main()
