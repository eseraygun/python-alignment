from __future__ import print_function
from six import text_type

try:
    import numpypy as numpy
except ImportError:
    import numpy


GAP_ELEMENT = '-'
GAP_CODE = 0


# Sequence --------------------------------------------------------------------

class BaseSequence(object):

    def __init__(self, elements, id=None):
        self.elements = elements
        self.id = id

    def key(self):
        return tuple(self.elements)

    def reversed(self):
        return type(self)(self.elements[::-1], id=self.id)

    def __eq__(self, other):
        if self.id is None or other.id is None:
            return self.elements == other.elements
        else:
            return self.id == other.id

    def __hash__(self):
        if self.id is None:
            return hash(self.key())
        else:
            return hash(self.id)

    def __len__(self):
        return len(self.elements)

    def __getitem__(self, item):
        return self.elements[item]

    def __setitem__(self, key, value):
        self.elements[key] = value

    def __iter__(self):
        return iter(self.elements)

    def __repr__(self):
        return repr(self.elements)

    def __str__(self):
        if self.id is None:
            result = ''
        else:
            result = '> %s\n' % self.id
        result += ' '.join(str(e) for e in self.elements)
        return result

    def __unicode__(self):
        if self.id is None:
            result = u''
        else:
            result = u'> %s\n' % self.id
        result += u' '.join(text_type(e) for e in self.elements)
        return result


class Sequence(BaseSequence):

    def __init__(self, elements=None, id=None):
        if elements is None:
            super(Sequence, self).__init__(list(), id)
        else:
            super(Sequence, self).__init__(list(elements), id)

    def push(self, element):
        self.elements.append(element)

    def pop(self):
        return self.elements.pop()


class EncodedSequence(BaseSequence):

    def __init__(self, argument, id=None):
        if isinstance(argument, int):
            super(EncodedSequence, self).__init__(
                numpy.zeros(argument, int), id)
            self.position = 0
        else:
            if isinstance(argument, numpy.ndarray) \
                    and argument.dtype.name.startswith('int'):
                super(EncodedSequence, self).__init__(
                    numpy.array(argument), id)
            else:
                super(EncodedSequence, self).__init__(
                    numpy.array(list(argument), int), id)
            self.position = len(self.elements)

    def push(self, element):
        self.elements[self.position] = element
        self.position += 1

    def pop(self):
        self.position -= 1
        return int(self.elements[self.position])

    def key(self):
        return tuple(int(e) for e in self.elements[:self.position])

    def reversed(self):
        return EncodedSequence(
            self.elements[self.position - len(self.elements) - 1::-1],
            id=self.id,
        )

    def __len__(self):
        return self.position

    def __iter__(self):
        return (int(e) for e in self.elements)


# Tests -----------------------------------------------------------------------

if __name__ == '__main__':
    s1 = Sequence('what a beautiful day'.split())
    s2 = Sequence('what a disappointingly bad day'.split())
    print('s1', s1)
    print('s2', s2)
    print('')

    from alignment.vocabulary import Vocabulary
    v = Vocabulary()
    e1 = v.encodeSequence(s1)
    e2 = v.encodeSequence(s2)
    print('v', v)
    print('e1', e1)
    print('e2', e2)
    print('')

    from alignment.sequencealigner import SimpleScoring
    from alignment.sequencealigner import GlobalSequenceAligner
    s = SimpleScoring(2, -1)
    a = GlobalSequenceAligner(s, -2)
    score, alignments = a.align(e1, e2, backtrace=True)
    for alignment in alignments:
        as1 = v.decodeSequence(alignment.first)
        as2 = v.decodeSequence(alignment.second)
        print(alignment.percentIdentity())
        print(as1)
        print(as2)
        print('')
