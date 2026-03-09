import base64
import os
from io import BytesIO
from pathlib import Path
from textwrap import fill

import qrcode
from PIL import Image, ImageDraw, ImageFont

from ..schemas import CertificateRecord


def _font_candidates(bold: bool) -> list[Path | str]:
    backend_root = Path(__file__).resolve().parents[2]
    pil_fonts_dir = Path(ImageFont.__file__).resolve().parent / 'fonts'

    env_var = 'CERT_FONT_BOLD_PATH' if bold else 'CERT_FONT_REGULAR_PATH'
    configured = os.getenv(env_var, '').strip()

    if bold:
        names = ['DejaVuSans-Bold.ttf', 'Arial Bold.ttf', 'LiberationSans-Bold.ttf']
        relative = ['arialbd.ttf', 'calibrib.ttf']
        linux = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
            '/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf',
        ]
        windows = ['C:/Windows/Fonts/arialbd.ttf', 'C:/Windows/Fonts/calibrib.ttf']
        mac = ['/System/Library/Fonts/Supplemental/Arial Bold.ttf']
    else:
        names = ['DejaVuSans.ttf', 'Arial.ttf', 'LiberationSans-Regular.ttf']
        relative = ['arial.ttf', 'calibri.ttf']
        linux = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
            '/usr/share/fonts/truetype/msttcorefonts/Arial.ttf',
        ]
        windows = ['C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/calibri.ttf']
        mac = ['/System/Library/Fonts/Supplemental/Arial.ttf']

    candidates: list[Path | str] = []
    if configured:
        candidates.append(Path(configured))

    for name in names:
        candidates.append(pil_fonts_dir / name)
    for name in relative:
        candidates.append(backend_root / 'assets' / 'fonts' / name)
    candidates.extend(Path(path) for path in linux + windows + mac)
    candidates.extend(names)
    return candidates


def _load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    for candidate in _font_candidates(bold=bold):
        try:
            return ImageFont.truetype(str(candidate), size)
        except OSError:
            continue

    return ImageFont.load_default()


def _draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    canvas_width: int,
    font: ImageFont.ImageFont,
    fill_color: tuple[int, int, int],
) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (canvas_width - text_width) // 2
    draw.text((x, y), text, font=font, fill=fill_color)
    return text_height


def _draw_centered_text_in_region(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    left: int,
    right: int,
    font: ImageFont.ImageFont,
    fill_color: tuple[int, int, int],
) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = left + ((right - left) - text_width) // 2
    draw.text((x, y), text, font=font, fill=fill_color)
    return text_height


def _load_signature_image(data_url: str | None) -> Image.Image | None:
    if not data_url:
        return None

    prefix = 'data:image/png;base64,'
    if not data_url.startswith(prefix):
        return None

    encoded_payload = data_url[len(prefix) :]
    try:
        raw = base64.b64decode(encoded_payload, validate=True)
        signature_image = Image.open(BytesIO(raw)).convert('RGBA')
        return signature_image
    except Exception:
        return None


def _load_company_logo() -> Image.Image | None:
    configured_logo_path = os.getenv('CERT_COMPANY_LOGO_PATH', '').strip()
    backend_root = Path(__file__).resolve().parents[2]

    candidates: list[Path] = []
    if configured_logo_path:
        candidates.append(Path(configured_logo_path))

    candidates.extend(
        [
            backend_root / 'assets' / 'orbit_linker.png',
            backend_root / 'assets' / 'orbit_linker_logo.png',
            backend_root / 'assets' / 'logo.png',
            Path.home() / 'Documents' / 'Logo.png',
        ]
    )

    for candidate in candidates:
        try:
            if candidate.exists():
                return Image.open(candidate).convert('RGBA')
        except Exception:
            continue

    return None


