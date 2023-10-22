import copy


""" ------------------------------------------------------------------------------------
maths
"""


def _matrix_eliminate(r1, r2, col, target=0):
    """
    Part of Gauss-Jordan elimination algorithm for matrix inversion.

    https://stackoverflow.com/a/61741074/13806195
    """
    fac = (r2[col] - target) / r1[col]
    for i in range(len(r2)):
        r2[i] -= fac * r1[i]


def _matrix_gauss(a):
    """
    Part of Gauss-Jordan elimination algorithm for matrix inversion.

    https://stackoverflow.com/a/61741074/13806195
    """
    for i in range(len(a)):
        if a[i][i] == 0:
            for j in range(i + 1, len(a)):
                if a[i][j] != 0:
                    a[i], a[j] = a[j], a[i]
                    break
            else:
                raise ValueError("Matrix is not invertible")
        for j in range(i + 1, len(a)):
            _matrix_eliminate(a[i], a[j], i)
    for i in range(len(a) - 1, -1, -1):
        for j in range(i - 1, -1, -1):
            _matrix_eliminate(a[i], a[j], i)
    for i in range(len(a)):
        _matrix_eliminate(a[i], a[i], i, target=1)
    return a


class BaseMatrix(object):
    """
    "Square matrix" of arbitrary size.

    Square means same number of rows and columns.

    Intended to be subclassed.
    """

    size = 0
    """
    MUST be overriden in subclasses
    """

    def __init__(self, *args):
        assert self.size != 0
        if not self.size * self.size == len(args):
            raise ValueError(
                "Not enough argument provided: expected {} got {}"
                "".format(self.size * self.size, len(args))
            )
        self._array = [
            list(args[self.size * i : self.size * (i + 1)]) for i in range(self.size)
        ]  # type: list[list[float]]

    def __repr__(self):
        flatten = sum(self._array, [])
        return "{}({})".format(self.__class__.__name__, ",".join(map(str, flatten)))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._array == other._array
        return False

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            return self.from_2dsequence(
                [
                    [sum(a * b for a, b in zip(r, c)) for c in zip(*other.as_2Dlist())]
                    for r in self.as_2Dlist()
                ]
            )
        raise TypeError(
            "Cannot multiple {} by {}".format(self.__class__, other.__class__)
        )

    def as_2Dlist(self):
        # type: () -> list[list[float]]
        return copy.deepcopy(self._array)

    def as_2Dtuple(self):
        # type: () -> tuple[tuple[float, ...], ...]
        return tuple([tuple(row) for row in self._array])

    def determinant(self):
        """
        Returns the determinant of this matrix.
        """
        determinant = 1
        m = self.as_2Dlist()

        for i in range(self.size):
            for j in range(i + 1, self.size):
                if m[i][i] == 0:
                    m[i][i] = 1
                x = m[j][i] / m[i][i]
                for k in range(self.size):
                    m[j][k] -= x * m[i][k]

        for i in range(self.size):
            determinant *= m[i][i]

        return determinant

    def invert(self):
        """
        Invert this matrix on place.
        """
        self._array = self.inverted()._array

    def inverted(self):
        """
        Return the inverse of this matrix.

        Use Gauss-Jordan elimination algorithm.

        SRC: https://stackoverflow.com/a/61741074/13806195
        """
        buffer_m = [[] for _ in self._array]
        for i, row in enumerate(self._array):
            buffer_m[i].extend(row + [0] * i + [1] + [0] * (self.size - i - 1))

        _matrix_gauss(buffer_m)
        buffer_m = [buffer_m[i][len(buffer_m[i]) // 2 :] for i in range(len(buffer_m))]
        return self.from_2dsequence(buffer_m)

    def set_diagonal(self, vector):
        """
        Set the diagonal row of the given matrix with given vector
        """
        self._array = self.with_diagonal(vector)._array

    def transpose(self):
        """
        Return a new transposed matrix by swapping rows and cols
        """
        self._array = self.transposed()._array

    def transposed(self):
        """
        Return a new transposed matrix by swapping rows and cols
        """
        return self.from_2dsequence([list(r) for r in zip(*self.as_2Dlist())])

    def with_diagonal(self, vector):
        """
        Set the diagonal row of the given matrix with given vector

        Args:
            vector(BaseVector): vector instance.
        """
        if not vector.size == self.size:
            raise TypeError(
                "Matrix.size:{} != Vector.size:{}".format(self.size, vector.size)
            )

        new_array = self.as_2Dlist()
        for size_index in range(len(new_array)):
            new_array[size_index][size_index] = vector[size_index]

        return self.from_2dsequence(new_array)

    @classmethod
    def from_2dsequence(cls, source):
        """
        Args:
            source(list[list[float]] or tuple):
                a one-level-nested list or tuple of floats.
                must correspond to the expected size of the matrix

        Returns:
            new instance
        """
        flatten = sum(source, [] if isinstance(source, list) else tuple())
        return cls(*flatten)

    @classmethod
    def init_with_zeros(cls):
        """
        Create a matrix instance full of zeros.
        """
        return cls(*([0.0] * (cls.size * cls.size)))

    @classmethod
    def init_as_identity(cls):
        """
        Create an indentity matrix instance.
        """
        instance = cls.init_with_zeros()
        vector_class = BaseVector.get_class_for_size(cls.size)
        if not vector_class:
            raise RuntimeError("No Vector class found for size={}".format(cls.size))

        instance.set_diagonal(vector_class(*([1.0] * cls.size)))
        return instance


class Matrix2x2(BaseMatrix):
    size = 2


class Matrix3x3(BaseMatrix):
    size = 3


class Matrix4x4(BaseMatrix):
    size = 4


class BaseVector(object):
    """
    Define an axis in arbitrary multidimensional space.

    Intended to be subclassed.
    """

    size = 0
    """
    MUST be overriden in subclasses
    """

    def __init__(self, *args):
        assert self.size != 0
        if not self.size == len(args):
            raise ValueError(
                "Not enough argument provided: expected {} got {}"
                "".format(self.size, len(args))
            )
        self._array = list(args)  # type: list[float]

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ",".join(map(str, self._array)))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._array == other._array
        return False

    def __getitem__(self, key):
        """
        Returns the element at key in the vector.
        """
        return self._array[key]

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            other_array = other.as_2Dlist()
            this_array = self.as_2Dlist()
            new_array = [this_array[i] * other_array[i] for i in range(self.size)]
            return self.__class__(*new_array)

        # vector/matrix dot product
        elif isinstance(other, BaseMatrix):
            new_array = [
                sum(x * y for x, y in zip(r, self.as_2Dlist()))
                for r in other.as_2Dlist()
            ]
            return self.__class__(*new_array)

        raise TypeError(
            "Cannot multiple {} by {}".format(self.__class__, other.__class__)
        )

    def as_2Dlist(self):
        # type: () -> list[float]
        return copy.copy(self._array)

    def as_2Dtuple(self):
        # type: () -> tuple[float, ...]
        return tuple(self._array)

    @classmethod
    def get_class_for_size(cls, size):
        # type: (int) -> BaseVector | None
        """
        Return the Vector class that correspond to the given size.

        Example a size of 3 should return a Vector3 class.
        """
        for subclass in cls.__subclasses__():
            if subclass.size == size:
                return subclass
        return None


class Vector2(BaseVector):
    size = 2


class Vector3(BaseVector):
    size = 3


class Vector4(BaseVector):
    size = 4


""" ------------------------------------------------------------------------------------
color-science
"""

ChromaticitiesType = tuple[
    tuple[float, float],
    tuple[float, float],
    tuple[float, float],
]
WhitepointType = tuple[float, float]


class Gamut(object):
    """
    Simple dataclass to group a gamut and its whitepoint.

    Args:
        chromaticities: primaries in CIE xy coordinates as [[red.x, red.y], [green...], [blue...]]
        whitepoint: reference white in CIE xy coordiates as [x, y]
    """

    def __init__(self, chromaticities, whitepoint):
        # type: (ChromaticitiesType, WhitepointType) -> None
        self._chromaticities = chromaticities
        self._whitepoint = whitepoint

    @property
    def chromaticities(self) -> ChromaticitiesType:
        return self._chromaticities

    @property
    def whitepoint(self) -> WhitepointType:
        return self._whitepoint

    def are_chromaticities_identity(self):
        """
        Returns:
            True if the chromaticities correspond cover the whole CIE xy space.
        """
        return self._chromaticities == [[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]]


def compute_normalized_primary_matrix(chromaticities, whitepoint):
    # type: (ChromaticitiesType, WhitepointType) -> Matrix3x3
    """
    Calculate the normalized primaries matrix for the specified chromaticities and whitepoint.

    Derived from:
        SMPTE Recommended Practice - Derivation of Basic Television Color Equations
        https://ieeexplore.ieee.org/document/7291155
    """
    # tuple[tuple] to list[list]
    chs = [list(row) for row in chromaticities]

    # compute z coordinates
    # 3x2 -> 3x3 matrix conversion
    for c in chs:
        c.append(1.0 - c[0] - c[1])
    chs = Matrix3x3.from_2dsequence(chs)
    Wz = 1 - whitepoint[0] - whitepoint[1]

    P = chs.transposed()
    W = Vector3(*[whitepoint[0] / whitepoint[1], 1.0, Wz / whitepoint[1]])
    C = W * P.inverted()
    Cm = Matrix3x3.init_with_zeros().with_diagonal(C)
    return P * Cm


def get_conversion_matrix(gamut_src, gamut_dst):
    # type: (Gamut, Gamut) -> Matrix3x3
    """
    Get the 3x3 matrix to convert the given source gamut to given destination gamut.

    note that NO chromatic adaption is performed.
    """

    src_to_xyz = Matrix3x3.init_as_identity()
    if not gamut_src.are_chromaticities_identity():
        src_to_xyz = compute_normalized_primary_matrix(
            gamut_src.chromaticities, gamut_src.whitepoint
        )

    dst_to_xyz = Matrix3x3.init_as_identity()
    if not gamut_dst.are_chromaticities_identity():
        dst_to_xyz = compute_normalized_primary_matrix(
            gamut_dst.chromaticities, gamut_dst.whitepoint
        )

    return dst_to_xyz.inverted() * src_to_xyz
