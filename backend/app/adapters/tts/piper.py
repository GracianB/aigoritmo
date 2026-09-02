from __future__ import annotations

import asyncio
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from app.adapters.tts.base import TtsError
from app.domain.models import VoiceConfig
from app.domain.speech import prepare_for_speech

CREATE_NO_WINDOW = 0x08000000
_CACHE_MAX = 64
_SYNTH_TIMEOUT = 45.0
_MEM_CACHE: dict[str, bytes] = {}
_INFLIGHT: dict[str, asyncio.Task[bytes]] = {}
_LOCK: asyncio.Lock | None = None


def _lock() -> asyncio.Lock:
    global _LOCK
    if _LOCK is None:
        _LOCK = asyncio.Lock()
    return _LOCK


def _hide_window_kwargs() -> dict:
    if sys.platform != "win32":
        return {}
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    return {
        "creationflags": CREATE_NO_WINDOW,
        "startupinfo": startup,
    }


def _is_wav(data: bytes) -> bool:
    return len(data) > 44 and data[:4] == b"RIFF" and data[8:12] == b"WAVE"


class PiperProvider:
    def __init__(
        self,
        executable: Path,
        models_dir: Path,
        fallback_voice: str = "es-odal-medium",
    ) -> None:
        self._executable = Path(executable)
        self._models_dir = Path(models_dir)
        self._fallback_voice = fallback_voice
        self._root = self._executable.parent
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
                str(model.resolve()),
                text,
                str(getattr(options, "length_scale", 1.08)),
                str(getattr(options, "noise_scale", 0.667)),
                str(getattr(options, "noise_w", 0.8)),
                str(getattr(options, "sentence_silence", 0.38)),
                str(getattr(options, "speaker", "")),
            ]
        )
        return hashlib.sha1(payload.encode("utf-8")).hexdigest()

    def _remember(self, key: str, wav: bytes) -> None:
        if not wav:
            return
        if len(_MEM_CACHE) >= _CACHE_MAX and key not in _MEM_CACHE:
            _MEM_CACHE.pop(next(iter(_MEM_CACHE)))
        _MEM_CACHE[key] = wav
        try:
            (self._disk / f"{key}.wav").write_bytes(wav)
        except OSError:
            pass

    def _from_disk(self, key: str) -> bytes | None:
        path = self._disk / f"{key}.wav"
        if not path.is_file():
            return None
        try:
            wav = path.read_bytes()
        except OSError:
            return None
        if not _is_wav(wav):
            try:
                path.unlink()
            except OSError:
                pass
            return None
        return wav

    async def synthesize(
        self,
        text: str,
        voice_id: str,
        options: VoiceConfig | None = None,
    ) -> bytes:
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
        disk = self._from_disk(key)
        if disk:
            _MEM_CACHE[key] = disk
            return disk

        async with _lock():
            cached = _MEM_CACHE.get(key)
            if cached:
                return cached
            disk = self._from_disk(key)
            if disk:
                _MEM_CACHE[key] = disk
                return disk
            task = _INFLIGHT.get(key)
            if task is None:
                task = asyncio.create_task(self._run(spoken, model, options))
                _INFLIGHT[key] = task

        try:
            wav = await task
        except Exception:
            async with _lock():
                if _INFLIGHT.get(key) is task:
                    _INFLIGHT.pop(key, None)
            raise

        async with _lock():
            if _INFLIGHT.get(key) is task:
                _INFLIGHT.pop(key, None)
            self._remember(key, wav)
        return wav

    def _build_cmd(self, model: Path, out_path: Path, options: VoiceConfig | None) -> list[str]:
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
        if speaker not in (None, ""):
            cmd.extend(["--speaker", str(speaker)])
        return cmd

    def _run_piper(self, cmd: list[str], text: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            cmd,
            input=text.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(self._root),
            timeout=_SYNTH_TIMEOUT,
            check=False,
            **_hide_window_kwargs(),
        )

    async def _run(self, text: str, model: Path, options: VoiceConfig | None) -> bytes:
        fd, tmp_name = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        out_path = Path(tmp_name)
        cmd = self._build_cmd(model, out_path, options)
        try:
            try:
                proc = await asyncio.to_thread(self._run_piper, cmd, text)
            except subprocess.TimeoutExpired:
                raise TtsError(
                    "piper_unavailable",
                    "Piper tardó demasiado en sintetizar.",
                ) from None
            except FileNotFoundError:
                raise TtsError(
                    "piper_unavailable",
                    f"No se pudo ejecutar Piper: {self._executable}",
                ) from None
            except OSError as exc:
                raise TtsError("piper_unavailable", f"Piper no arrancó: {exc}") from exc

            stderr = (proc.stderr or b"").decode("utf-8", errors="replace").strip()[:400]
            if proc.returncode != 0:
                raise TtsError("piper_unavailable", f"Piper falló ({proc.returncode}): {stderr}")

            try:
                wav = out_path.read_bytes()
            except OSError as exc:
                raise TtsError("piper_unavailable", f"No se pudo leer el WAV: {exc}") from exc

            if not _is_wav(wav):
                raise TtsError(
                    "piper_unavailable",
                    f"Piper no generó un WAV válido: {stderr or 'salida vacía'}",
                )
            return wav
        finally:
            try:
                out_path.unlink(missing_ok=True)
            except OSError:
                pass