def render_certificate_image(record: CertificateRecord, image_format: str = 'png') -> bytes:
    width, height = 1800, 1273
    image = Image.new('RGB', (width, height), '#fcf9f2')
    draw = ImageDraw.Draw(image)

    # Layered border to create a formal certificate look.
    draw.rectangle((45, 45, width - 45, height - 45), outline='#b08d57', width=8)
    draw.rectangle((85, 85, width - 85, height - 85), outline='#1d7a59', width=3)

    title_font = _load_font(84, bold=True)
    subtitle_font = _load_font(38, bold=False)
    name_font = _load_font(88, bold=True)
    body_font = _load_font(44, bold=False)
    small_font = _load_font(34, bold=False)
    strong_small_font = _load_font(34, bold=True)
    fallback_logo_font = _load_font(54, bold=True)

    logo = _load_company_logo()
    y = 112
    if logo is not None:
        resampling = getattr(Image, 'Resampling', Image)
        logo.thumbnail((560, 145), resampling.LANCZOS)
        logo_x = (width - logo.width) // 2
        image.paste(logo, (logo_x, y), logo)
        y += logo.height + 44
    else:
        y += _draw_centered_text(
            draw,
            'Orbit-Linker',
            y,
            width,
            fallback_logo_font,
            (15, 55, 41),
        )
        y += 34

    y += _draw_centered_text(draw, 'Certificate of Completion', y, width, title_font, (23, 81, 63))
    y += 34
    y += _draw_centered_text(
        draw,
        'This is proudly awarded to',
        y,
        width,
        subtitle_font,
        (70, 90, 82),
    )
    y += 24

    recipient_name = record.payload.recipient_name
    y += _draw_centered_text(draw, recipient_name, y, width, name_font, (15, 55, 41))
    y += 38

    course_line = f'for successfully completing "{record.payload.course_name}"'
    for line in fill(course_line, width=54).splitlines():
        y += _draw_centered_text(draw, line, y, width, body_font, (32, 44, 39))
        y += 10

    y += 26
    issue_label = f'Issued on: {record.payload.issue_date.isoformat()}'
    y += _draw_centered_text(draw, issue_label, y, width, strong_small_font, (23, 81, 63))

    issuer_name = record.payload.issuer_name or 'Authorized Issuer'
    signature_region_left = 220
    signature_region_right = 760
    signature_line_y = height - 260

    signature_image = _load_signature_image(record.payload.issuer_signature_data_url)
    if signature_image is not None:
        resampling = getattr(Image, 'Resampling', Image)
        signature_image.thumbnail((420, 130), resampling.LANCZOS)
        signature_center_x = (signature_region_left + signature_region_right) // 2
        signature_x = signature_center_x - signature_image.width // 2
        signature_y = signature_line_y - signature_image.height - 12
        image.paste(signature_image, (signature_x, signature_y), signature_image)

    draw.line((signature_region_left, signature_line_y, signature_region_right, signature_line_y), fill='#1d7a59', width=3)
    _draw_centered_text_in_region(
        draw,
        issuer_name,
        signature_line_y + 16,
        signature_region_left,
        signature_region_right,
        small_font,
        (34, 52, 46),
    )
    _draw_centered_text_in_region(
        draw,
        'Issuer Signature',
        signature_line_y + 56,
        signature_region_left,
        signature_region_right,
        small_font,
        (89, 107, 99),
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(record.verification_url)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color='#124534', back_color='white').convert('RGB')
    qr_image = qr_image.resize((250, 250))

    qr_box_x, qr_box_y = width - 395, height - 362
    draw.rectangle(
        (qr_box_x - 18, qr_box_y - 18, qr_box_x + 268, qr_box_y + 268),
        fill='#f8fffb',
        outline='#1d7a59',
        width=3,
    )
    image.paste(qr_image, (qr_box_x, qr_box_y))

    certificate_id_line = f'Certificate ID: {record.certificate_id}'
    draw.text((130, height - 130), certificate_id_line, font=small_font, fill=(77, 96, 88))

    output = BytesIO()
    normalized_format = image_format.lower()
    if normalized_format in {'jpg', 'jpeg'}:
        image.save(output, format='JPEG', quality=95)
    else:
        image.save(output, format='PNG')

    return output.getvalue()
