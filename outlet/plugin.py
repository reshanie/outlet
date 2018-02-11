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


from discord import TextChannel
from outlet import errors


class Plugin(object):
    """
    Plugin class. Create your own plugins by inheriting this class.

    Events
    ======

    To use the raw events, you can overwrite them like a regular discord client. For example ::

        class Plugin(outlet.Plugin):
            async def on_ready(self):
                print("I'm ready!")



    The Plugin class *must* be named Plugin for it to be used.

    Commands
    ========

    You can also create commands with the command decorator.
    Commands are passed a :class:`Context`, which has information about the message and helper functions.
    For example ::
        @outlet.command("ping")
        async def ping_pong(ctx):
            ctx.send("pong")


    """

    #: Name of plugin.
    __plugin__ = "default"

    def __init__(self, bot):
        #: Bot the plugin belongs to
        self.bot = bot

        # clone bot
        self.get_resource = self.bot.get_resource

        self.http = self.bot.http_session

        self.log = self.bot.log

        self.commands = {}
        self.event_listeners = {
            "on_message": []
        }
        self.bg_tasks = []

        self.running_bg_tasks = []

        self.collect_commands()
        self.collect_event_listeners()
        self.collect_bg_tasks()

    def collect_commands(self):
        # collects commands

        self.log.debug("getting commands")

        for name in dir(self):  # get commands
            o = getattr(self, name)
            if getattr(o, "is_command", False):
                for cmd in o.command:
                    self.commands[cmd] = o

        self.log.info("loaded {} commands".format(len(self.commands)))

    def collect_event_listeners(self):
        # collects event listeners

        self.log.debug("getting event listeners")

        for name in dir(self):
            o = getattr(self, name)
            if getattr(o, "is_event_listener", False):
                self.event_listeners[o.event].append(o)

        listeners = sum([len(e) for e in self.event_listeners.values()])

        self.log.info("loaded {} event listeners".format(listeners))

    def collect_bg_tasks(self):
        # collects background tasks

        self.log.debug("getting event listeners")

        for name in dir(self):
            o = getattr(self, name)
            if getattr(o, "is_bg_task", False):
                self.bg_tasks.append(o)

        self.log.info("loaded {} background tasks".format(len(self.bg_tasks)))

    def create_task(self, *args, **kwargs):
        """
        Shortcut to :meth:`Plugin.bot.loop.create_task`

        Call this on a coroutine to run it without blocking.

        :returns: asyncio.Task
        """

        return self.bot.loop.create_task(*args, **kwargs)

    async def start_bg_tasks(self):
        self.log.info("cancelling running background tasks")
        for bg_task in self.running_bg_tasks:  # first cancel the running tasks
            if not bg_task.done():
                bg_task.cancel()

        self.log.info("starting background tasks")
        for bg_task in self.bg_tasks:
            self.bg_tasks.append(
                self.create_task(bg_task(self.bot.loop))  # create the task, use the bot's event loop
            )

            self.log.debug("started {}".format(bg_task.__name__))

    # bot level event handling

    async def __on_message__(self, message):
        self.create_task(self.on_message(message))

        if isinstance(message.channel, TextChannel):
            for event_listener in self.event_listeners["on_message"]:
                if event_listener.channel is not None and message.channel.name != event_listener.channel:
                    continue

                self.create_task(event_listener(message))

        # command handling
        if message.content.startswith(self.bot.prefix) and message.content != self.bot.prefix:
            self.log.info("command received")

            if message.author == self.bot.user:  # ignore myself!
                return

            no_prefix = message.content[len(self.bot.prefix):]
            cmd = no_prefix.split(" ")[0]

            if cmd in self.commands:
                try:
                    await self.commands[cmd](message, no_prefix)
                except errors.CommandError as e:
                    self.log.info("command raised {}: {!s}".format(e.__class__.__name__, e))

                    await message.channel.send(e)

    async def __on_ready__(self):
        self.create_task(self.start_bg_tasks())

        self.create_task(self.on_ready())

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

    async def on_guild_role_create(self, role):
        pass

    async def on_guild_role_delete(self, role):
        pass

    async def on_guild_role_update(self, before, after):
        pass

    async def on_guild_emojis_update(self, guild, before, after):
        pass

    async def on_guild_available(self, guild):
        pass

    async def on_guild_unavailable(self, guild):
        pass

    async def on_member_ban(self, guild, user):
        pass

    async def on_member_unban(self, guild, user):
        pass
