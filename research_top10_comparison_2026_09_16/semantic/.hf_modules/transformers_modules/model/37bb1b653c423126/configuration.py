from transformers.models.qwen3.configuration_qwen3 import Qwen3Config


class PPLXQwen3Config(Qwen3Config):
    model_type = "bidirectional_pplx_qwen3"
