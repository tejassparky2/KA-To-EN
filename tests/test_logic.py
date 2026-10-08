"""Unit tests for the pure timing/budget logic (no network, no API keys)."""

from reeldub.asr import group_words, plan_chunks
from reeldub.segments import Script, Segment, merge_short, slot_end
from reeldub.timeline import plan_fit
from reeldub.translate import budgets, count_syllables, syllable_budget
from reeldub.voice import best_window


def _script(spans, total):
    return Script(segments=[Segment(id=i, start=s, end=e, kn=f"k{i}") for i, (s, e) in enumerate(spans)], total=total)


def test_plan_chunks_cuts_in_pauses_and_respects_max():
    silences = [(9.0, 10.0), (19.0, 21.0), (33.0, 34.0)]
    chunks = plan_chunks(silences, total=50.0, max_len=25.0)
    assert chunks[0] == (0.0, 20.0)  # last pause midpoint within 25 s
    assert all(e - s <= 25.0 for s, e in chunks)
    assert chunks[-1][1] == 50.0
    assert all(a[1] == b[0] for a, b in zip(chunks, chunks[1:]))


def test_plan_chunks_hard_split_without_pauses():
    assert plan_chunks([], total=60.0, max_len=25.0) == [(0.0, 25.0), (25.0, 50.0), (50.0, 60.0)]


def test_plan_chunks_short_clip_single_chunk():
    assert plan_chunks([(2.0, 3.0)], total=12.0) == [(0.0, 12.0)]


def test_slot_end_uses_following_pause():
    sc = _script([(0.0, 2.0), (3.0, 5.0)], total=8.0)
    assert slot_end(sc.segments, 0, sc.total) == 3.0 - 0.05
    assert slot_end(sc.segments, 1, sc.total) == 8.0 - 0.05


def test_merge_short_folds_tiny_phrases():
    segs = [Segment(0, 0.0, 2.0, "a"), Segment(1, 2.1, 2.5, "b"), Segment(2, 4.0, 6.0, "c")]
    out = merge_short(segs)
    assert [s.kn for s in out] == ["a b", "c"]
    assert [s.id for s in out] == [0, 1]
    assert out[0].end == 2.5


def test_group_words_splits_on_pause():
    words = [(0.0, 0.3, "a"), (0.35, 0.6, "b"), (1.5, 1.8, "c")]
    segs = group_words(words, max_gap=0.45)
    assert [s.kn for s in segs] == ["a b", "c"]


def test_count_syllables_reasonable():
    assert count_syllables("hello") == 2
    assert count_syllables("today I will make ragi mudde") in range(8, 12)
    assert count_syllables("") == 0


def test_budgets_follow_slot_length():
    sc = _script([(0.0, 2.0), (2.5, 4.0)], total=4.5)
    b = budgets(sc)
    assert b[0] == syllable_budget(2.45)
    assert b[1] == syllable_budget(4.45 - 2.5)


def test_plan_fit_statuses():
    sc = _script([(0.0, 1.0), (2.0, 3.0), (4.0, 5.0), (6.0, 7.0)], total=8.0)
    # slots: 1.95, 1.95, 1.95, 1.95
    fits = plan_fit(sc, [1.5, 2.2, 2.6, 4.0])
    assert [f.status for f in fits] == ["ok", "stretched", "over_accept", "too_long"]
    assert fits[0].tempo == 1.0
    assert fits[3].tempo == 1.4


def test_best_window_prefers_dense_speech():
    sc = _script([(0.0, 1.0), (5.0, 9.0), (9.2, 13.0), (13.1, 14.5)], total=20.0)
    s, e = best_window(sc, 10.0)
    assert (s, e) == (5.0, 14.5)


def test_speech_phrases_between_pauses():
    from reeldub.asr import speech_phrases
    assert speech_phrases([(0.0, 0.5), (3.0, 3.6), (5.9, 6.0)], total=6.0) == [(0.5, 3.0), (3.6, 5.9)]
    long = speech_phrases([(10.0, 10.5)], total=40.0, max_len=15.0)
    assert all(e - s <= 15.0 for s, e in long) and long[0][0] == 0.0 and long[-1][1] == 40.0
