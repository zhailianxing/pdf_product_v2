export const kpiData = {
  totalReports: 1248,
  passRate: 78.5,
  failRate: 21.5,
  avgProcessTime: 1.8,
  trends: {
    totalReports: '+12%',
    passRate: '+2.3%',
    failRate: '-2.3%',
    avgProcessTime: '-0.4s',
  },
}

export const pendingQueue = [
  {
    id: 'r001',
    name: 'F1 博坦.pdf',
    supplier: '博坦',
    reason: 'S元素范围异常',
    uploadTime: '2026-06-02 09:15',
  },
  {
    id: 'r002',
    name: 'F1 轩诺.pdf',
    supplier: '轩诺',
    reason: 'S元素不合格未判断',
    uploadTime: '2026-06-02 08:42',
  },
  {
    id: 'r003',
    name: 'C3 巨力.pdf',
    supplier: '巨力',
    reason: '化学成分范围识别单边',
    uploadTime: '2026-06-01 16:30',
  },
  {
    id: 'r004',
    name: 'C3 威地威.pdf',
    supplier: 'VDV',
    reason: '硬度与冲击功识别混合',
    uploadTime: '2026-06-01 14:20',
  },
  {
    id: 'r005',
    name: 'F1 博坦-2.pdf',
    supplier: '博坦',
    reason: '炉号缺失或无法识别',
    uploadTime: '2026-06-01 11:05',
  },
]

export const modelMatrix = {
  vendors: ['VDV', '迪宝', '轩诺', '巨力', '博坦'],
  models: [
    { key: '8b', label: '3-VL-8B' },
    { key: '32b', label: '3-VL-32B' },
    { key: '235b', label: '3-VL-235B' },
    { key: 'flash', label: '3-VL-Flash' },
    { key: 'plus', label: '3-VL-Plus' },
  ],
  results: {
    VDV: {
      '8b': { status: 'warn', text: '√* 硬度和冲击功识别混合' },
      '32b': { status: 'pass', text: '√' },
      '235b': { status: 'pass', text: '√' },
      flash: { status: 'fail', text: '× 范围/炉号抓不出' },
      plus: { status: 'warn', text: '√* 温度冲击功混合' },
    },
    迪宝: {
      '8b': { status: 'pass', text: '√' },
      '32b': { status: 'pass', text: '√' },
      '235b': { status: 'empty', text: '—' },
      flash: { status: 'empty', text: '—' },
      plus: { status: 'pass', text: '√' },
    },
    轩诺: {
      '8b': { status: 'warn', text: '√* S元素未判断' },
      '32b': { status: 'warn', text: '√* S元素未判断' },
      '235b': { status: 'warn', text: '√* delta Fe识别为Fe' },
      flash: { status: 'empty', text: '—' },
      plus: { status: 'warn', text: '√* S元素未判断' },
    },
    巨力: {
      '8b': { status: 'fail', text: '× 化学成分单边识别' },
      '32b': { status: 'fail', text: '× 力学性能引用原标准' },
      '235b': { status: 'fail', text: '× 力学性能识别错误' },
      flash: { status: 'empty', text: '—' },
      plus: { status: 'fail', text: '× 成分力学识别错误' },
    },
    博坦: {
      '8b': { status: 'fail', text: '× 化学成分单边识别' },
      '32b': { status: 'warn', text: '√* S元素范围不对' },
      '235b': { status: 'warn', text: '√* S元素范围不对' },
      flash: { status: 'empty', text: '—' },
      plus: { status: 'empty', text: '—' },
    },
  },
}

