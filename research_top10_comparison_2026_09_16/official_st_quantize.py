import torch
import numpy as np
from typing import Literal
from sentence_transformers.models import Module


class Quantizer(torch.nn.Module):
    def __init__(self, hard: bool = True):
        """
        Args:
            hard: Whether to use hard or soft quantization. Defaults to True.
        """
        super().__init__()
        self._hard = hard

    def _hard_quantize(self, x, *args, **kwargs) -> torch.Tensor:
        raise NotImplementedError

    def _soft_quantize(self, x, *args, **kwargs) -> torch.Tensor:
        raise NotImplementedError

    def forward(self, x, *args, **kwargs) -> torch.Tensor:
        soft = self._soft_quantize(x, *args, **kwargs)

        if not self._hard:
            result = soft
        else:
            result = (
                self._hard_quantize(x, *args, **kwargs).detach() + soft - soft.detach()
            )

        return result


class Int8TanhQuantizer(Quantizer):
    def __init__(
        self,
        hard: bool = True,
    ):
        super().__init__(hard=hard)
        self.qmin = -128
        self.qmax = 127

    def _soft_quantize(self, x, *args, **kwargs):
        return torch.tanh(x)

    def _hard_quantize(self, x, *args, **kwargs):
        soft = self._soft_quantize(x)
        int_x = torch.round(soft * self.qmax)
        int_x = torch.clamp(int_x, self.qmin, self.qmax)
        return int_x


class BinaryTanhQuantizer(Quantizer):
    def __init__(
        self,
        hard: bool = True,
        scale: float = 1.0,
    ):
        super().__init__(hard)
        self._scale = scale

    def _soft_quantize(self, x, *args, **kwargs):
        return torch.tanh(self._scale * x)

    def _hard_quantize(self, x, *args, **kwargs):
        return torch.where(x >= 0, 1.0, -1.0)
    

class PackedBinaryQuantizer:
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        bits = np.where(x.cpu().numpy() >=  0, True, False)
        packed = np.packbits(bits, axis=-1)
        return torch.from_numpy(packed).to(x.device)


class FlexibleQuantizer(Module):
    def __init__(self):
        super().__init__()
        self._int8_quantizer = Int8TanhQuantizer()
        self._binary_quantizer = BinaryTanhQuantizer()
        self._packed_binary_quantizer = PackedBinaryQuantizer()

    def forward(
        self,
        features: dict[str, torch.Tensor],
        quantization: Literal["int8", "binary", "ubinary"] = "int8",
        **kwargs
    ) -> dict[str, torch.Tensor]:
        if quantization == "int8":
            features["sentence_embedding"] = self._int8_quantizer(
                features["sentence_embedding"]
            )
        elif quantization == "binary":
            features["sentence_embedding"] = self._binary_quantizer(
                features["sentence_embedding"]
            )
        elif quantization == "ubinary":
            features["sentence_embedding"] = self._packed_binary_quantizer(
                features["sentence_embedding"]
            )
        else:
            raise ValueError(
                f"Invalid quantization type: {quantization}. Must be 'binary', 'ubinary', or 'int8'."
            )
        return features

    @classmethod
    def load(
        cls,
        model_name_or_path: str,
        subfolder: str = "",
        token: bool | str | None = None,
        cache_folder: str | None = None,
        revision: str | None = None,
        local_files_only: bool = False,
        **kwargs,
    ):
        return cls()
        
    def save(self, output_path: str, *args, **kwargs) -> None: 
        return
