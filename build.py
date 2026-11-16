# -*- coding: utf-8 -*-
"""電子名片素材產生器：從名片 .ai 裁出 logo／產品圖，產生 contact.vcf 與各種 QR。
改資料 → 改下面 CARD → 重跑：py -3.14 build.py
"""
import os
import sys

import fitz  # PyMuPDF
import segno

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "output")
AI_FILE = r"C:\Users\pm\我的雲端硬碟\個人資料\名片\許博凱特助.ai"

# 名片網頁上線後的網址（換網址要改這裡並重跑，QR 才會對）
PAGE_URL = "https://pokaihsu1243-create.github.io/ecard/"

CARD = {
    "family": "許",
    "given": "博凱",
    "name_en": "Po-Kai Hsu",
    "org": "許瑞興工業股份有限公司 Safety Control Cable Ind. Co., Ltd.",
    "title": "總經理特助 Special Assistant to the General Manager",
    "mobile": "+886912801668",
    "office": "+88647323141,1506",  # 逗號＝撥通後暫停再按分機
    "fax": "+88647322419",
    "email": "sa03082@safety.com.tw",
    "url": "https://www.safety.com.tw/",
    "street": "No. 749, Sec. 3, Chung-shan Rd.",
    "city": "Changhua City",
    "zip": "50068",
    "country": "Taiwan",
}
LINKS = {
    "line": "https://line.me/ti/p/ncyHMv-r6Z",
    "whatsapp": "https://wa.me/qr/6G3AUC2A55OZF1",
    "wechat": "https://u.wechat.com/MAf4shgs48GrMHYkQsNRpGw?s=4",
}


def vcard(c):
    # vCard 3.0：文字欄位裡的逗號要跳脫，否則「Co., Ltd.」會被切開
    c = dict(c)
    for k in ("org", "title", "street"):
        c[k] = c[k].replace(",", "\\,")
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{c['family']};{c['given']};;;",
        f"FN:{c['family']}{c['given']} {c['name_en']}",
        f"ORG:{c['org']}",
        f"TITLE:{c['title']}",
        f"TEL;TYPE=CELL:{c['mobile']}",
        f"TEL;TYPE=WORK,VOICE:{c['office']}",
        f"TEL;TYPE=WORK,FAX:{c['fax']}",
        f"EMAIL;TYPE=WORK:{c['email']}",
        f"URL:{c['url']}",
        f"ADR;TYPE=WORK:;;{c['street']};{c['city']};;{c['zip']};{c['country']}",
        "END:VCARD",
    ]
    return "\r\n".join(lines) + "\r\n"


def crop_assets():
    if not os.path.exists(AI_FILE):
        print("找不到名片 .ai，略過裁圖（沿用現有 assets）")
        return
    page = fitz.open(AI_FILE)[0]
    k = 1.02 * 72 / 200  # 200dpi 預覽圖座標 → PDF 點

    def clip(x0, y0, x1, y1, name, dpi):
        rect = fitz.Rect(x0 * k, y0 * k, x1 * k, y1 * k)
        page.get_pixmap(dpi=dpi, clip=rect).save(os.path.join(ASSETS, name))

    clip(280, 566, 968, 656, "logo.png", 330)
    clip(1690, 560, 2102, 834, "products.png", 300)
    clip(286, 727, 460, 800, "certs.png", 400)
    clip(1400, 570, 1686, 836, "map.png", 420)


def qr(data, path, scale=12, dark="#000000"):
    segno.make(data, error="m").save(path, scale=scale, border=3, dark=dark, light="#ffffff")


def main():
    os.makedirs(ASSETS, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    crop_assets()

    vcf = vcard(CARD)
    with open(os.path.join(HERE, "contact.vcf"), "w", encoding="utf-8", newline="") as f:
        f.write(vcf)

    for key, url in LINKS.items():
        qr(url, os.path.join(ASSETS, f"qr-{key}.png"), scale=10)
    # 名片網頁 QR：頁面上顯示用＋印名片背面／手機鎖定畫面用（大圖）
    qr(PAGE_URL, os.path.join(ASSETS, "qr-page.png"), scale=10)
    qr(PAGE_URL, os.path.join(OUT, "名片QR_網頁版.png"), scale=30)
    segno.make(PAGE_URL, error="m").save(os.path.join(OUT, "名片QR_網頁版.svg"), scale=10, border=3)
    # 離線備用：資料直接編進 QR，沒網路也能存聯絡人
    qr(vcf, os.path.join(OUT, "名片QR_離線vCard.png"), scale=14)
    print("完成：", HERE)


if __name__ == "__main__":
    sys.exit(main())
