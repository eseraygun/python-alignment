from six import iteritems

from abc import ABCMeta

from .sequence import GAP_CODE
from .profile import SoftElement
from .profile import Profile
from .sequencealigner import Scoring
from .sequencealigner import SequenceAlignment
from .sequencealigner import SequenceAligner
from .sequencealigner import GlobalSequenceAligner
from .sequencealigner import StrictGlobalSequenceAligner
from .sequencealigner import LocalSequenceAligner


# Scoring ---------------------------------------------------------------------

class SoftScoring(Scoring):

    def __init__(self, scoring):
        self.scoring = scoring

    def __call__(self, firstElement, secondElement):
        score = 0.0
        for a, p in iteritems(firstElement.probabilities()):
            for b, q in iteritems(secondElement.probabilities()):
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

# noinspection PyAbstractClass
class ProfileAligner(SequenceAligner):
    __metaclass__ = ABCMeta

    def emptyAlignment(self, first, second):
        return ProfileAlignment(Profile(), Profile())


class GlobalProfileAligner(ProfileAligner, GlobalSequenceAligner):
    pass


class StrictGlobalProfileAligner(ProfileAligner, StrictGlobalSequenceAligner):
    pass


class LocalProfileAligner(ProfileAligner, LocalSequenceAligner):
    pass
