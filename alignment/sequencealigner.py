from six import text_type
from six.moves import range

try:
    import numpypy as numpy
except ImportError:
    import numpy
from abc import ABCMeta
from abc import abstractmethod

from .sequence import GAP_CODE
from .sequence import EncodedSequence


# Scoring ---------------------------------------------------------------------

class Scoring(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self, firstElement, secondElement):
        return 0


class SimpleScoring(Scoring):

    def __init__(self, matchScore, mismatchScore):
        self.matchScore = matchScore
        self.mismatchScore = mismatchScore

    def __call__(self, firstElement, secondElement):
        if firstElement == secondElement:
            return self.matchScore
        else:
            return self.mismatchScore


# Alignment -------------------------------------------------------------------

class SequenceAlignment(object):

    def __init__(self, first, second, gap=GAP_CODE, other=None):
        self.first = first
        self.second = second
        self.gap = gap
        if other is None:
            self.scores = [0] * len(first)
            self.score = 0
            self.identicalCount = 0
            self.similarCount = 0
            self.gapCount = 0
        else:
            self.scores = list(other.scores)
            self.score = other.score
            self.identicalCount = other.identicalCount
            self.similarCount = other.similarCount
            self.gapCount = other.gapCount

    def push(self, firstElement, secondElement, score=0):
        self.first.push(firstElement)
        self.second.push(secondElement)
        self.scores.append(score)
        self.score += score
        if firstElement == secondElement:
            self.identicalCount += 1
        if score > 0:
            self.similarCount += 1
        if firstElement == self.gap or secondElement == self.gap:
            self.gapCount += 1
        pass

    def pop(self):
        firstElement = self.first.pop()
        secondElement = self.second.pop()
        score = self.scores.pop()
        self.score -= score
        if firstElement == secondElement:
            self.identicalCount -= 1
        if score > 0:
            self.similarCount -= 1
        if firstElement == self.gap or secondElement == self.gap:
            self.gapCount -= 1
        return firstElement, secondElement

    def key(self):
        return self.first.key(), self.second.key()

    def reversed(self):
        first = self.first.reversed()
        second = self.second.reversed()
        return type(self)(first, second, self.gap, self)

    def percentIdentity(self):
        try:
            return float(self.identicalCount) / len(self) * 100.0
        except ZeroDivisionError:
            return 0.0

    def percentSimilarity(self):
        try:
            return float(self.similarCount) / len(self) * 100.0
        except ZeroDivisionError:
            return 0.0

    def percentGap(self):
        try:
            return float(self.gapCount) / len(self) * 100.0
        except ZeroDivisionError:
            return 0.0

    def quality(self):
        return self.score, \
            self.percentIdentity(), \
            self.percentSimilarity(), \
            -self.percentGap()

    def __len__(self):
        assert len(self.first) == len(self.second)
        return len(self.first)

    def __getitem__(self, item):
        return self.first[item], self.second[item]

    def __repr__(self):
        return repr((self.first, self.second))

    def __str__(self):
        first = [str(e) for e in self.first.elements]
        second = [str(e) for e in self.second.elements]
        for i in range(len(first)):
            n = max(len(first[i]), len(second[i]))
            format = '%-' + str(n) + 's'
            first[i] = format % first[i]
            second[i] = format % second[i]
        return '%s\n%s' % (' '.join(first), ' '.join(second))

    def __unicode__(self):
        first = [text_type(e) for e in self.first.elements]
        second = [text_type(e) for e in self.second.elements]
        for i in range(len(first)):
            n = max(len(first[i]), len(second[i]))
            format = u'%-' + text_type(n) + u's'
            first[i] = format % first[i]
            second[i] = format % second[i]
        return u'%s\n%s' % (u' '.join(first), u' '.join(second))


# Aligner ---------------------------------------------------------------------

