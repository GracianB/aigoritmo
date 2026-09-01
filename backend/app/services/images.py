import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image


class ImageStore:
    def __init__(self, directory: Path) -> None:
        self._directory = directory
        self._directory.mkdir(parents=True, exist_ok=True)

    def save_png(self, image_bytes: bytes) -> str:
        clip_id = str(uuid.uuid4())
        path = self._directory / f"{clip_id}.png"
        if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            path.write_bytes(image_bytes)
            return clip_id
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        image.save(path, format="PNG")
        return clip_id
