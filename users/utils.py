"""Вспомогательные хелперы и валидаторы приложения users."""
import io
import secrets

from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from PIL import Image, ImageDraw, ImageFont

from .constants import (
    AVATAR_FALLBACK_LETTER,
    AVATAR_FONT_FILE,
    AVATAR_FONT_RATIO,
    AVATAR_SIDE_PX,
    AVATAR_TEXT_ANCHOR,
    AVATAR_TEXT_COLOR,
)

PHONE_REGEX = r"^(\+7|8)\d{10}$"
GITHUB_URL_REGEX = r"^https?://(www\.)?github\.com/.+"

phone_validator = RegexValidator(
    regex=PHONE_REGEX,
    message="Телефон в формате 8XXXXXXXXXX или +7XXXXXXXXXX",
)
github_validator = RegexValidator(
    regex=GITHUB_URL_REGEX,
    message="Ссылка должна вести на github.com",
)

# Палитра для placeholder-аватаров.
PALETTE_OCEAN = "#4A6FA5"
PALETTE_PLUM = "#7E5BA6"
PALETTE_OLIVE = "#5F8A55"
PALETTE_TANGERINE = "#D38844"
PALETTE_RUBY = "#C25667"
PALETTE_CYAN = "#449494"
PALETTE_GRAPHITE = "#697384"
PALETTE_VIOLET = "#9166A0"
PALETTE_FOREST = "#4D7E47"
PALETTE_TERRACOTTA = "#B65F3E"

PALETTE = (
    PALETTE_OCEAN,
    PALETTE_PLUM,
    PALETTE_OLIVE,
    PALETTE_TANGERINE,
    PALETTE_RUBY,
    PALETTE_CYAN,
    PALETTE_GRAPHITE,
    PALETTE_VIOLET,
    PALETTE_FOREST,
    PALETTE_TERRACOTTA,
)


def to_canonical_phone(value):
    """Приводит 8XXXXXXXXXX к +7XXXXXXXXXX."""
    if value and value.startswith("8") and len(value) == 11:
        return f"+7{value[1:]}"
    return value


def render_avatar(letter, side=AVATAR_SIDE_PX):
    """Рисует PNG: одна заглавная буква на однотонном фоне."""
    canvas = Image.new("RGB", (side, side), color=secrets.choice(PALETTE))
    pen = ImageDraw.Draw(canvas)

    char = (letter or AVATAR_FALLBACK_LETTER)[0].upper()
    target_size = int(side * AVATAR_FONT_RATIO)
    try:
        font = ImageFont.truetype(AVATAR_FONT_FILE, size=target_size)
    except OSError:
        try:
            font = ImageFont.load_default(size=target_size)
        except TypeError:
            font = ImageFont.load_default()

    box = pen.textbbox(AVATAR_TEXT_ANCHOR, char, font=font)
    text_w, text_h = box[2] - box[0], box[3] - box[1]
    pen.text(
        ((side - text_w) / 2 - box[0], (side - text_h) / 2 - box[1]),
        char,
        fill=AVATAR_TEXT_COLOR,
        font=font,
    )

    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    buf.seek(0)
    return ContentFile(buf.getvalue())
