from alignment.sequence import *
from alignment.profile import *

# Vocabulary -------------------------------------------------------------------

class Vocabulary(object):

	def __init__(self):
		"""
		Ensures self.has(GAP_ELEMENT)
		    and self.encode(GAP_ELEMENT) == GAP_CODE
		    and len(self) == 1
		"""
		self.__elementToCode = {GAP_ELEMENT: GAP_CODE}
		self.__codeToElement = {GAP_CODE: GAP_ELEMENT}

	def has(self, element):
		"""
		Ensures result iff element is in the vocabulary
		"""
		return element in self.__elementToCode

	def hasCode(self, code):
		"""
		Ensures result iff there exists an element in the vocabulary such that self.encode(element) == code
		"""
		return code in self.__codeToElement

	def encode(self, element):
		"""
		Ensures self.decode(result) == element
		    and len(self) == old len(self) if old self.has(element)
		    and len(self) == old len(self) + 1 otherwise
		"""
		code = self.__elementToCode.get(element)
		if code is None:
			code = len(self.__elementToCode)
			self.__elementToCode[element] = code
			self.__codeToElement[code] = element
		return code

	def decode(self, code):
		"""
		Ensures self.encode(result) == code if self.hasCode(code)
		    and KeyError otherwise
		"""
		try:
			return self.__codeToElement[code]
		except KeyError:
			raise KeyError("there is not any elements in the vocabulary encoded as %r" % code)

	def encodeSequence(self, sequence):
		"""
		Ensures for each position i, result[i] == self.encode(sequence[i])
		"""
		encoded = EncodedSequence(len(sequence), id=sequence.id)
		for element in sequence:
			encoded.push(self.encode(element))
		return encoded

	def decodeSequence(self, sequence):
		"""
		Ensures for each position i, result[i] == self.decode(sequence[i])
		"""
		decoded = Sequence(id=sequence.id)
		for code in sequence:
			decoded.push(self.decode(code))
		return decoded

	def decodeSequenceAlignment(self, alignment):
		"""
		Ensures result.first == self.decodeSequence(alignment.first)
		    and result.second == self.decodeSequence(alignment.second)
		    and result.gap == self.decode(alignment.gap)
		"""
		first = self.decodeSequence(alignment.first)
		second = self.decodeSequence(alignment.second)
		return SequenceAlignment(first, second, self.decode(alignment.gap), alignment)

	def decodeSoft(self, softCode):
		"""
		Ensures for each code in softCode, result[v.decode(code)] == softCode[code]
		    and len(result) == len(softCode)
		"""
		weights = dict()
		for code, weight in softCode.pairs():
			weights[self.__codeToElement[code]] = weight
		return SoftElement(weights)

	def decodeProfile(self, profile):
		"""
		Ensures for each position i, result[i] == self.decodeSoft(sequence[i])
		"""
		decoded = Profile()
		for softCode in profile:
			decoded.push(self.decodeSoft(softCode))
		return decoded

	def decodeProfileAlignment(self, alignment):
		"""
		Ensures result.first == self.decodeProfile(alignment.first)
		    and result.second == self.decodeProfile(alignment.second)
		    and result.gap == self.decodeSoft(alignment.gap)
		"""
		first = self.decodeProfile(alignment.first)
		second = self.decodeProfile(alignment.second)
		return ProfileAlignment(first, second, self.decodeSoft(alignment.gap), alignment)

	def elements(self):
		return [self.decode(c) for c in sorted(self.__codeToElement)]

	def __len__(self):
		return len(self.__elementToCode)

	def __iter__(self):
		return iter(self.__elementToCode)

	def __repr__(self):
		return repr(self.elements())

# Cyclic imports.
from alignment.sequencealigner import SequenceAlignment
from alignment.profilealigner import ProfileAlignment
