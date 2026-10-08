"""Split the reel's audio into her voice and everything else (music, room, effects).

Model choice is about speed on this kind of machine. Measured here on 4 CPU cores, 26 s of audio:
  UVR-MDX-NET-Voc_FT.onnx          33 s   (~1.3x real time)  <- default without a GPU
  htdemucs_ft.yaml                150 s   (~5.8x)
  model_bs_roformer_ep_317...    669 s   (~26x)             <- default with a CUDA GPU (best quality, SDR ~12.97)
The music bed is computed as original - vocals, so nothing but the voice is lost.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from . import media

CPU_MODEL = "UVR-MDX-NET-Voc_FT.onnx"
GPU_MODEL = "model_bs_roformer_ep_317_sdr_12.9755.ckpt"


def default_model() -> str:
    try:
        import torch
        return GPU_MODEL if torch.cuda.is_available() else CPU_MODEL
    except ImportError:
        return CPU_MODEL


def separate(audio_wav: Path, workdir: Path, model: str | None = None) -> tuple[Path, Path]:
    """Return (vocals.wav, bed.wav)."""
    from audio_separator.separator import Separator  # heavy import; only when needed

    model = model or default_model()
    tmp = workdir / "sep_tmp"
    tmp.mkdir(exist_ok=True)
    sep = Separator(output_dir=str(tmp), output_single_stem="Vocals", log_level=30)
    sep.load_model(model_filename=model)
    outputs = sep.separate(str(audio_wav))
    vocal_file = next((tmp / Path(o).name for o in outputs if "vocal" in Path(o).name.lower()), None)
    if vocal_file is None or not vocal_file.exists():
        raise RuntimeError(f"separator produced no vocals stem: {outputs}")

    vocals = workdir / "vocals.wav"
    media.ffmpeg("-i", str(vocal_file), "-ar", str(media.SR), "-ac", "2", "-c:a", "pcm_s16le", str(vocals))
    shutil.rmtree(tmp, ignore_errors=True)
    bed = media.subtract(audio_wav, vocals, workdir / "bed.wav")
    return vocals, bed
