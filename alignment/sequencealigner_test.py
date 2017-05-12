from abc import ABCMeta

from .vocabulary import Vocabulary
from .sequence import Sequence
from .sequencealigner import SimpleScoring
from .sequencealigner import GlobalSequenceAligner
from .sequencealigner import StrictGlobalSequenceAligner
from .sequencealigner import LocalSequenceAligner


DEFAULT_MATCH_SCORE = 3
DEFAULT_MISMATCH_SCORE = -1
DEFAULT_GAP_SCORE = -2

DEFAULT_SCORING = SimpleScoring(DEFAULT_MATCH_SCORE, DEFAULT_MISMATCH_SCORE)


def _align(first, second, aligner, **kwargs):
    vocab = Vocabulary()
    score, encodeds = aligner.align(
        vocab.encodeSequence(Sequence(first)),
        vocab.encodeSequence(Sequence(second)),
        backtrace=True,
        **kwargs
    )
    return score, [vocab.decodeSequenceAlignment(encoded) for encoded in encodeds]


class SequenceAlignerTests(object):
    __metaclass__ = ABCMeta
    ALIGNER = None

    def align(self, first, second):
        return _align(first, second, aligner=self.ALIGNER)

    # FIXME Aligners generate empty alignments when there is no match.
    def ignore_no_match(self):
        score, alignments = self.align('ab', 'xy')
        assert len(alignments) == 0
        assert score == 0

    def test_exact_match(self):
        score, alignments = self.align('ab', 'ab')
        print("alignment:", alignments[0])
        assert len(alignments) == 1
        assert str(alignments[0].first) == 'a b'
        assert str(alignments[0].second) == 'a b'
        assert alignments[0].percentIdentity() == 100.0
        assert alignments[0].percentSimilarity() == 100.0
        assert alignments[0].percentGap() == 0.0
        assert score == DEFAULT_MATCH_SCORE * 2
        assert alignments[0].score == score

    def test_exact_left_partial_match(self):
        score, alignments = self.align('xaby', 'ab')
        assert len(alignments) == 1
        assert str(alignments[0].first) == 'a b'
        assert str(alignments[0].second) == 'a b'
        assert alignments[0].score == score
        assert alignments[0].percentIdentity() == 100.0
        assert alignments[0].percentSimilarity() == 100.0
        assert alignments[0].percentGap() == 0.0
        assert score == DEFAULT_MATCH_SCORE * 2

    def test_exact_right_partial_match(self):
        score, alignments = self.align('ab', 'xaby')
        assert len(alignments) == 1
        assert str(alignments[0].first) == 'a b'
        assert str(alignments[0].second) == 'a b'
        assert alignments[0].percentIdentity() == 100.0
        assert alignments[0].percentSimilarity() == 100.0
        assert alignments[0].percentGap() == 0.0
        assert score == DEFAULT_MATCH_SCORE * 2
        assert alignments[0].score == score

    def test_exact_left_partial_match_with_gap(self):
        score, alignments = self.align('xaby', 'aob')
        assert len(alignments) == 1
        assert str(alignments[0].first) == 'a - b'
        assert str(alignments[0].second) == 'a o b'
        assert alignments[0].percentIdentity() == 2.0 / 3.0 * 100.0
        assert alignments[0].percentSimilarity() == 2.0 / 3.0 * 100.0
        assert alignments[0].percentGap() == 1.0 / 3.0 * 100.0
        assert score == DEFAULT_MATCH_SCORE * 2 + DEFAULT_GAP_SCORE
        assert alignments[0].score == score

    def test_exact_left_partial_match_with_mismatch(self):
        score, alignments = self.align('xamby', 'aob')
        assert len(alignments) == 1
        assert str(alignments[0].first) == 'a m b'
        assert str(alignments[0].second) == 'a o b'
        assert alignments[0].percentIdentity() == 2.0 / 3.0 * 100.0
        assert alignments[0].percentSimilarity() == 2.0 / 3.0 * 100.0
        assert alignments[0].percentGap() == 0.0
        assert score == DEFAULT_MATCH_SCORE * 2 + DEFAULT_MISMATCH_SCORE
        assert alignments[0].score == score


class TestGlobalSequenceAligner(SequenceAlignerTests):
    ALIGNER = GlobalSequenceAligner(DEFAULT_SCORING, DEFAULT_GAP_SCORE)

    def test_multiple_alignments(self):
        score, alignments = self.align('xabcabcy', 'abc')
        assert len(alignments) == 1
        assert str(alignments[0].first) == 'a b c'
        assert str(alignments[0].second) == 'a b c'
        assert alignments[0].percentIdentity() == 3.0 / 3.0 * 100.0
        assert alignments[0].percentSimilarity() == 3.0 / 3.0 * 100.0
        assert alignments[0].percentGap() == 0.0
        assert score == DEFAULT_MATCH_SCORE * 3
        assert alignments[0].score == score

    def test_shortest_path_alignment(self):
        # this tests that it doesn't pick longer paths on the way
        # (e.g. goes up instead of diagonally)
        score, alignments = self.align('aac', 'bac')
        assert len(alignments) == 1
        assert str(alignments[0].first) == 'a a c'
        assert str(alignments[0].second) == 'b a c'
        assert alignments[0].percentIdentity() == 2.0 / 3.0 * 100.0
        assert alignments[0].percentSimilarity() == 2.0 / 3.0 * 100.0
        assert alignments[0].percentGap() == 0.0
        assert score == DEFAULT_MATCH_SCORE * 2 + DEFAULT_MISMATCH_SCORE
        assert alignments[0].score == score


