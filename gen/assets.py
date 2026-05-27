# -*- coding: utf-8 -*-
"""파비콘·아이콘·OG 이미지 생성 (브랜드 로즈골드 그라데이션)."""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

BG = (11, 11, 14)
GRAD = [(244, 210, 156), (233, 184, 167), (201, 138, 107)]  # gold→rose→copper

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def grad_color(t):
    if t < 0.45:
        return lerp(GRAD[0], GRAD[1], t / 0.45)
    return lerp(GRAD[1], GRAD[2], (t - 0.45) / 0.55)

def radial_icon(size, rounded=True, pad_ratio=0.0):
    img = Image.new("RGBA", (size, size), BG + (255,))
    d = ImageDraw.Draw(img)
    cx = cy = size / 2
    r = size / 2 * (1 - pad_ratio)
    # 라디얼 그라데이션 원
    for i in range(int(r), 0, -1):
        t = 1 - i / r
        # 상단-좌측 specular: 살짝 밝게
        col = grad_color(t)
        d.ellipse([cx - i, cy - i, cx + i, cy + i], fill=col + (255,))
    # specular 하이라이트
    hl = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    hr = r * 0.32
    hx, hy = cx - r * 0.32, cy - r * 0.32
    hd.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255, 90))
    hl = hl.filter(ImageFilter.GaussianBlur(max(1, size // 20)))
    img = Image.alpha_composite(img, hl)
    # 다크 림
    d2 = ImageDraw.Draw(img)
    d2.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(11, 11, 14, 160), width=max(1, size // 64))
    if rounded:
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, size, size], radius=int(size * 0.22), fill=255)
        out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        out.paste(img, (0, 0), mask)
        return out
    return img

def maskable(size):
    # maskable: 안전 영역 확보 위해 원을 더 작게(패딩)
    img = Image.new("RGBA", (size, size), BG + (255,))
    inner = radial_icon(int(size * 0.66), rounded=False)
    off = (size - inner.width) // 2
    img.paste(inner, (off, off), inner)
    return img

def save(img, name):
    img.convert("RGBA").save(os.path.join(ROOT, name))

def main():
    # PWA 아이콘
    radial_icon(192).save(os.path.join(ROOT, "icon-192.png"))
    radial_icon(512).save(os.path.join(ROOT, "icon-512.png"))
    maskable(512).save(os.path.join(ROOT, "icon-maskable-512.png"))
    radial_icon(180).save(os.path.join(ROOT, "apple-touch-icon.png"))
    # favicon.ico (멀티사이즈)
    ico = radial_icon(64)
    ico.save(os.path.join(ROOT, "favicon.ico"),
             sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    # 로고 (헤더/푸터/OG 용) — 원형 아이콘 + 텍스트
    for w in (80, 160, 320, 800):
        radial_icon(w).save(os.path.join(ASSETS, f"logo-{w}.png" if w != 800 else "logo.png"))
    # OG 커버 1200x630
    og = Image.new("RGB", (1200, 630), BG)
    d = ImageDraw.Draw(og)
    # 우측 상단 그라데이션 광원
    glow = Image.new("RGBA", (1200, 630), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(420, 0, -2):
        t = 1 - i / 420
        c = grad_color(t)
        gd.ellipse([1000 - i, 80 - i, 1000 + i, 80 + i], fill=c + (int(60 * t),))
    og = Image.alpha_composite(og.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(og)
    icon = radial_icon(120)
    og.paste(icon, (90, 90), icon)
    def font(sz):
        for p in ["/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
            if os.path.exists(p):
                return ImageFont.truetype(p, sz)
        return ImageFont.load_default()
    d.text((90, 250), "마사지바삭", font=font(86), fill=(243, 243, 245))
    d.text((92, 360), "수도권·부산 24시 프리미엄 출장마사지", font=font(40), fill=(201, 138, 107))
    d.text((92, 430), "본사 직접 배차 · 정찰 요금 · 82개 행정구", font=font(32), fill=(154, 154, 163))
    d.text((92, 520), "0508-202-4717 · 연중무휴 24시간", font=font(34), fill=(214, 178, 116))
    og.save(os.path.join(ASSETS, "og-cover.jpg"), quality=86)
    print("assets generated:", sorted(os.listdir(ASSETS)))

if __name__ == "__main__":
    main()
