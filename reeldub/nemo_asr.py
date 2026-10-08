"""Run an AI4Bharat IndicConformer .nemo checkpoint on a list of WAV files and print JSON texts.

Runs inside the NeMo environment (separate venv), called by asr.transcribe_indicconformer:
    python nemo_asr.py MODEL.nemo out.json a.wav b.wav ...
Uses the CTC head of the hybrid RNNT/CTC model: CTC emits one label per audio frame, so unlike Whisper it
cannot run on and invent sentences that weren't said.
"""

import json
import sys


def main():
    model_path, out_path, *wavs = sys.argv[1:]
    from nemo.collections.asr.models import ASRModel

    model = ASRModel.restore_from(model_path, map_location="cpu")
    model.eval()
    try:
        model.change_decoding_strategy(decoder_type="ctc")
    except TypeError:  # non-hybrid checkpoint
        pass
    results = model.transcribe(wavs, batch_size=4)
    if isinstance(results, tuple):  # older NeMo returns (best, all)
        results = results[0]
    texts = [r if isinstance(r, str) else getattr(r, "text", str(r)) for r in results]
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
