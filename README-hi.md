# dsh-pipeline-check — परियोजना की संपूर्ण प्रक्रिया की दस्तावेज़ शृंखला रजिस्टर की जाँच

`dsh-pipeline-check` परियोजना की संपूर्ण प्रक्रिया की दस्तावेज़ शृंखला का एक रजिस्टर पढ़ता है — परियोजना हेडर और प्रत्येक चरण-दस्तावेज़ की एक पंक्ति — और उसी रजिस्टर की पूर्णता तथा आंतरिक सुसंगति की जाँच करता है: क्या परियोजना अंकित है, क्या हर पंक्ति अपना चरण या दस्तावेज़ बताती है, क्या चरण आपके घोषित क्रम में आते हैं, क्या अनुमोदन और हस्ताक्षर की तिथियाँ पढ़ी जा सकती हैं और उनका क्रम बनता है, क्या दस्तावेज़ क्रमांक अद्वितीय हैं, क्या राशियाँ संख्या के रूप में पढ़ी जा सकती हैं, और क्या किसी दस्तावेज़ के नाम में टेम्पलेट प्लेसहोल्डर शेष नहीं है।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| नई स्थापना पर चरण-क्रम वाला नियम `skipped` बताता है। कुछ टूटा हुआ है क्या? | नहीं। `PC-003` रजिस्टर के चरणों की तुलना नियम-पैक की `order` सूची से करता है, और वह सूची खाली यानी अनकॉन्फ़िगर आती है, इसलिए यह नियम चुपचाप पास होने के बजाय स्वयं को `skipped` में बताता है। `order` में अपनी संस्था का चरण-क्रम भरें (पैक का उदाहरण: 立项, 可行性研究, 初步设计, 概算, 招标, 合同, 开工, 变更, 结算, 决算), फिर यह केवल देखता है कि रजिस्टर में आए चरण उसी क्रम में हैं और बीच का चरण छोड़ना स्वीकार्य है; किसी चरण को छोड़ना उचित था या नहीं, यह नहीं आँकता, और इसका आधार बताता है कि कोई उद्धरण-योग्य धारा नहीं है, इसलिए यह `info` तक सीमित है। |
| रजिस्टर में हस्ताक्षर की तिथि अनुमोदन की तिथि से पहले है — क्या यह पकड़ में आता है? | हाँ। `PC-004` `signedAt` की तुलना `approvedAt` से करता है: दोनों तिथियाँ पढ़ी जा सकें और हस्ताक्षर अनुमोदन से पहले न पड़े; एक ही दिन को बाद का नहीं माना जाता। जो तिथि पढ़ी न जा सके वह अलग से दर्ज होती है, चुपचाप छोड़ी नहीं जाती। यह केवल इन दो तिथियों की तुलना करता है: हस्ताक्षर अधिकार-सीमा से बाहर था या अनुमोदन वैध था, यह नहीं आँकता। |
| राशि `1,200.50` या `1200万元` लिखी है — क्या यह पढ़ी जाएगी? | हाँ। `PC-006` हज़ार-विभाजक या इकाई सहित राशि स्वीकार करता है और केवल वह राशि दर्ज करता है जिसे संख्या के रूप में न पढ़ा जा सके। यह केवल पढ़े जाने की जाँच करता है: राशि प्राक्कलन से अधिक है या उसके लिए अनुमोदन चाहिए था, यह यह नियम तय नहीं करता। |
| किसी पंक्ति में न चरण का नाम है, न दस्तावेज़ का नाम। | `PC-002` हर पंक्ति में `stage` या `document` में से कम से कम एक भरा होने की अपेक्षा करता है और जिस पंक्ति में दोनों न हों उसे दर्ज करता है। यह देखता है कि कम से कम एक भरा है; वह चरण होना ही चाहिए था या नहीं, और उसके दस्तावेज़ पूरे हैं या नहीं, यह नहीं आँकता। |
| एक ही दस्तावेज़ क्रमांक दो पंक्तियों में आया है। | `PC-005` दोहराया गया `docNo` दर्ज करता है और तुलना करते समय खाली स्थान छोड़ देता है, क्योंकि दोहराव से न दोहराव हटता है न राशियों का जोड़ सही रहता है। यह नहीं बता सकता कि यह दोहरा पंजीकरण है या दो दस्तावेज़ों को गलती से एक ही क्रमांक दिया गया, इसलिए मिलान पर मानवीय पुष्टि चाहिए। |
| दस्तावेज़ के नाम में अब भी `【待填】` या `TBD` लिखा है। | `PC-007` हर उस पंक्ति को दर्ज करता है जिसके `document` में पैक का कोई टेम्पलेट-शब्द हो: 【, 】, `{{`, `}}`, XXX, xxx, 待填, 待补充, TBD, todo, 示例; टेम्पलेट से उतारा रजिस्टर बिना निपटाए चरण को निपटा हुआ दिखाता है। केवल सूचीबद्ध शब्द खोजे जाते हैं, और `terms` अपने टेम्पलेट के अनुसार बदला जा सकता है। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
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

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-pipeline-check
dsh --profile <name> --dump-config | grep 'dsh-pipeline-check'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/pipeline-check.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-pipeline-check
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-pipeline-check contributors.
