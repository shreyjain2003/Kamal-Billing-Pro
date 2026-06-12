import asyncio
from bleak import BleakScanner, BleakClient
from PIL import Image, ImageDraw, ImageFont

CHAR_UUID = "bef8d6c9-9c21-4c9e-b632-bd58c1009f9f"
PAPER_WIDTH_DOTS = 384
HEADING_FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def heading_image_command(text):
    margin = 12
    max_text_width = PAPER_WIDTH_DOTS - (margin * 2)

    for size in range(46, 23, -1):
        font = ImageFont.truetype(HEADING_FONT, size)
        bbox = ImageDraw.Draw(Image.new("L", (1, 1), 255)).textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_text_width:
            break

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    image_height = text_height + 18
    image = Image.new("L", (PAPER_WIDTH_DOTS, image_height), 255)
    draw = ImageDraw.Draw(image)
    left = (PAPER_WIDTH_DOTS - text_width) // 2 - bbox[0]
    top = (image_height - text_height) // 2 - bbox[1]
    draw.text((left, top), text, font=font, fill=0)

    width_bytes = PAPER_WIDTH_DOTS // 8
    data = bytearray()

    for y in range(image.height):
        for x_byte in range(width_bytes):
            byte = 0
            for bit in range(8):
                x = (x_byte * 8) + bit
                if image.getpixel((x, y)) < 128:
                    byte |= 0x80 >> bit
            data.append(byte)

    return (
        b"\x1D\x76\x30\x00"
        + bytes([width_bytes % 256, width_bytes // 256, image.height % 256, image.height // 256])
        + bytes(data)
    )


async def print_receipt(text):

    try:

        device = await BleakScanner.find_device_by_name(
            "MPT-II",
            timeout=5
        )

        if not device:
            print("Printer not found")
            return False

        async with BleakClient(
            device,
            timeout=20
        ) as client:

            lines = text.splitlines()
            title = lines[0] if lines else ""
            body = "\n".join(lines[1:])

            payload = b"\x1B\x40"
            payload += heading_image_command(title.strip())
            payload += b"\n"
            payload += b"\x1B\x61\x00"
            payload += body.encode()
            payload += b"\n\n\n"

            await client.write_gatt_char(
                CHAR_UUID,
                payload,
                response=True
            )

            print("Printed Successfully")

            return True

    except Exception as e:

        print("PRINT ERROR:", e)

        return False