class TestStrictGlobalSequenceAligner(SequenceAlignerTests):
    ALIGNER = StrictGlobalSequenceAligner(DEFAULT_SCORING, DEFAULT_GAP_SCORE)

    def test_exact_left_partial_match(self):
        score, alignments = self.align('xaby', 'ab')
        assert len(alignments) == 1
        assert str(alignments[0].first) == 'x a b y'
        assert str(alignments[0].second) == '- a b -'
        assert alignments[0].score == score
        assert alignments[0].percentIdentity() == 2.0 / 4.0 * 100.0
        assert alignments[0].percentSimilarity() == 2.0 / 4.0 * 100.0
        assert alignments[0].percentGap() == 2.0 / 4.0 * 100.0
        assert score == DEFAULT_MATCH_SCORE * 2 + DEFAULT_GAP_SCORE * 2

    def test_exact_right_partial_match(self):
        score, alignments = self.align('ab', 'xaby')
        assert len(alignments) == 1
        assert str(alignments[0].first) == '- a b -'
        assert str(alignments[0].second) == 'x a b y'
        assert alignments[0].percentIdentity() == 2.0 / 4.0 * 100.0
        assert alignments[0].percentSimilarity() == 2.0 / 4.0 * 100.0
        assert alignments[0].percentGap() == 2.0 / 4.0 * 100.0
        assert score == DEFAULT_MATCH_SCORE * 2 + DEFAULT_GAP_SCORE * 2
        assert alignments[0].score == score

    def test_exact_left_partial_match_with_gap(self):
        score, alignments = self.align('xaby', 'aob')
        assert len(alignments) == 1
        assert str(alignments[0].first) == 'x a - b y'
        assert str(alignments[0].second) == '- a o b -'
        assert alignments[0].percentIdentity() == 2.0 / 5.0 * 100.0
        assert alignments[0].percentSimilarity() == 2.0 / 5.0 * 100.0
        assert alignments[0].percentGap() == 3.0 / 5.0 * 100.0
        assert score == DEFAULT_MATCH_SCORE * 2 + DEFAULT_GAP_SCORE * 3
        assert alignments[0].score == score

    def test_exact_left_partial_match_with_mismatch(self):
        score, alignments = self.align('xamby', 'aob')
        assert len(alignments) == 1
        assert str(alignments[0].first) == 'x a m b y'
        assert str(alignments[0].second) == '- a o b -'
        assert alignments[0].percentIdentity() == 2.0 / 5.0 * 100.0
        assert alignments[0].percentSimilarity() == 2.0 / 5.0 * 100.0
        assert alignments[0].percentGap() == 2.0 / 5.0 * 100.0
        assert score == DEFAULT_MATCH_SCORE * 2 + DEFAULT_MISMATCH_SCORE + DEFAULT_GAP_SCORE * 2
        assert alignments[0].score == score

    def test_multiple_alignments(self):
        score, alignments = self.align('xabcabcy', 'abc')
        assert len(alignments) == 1
        assert str(alignments[0].first) == 'x a b c a b c y'
        assert str(alignments[0].second) == '- a b c - - - -'
        assert alignments[0].percentIdentity() == 3.0 / 8.0 * 100.0
        assert alignments[0].percentSimilarity() == 3.0 / 8.0 * 100.0
        assert alignments[0].percentGap() == 5.0 / 8.0 * 100.0
        assert score == DEFAULT_MATCH_SCORE * 3 + DEFAULT_GAP_SCORE * 5
        assert alignments[0].score == score


class TestLocalSequenceAligner(SequenceAlignerTests):
    ALIGNER = LocalSequenceAligner(DEFAULT_SCORING, DEFAULT_GAP_SCORE)

    def test_multiple_alignments(self):
        score, alignments = self.align('xabcabcy', 'abc')
        assert len(alignments) == 2
        assert str(alignments[0].first) == 'a b c'
        assert str(alignments[0].second) == 'a b c'
        assert alignments[0].percentIdentity() == 3.0 / 3.0 * 100.0
        assert alignments[0].percentSimilarity() == 3.0 / 3.0 * 100.0
        assert alignments[0].percentGap() == 0.0
        assert score == DEFAULT_MATCH_SCORE * 3
        assert alignments[0].score == score

    def test_multiple_gap_alignments(self):
        score, alignments = self.align('abxc', 'axbc')
        assert len(alignments) == 2
        assert set([(str(a.first), str(a.second)) for a in alignments]) == {
            ('a b x - c', 'a - x b c'),
            ('a - b x c', 'a x b - c'),
        }
        assert alignments[0].percentIdentity() == 3.0 / 5.0 * 100.0
        assert alignments[0].percentSimilarity() == 3.0 / 5.0 * 100.0
        assert alignments[0].percentGap() == 2.0 / 5.0 * 100.0
        assert score == DEFAULT_MATCH_SCORE * 3 + DEFAULT_GAP_SCORE * 2
        assert alignments[0].score == score

    def test_shortest_path_alignment(self):
        # this tests that it doesn't pick longer paths on the way
        # (e.g. goes up instead of diagonally)
        score, alignments = self.align('aac', 'bac')
        assert len(alignments) == 1
        assert str(alignments[0].first) == 'a c'
        assert str(alignments[0].second) == 'a c'
        assert alignments[0].percentIdentity() == 3.0 / 3.0 * 100.0
        assert alignments[0].percentSimilarity() == 3.0 / 3.0 * 100.0
        assert alignments[0].percentGap() == 0.0
        assert score == DEFAULT_MATCH_SCORE * 2
        assert alignments[0].score == score
