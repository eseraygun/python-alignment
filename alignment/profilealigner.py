from alignment.profile import *
from alignment.sequencealigner import *


# Scoring ---------------------------------------------------------------------

class SoftScoring(Scoring):

    def __init__(self, scoring):
        self.scoring = scoring

    def __call__(self, firstElement, secondElement):
        score = 0.0
        for a, p in firstElement.probabilities().iteritems():
            for b, q in secondElement.probabilities().iteritems():
                score += p * q * self.scoring(a, b)
        return score


# Alignment -------------------------------------------------------------------

class ProfileAlignment(SequenceAlignment):

    def __init__(self, first, second, gap=GAP_CODE, other=None):
        if isinstance(gap, SoftElement):
            softGap = gap
        else:
            softGap = SoftElement({gap: 1})
        super(ProfileAlignment, self).__init__(first, second, softGap, other)


# Aligner ---------------------------------------------------------------------

class ProfileAligner(SequenceAligner):

    def emptyAlignment(self, first, second):
        return ProfileAlignment(Profile(), Profile())


class GlobalProfileAligner(ProfileAligner, GlobalSequenceAligner):
    pass


class StrictGlobalProfileAligner(ProfileAligner, StrictGlobalSequenceAligner):
    pass


class LocalProfileAligner(ProfileAligner, LocalSequenceAligner):
    pass
