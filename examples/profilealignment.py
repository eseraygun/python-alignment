from __future__ import print_function

from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner
from alignment.profile import Profile
from alignment.profilealigner import SoftScoring, GlobalProfileAligner


# Create sequences to be aligned.
a = Sequence('what a beautiful day'.split())
b = Sequence('what a disappointingly bad day'.split())
print('Sequence A:', a)
print('Sequence B:', b)
print('')

# Create a vocabulary and encode the sequences.
v = Vocabulary()
aEncoded = v.encodeSequence(a)
bEncoded = v.encodeSequence(b)
print('Encoded A:', aEncoded)
print('Encoded B:', bEncoded)
print('')

# Create a scoring and align the sequences using global aligner.
scoring = SimpleScoring(2, -1)
aligner = GlobalSequenceAligner(scoring, -2)
score, alignments = aligner.align(aEncoded, bEncoded, backtrace=True)

# Create sequence profiles out of alignments.
profiles = [Profile.fromSequenceAlignment(a) for a in alignments]
for encoded in profiles:
    profile = v.decodeProfile(encoded)
    print(profile)
print('')

# Create a soft scoring and align the first profile against sequence A.
scoring = SoftScoring(scoring)
aligner = GlobalProfileAligner(scoring, -2)
score, alignments = aligner.align(profiles[0], Profile.fromSequence(aEncoded),
                                  backtrace=True)
for encoded in alignments:
    alignment = v.decodeProfileAlignment(encoded)
    print(alignment)
