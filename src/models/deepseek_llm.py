"""DeepSeek-R1 inference wrapper for GPU 0."""
from __future__ import annotations

from dataclasses import dataclass

from llama_cpp import Llama


@dataclass
class DeepSeekResponse:
    thought: str
    content: str


class DeepSeekLLM:
    def __init__(self, model_path: str) -> None:
        self.model_path = model_path
        self.client = Llama(
            model_path=self.model_path,
            n_gpu_layers=-1,
            n_ctx=65536,
        )

    def generate(self, prompt: str) -> DeepSeekResponse:
        response = self.client(
            prompt,
            max_tokens=2048,
            temperature=0.7,
            stop=None,
        )
        text = response["choices"][0]["text"]
        thought = ""
        content = text

        if "<think>" in text and "</think>" in text:
            before, rest = text.split("<think>", 1)
            thought_body, after = rest.split("</think>", 1)
            thought = thought_body.strip()
            content = (before + after).strip()

        return DeepSeekResponse(thought=thought, content=content)
