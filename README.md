# dsh-pipeline-check

**Boundary:** this plugin checks a **项目全流程文件链条台账** for what a register can be held to — that the
project is identified, that each row names its stage or document, that the stages follow the sequence you
declare, that approval and signing dates parse and follow each other, that document numbers are unique, that
amounts parse, and that no template placeholder survives. It does **not** decide whether a project is
compliant, whether an approval exceeded authority, whether spending breached the estimate, or who is
accountable. **Those depend on the institution's investment rules and approval limits.**

> ### ⚠️ There is no national standard for this, and the pack does not pretend otherwise
>
> **Which stages a project passes through, and in what order, is set by each institution's project and
> investment rules** — and it differs sharply between industries (power, municipal, building, water) and
> between government-funded and enterprise-funded projects. **No unified national standard exists**, so this
> pack does not fabricate a standard number: every rule's `excerpt` states plainly that its basis is chain
> self-consistency or traceability and that **no citable clause exists**. A test asserts that every excerpt
> carries such an admission.
>
> **The plugin ships no stage list.** `PC-003`'s `stageOrder` ships **empty**, and with nothing configured it
> reports itself in `skipped` rather than inventing a stage sequence. Configure it like this:
>
> ```yaml
> order: [立项, 可行性研究, 初步设计, 概算, 招标, 合同, 开工, 变更, 结算, 决算]
> ```
>
> The check then verifies that the stages appearing in the register are **in** that order, skipping stages the
> project legitimately did not pass through; it never judges whether a skip was permissible.

## Compatibility

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a portfolio of projects use `ptc` |

## What it does

Registers the `pipeline_check` tool. It reads one project-chain register — the project header plus one row per
stage document — applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis |
|---|---|---|---|
| `PC-001` | the register names its project and number | warn | traceability |
| `PC-002` | each row names its stage or document | warn | completeness |
| `PC-003` | stages follow your configured sequence (off by default) | info | local order table |
| `PC-004` | signing is not earlier than approval | warn | date consistency |
| `PC-005` | document numbers are unique | warn | register uniqueness |
| `PC-006` | amounts parse as numbers | warn | comparability |
| `PC-007` | document names hold no unreplaced placeholder | warn | register integrity |
| `PC-008` | stage numbers are unique | warn | register uniqueness |

## Install

```sh
dsh plugin --profile <name> add dsh-pipeline-check
dsh --profile <name> --dump-config | grep 'dsh-pipeline-check'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/pipeline-check.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `PC-003` `order` — your stage sequence. Empty means the rule does not run. A stage written with a trailing
  note (`招标（二次）`) matches its base name.
- `PC-004` `field` / `notBeforeField` — the date pair to compare, defaults to signing against approval. Add a
  second rule for the effective date.
- `PC-007` `terms` — the placeholders to look for.

## Material format

The tool accepts JSON or YAML:

```yaml
project: 某某技改项目
projectNo: XM-2026-018
rows:
  - { 序号: '1', 环节: 立项, 文件名称: 项目立项批复, 文件编号: LX-2026-001,
      金额: 1200万元, 批复日期: 2026-01-10, 签署日期: 2026-01-15, 生效日期: 2026-01-16 }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens; the register's own
column names are kept, so a finding names the column it read. Amounts may carry thousands separators and
units (`1,200.50`, `1200万元`).

## Rule sources

Rule data lives in `rules/pipeline-check.yaml`. Because no national standard governs a project's stage chain,
the pack's `basis` entries say so explicitly instead of citing one. The load-time guard still requires every
rule to carry a document, a clause, an excerpt and a source, and still forbids a `derived-from-principle` or
locally configured check from being `error`.

## Troubleshooting

- **`PC-003` reports itself as skipped.** Its order table is empty. Which stages a project passes through is
  your institution's rule, and the plugin will not guess it.
- **`PC-003` fires on a stage name.** The name is not in your order table. Either correct the register or add
  the stage — the finding says which name it could not place.
- **`PC-006` fires on an amount I can read.** The reader accepts `1,200.50` and `1200万元`; a cell holding a
  range (`约 1200 万`) or a note is reported as unparseable on purpose.
- **`PC-005` fires twice on one document.** That can be legitimate for an amendment reusing a number. Say so
  in the remark rather than deleting a row.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-pipeline-check@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-pipeline-check   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and
the check engine, and the rule pack declares every check.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-pipeline-check contributors.
