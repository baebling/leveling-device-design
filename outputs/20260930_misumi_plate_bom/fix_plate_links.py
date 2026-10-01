from pathlib import Path
from openpyxl import load_workbook

target = Path(__file__).with_name('2026_BIZ-Lab_창업클럽_시제품_재료비관리_미스미판재_반영.xlsx')
url = 'https://kr.misumi-ec.com/vona2/detail/110302243870/?ProductCode=A6061LNN-120-70-8'

book = load_workbook(target)
sheet = book['Sheet1']
for row in (60, 61, 62):
    cell = sheet[f'G{row}']
    cell.value = url
    cell.hyperlink = url
book.save(target)
