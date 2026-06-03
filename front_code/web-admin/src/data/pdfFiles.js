/** mock_data 目录下的 PDF 文件列表 */
export const MOCK_PDF_FILES = [
  'C3 威地威.pdf',
  'C3 巨力.pdf',
  'F1 博坦.pdf',
  'F1 轩诺.pdf',
  'F3 迪宝.pdf',
  'R470材质证明.pdf',
  '高纬材质证明.pdf',
]

const SUPPLIER_PDF_MAP = {
  博坦: 'F1 博坦.pdf',
  轩诺: 'F1 轩诺.pdf',
  VDV: 'C3 威地威.pdf',
  威地威: 'C3 威地威.pdf',
  迪宝: 'F3 迪宝.pdf',
  巨力: 'C3 巨力.pdf',
  高纬: '高纬材质证明.pdf',
  R470: 'R470材质证明.pdf',
}

export function resolvePdfFileName(fileName, supplier, aiStatus = 'pass') {
  if (fileName && MOCK_PDF_FILES.includes(fileName)) {
    return fileName
  }

  if (fileName) {
    const baseName = fileName.replace(/\.pdf$/i, '')
    const partial = MOCK_PDF_FILES.find(
      (f) => f.includes(baseName) || baseName.includes(f.replace(/\.pdf$/i, '')),
    )
    if (partial) return partial
  }

  if (supplier) {
    const direct = SUPPLIER_PDF_MAP[supplier]
    if (direct) return direct

    const fuzzy = Object.entries(SUPPLIER_PDF_MAP).find(([key]) => supplier.includes(key))
    if (fuzzy) return fuzzy[1]
  }

  return aiStatus === 'fail' ? 'F1 博坦.pdf' : 'C3 威地威.pdf'
}

export function getPdfUrl(fileName, supplier, aiStatus = 'pass') {
  const resolved = resolvePdfFileName(fileName, supplier, aiStatus)
  return `/mock_pdfs/${encodeURIComponent(resolved)}`
}
