import inspect
from typing import Callable
import torch
from transformers import Qwen3Model
from transformers.cache_utils import Cache
from transformers.masking_utils import create_causal_mask
from transformers.modeling_outputs import BaseModelOutputWithPooling
from transformers.processing_utils import Unpack
from transformers.utils import TransformersKwargs
from .configuration import PPLXQwen3Config

# The transformers `create_causal_mask` signature has shifted over releases:
#   * <= 5.1: kwarg is `input_embeds`, `cache_position` is required positional
#   * 5.2 - 5.5: renamed to `inputs_embeds`, `cache_position` still required
#   * 5.6 - 5.8: `cache_position` has a default (kept for BC)
#   * >= 5.9: `cache_position` removed entirely
# Detect once at import time which names this transformers exposes.
_CCM_PARAMS = inspect.signature(create_causal_mask).parameters
_CCM_EMBEDS_KEY = "inputs_embeds" if "inputs_embeds" in _CCM_PARAMS else "input_embeds"
_CCM_ACCEPTS_CACHE_POSITION = "cache_position" in _CCM_PARAMS


# From modeling_t5gemma.py
def bidirectional_mask_function(attention_mask: torch.Tensor | None) -> Callable:
    """
    This creates bidirectional attention mask.
    """

    def inner_mask(batch_idx: int, head_idx: int, q_idx: int, kv_idx: int) -> bool:
        if attention_mask is None:
            return torch.ones((), dtype=torch.bool)
        return attention_mask[batch_idx, kv_idx].to(torch.bool)

    return inner_mask


class PPLXQwen3Model(Qwen3Model):
    _supports_flash_attn = True
    _supports_sdpa = True

    config_class = PPLXQwen3Config

    def __init__(self, config):
        super().__init__(config)
        self.post_init()

    def post_init(self):
        super().post_init()
        # Override to set all layers to non-causal attention. This'll work with attn_implementation="flash_attention_2" or "sdpa"
        for layer in self.layers:
            layer.self_attn.is_causal = False

    def forward(
        self,
        input_ids: torch.LongTensor | None = None,
        attention_mask: torch.Tensor | None = None,
        position_ids: torch.LongTensor | None = None,
        past_key_values: Cache | None = None,
        inputs_embeds: torch.FloatTensor | None = None,
        use_cache: bool | None = None,
        cache_position: torch.LongTensor | None = None,
        **kwargs: Unpack[TransformersKwargs],
    ) -> BaseModelOutputWithPooling:
        if inputs_embeds is None:
            inputs_embeds = self.embed_tokens(input_ids)
            input_ids = None

        mask_kwargs = {
            "config": self.config,
            _CCM_EMBEDS_KEY: inputs_embeds,
            "attention_mask": attention_mask,
            "past_key_values": None,
            "position_ids": position_ids,
            "or_mask_function": bidirectional_mask_function(attention_mask),
        }
        if _CCM_ACCEPTS_CACHE_POSITION:
            mask_kwargs["cache_position"] = torch.arange(
                inputs_embeds.shape[1], device=inputs_embeds.device, dtype=torch.long
            )
        attention_mask = {"full_attention": create_causal_mask(**mask_kwargs)}

        outputs = super().forward(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            cache_position=cache_position,
            **kwargs,
        )
        return outputs