class SequenceAligner(object):
    __metaclass__ = ABCMeta

    def __init__(self, scoring, gapScore):
        self.scoring = scoring
        self.gapScore = gapScore

    def align(self, first, second, backtrace=False):
        f = self.computeAlignmentMatrix(first, second)
        score = self.bestScore(f)
        if backtrace:
            alignments = self.backtrace(first, second, f)
            return score, alignments
        else:
            return score

    def emptyAlignment(self, first, second):
        # Pre-allocate sequences.
        return SequenceAlignment(
            EncodedSequence(len(first) + len(second), id=first.id),
            EncodedSequence(len(first) + len(second), id=second.id),
        )

    @abstractmethod
    def computeAlignmentMatrix(self, first, second):
        return numpy.zeros(0, int)

    @abstractmethod
    def bestScore(self, f):
        return 0

    @abstractmethod
    def backtrace(self, first, second, f):
        return list()


class GlobalSequenceAligner(SequenceAligner):

    def __init__(self, scoring, gapScore):
        super(GlobalSequenceAligner, self).__init__(scoring, gapScore)

    def computeAlignmentMatrix(self, first, second):
        m = len(first) + 1
        n = len(second) + 1
        f = numpy.zeros((m, n), int)
        for i in range(1, m):
            for j in range(1, n):
                # Match elements.
                ab = f[i - 1, j - 1] \
                    + self.scoring(first[i - 1], second[j - 1])

                # Gap on first sequence.
                if i == m - 1:
                    ga = f[i, j - 1]
                else:
                    ga = f[i, j - 1] + self.gapScore

                # Gap on second sequence.
                if j == n - 1:
                    gb = f[i - 1, j]
                else:
                    gb = f[i - 1, j] + self.gapScore

                f[i, j] = max(ab, max(ga, gb))
        return f

    def bestScore(self, f):
        return f[-1, -1]

    def backtrace(self, first, second, f):
        m, n = f.shape
        alignments = list()
        alignment = self.emptyAlignment(first, second)
        self.backtraceFrom(first, second, f, m - 1, n - 1,
                           alignments, alignment)
        return alignments

    def backtraceFrom(self, first, second, f, i, j, alignments, alignment):
        if i == 0 or j == 0:
            alignments.append(alignment.reversed())
        else:
            m, n = f.shape
            c = f[i, j]
            p = f[i - 1, j - 1]
            x = f[i - 1, j]
            y = f[i, j - 1]
            a = first[i - 1]
            b = second[j - 1]
            if c == p + self.scoring(a, b):
                alignment.push(a, b, c - p)
                self.backtraceFrom(first, second, f, i - 1, j - 1,
                                   alignments, alignment)
                alignment.pop()
            else:
                if i == m - 1:
                    if c == y:
                        self.backtraceFrom(first, second, f, i, j - 1,
                                           alignments, alignment)
                elif c == y + self.gapScore:
                    alignment.push(alignment.gap, b, c - y)
                    self.backtraceFrom(first, second, f, i, j - 1,
                                       alignments, alignment)
                    alignment.pop()
                if j == n - 1:
                    if c == x:
                        self.backtraceFrom(first, second, f, i - 1, j,
                                           alignments, alignment)
                elif c == x + self.gapScore:
                    alignment.push(a, alignment.gap, c - x)
                    self.backtraceFrom(first, second, f, i - 1, j,
                                       alignments, alignment)
                    alignment.pop()


