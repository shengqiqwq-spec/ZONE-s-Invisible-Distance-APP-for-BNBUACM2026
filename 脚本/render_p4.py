import pymupdf

doc = pymupdf.open('bnbu-campus-map/UICDiscover20190515.pdf')
page = doc[3]  # 第4页
r = page.rect
print('page rect:', r)

# 整页高清
pix = page.get_pixmap(matrix=pymupdf.Matrix(4, 4))
pix.save('bnbu-campus-map/pdf_pages/page_004_hires.png')
print('hires full:', pix.width, pix.height)

# 底部表格区域（下 30%）
clip = pymupdf.Rect(r.x0, r.y0 + r.height * 0.70, r.x1, r.y1)
pix2 = page.get_pixmap(matrix=pymupdf.Matrix(8, 8), clip=clip)
pix2.save('bnbu-campus-map/pdf_pages/page_004_table.png')
print('table crop:', pix2.width, pix2.height)

# 地图主体（上 70%）
clip3 = pymupdf.Rect(r.x0, r.y0, r.x1, r.y0 + r.height * 0.72)
pix3 = page.get_pixmap(matrix=pymupdf.Matrix(5, 5), clip=clip3)
pix3.save('bnbu-campus-map/pdf_pages/page_004_map.png')
print('map crop:', pix3.width, pix3.height)
