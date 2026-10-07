/**
 * dsh-pipeline-check — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'pipeline_check'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  stageNo: ['序号', '环节序号', '编号', 'stageNo', 'no'],
  stage: ['环节', '阶段', '项目阶段', 'stage'],
  document: ['文件名称', '文档名称', '文件', 'document'],
  docNo: ['文件编号', '文档编号', '编号', 'docNo'],
  version: ['版本', '版次', '文件版本', 'version'],
  amount: ['金额', '合同金额', '投资额', 'amount'],
  approvedAt: ['批复日期', '批准日期', '审批日期', 'approvedAt'],
  signedAt: ['签署日期', '签订日期', '签约日期', 'signedAt'],
  effectiveAt: ['生效日期', '生效时间', 'effectiveAt'],
  owner: ['责任人', '负责人', 'owner'],
  status: ['状态', '办理状态', 'status'],
  note: ['备注', '说明', 'note', 'remark'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'stages', '环节'],
  columns: COLUMNS,
  header: {
  project: ['project', '项目名称', '工程名称'],
  projectNo: ['projectNo', '项目编号', '工程编号'],
  owner: ['owner', '建设单位', '项目单位'],
  plannedAmount: ['plannedAmount', '计划投资', '概算金额'],
  checkedAt: ['checkedAt', '核对日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '环节',
  'stage',
  '文件名称',
  'document',
  '文件编号',
  'docNo',
  '金额',
  'amount',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