class StrictGlobalSequenceAligner(SequenceAligner):

    def __init__(self, scoring, gapScore):
        super(StrictGlobalSequenceAligner, self).__init__(scoring, gapScore)

    def computeAlignmentMatrix(self, first, second):
        m = len(first) + 1
        n = len(second) + 1
        f = numpy.zeros((m, n), int)
        for i in range(1, m):
            f[i, 0] = f[i - 1, 0] + self.gapScore
        for j in range(1, n):
            f[0, j] = f[0, j - 1] + self.gapScore
        for i in range(1, m):
            for j in range(1, n):
                # Match elements.
                ab = f[i - 1, j - 1] \
                    + self.scoring(first[i - 1], second[j - 1])

                # Gap on first sequence.
                ga = f[i, j - 1] + self.gapScore

                # Gap on second sequence.
                gb = f[i - 1, j] + self.gapScore

                f[i, j] = max(ab, max(ga, gb))
        return f

    def bestScore(self, f):
        return f[-1, -1]

    def backtrace(self, first, second, f):
        m, n = f.shape
        alignments = list()
        alignment = self.emptyAlignment(first, second)
        self.backtraceFrom(first, second, f, m - 1, n - 1,
                           alignments, alignment)
        return alignments

    def backtraceFrom(self, first, second, f, i, j, alignments, alignment):
        if i == 0 and j == 0:
            alignments.append(alignment.reversed())
        else:
            c = f[i, j]
            if i != 0:
                x = f[i - 1, j]
                a = first[i - 1]
                if c == x + self.gapScore:
                    alignment.push(a, alignment.gap, c - x)
                    self.backtraceFrom(first, second, f, i - 1, j,
                                       alignments, alignment)
                    alignment.pop()
                    return
            if j != 0:
                y = f[i, j - 1]
                b = second[j - 1]
                if c == y + self.gapScore:
                    alignment.push(alignment.gap, b, c - y)
                    self.backtraceFrom(first, second, f, i, j - 1,
                                       alignments, alignment)
                    alignment.pop()
            if i != 0 and j != 0:
                p = f[i - 1, j - 1]
                # Silence the code inspection warning. We know at this point
                # that a and b are assigned to values.
                # noinspection PyUnboundLocalVariable
                if c == p + self.scoring(a, b):
                    alignment.push(a, b, c - p)
                    self.backtraceFrom(first, second, f, i - 1, j - 1,
                                       alignments, alignment)
                    alignment.pop()


class LocalSequenceAligner(SequenceAligner):

    def __init__(self, scoring, gapScore, minScore=None):
        super(LocalSequenceAligner, self).__init__(scoring, gapScore)
        self.minScore = minScore

    def computeAlignmentMatrix(self, first, second):
        m = len(first) + 1
        n = len(second) + 1
        f = numpy.zeros((m, n), int)
        for i in range(1, m):
            for j in range(1, n):
                # Match elements.
                ab = f[i - 1, j - 1] \
                    + self.scoring(first[i - 1], second[j - 1])

                # Gap on sequenceA.
                ga = f[i, j - 1] + self.gapScore

                # Gap on sequenceB.
                gb = f[i - 1, j] + self.gapScore

                f[i, j] = max(0, max(ab, max(ga, gb)))
        return f

    def bestScore(self, f):
        return f.max()

    def backtrace(self, first, second, f):
        m, n = f.shape
        alignments = list()
        alignment = self.emptyAlignment(first, second)
        if self.minScore is None:
            minScore = self.bestScore(f)
        else:
            minScore = self.minScore
        for i in range(m):
            for j in range(n):
                if f[i, j] >= minScore:
                    self.backtraceFrom(first, second, f, i, j,
                                       alignments, alignment)
        return alignments

    def backtraceFrom(self, first, second, f, i, j, alignments, alignment):
        if f[i, j] == 0:
            alignments.append(alignment.reversed())
        else:
            c = f[i, j]
            p = f[i - 1, j - 1]
            x = f[i - 1, j]
            y = f[i, j - 1]
            a = first[i - 1]
            b = second[j - 1]
            if c == p + self.scoring(a, b):
                alignment.push(a, b, c - p)
                self.backtraceFrom(first, second, f, i - 1, j - 1,
                                   alignments, alignment)
                alignment.pop()
            else:
                if c == y + self.gapScore:
                    alignment.push(alignment.gap, b, c - y)
                    self.backtraceFrom(first, second, f, i, j - 1,
                                       alignments, alignment)
                    alignment.pop()
                if c == x + self.gapScore:
                    alignment.push(a, alignment.gap, c - x)
                    self.backtraceFrom(first, second, f, i - 1, j,
                                       alignments, alignment)
                    alignment.pop()
