"""Render editable Chinese itinerary text over illustration panels; no map API."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
FONT = Path('C:/Windows/Fonts/msyh.ttc')
FONT_BOLD = Path('C:/Windows/Fonts/msyhbd.ttc')
SIZE = (1120, 1600)
PANEL_BOXES = [(28, 267, 1092, 606), (28, 623, 1092, 962), (28, 979, 1092, 1318)]
ART_CROPS = [(0.02, 0.05, 0.98, 0.36), (0.02, 0.36, 0.98, 0.66), (0.02, 0.67, 0.98, 0.96)]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT
    if not path.exists():
        raise RuntimeError('Missing Windows Chinese font; set FONT/FONT_BOLD in the script.')
    return ImageFont.truetype(str(path), size)


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines, current = [], ''
    for char in text:
        proposal = current + char
        if current and draw.textlength(proposal, font=face) > max_width:
            lines.append(current)
            current = char
        else:
            current = proposal
    if current:
        lines.append(current)
    return lines


def render(source: Path) -> Path:
    data = json.loads(source.read_text(encoding='utf-8'))
    required = {'title', 'subtitle', 'tag', 'art', 'theme', 'steps', 'summary', 'footer'}
    if missing := required - data.keys():
        raise ValueError(f'Missing fields: {sorted(missing)}')
    if len(data['steps']) != 3:
        raise ValueError('Template requires exactly three steps')
    if '林序聊AI' in data['title'] or '林序聊AI' in data['footer']:
        raise ValueError('Brand label is drawn by the fixed template')

    art = Image.open(ROOT / data['art']).convert('RGB')
    paper = (248, 242, 226) if data['theme'] == 'autumn' else (240, 242, 231)
    accent = (157, 68, 31) if data['theme'] == 'autumn' else (64, 99, 94)
    dark = (60, 35, 23)
    image = Image.new('RGB', SIZE, paper)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, SIZE[0], 18), fill=accent)
    draw.text((50, 42), data['tag'], font=font(25), fill=accent)
    title_face = font(62, True)
    if draw.textlength(data['title'], font=title_face) > 1020:
        title_face = font(54, True)
    draw.text((48, 80), data['title'], font=title_face, fill=dark)
    draw.text((52, 184), data['subtitle'], font=font(32), fill=accent)
    draw.line((48, 244, 1070, 244), fill=accent, width=3)

    for i, (step, box, fractions) in enumerate(zip(data['steps'], PANEL_BOXES, ART_CROPS), start=1):
        ax1, ay1, ax2, ay2 = fractions
        crop = art.crop((int(art.width * ax1), int(art.height * ay1), int(art.width * ax2), int(art.height * ay2)))
        panel = ImageOps.fit(crop, (box[2] - box[0], box[3] - box[1]), method=Image.Resampling.LANCZOS)
        image.paste(panel, box[:2])
        overlay = Image.new('RGBA', (565, box[3] - box[1]), (250, 245, 231, 238))
        image.paste(overlay, (box[0], box[1]), overlay)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle(box, radius=18, outline=(202, 172, 132), width=3)
        left, top = box[0] + 30, box[1] + 18
        draw.text((left, top), f'{i:02d}', font=font(55, True), fill=accent)
        draw.text((left + 116, top + 13), step['time'], font=font(29, True), fill=dark)
        draw.text((left, top + 86), step['name'], font=font(38, True), fill=dark)
        y = top + 151
        for line in wrap(draw, step['note'], font(25), 490)[:3]:
            draw.text((left, y), line, font=font(25), fill=dark)
            y += 38
        draw.text((left, box[3] - 49), step['budget'], font=font(26, True), fill=accent)

    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((32, 1354, 1088, 1460), radius=18, fill=(235, 223, 199))
    draw.text((59, 1374), data['summary'], font=font(28, True), fill=dark)
    draw.text((49, 1491), data['footer'], font=font(21), fill=(101, 88, 74))
    draw.text((867, 1530), '林序聊AI', font=font(31, True), fill=accent)
    output = ROOT / 'examples' / 'posters' / (source.stem + '.png')
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, optimize=True)
    return output


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python scripts/render_poster.py examples/first-meeting.json')
    print(render(ROOT / sys.argv[1]))
