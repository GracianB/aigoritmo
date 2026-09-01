from typing import Literal

from pydantic import BaseModel, Field


class VoiceConfig(BaseModel):
    provider: Literal["piper"] = "piper"
    voice_id: str
    fallback_voice_id: str = "es-odal-medium"
    length_scale: float = 1.08
    noise_scale: float = 0.667
    noise_w: float = 0.8
    sentence_silence: float = 0.38
    speaker: int | None = None


class LlmConfig(BaseModel):
    provider: Literal["ollama", "spacexai"]
    model: str
    catalog_model: str | None = None
    preferred_provider: Literal["ollama", "spacexai"] | None = None


class Capabilities(BaseModel):
    chatter: bool = True
    generate_images: bool = False
    analyze_image: bool = False
    transcribe_audio: bool = False
    improve_content: bool = False
    podcaster: bool = False
    social_media: bool = False
    video_editor: bool = False


class Avatar(BaseModel):
    id: str
    name: str
    description: str = ""
    video: str | None = None
    poster: str
    voice: VoiceConfig
    llm: LlmConfig
    system_prompt: str
    welcome: str = ""
    feature: str = ""
    capabilities: Capabilities = Field(default_factory=Capabilities)


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class Conversation(BaseModel):
    id: str
    avatar_id: str
    messages: list[ChatMessage] = Field(default_factory=list)
