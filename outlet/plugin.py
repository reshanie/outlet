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


from outlet import errors


class Plugin(object):
    """
    Plugin class. Create your own plugins by inheriting this class.

    :attr outlet.DiscordBot bot: Bot the plugin belongs to.

    Events
    ------

    To use the raw events, you can overwrite them like a regular discord client. For example ::
        class Plugin(outlet.Plugin):
            async def on_ready(self):
                print("I'm ready!")

    The Plugin class *must* be named Plugin for it to be used.

    Commands
    --------

    You can also create commands using the class's command decorator.
    Commands are passed a :class:`Context`, which has information about the message and helper functions.

    @self.command("ping")
    async def ping_pong(ctx):
        ctx.send("pong")
    """

    def __init__(self, bot):
        self.bot = bot
        self.log = self.bot.log

        self.commands = []

        self.get_commands()

    def get_commands(self):
        # inits commands
        for name in dir(self):  # get commands
            o = getattr(self, name)
            if getattr(o, "is_command", False):
                self.commands.append(o)

    def create_task(self, *args, **kwargs):
        """
        Shortcut to Plugin.bot.loop.create_task

        Call this on a coroutine to run it without blocking.

        :returns: asyncio.Task
        """

        self.bot.loop.create_task(*args, **kwargs)

    # bot level event handling

    async def __on_message__(self, message):
        self.create_task(self.on_message(message))

        # command handling
        if message.content.startswith(self.bot.prefix) and message.content != self.bot.prefix:
            self.log.info("command received")

            if message.author == self.user:  # ignore myself!
                return

            no_prefix = message.content[len(self.bot.prefix):]

            for command in self.commands:
                try:
                    await command(message, no_prefix)
                except errors.CommandError as e:
                    self.log.info("command raised exception {!s}".format(e))

                    await message.channel.send(e)

    # plugin level event handling

    async def on_ready(self):
        pass

    async def on_shard_ready(self, shard_id):
        pass

    async def on_typing(self, channel, user, when):
        pass

    async def on_message(self, message):
        pass

    async def on_message_delete(self, message):
        pass

    async def on_message_edit(self, before, after):
        pass

    async def on_reaction_add(self, reaction, user):
        pass

    async def on_reaction_remove(self, reaction, user):
        pass

    async def on_reaction_clear(self, message, reactions):
        pass

    async def on_private_channel_delete(self, channel):
        pass

    async def on_private_channel_create(self, channel):
        pass

    async def on_private_channel_update(self, before, after):
        pass

    async def on_guild_channel_create(self, channel):
        pass

    async def on_guild_channel_delete(self, channel):
        pass

    async def on_guild_channel_update(self, before, after):
        pass

    async def on_member_join(self, member):
        pass

    async def on_member_remove(self, member):
        pass

    async def on_member_update(self, before, after):
        pass

    async def on_guild_join(self, guild):
        pass

    async def on_guild_remove(self, guild):
        pass

    async def on_guild_update(self, before, after):
        pass
