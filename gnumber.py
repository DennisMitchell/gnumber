class Gnumber:
	_denominator = 10 ** 500
	_denominator_log = 500

	@classmethod
	def _from_int(cls, integer):
		retval = cls()
		retval._real = integer * cls._denominator
		return retval

	@classmethod
	def _part_to_str(cls, part, decimal_digits = 8):
		scale = -cls._denominator_log
		retval = '-'[: part < 0]
		numerator = str(abs(part))
		retval += (numerator[:scale] or '0') + '.' + numerator[scale : scale + decimal_digits or None].rjust(-scale, '0')
		retval = retval.rstrip('0').rstrip('.')
		return retval

	@classmethod
	def _part_to_repr(cls, part):
		return cls._part_to_str(part, decimal_digits = cls._denominator_log)

	@classmethod
	def _str_to_part(cls, part):
		scale = cls._denominator_log
		decimal_parts = iter(part.split('.'))
		return int(next(decimal_parts, '0') + next(decimal_parts, '0')[:scale].ljust(scale, '0'))

	def __add__(self, value):
		retval = self.__class__()
		retval._real = self._real + value._real
		retval._imag = self._imag + value._imag
		return retval

	def __bool__(self):
		return self._real != 0 or self._imag != 0

	def __eq__(self, value):
		return self._from_int(self._real == value._real and self._imag == value._imag)

	def __getitem__(self, index):
		return self

	def __init__(self, *values):
		coordinates = iter(values)
		self._real = self._str_to_part(next(coordinates, '0'))
		self._imag = self._str_to_part(next(coordinates, '0'))

	def __iter__(self):
		yield self

	def __len__(self):
		return 1

	def __mul__(self, value):
		retval = self._mul_noscale(value)._roundiv(self.__class__._denominator)
		return retval

	def __ne__(self, value):
		return self._from_int(self._real != value._real or self._imag != value._imag)

	def __neg__(self):
		retval = self.__class__()
		retval._real = -self._real
		retval._imag = -self._imag
		return retval

	def __repr__(self):
		class_name = self.__class__.__name__
		part_to_repr = self.__class__._part_to_repr
		if self._imag == 0:
			return "%s('%s')" % (class_name, part_to_repr(self._real))
		return "%s('%s', '%s')" % (class_name, part_to_repr(self._real), part_to_repr(self._imag))

	def __rtruediv__(self, value):
		return value / self

	def __setitem__(self, index, value):
		self._real = value._real
		self._imag = value._imag

	def __str__(self):
		part_to_str = self.__class__._part_to_str
		if self._imag == 0:
			return part_to_str(self._real)
		return '(%s, %s)' % (part_to_str(self._real), part_to_str(self._imag))

	def __sub__(self, value):
		retval = self.__class__()
		retval._real = self._real - value._real
		retval._imag = self._imag - value._imag
		return retval

	def __truediv__(self, value):
		conjugate = value.conjugate()
		denominator = self.__class__._denominator
		retval = self._mul_noscale(conjugate)._roundiv((value * conjugate)._real)
		return retval

	def _roundiv(self, value):
		retval = self.__class__()
		double_quotient = (self._real << 1) // value
		retval._real = (double_quotient >> 1) | (double_quotient & 1)
		double_quotient = (self._imag << 1) // value
		retval._imag = (double_quotient >> 1) | (double_quotient & 1)
		return retval

	def _mul_noscale(self, value):
		retval = self.__class__()
		retval._real = self._real * value._real - self._imag * value._imag
		retval._imag = self._real * value._imag + self._imag * value._real
		return retval

	def conjugate(self):
		retval = self.__class__()
		retval._real = self._real
		retval._imag = -self._imag
		return retval

	def exp(self):
		denominator = self.__class__._denominator
		term = self.__class__()
		result = self.__class__()
		scale = 10 ** (3 * ((abs(self._real) + abs(self._imag)) // denominator) + 3 >> 1)
		term._real = denominator * scale
		index = denominator
		while term:
			result += term
			term = term._mul_noscale(self)._roundiv(index)
			index += denominator
		return result._roundiv(scale)