# dsh-pipeline-check — Verificación del registro de la cadena documental de todo el proceso de un proyecto

`dsh-pipeline-check` lee un registro de la cadena documental de todo el proceso de un proyecto —la cabecera del proyecto más una fila por documento de etapa— y comprueba la completitud y la coherencia interna de ese registro: que el proyecto esté identificado, que cada fila nombre su etapa o su documento, que las etapas sigan la secuencia que usted declara, que las fechas de aprobación y de firma se puedan analizar y respeten su orden, que los números de documento sean únicos, que los importes se analicen como números y que no quede ningún marcador de plantilla en el nombre de un documento.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| La regla del orden de etapas informa `skipped` en una instalación nueva. ¿Hay algo roto? | No. `PC-003` compara las etapas del registro con la lista `order` del paquete de reglas, y esa lista viene vacía, es decir sin configurar, así que la regla se informa a sí misma en `skipped` en lugar de pasar en silencio. Rellene `order` con la secuencia de su institución (el ejemplo del paquete es 立项, 可行性研究, 初步设计, 概算, 招标, 合同, 开工, 变更, 结算, 决算) y entonces solo comprueba que las etapas que aparecen en el registro sigan ese orden, admitiéndose un salto; nunca juzga si saltarse una etapa era admisible, y su base deja constancia de que no existe cláusula citable, por lo que está limitada a `info`. |
| La fecha de firma del registro es anterior a la de aprobación, ¿se detecta? | Sí. `PC-004` compara `signedAt` con `approvedAt`: ambas deben analizarse como fechas y la firma no debe ser anterior a la aprobación, y el mismo día cuenta como no posterior. Una fecha que no puede analizar se informa por separado en lugar de dejarse pasar. Solo compara esas dos fechas: no juzga si la firma excedió la autoridad ni si la aprobación era válida. |
| Un importe figura como `1,200.50` o `1200万元`, ¿se lee igualmente? | Sí. `PC-006` acepta importes con separador de miles o con unidad e informa solo del importe que no puede analizar como número. Comprueba únicamente que sea analizable: si el importe rebasa el presupuesto o si requería aprobación no lo decide esta regla. |
| Una fila no trae nombre de etapa ni nombre de documento. | `PC-002` exige al menos uno de los dos, `stage` o `document`, en cada fila, e informa de la fila que no trae ninguno. Comprueba que al menos uno esté relleno; no juzga si esa etapa debía tramitarse ni si los documentos de esa etapa están completos. |
| El mismo número de documento aparece en dos filas. | `PC-005` informa de un `docNo` repetido e ignora los espacios en blanco al comparar, porque la repetición impide la deduplicación y hace que los importes se cuenten dos veces. No distingue un registro duplicado de dos documentos a los que se dio por error el mismo número, así que una coincidencia requiere confirmación humana. |
| El nombre del documento aún dice `【待填】` o `TBD`. | `PC-007` informa de toda fila cuyo `document` contenga uno de los términos de plantilla del paquete: 【, 】, `{{`, `}}`, XXX, xxx, 待填, 待补充, TBD, todo, 示例; un registro copiado de una plantilla hace que una etapa no tramitada parezca resuelta. Solo se buscan los términos listados, y `terms` puede ajustarse a su plantilla. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-pipeline-check
dsh --profile <name> --dump-config | grep 'dsh-pipeline-check'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/pipeline-check.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-pipeline-check
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-pipeline-check contributors.
