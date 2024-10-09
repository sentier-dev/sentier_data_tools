# MIT License

# Copyright (c) 2024 Sebastian Kucharzyk

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from enum import Enum
from typing import Any

import peewee


class EnumField(peewee.CharField):
    """
    An EnumField for Peewee to store Python Enum types.

    This field stores the name of an Enum member as a string in the database.
    It automatically handles conversion to and from the Enum type when reading
    or writing to the database.

    Attributes:
        enum (Type[Enum]): The Enum class that this field will store.

    Usage Example:

        class Color(Enum):
            RED = 1
            GREEN = 2
            BLUE = 3

        class MyModel(peewee.Model):
            color = EnumField(Color)

        instance = MyModel.create(color=Color.RED)
        assert instance.color == Color.RED
    """

    def __init__(self, enum: type[Enum], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not issubclass(enum, Enum):
            raise TypeError("enum must be a subclass of Enum")
        self.enum = enum

    def db_value(self, member: Enum) -> Any:
        if member is None:
            return None
        if not isinstance(member, self.enum):
            raise TypeError(
                f"Expected a member of {self.enum.__name__}, got {type(member).__name__}"
            )
        return super().db_value(member.name)

    def python_value(self, value: Any) -> Any:
        if value is None and self.null:
            return None
        try:
            return self.enum[value]
        except KeyError as err:
            raise peewee.IntegrityError(
                f"Value '{value}' is not a valid member name of '{self.enum.__name__}'"
            ) from err

    def __set__(self, instance: peewee.Model, value: Any):
        if value is not None and not isinstance(value, self.enum):
            raise TypeError(
                f"Expected a member of {self.enum.__name__} or None, got {type(value).__name__}"
            )
        super().__set__(instance, value)
