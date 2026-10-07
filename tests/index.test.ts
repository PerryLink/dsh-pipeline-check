import { describeTablePlugin } from './table-plugin-suite.ts'
import { Config } from '../src/config.ts'
import { parseMaterial, runCheck, SPEC } from '../src/model.ts'
import { buildView } from '../src/view.ts'
import { inject, name, resolvePackageFile, TOOL_NAME } from '../src/index.ts'

describeTablePlugin({
  name,
  inject,
  TOOL_NAME,
  resolvePackageFile,
  Config,
  rulesFile: 'rules/pipeline-check.yaml',
  parseMaterial,
  runCheck,
  buildView,
  columnNames: SPEC.columns,
  samples: {
    good: {
      project: '某某技改项目',
      projectNo: 'XM-2026-018',
      rows: [
        {
          序号: '1',
          环节: '立项',
          文件名称: '项目立项批复',
          文件编号: 'LX-2026-001',
          金额: '1200万元',
          批复日期: '2026-01-10',
          签署日期: '2026-01-15',
        },
      ],
    },
    unknownColumn: { rows: [{ 备注: '甲' }] },
  },
})
