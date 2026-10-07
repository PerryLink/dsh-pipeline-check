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

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
pnpm pack
dsh plugin --profile <name> add ./*.tgz
dsh --profile <name> --dump-config | grep 'dsh-pipeline-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`. As chaves e os parâmetros de cada regra estão em [README.md](README.md#configuration) (versão principal em inglês).

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-pipeline-check
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-pipeline-check contributors.
