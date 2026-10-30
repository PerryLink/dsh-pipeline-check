# dsh-pipeline-check — 项目全流程文件链条核对

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

<!-- topblock:v1 -->
> **这是什么**　项目全流程文件链条核对。输出一份「哪一行、哪一栏、差什么」的清单。
> **给谁用**　项目管理、投资管理；不用懂命令行。
> **你交什么**　这项核对用到的原始材料（表格、清单或文书）；不改原件。Excel 可先转成 JSON/YAML，对话里也能代转。
> **它不做什么**　不判合规、不认定责任、不替代审核人；只列材料内部能逐条指认的差异。
> **怎么开始**　在 WorkBuddy / 扣子搜「职业文档核对全集」（总包，本检查是其中一项；上架以商城为准）；或命令行：
> `dsh plugin --profile <name> add dsh-pipeline-check`
<!-- /topblock:v1 -->

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)
[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-pipeline-check?metric=downloads)](https://dshfind.com/en/plugins/PerryLink/dsh-pipeline-check?ref=badge)

`dsh-pipeline-check` 读取一份项目全流程文件链条台账——表头加每个环节文件一行——核对这份台账自身的齐备与自洽：是否写明项目、每行是否填写环节或文件、环节是否按你配置的顺序出现、批复与签署日期是否可解析且先后成立、文件编号是否唯一、金额是否可解析为数值、文件名称栏是否残留模板占位符。

## Install

```sh
dsh plugin --profile <name> add dsh-pipeline-check
dsh --profile <name> --dump-config | grep 'dsh-pipeline-check'
```

## 实际输出长什么样

![dsh-pipeline-check 工作流图：文档 → 规则包 → 核对结果。](docs/assets/dsh-pipeline-check-flow.svg)

*工作流概览：文档 → 规则包 → 核对结果。下面的示例使用实际命令面。*


本插件对自己 `PC-001` 测试夹具的**真实输出**，不是示意图。规则库不伪造引文，因此每条发现都会同时写明所引条款，以及该条款原文本次未取得。

## 它回答什么问题

### 示例

下表是示例集：第一行是详细走查，其余行是简短案例。


#### 详细输出

**工具** `pipeline_check`

**输入**

~~~json
{"project":"某某技改项目","projectNo":"XM-2026-018","rows":[{"序号":"1","环节":"","文件名称":"","文件编号":"LX-2026-001"}]}
~~~
 
**输出**

~~~json
{
  "id": "dsh-pipeline-check.PC-002.de09b5a6",
  "ruleId": "PC-002",
  "severity": "warn",
  "locator": {
    "row": 1,
    "field": "stage"
  },
  "found": "第 1 行 stage、document 都为空",
  "expected": "stage、document 至少应填写一项",
  "fix": "补填环节名称与文件名称；本条只核对是否填写，不判断该环节是否应当办理"
}
~~~

*来源 `dsh-pipeline-check/tests/fixtures/PC-002/PC-002-unsafe.json (cases.json expects 1×PC-002); executed parseMaterial+runCheck, checkedAt=2026-10-06T00:00:00.000Z`*

| 你会问 | 它怎么答 |
|---|---|
| 新装上台账后，环节顺序那条规则报的是 `skipped`，是坏了吗？ | 不是。`PC-003` 拿台账里的环节与规则库的 `order` 清单比对，而这份清单出厂为空、即未配置，因此本条报告自己进入 `skipped`，而不是静默通过。把本单位的环节顺序填进 `order`（规则库的示例是 立项、可行性研究、初步设计、概算、招标、合同、开工、变更、结算、决算），它就只核对台账里出现的环节是否按这个顺序出现、允许中间跳过；跳过是否合规它不判断，其依据也写明没有可引条文，故封顶 `info`。 |
| 台账里的签署日期早于批复日期，能查出来吗？ | 能。`PC-004` 比较 `signedAt` 与 `approvedAt`：两个日期都要能解析，且签署日期不得早于批复日期，同一天视为不晚于。解析不了的日期会单独报出，不会静默跳过。它只比较这两个日期，不判断签署是否越权、批复是否有效。 |
| 金额写成 `1,200.50` 或 `1200万元`，还读得出来吗？ | 读得出来。`PC-006` 接受带千分位或带单位的写法，只有解析不成数值的金额才报出。它只核对可解析性：金额是否超过概算、是否应当审批，本条不作判断。 |
| 某一行既没填环节名称，也没填文件名称。 | `PC-002` 要求每行至少填写 `stage` 与 `document` 中的一项，两项都没有就报出该行。它只核对是否至少填了一项；该环节是否应当办理、该环节的文件是否齐全，它不作判断。 |
| 同一个文件编号在两行里各出现一次。 | `PC-005` 会报出重复的 `docNo`，比较时忽略空白字符；重复既妨碍去重，也让金额累计被重复计算。它分不清是重复登记还是两份文件被错编成同一号，命中需人工确认。 |
| 文件名称栏还写着 `【待填】` 或 `TBD`。 | `PC-007` 会报出 `document` 含有规则库所列模板词的行：【、】、`{{`、`}}`、XXX、xxx、待填、待补充、TBD、todo、示例；照抄模板的台账会让没办的环节看起来已经办结。它只检索所列的词，`terms` 可按本单位模板调整。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
|---|---|---|
| 本机构项目管理办法与投资管理制度（无国家标准） | 无统一标准（本条依据为台账可追溯性） | PC-001 |
| 本机构项目管理办法与投资管理制度（无国家标准） | 无统一标准（本条依据为链条齐备性） | PC-002 |
| 本机构项目管理办法与投资管理制度（无国家标准） | 无统一标准（本条依据为本机构配置的环节顺序表） | PC-003 |
| 本机构项目管理办法与投资管理制度（无国家标准） | 无统一标准（本条依据为日期自洽） | PC-004 |
| 本机构项目管理办法与投资管理制度（无国家标准） | 无统一标准（本条依据为台账唯一性） | PC-005, PC-008 |
| 本机构项目管理办法与投资管理制度（无国家标准） | 无统一标准（本条依据为金额可比性） | PC-006 |
| 本机构项目管理办法与投资管理制度（无国家标准） | 无统一标准（本条依据为台账真实性） | PC-007 |

**边界（中文译文，以英文原文为准）：** 本插件核对一份 **项目全流程文件链条台账** 在台账层面可以要求到的内容——是否写明项目，每行是否填写环节或文件，环节是否按你声明的顺序出现，批复与签署日期是否可解析且先后成立，文件编号是否唯一，金额是否可解析，以及是否残留模板占位符。它**不**判定项目是否合规、批复是否越权、支出是否超出概算，或应由谁负责。**这些取决于本机构的投资制度与审批权限。**

> ### ⚠️ 此事没有国家标准，本规则库也不假装有（以英文原文为准）
>
> **项目经过哪些环节、顺序如何，由各机构的项目与投资制度设定**——而且行业之间（电力、市政、建筑、水利）、政府投资项目与企业投资项目之间差异很大。**并不存在统一的国家标准**，因此本规则库不会伪造一个标准号：每条规则的 `excerpt` 都明确写出，其依据是链条自洽或可追溯性，并且**不存在可引用的条款**。有一项测试断言每条 excerpt 都带有这类声明。
>
> **本插件不附带环节清单。** `PC-003` 的 `stageOrder` 出厂为**空**，在未配置任何内容时，它会把自己记入 `skipped`，而不是编造一个环节顺序。配置方式如下：
>
> ```yaml
> order: [立项, 可行性研究, 初步设计, 概算, 招标, 合同, 开工, 变更, 结算, 决算]
> ```
>
> 此后的核对会确认台账中出现的环节是否**按**该顺序出现，并跳过项目确实没有经过的环节；它从不判断跳过是否被允许。

## Compatibility

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-rc.2`。**已声明 `engines.dsh`**：0.2.1 起由宿主单独裁决，范围为 `>=0.2.1-0 <0.3.0` |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/pipeline-check.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-pipeline-check
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## PerryLink DSH Plugin Family

完整清单（62 个核查器 + 通用插件）见 [按材料选核查器](https://perrylink.github.io/zh/checkers/choose/)；本仓只是其中一个。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-pipeline-check contributors.
