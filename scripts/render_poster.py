"""Render verified itinerary copy over watercolor artwork."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SERIF = Path("C:/Windows/Fonts/simsun.ttc")
SERIF_BOLD = Path("C:/Windows/Fonts/simsun.ttc")
KAI = Path("C:/Windows/Fonts/simkai.ttf")
SANS = Path("C:/Windows/Fonts/msyh.ttc")
SANS_BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")
LATIN = Path("C:/Windows/Fonts/times.ttf")
WIDTH, HEIGHT = 1049, 1499
BROWN = (59, 30, 18)
RUST = (150, 67, 31)
MUTED = (104, 70, 48)
PANELS = [(236, 574), (586, 922), (935, 1253)]


def face(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not path.exists():
        raise RuntimeError(f"Required font missing: {path}")
    return ImageFont.truetype(str(path), size)


def fit_font(draw: ImageDraw.ImageDraw, text: str, path: Path, size: int, width: int) -> ImageFont.FreeTypeFont:
    while size > 18 and draw.textlength(text, font=face(path, size)) > width:
        size -= 2
    return face(path, size)


def lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    result: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        if current and draw.textlength(candidate, font=font) > max_width:
            result.append(current)
            current = char
        else:
            current = candidate
    if current:
        result.append(current)
    return result


def caption(draw: ImageDraw.ImageDraw, label: str, body: str, x: int, y: int, width: int) -> None:
    draw.text((x, y), label, font=face(SANS_BOLD, 24), fill=RUST)
    body_font = face(SANS, 17)
    for index, line in enumerate(lines(draw, body, body_font, width)[:3]):
        draw.text((x, y + 37 + index * 27), line, font=body_font, fill=BROWN)


def render(source: Path) -> Path:
    data = json.loads(source.read_text(encoding="utf-8"))
    required = {"title", "subtitle", "tag", "art", "theme", "steps", "summary", "footer"}
    if missing := required - data.keys():
        raise ValueError(f"Missing fields: {sorted(missing)}")
    if len(data["steps"]) != 3:
        raise ValueError("Template requires exactly three steps")
    art = Image.open(ROOT / data["art"]).convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(art)

    title_font = fit_font(draw, data["title"], SERIF_BOLD, 70, 735)
    draw.text((47, 59), data["title"], font=title_font, fill=BROWN, stroke_width=1)
    subtitle_font = fit_font(draw, data["subtitle"], SERIF, 27, 710)
    draw.line((48, 179, 105, 179), fill=RUST, width=2)
    draw.text((125, 160), data["subtitle"], font=subtitle_font, fill=BROWN)
    draw.line((940, 179, 997, 179), fill=RUST, width=2)

    for index, (step, bounds) in enumerate(zip(data["steps"], PANELS), 1):
        y0, y1 = bounds
        draw.rounded_rectangle((35, y0 + 17, 137, y0 + 99), radius=32, fill=(229, 191, 158))
        draw.text((51, y0 + 18), f"{index:02d}", font=face(LATIN, 68), fill=BROWN)
        time_font = fit_font(draw, step["time"], SANS_BOLD, 25, 253)
        draw.text((151, y0 + 32), step["time"], font=time_font, fill=BROWN)
        name_font = fit_font(draw, step["name"], SERIF_BOLD, 32, 386)
        draw.text((50, y0 + 106), step["name"], font=name_font, fill=BROWN, stroke_width=1)

        note_font = face(KAI, 22)
        note_lines: list[str] = []
        for segment in step["note"].replace("。", "。\n", 1).splitlines():
            note_lines.extend(lines(draw, segment, note_font, 367))
        for j, line in enumerate(note_lines[:3]):
            draw.text((51, y0 + 160 + j * 32), line, font=note_font, fill=BROWN)

        draw.line((52, y1 - 71, 395, y1 - 71), fill=(201, 154, 111), width=1)
        budget_font = fit_font(draw, step["budget"], SANS_BOLD, 20, 365)
        draw.text((51, y1 - 56), step["budget"], font=budget_font, fill=RUST)

    captions = {
        "first-meeting": (("顺路安排", "咖啡 → 胡同街面 → 可选晚餐"), ("两人费用", "咖啡参考约¥92；晚餐另计"), ("自然结束", "喝完咖啡即可各自返程")),
        "half-day": (("顺路安排", "咖啡 → 武康路 → 可选晚餐"), ("两人费用", "咖啡预留¥80—120，非报价"), ("自然结束", "散步后可各自返程")),
        "rainy-day": (("雨天安排", "咖啡后可直接返程"), ("两人费用", "饮品预留¥120—200，非报价"), ("可选晚餐", "需双方同意并确认有位")),
    }
    footer_cards = captions.get(source.stem, (
        ("路线安排", data["summary"]),
        ("核心费用", data["steps"][0]["budget"]),
        ("出发前", "复核营业、价格和交通"),
    ))
    for x, item in zip((39, 377, 713), footer_cards):
        caption(draw, *item, x + 13, 1283, 273)

    cover = Image.new("RGBA", (WIDTH, 74), (250, 243, 226, 222))
    art.paste(cover, (0, 1416), cover)
    draw = ImageDraw.Draw(art)
    footer = data["footer"].replace("｜", " · ")
    footer_font = fit_font(draw, footer, SANS, 14, 700)
    draw.text((45, 1432), footer, font=footer_font, fill=MUTED)
    draw.text((45, 1454), "地点来源与使用许可见仓库说明；插画不作导航。", font=face(SANS, 13), fill=MUTED)
    draw.text((885, 1430), "林序聊AI", font=face(SANS_BOLD, 24), fill=RUST)

    output = ROOT / "examples" / "posters" / f"{source.stem}.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    art.save(output, optimize=True)
    return output


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/render_poster.py examples/first-meeting.json")
    print(render(ROOT / sys.argv[1]))
