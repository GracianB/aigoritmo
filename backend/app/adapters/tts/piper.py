import asyncio
import hashlib
import os
import sys
import tempfile
from contextlib import suppress
from pathlib import Path

from app.adapters.tts.base import TtsError
from app.domain.models import VoiceConfig
from app.domain.speech import prepare_for_speech

CREATE_NO_WINDOW = 0x08000000
_CACHE_MAX = 64
_SYNTH_TIMEOUT = 45.0
_MEM_CACHE: dict[str, bytes] = {}
_LOCK: asyncio.Lock | None = None


def _lock() -> asyncio.Lock:
    global _LOCK
    if _LOCK is None:
        _LOCK = asyncio.Lock()
    return _LOCK


class PiperProvider:
    def __init__(self, executable: Path, models_dir: Path, fallback_voice: str = "es-odal-medium") -> None:
        self._executable = executable
        self._models_dir = models_dir
        self._fallback_voice = fallback_voice
        self._root = executable.parent
        self._espeak = self._root / "espeak-ng-data"
        self._disk = self._root / "wav_cache"
        self._disk.mkdir(parents=True, exist_ok=True)

    def _model_path(self, voice_id: str, fallback_voice_id: str | None = None) -> Path:
        path = self._models_dir / f"{voice_id}.onnx"
        if path.is_file():
            return path
        for candidate in (fallback_voice_id, self._fallback_voice):
            if not candidate:
                continue
            fallback = self._models_dir / f"{candidate}.onnx"
            if fallback.is_file():
                return fallback
        raise TtsError(
            "piper_unavailable",
            f"Modelo Piper no encontrado: {path.name} en {self._models_dir}",
        )

    def _cache_key(self, text: str, model: Path, options: VoiceConfig | None) -> str:
        payload = "|".join(
            [
                str(model),
                text,
                str(getattr(options, "length_scale", 1.08)),
                str(getattr(options, "noise_scale", 0.667)),
                str(getattr(options, "noise_w", 0.8)),
                str(getattr(options, "sentence_silence", 0.38)),
                str(getattr(options, "speaker", "")),
            ]
        )
        return hashlib.sha1(payload.encode("utf-8")).hexdigest()

    async def synthesize(self, text: str, voice_id: str, options: VoiceConfig | None = None) -> bytes:
        spoken = prepare_for_speech(text)
        if not spoken:
            return b""
        if not self._executable.is_file():
            raise TtsError(
                "piper_unavailable",
                f"No está piper.exe en {self._executable}",
            )
        model = self._model_path(voice_id, options.fallback_voice_id if options else None)
        key = self._cache_key(spoken, model, options)
        cached = _MEM_CACHE.get(key)
        if cached:
            return cached
        disk = self._disk / f"{key}.wav"
        if disk.is_file():
            wav = disk.read_bytes()
            _MEM_CACHE[key] = wav
            return wav

        async with _lock():
            cached = _MEM_CACHE.get(key)
            if cached:
                return cached
            if disk.is_file():
                wav = disk.read_bytes()
                _MEM_CACHE[key] = wav
                return wav
            wav = await self._run(spoken, model, options)
            if wav:
                if len(_MEM_CACHE) >= _CACHE_MAX:
                    _MEM_CACHE.pop(next(iter(_MEM_CACHE)))
                _MEM_CACHE[key] = wav
                try:
                    disk.write_bytes(wav)
                except OSError:
                    pass
            return wav

    async def _run(self, text: str, model: Path, options: VoiceConfig | None) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            out_path = Path(tmp.name)
        cmd = [
            str(self._executable),
            "--model",
            str(model),
            "--output_file",
            str(out_path),
            "--length_scale",
            str(getattr(options, "length_scale", 1.08)),
            "--noise_scale",
            str(getattr(options, "noise_scale", 0.667)),
            "--noise_w",
            str(getattr(options, "noise_w", 0.8)),
            "--sentence_silence",
            str(getattr(options, "sentence_silence", 0.38)),
            "--quiet",
        ]
        config = Path(str(model) + ".json")
        if config.is_file():
            cmd.extend(["--config", str(config)])
        if self._espeak.is_dir():
            cmd.extend(["--espeak_data", str(self._espeak)])
        speaker = getattr(options, "speaker", None)
        if speaker is not None:
            cmd.extend(["--speaker", str(speaker)])
        kwargs: dict = {"cwd": str(self._root)}
        if sys.platform == "win32":
            kwargs["creationflags"] = CREATE_NO_WINDOW
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                **kwargs,
            )
            try:
                _stdout, stderr = await asyncio.wait_for(
                    process.communicate(text.encode("utf-8")),
                    timeout=_SYNTH_TIMEOUT,
                )
            except TimeoutError:
                process.kill()
                with suppress(Exception):
                    await process.wait()
                raise TtsError("piper_unavailable", "Piper tardó demasiado en sintetizar.") from None
            if process.returncode != 0:
                detail = stderr.decode("utf-8", errors="replace")[:400]
                raise TtsError("piper_unavailable", f"Piper falló: {detail}")
            return out_path.read_bytes()
        finally:
            try:
                os.unlink(out_path)
            except OSError:
                pass
