# Copyright (c) 2018 James Patrick Dill
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re

from outlet import errors

mention = re.compile(r"<@!?([0-9]+)>")
username = re.compile("(.+#[0-9]{4})")


class Converter(object):
    """
    A converter converts a raw argument to a command to a usable value.

    Custom converters should inherit outlet.BaseConverter, and must have a convert(value, ctx) classmethod.
    If the value can't be converted, it should raise outlet.errors.WrongType
    """

    @classmethod
    def convert(cls, value, ctx):
        return


# basic converters


class String(Converter):
    """String converter. Just returns the raw value."""

    @classmethod
    def convert(cls, value, ctx):
        return value


class Number(Converter):
    """Number converter. Will return int or float"""

    @classmethod
    def convert(cls, value, ctx):
        try:
            return float(value) if "." in value else int(value)
        except ValueError:
            raise errors.WrongType("`{}` isn't a number.".format(value))


class Member(Converter):
    """
    Member converter. Converts a mention to :class:`discord.Member` . The mention must be for a member of the guild.

    This converter works with @mentions or username#1234
    """

    @classmethod
    def convert(cls, value, ctx):
        user_id = mention.match(value)
        user_tag = username.match(value)

        if not (user_tag or user_id):
            raise errors.WrongType("`{}` isn't a username or mention.".format(value))

        if user_id:
            user_id = int(user_id.group(1))
            member = ctx.guild.get_member(user_id)

            if member is None:
                raise errors.WrongType("{} isn't a member of this server".format(value))

            return member
        else:
            member = ctx.guild.get_member_named(value)
            if member is None:
                raise errors.WrongType("{} isn't a member of this server".format(value))

            return member
