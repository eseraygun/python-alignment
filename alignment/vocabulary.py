from .sequence import GAP_ELEMENT
from .sequence import GAP_CODE
from .sequence import Sequence
from .sequence import EncodedSequence
from .profile import SoftElement
from .profile import Profile


# Vocabulary ------------------------------------------------------------------

class Vocabulary(object):
    def __init__(self):
        self.__elementToCode = {GAP_ELEMENT: GAP_CODE}
        self.__codeToElement = {GAP_CODE: GAP_ELEMENT}

    def has(self, element):
        return element in self.__elementToCode

    def hasCode(self, code):
        return code in self.__codeToElement

    def encode(self, element):
        code = self.__elementToCode.get(element)
        if code is None:
            code = len(self.__elementToCode)
            self.__elementToCode[element] = code
            self.__codeToElement[code] = element
        return code

    def decode(self, code):
        try:
            return self.__codeToElement[code]
        except KeyError:
            raise KeyError(
                'there is no elements in the vocabulary encoded as %r'
                % code)

    def encodeSequence(self, sequence):
        encoded = EncodedSequence(len(sequence), id=sequence.id)
        for element in sequence:
            encoded.push(self.encode(element))
        return encoded

    def decodeSequence(self, sequence):
        decoded = Sequence(id=sequence.id)
        for code in sequence:
            decoded.push(self.decode(code))
        return decoded

    def decodeSequenceAlignment(self, alignment):
        first = self.decodeSequence(alignment.first)
        second = self.decodeSequence(alignment.second)
        return SequenceAlignment(first, second, self.decode(alignment.gap),
                                 alignment)

    def decodeSoft(self, softCode):
        weights = dict()
        for code, weight in softCode.pairs():
            weights[self.__codeToElement[code]] = weight
        return SoftElement(weights)

    def decodeProfile(self, profile):
        decoded = Profile()
        for softCode in profile:
            decoded.push(self.decodeSoft(softCode))
        return decoded

    def decodeProfileAlignment(self, alignment):
        first = self.decodeProfile(alignment.first)
        second = self.decodeProfile(alignment.second)
        return ProfileAlignment(first, second,
                                self.decodeSoft(alignment.gap),
                                alignment)

    def elements(self):
        return [self.decode(c) for c in sorted(self.__codeToElement)]

    def __len__(self):
        return len(self.__elementToCode)

    def __iter__(self):
        return iter(self.__elementToCode)

    def __repr__(self):
        return repr(self.elements())


# Cyclic imports.
from .sequencealigner import SequenceAlignment
from .profilealigner import ProfileAlignment
