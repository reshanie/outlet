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

import time
from functools import wraps
from inspect import Signature, Parameter

from outlet import errors, converters


class Context(object):
    """
    Command context, passed to command functions for easier handling

    :attr discord.Message message: Message
    :attr discord.Guild guild: Guild the message was sent in
    :attr discord.Channel channel: Channel the message was sent in
    :attr discord.Member: author: Author of the message
    """

    def __init__(self, message):
        self.message = message

        self.guild = message.guild
        self.channel = message.channel
        self.author = message.author

    async def send(self, *args, **kwargs):
        """
        Coroutine

        Sends a message in the context's channel. Pass the same arguments or keywords that you would to
        :meth:`discord.Channel.send`
        """

        await self.channel.send(*args, **kwargs)


def convert_arguments(args, signature, ctx):
    """
    This is used internally by the bot.

    Converts a list of arguments for a command against the command's signature using converters.

    :param list args: Arguments
    :param Signature signature:  Function signature
    :param Context ctx: Command context
    :return: list
    """

    if len(signature.parameters) == 2:  # command doesn't take any arguments
        return []

    params = list(signature.parameters.values())[2:]  # convert parameters to list, ignore self and ctx

    has_var_positional = params[-1].kind == Parameter.VAR_POSITIONAL  # has *arg

    min_args = len(params) - 1 if has_var_positional else len(params)  # *arg not required
    max_args = 999 if has_var_positional else len(params)

    if len(args) < min_args:
        raise errors.MissingArguments("{} argument(s) are required for this command".format(min_args))
    elif len(args) > max_args:
        raise errors.TooManyArguments("Only {} argument(s) are allowed for this command".format(max_args))

    converted_args = []

    for i in range(len(params)):
        if len(args) == 0:
            break

        while args[0] == "":  # ignore empty arguments caused by double spaces
            del args[0]

        converter = params[i].annotation

        if converter == Parameter.empty:  # use String by default
            converter = converters.String

        # if not issubclass(type(converter), converters.Converter):  # check that it's actually a converter
        #     raise TypeError("all converters should be a subclass of outlet.converters.Converter")

        new_value = converter.convert(args[0], ctx)
        converted_args.append(new_value)

        del args[0]

        if params[i].kind == Parameter.VAR_POSITIONAL:  # if *arg, convert the rest
            while len(args) > 0:
                new_value = converter.convert(args[0], ctx)
                converted_args.append(new_value)

                del args[0]

    return converted_args


def help_message(sig, doc):
    msg = ""

    params = list(sig.parameters.values())
    params = params[2:] if len(params) > 2 else []

    for arg in params:
        type_ = "String" if arg.annotation == Parameter.empty else arg.annotation.__name__

        msg += "{}<{}: {}> ".format("*" if arg.kind == Parameter.VAR_POSITIONAL else "", arg.name, type_)

    return "{}\n\n{}".format(msg, doc or "")


def command(*cmd):
    """
    Decorator used to create commands.

    :param *cmd: The name(s) of the command, used to call it. Don't include the bot prefix.
    """

    def real_decorator(func):
        signature = Signature.from_callable(func)  # function signature is used to convert arguments

        @wraps(func)
        async def real_command(self_, message, content):
            content = content.split(" ")  # the content parameter doesn't include the command prefix

            command_ = content[0]  # actual named command
            args = content[1:] if len(content) > 1 else []  # list of arguments passed

            if command_ not in cmd:  # doesn't match this command
                return

            ctx = Context(message)  # message context is passed to function

            args = convert_arguments(args, signature, ctx)  # convert the arguments according to function signature
            # this will also checked for incorrect number of arguments

            returned = await func(self_, ctx, *args)

            # automatically send return value to channel if its a string
            if isinstance(returned, str):
                await ctx.send(returned)

        real_command.is_command = True
        real_command.command = cmd
        real_command.help_message = help_message(signature, func.__doc__)

        return real_command

    return real_decorator


# helpers

def require_permissions(*permission):
    """
    Decorator that makes command require named permission(s)

    :param str permission: permission(s) to require
    """

    def real_decorator(func):
        if getattr(func, "is_command", False):
            # @outlet.command("h")
            # @require_permissions("h")
            # async def h_command(self, ctx):

            raise SyntaxError("@require_permissions() decorator should be placed under the @command decorator")

        @wraps(func)
        async def new_func(self_, ctx, *args):
            author_permissions = ctx.author.permissions_in(ctx.channel)  # use per channel permissions

            for perm in permission:  # check all permissions
                if not getattr(author_permissions, perm, False):
                    raise errors.MissingPermission("This command requires the `{}` permission".format(perm))

            return await func(self_, ctx, *args)

        return new_func

    return real_decorator


def owner_only(func):
    """
    Decorator that only allows the owner of the guild to use command.
    """

    if getattr(func, "is_command", False):
        raise SyntaxError("@owner_only decorator should be placed under the @command decorator")

    @wraps(func)
    async def new_func(self_, ctx, *args):
        if ctx.author != ctx.guild.owner:
            raise errors.MissingPermission("Only the owner of the guild can use this command")

        return await func(self_, ctx, *args)

    return new_func


def cooldown(seconds):
    """
    Adds a per-server cooldown to a command.

    :param int seconds: Length of cooldown in seconds.
    :return:
    """

    def real_decorator(func):
        if getattr(func, "is_command", False):
            # @outlet.command("h")
            # @require_permissions("h")
            # async def h_command(self, ctx):

            raise SyntaxError("@require_permissions() decorator should be placed under the @command decorator")

        guild_calls = {}

        @wraps(func)
        async def new_func(self_, ctx, *args):
            if time.time() - guild_calls.get(ctx.guild.id, 0) < seconds:
                raise errors.CommandError("This command has a {} second cooldown.".format(seconds))

            guild_calls[ctx.guild.id] = time.time()

            return await func(self_, ctx, *args)

        return new_func

    return real_decorator