export const passResult = {
  materialGrade: 'ASTM A182 F316L',
  heatNumber: 'A123456',
  supplier: 'VDV',
  certificateNumber: 'MC-2026-004521',
  standard: 'EN 10204 3.1',
  batchNumber: 'LOT-20260528',
  date: '2026-05-28',
  chemicalComposition: 'OK',
  mechanicalProperties: 'OK',
  fields: [
    { label: 'Supplier', value: 'VDV Metal Co.' },
    { label: 'Certificate Number', value: 'MC-2026-004521' },
    { label: 'Material Grade', value: 'ASTM A182 F316L' },
    { label: 'Standard', value: 'EN 10204 3.1' },
    { label: 'Heat Number', value: 'A123456' },
    { label: 'Batch / Lot Number', value: 'LOT-20260528' },
    { label: 'Date', value: '2026-05-28' },
  ],
  chemical: [
    { element: 'C', actual: '0.018', requirement: '≤0.030', status: 'ok' },
    { element: 'Si', actual: '0.42', requirement: '≤0.75', status: 'ok' },
    { element: 'Mn', actual: '1.35', requirement: '≤2.00', status: 'ok' },
    { element: 'P', actual: '0.025', requirement: '≤0.045', status: 'ok' },
    { element: 'S', actual: '0.008', requirement: '≤0.030', status: 'ok' },
    { element: 'Cr', actual: '16.8', requirement: '16.0~18.0', status: 'ok' },
    { element: 'Ni', actual: '10.2', requirement: '10.0~14.0', status: 'ok' },
    { element: 'Mo', actual: '2.05', requirement: '2.0~3.0', status: 'ok' },
  ],
  mechanical: [
    { property: 'Yield Strength', actual: '245 MPa', requirement: '≥170 MPa', status: 'ok' },
    { property: 'Tensile Strength', actual: '520 MPa', requirement: '≥485 MPa', status: 'ok' },
    { property: 'Elongation', actual: '38%', requirement: '≥30%', status: 'ok' },
    { property: 'Hardness', actual: 'HB 165', requirement: '≤217 HB', status: 'ok' },
  ],
}

export const failResult = {
  materialGrade: 'ASTM A182 F316L',
  heatNumber: '—',
  supplier: '博坦',
  certificateNumber: 'BT-2026-00891',
  reasons: [
    '炉号 (Heat Number) 缺失或无法可靠识别',
    'S元素（硫）化学成分超出预设标准范围',
  ],
  fields: [
    { label: 'Supplier', value: '博坦 Steel', highlight: false },
    { label: 'Certificate Number', value: 'BT-2026-00891', highlight: false },
    { label: 'Material Grade', value: 'ASTM A182 F316L', highlight: false },
    { label: 'Standard', value: 'EN 10204 3.1', highlight: false },
    { label: 'Heat Number', value: '—', highlight: true },
    { label: 'Batch / Lot Number', value: 'LOT-20260530', highlight: false },
    { label: 'Date', value: '2026-05-30', highlight: false },
  ],
  chemical: [
    { element: 'C', actual: '0.022', requirement: '≤0.030', status: 'ok' },
    { element: 'Si', actual: '0.38', requirement: '≤0.75', status: 'ok' },
    { element: 'Mn', actual: '1.42', requirement: '≤2.00', status: 'ok' },
    { element: 'P', actual: '0.030', requirement: '≤0.045', status: 'ok' },
    { element: 'S', actual: '0.042', requirement: '≤0.030', status: 'fail' },
    { element: 'Cr', actual: '16.5', requirement: '16.0~18.0', status: 'ok' },
    { element: 'Ni', actual: '10.5', requirement: '10.0~14.0', status: 'ok' },
    { element: 'Mo', actual: '2.10', requirement: '2.0~3.0', status: 'ok' },
  ],
  mechanical: [
    { property: 'Yield Strength', actual: '238 MPa', requirement: '≥170 MPa', status: 'ok' },
    { property: 'Tensile Strength', actual: '495 MPa', requirement: '≥485 MPa', status: 'ok' },
    { property: 'Elongation', actual: '32%', requirement: '≥30%', status: 'ok' },
    { property: 'Hardness', actual: 'HB 172', requirement: '≤217 HB', status: 'ok' },
  ],
}

export const mockUsers = [
  { id: 1, username: 'admin', name: '系统管理员', role: 'admin', status: 'active', lastLogin: '2026-06-02 08:00' },
  { id: 2, username: 'auditor01', name: '张审核', role: 'auditor', status: 'active', lastLogin: '2026-06-01 17:30' },
  { id: 3, username: 'auditor02', name: '李质检', role: 'auditor', status: 'active', lastLogin: '2026-06-01 14:15' },
  { id: 4, username: 'auditor03', name: '王审核', role: 'auditor', status: 'inactive', lastLogin: '2026-05-28 09:00' },
]
