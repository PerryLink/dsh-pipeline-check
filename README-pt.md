# dsh-pipeline-check — Verificação do registo da cadeia documental de todo o processo de um projeto

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-pipeline-check` lê um registo da cadeia documental de todo o processo de um projeto —o cabeçalho do projeto mais uma linha por documento de etapa— e verifica a completude e a coerência interna desse registo: se o projeto está identificado, se cada linha nomeia a sua etapa ou o seu documento, se as etapas seguem a sequência que declara, se as datas de aprovação e de assinatura são analisáveis e respeitam a ordem, se os números de documento são únicos, se os montantes são analisáveis como números e se não resta nenhum marcador de modelo no nome de um documento.

## Como é a saída

![Terminal demo of dsh-pipeline-check: real output over its PC-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-pipeline-check/main/docs/assets/dsh-pipeline-check-demo.png)

Saída real deste plugin sobre o seu próprio fixture de teste `PC-001` — não é uma simulação. O pacote de regras não inventa citações, por isso cada achado nomeia a cláusula aplicada e avisa que o seu texto não foi obtido.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| A regra da ordem das etapas informa `skipped` numa instalação nova. Algo está avariado? | Não. `PC-003` compara as etapas do registo com a lista `order` do pacote de regras, e essa lista vem vazia, ou seja, por configurar, pelo que a regra se reporta a si mesma em `skipped` em vez de passar em silêncio. Preencha `order` com a sequência da sua instituição (o exemplo do pacote é 立项, 可行性研究, 初步设计, 概算, 招标, 合同, 开工, 变更, 结算, 决算) e então verifica apenas que as etapas que aparecem no registo sigam essa ordem, sendo um salto permitido; nunca julga se saltar uma etapa era admissível, e a sua base regista que não existe cláusula citável, pelo que está limitada a `info`. |
| A data de assinatura no registo é anterior à da aprovação — isso é detetado? | Sim. `PC-004` compara `signedAt` com `approvedAt`: ambas têm de ser analisáveis como datas e a assinatura não pode ser anterior à aprovação, contando o mesmo dia como não posterior. Uma data que não consegue analisar é reportada à parte em vez de ser deixada passar. Compara apenas essas duas datas: não julga se a assinatura excedeu a competência nem se a aprovação era válida. |
| Um montante está escrito como `1,200.50` ou `1200万元` — continua a ser lido? | Sim. `PC-006` aceita montantes com separador de milhares ou com unidade e reporta apenas o montante que não consegue analisar como número. Verifica só essa analisabilidade: se o montante excede o orçamento ou se exigia aprovação não é esta regra que decide. |
| Uma linha não traz nome de etapa nem nome de documento. | `PC-002` exige pelo menos um dos dois, `stage` ou `document`, em cada linha, e reporta a linha que não traz nenhum. Verifica que pelo menos um esteja preenchido; não julga se essa etapa devia ser tratada nem se os documentos dessa etapa estão completos. |
| O mesmo número de documento aparece em duas linhas. | `PC-005` reporta um `docNo` repetido e ignora os espaços em branco ao comparar, porque a repetição impede a deduplicação e faz com que os montantes sejam contados duas vezes. Não distingue um registo duplicado de dois documentos aos quais foi dado o mesmo número por erro, pelo que uma ocorrência exige confirmação humana. |
| O nome do documento ainda diz `【待填】` ou `TBD`. | `PC-007` reporta toda a linha cujo `document` contenha um dos termos de modelo do pacote: 【, 】, `{{`, `}}`, XXX, xxx, 待填, 待补充, TBD, todo, 示例; um registo copiado de um modelo faz com que uma etapa não tratada pareça resolvida. Só os termos listados são procurados, e `terms` pode ser ajustado ao seu modelo. |

## Normas que segue

| Documento | Número | Regras que o citam |
|---|---|---|
| 本机构项目管理办法与投资管理制度（无国家标准） | 无统一标准（本条依据为台账可追溯性） | PC-001 |
| 本机构项目管理办法与投资管理制度（无国家标准） | 无统一标准（本条依据为链条齐备性） | PC-002 |
| 本机构项目管理办法与投资管理制度（无国家标准） | 无统一标准（本条依据为本机构配置的环节顺序表） | PC-003 |
| 本机构项目管理办法与投资管理制度（无国家标准） | 无统一标准（本条依据为日期自洽） | PC-004 |
| 本机构项目管理办法与投资管理制度（无国家标准） | 无统一标准（本条依据为台账唯一性） | PC-005, PC-008 |
| 本机构项目管理办法与投资管理制度（无国家标准） | 无统一标准（本条依据为金额可比性） | PC-006 |
| 本机构项目管理办法与投资管理制度（无国家标准） | 无统一标准（本条依据为台账真实性） | PC-007 |

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
dsh plugin --profile <name> add dsh-pipeline-check
dsh --profile <name> --dump-config | grep 'dsh-pipeline-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/pipeline-check.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

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
