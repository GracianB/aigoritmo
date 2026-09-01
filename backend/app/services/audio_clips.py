import uuid
from pathlib import Path


class AudioClipStore:
    def __init__(self, directory: Path) -> None:
        self._directory = directory
        self._directory.mkdir(parents=True, exist_ok=True)

    def save(self, wav_bytes: bytes) -> str:
        clip_id = str(uuid.uuid4())
        path = self._directory / f"{clip_id}.wav"
        path.write_bytes(wav_bytes)
        return clip_id

    def path_for(self, clip_id: str) -> Path:
        path = self._directory / f"{clip_id}.wav"
        if not path.is_file():
            raise FileNotFoundError(clip_id)
        return path
