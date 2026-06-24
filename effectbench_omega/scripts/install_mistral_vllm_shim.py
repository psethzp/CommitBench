#!/usr/bin/env python
"""Install the local Mistral/vLLM tokenizer compatibility shim.

The current experiment venv uses a vLLM/transformers combination where
MistralCommonBackend/Pixtral helpers are missing a few methods vLLM expects.
This writes a small sitecustomize.py into the active Python environment so
Mistral-Small-3.2 can be served through the official Mistral tokenizer/config
and tool-call parser path.
"""

from __future__ import annotations

import site
from pathlib import Path


SHIM = '''"""Local compatibility patches for this experiment venv."""

try:
    from transformers.tokenization_utils_base import PreTrainedTokenizerBase

    if not hasattr(PreTrainedTokenizerBase, "is_fast"):
        PreTrainedTokenizerBase.is_fast = property(lambda self: False)
except Exception:
    pass

try:
    from transformers.tokenization_mistral_common import MistralCommonBackend

    def _mistral_get_chat_template(self, chat_template=None, tools=None):
        if chat_template is not None:
            return chat_template
        template = getattr(self, "chat_template", None)
        if template is not None:
            return template
        raise ValueError("MistralCommonBackend needs an explicit chat_template")

    def _mistral_get_added_vocab(self):
        return {}

    def _mistral_convert_tokens_to_string(self, tokens):
        if isinstance(tokens, str):
            tokens = [tokens]
        ids = [self.convert_tokens_to_ids(token) for token in tokens]
        return self.decode(ids, skip_special_tokens=False)

    MistralCommonBackend.get_chat_template = _mistral_get_chat_template
    MistralCommonBackend.get_added_vocab = _mistral_get_added_vocab
    MistralCommonBackend.convert_tokens_to_string = _mistral_convert_tokens_to_string
except Exception:
    pass

try:
    from PIL import Image
    from transformers.image_utils import load_image
    from vllm.transformers_utils.processors.pixtral import MistralCommonImageProcessor

    def _mistral_fetch_images(self, images):
        def _load_one(image):
            if isinstance(image, Image.Image):
                return image
            if isinstance(image, dict):
                image = image.get("url") or image.get("path") or image.get("image_url") or image
            if isinstance(image, str):
                return load_image(image)
            return image

        if images is None:
            return None
        if isinstance(images, list):
            return [_load_one(image) for image in images]
        return _load_one(images)

    if not hasattr(MistralCommonImageProcessor, "fetch_images"):
        MistralCommonImageProcessor.fetch_images = _mistral_fetch_images
except Exception:
    pass
'''


def main() -> None:
    site_packages = Path(site.getsitepackages()[0])
    site_packages.mkdir(parents=True, exist_ok=True)
    target = site_packages / "sitecustomize.py"
    target.write_text(SHIM, encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
