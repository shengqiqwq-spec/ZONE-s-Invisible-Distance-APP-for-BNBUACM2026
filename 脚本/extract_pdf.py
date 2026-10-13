import fitz, os

pdf_path = 'bnbu-campus-map/UICDiscover20190515.pdf'
doc = fitz.open(pdf_path)
print('pages:', doc.page_count)

os.makedirs('bnbu-campus-map/pdf_text', exist_ok=True)
os.makedirs('bnbu-campus-map/pdf_pages', exist_ok=True)

alltext = []
for i, page in enumerate(doc):
    txt = page.get_text()
    alltext.append(f'===== PAGE {i+1} =====\n{txt}')
    # 渲染为 png
    pix = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6))
    pix.save(f'bnbu-campus-map/pdf_pages/page_{i+1:03d}.png')

open('bnbu-campus-map/pdf_text/all.txt', 'w', encoding='utf-8').write('\n'.join(alltext))
print('done. text length:', sum(len(t) for t in alltext))
# 打印非空文本页索引，帮助定位地图页
for i, page in enumerate(doc):
    t = page.get_text().strip()
    if t:
        print(f'--- page {i+1} has text ({len(t)} chars) ---')
        print(t[:400])
