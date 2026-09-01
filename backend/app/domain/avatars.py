from pathlib import Path

import yaml

from app.domain.models import Avatar


class AvatarCatalog:
    def __init__(self, avatars_dir: Path) -> None:
        self._avatars_dir = avatars_dir
        self._by_id: dict[str, Avatar] = {}
        self.reload()

    def reload(self) -> None:
        loaded: dict[str, Avatar] = {}
        if not self._avatars_dir.is_dir():
            raise FileNotFoundError(f"avatars dir missing: {self._avatars_dir}")
        paths = sorted(self._avatars_dir.glob("*.yaml"))
        if not paths:
            raise FileNotFoundError(f"no avatar YAML files in {self._avatars_dir}")
        for path in paths:
            with path.open(encoding="utf-8") as handle:
                raw = yaml.safe_load(handle)
            avatar = Avatar.model_validate(raw)
            if avatar.id in loaded:
                raise ValueError(f"duplicate avatar id: {avatar.id}")
            loaded[avatar.id] = avatar
        self._by_id = loaded

    def get(self, avatar_id: str) -> Avatar:
        try:
            return self._by_id[avatar_id]
        except KeyError as exc:
            raise KeyError(f"unknown avatar: {avatar_id}") from exc

    def list(self) -> list[Avatar]:
        return sorted(self._by_id.values(), key=lambda avatar: avatar.name.lower())
