"""Kannada speech -> text with AI4Bharat's IndicConformer checkpoint, using stock NeMo modules (CPU ok).

Runs inside the NeMo venv, called by asr.transcribe_indicconformer:
    python nemo_asr.py MODEL.nemo out.json a.wav b.wav ...

Why not ASRModel.restore_from: the checkpoint was trained with AI4Bharat's NeMo fork. Its "multilingual"
tokenizer and "multisoftmax" heads are fork-only, so stock NeMo can't build the model class. But the CTC head
is a plain ConvASRDecoder whose 5632 outputs are 22 languages x 256 word-pieces (in the order of
tokenizer.langs) plus one blank at the end. Kannada is one fixed 256-wide slice, so we run the stock
preprocessor + Conformer encoder + CTC head and decode greedily inside that slice. CTC emits at most one
token per frame, so it cannot invent whole sentences the way Whisper can.
"""

import json
import sys
import tarfile
import tempfile
from pathlib import Path

LANG = "kn"
PIECES_PER_LANG = 256


def _strip_targets(cfg, drop=()):
    from omegaconf import OmegaConf
    d = OmegaConf.to_container(cfg, resolve=True)
    d.pop("_target_", None)
    for k in drop:
        d.pop(k, None)
    return d


def load(model_path: str):
    import torch
    from nemo.collections.asr.modules import AudioToMelSpectrogramPreprocessor, ConformerEncoder, ConvASRDecoder
    from omegaconf import OmegaConf

    tmp = Path(tempfile.mkdtemp())
    with tarfile.open(model_path) as tf:
        tf.extract("./model_config.yaml", tmp)
        tf.extract("./model_weights.ckpt", tmp)
    cfg = OmegaConf.load(tmp / "model_config.yaml")
    state = torch.load(tmp / "model_weights.ckpt", map_location="cpu", weights_only=False)

    pre = AudioToMelSpectrogramPreprocessor(**_strip_targets(cfg.preprocessor))
    pre.featurizer.dither = 0.0  # deterministic inference
    enc = ConformerEncoder(**_strip_targets(cfg.encoder))
    dec_cfg = _strip_targets(cfg.aux_ctc.decoder, drop=("multisoftmax",))
    dec = ConvASRDecoder(**dec_cfg)
    for name, mod in (("preprocessor", pre), ("encoder", enc), ("ctc_decoder", dec)):
        sub = {k[len(name) + 1:]: v for k, v in state.items() if k.startswith(name + ".")}
        mod.load_state_dict(sub, strict=name != "preprocessor")
        mod.eval()

    langs = list(cfg.tokenizer.langs.keys())
    lo = langs.index(LANG) * PIECES_PER_LANG
    vocab = list(cfg.aux_ctc.decoder.vocabulary)
    blank = len(vocab)  # ConvASRDecoder appends the blank as the last class
    return pre, enc, dec, lo, vocab, blank


def transcribe(wav: str, pre, enc, dec, lo, vocab, blank) -> str:
    import soundfile as sf
    import torch

    audio, sr = sf.read(wav, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    assert sr == 16000, f"{wav}: expected 16 kHz, got {sr}"
    with torch.no_grad():
        x = torch.from_numpy(audio)[None]
        feats, flen = pre(input_signal=x, length=torch.tensor([x.shape[1]]))
        encoded, elen = enc(audio_signal=feats, length=flen)
        logp = dec(encoder_output=encoded)[0, : int(elen[0])]  # (T, 5633)
    cols = list(range(lo, lo + PIECES_PER_LANG)) + [blank]
    best = logp[:, cols].argmax(dim=-1).tolist()
    pieces, prev = [], None
    for idx in best:
        if idx != prev and idx != PIECES_PER_LANG:  # collapse repeats, drop blank
            piece = vocab[lo + idx]
            if piece != "<unk>":
                pieces.append(piece)
        prev = idx
    return "".join(pieces).replace("▁", " ").strip()


def main():
    model_path, out_path, *wavs = sys.argv[1:]
    parts = load(model_path)
    texts = [transcribe(w, *parts) for w in wavs]
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
