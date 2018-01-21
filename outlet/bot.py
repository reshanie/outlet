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

import glob
import logging
import os

import discord

import sys

from outlet import util

log = logging.getLogger("outlet")


class DiscordBot(discord.Client):
    """
    Bot class. All of the code for your bot is written in plugins, this class simply collects all the plugins and
    funnels the events into them.

    :param str token: Bot token used to connect to Discord
    :param str plugin_dir: Directory where plugin files are stored.
    :keyword str prefix: Bot prefix. Defaults to "!"
    :keyword logger: Logger to be used by bot. If none is given, Outlet's logger is used.
    """

    def __init__(self, token, plugin_dir, prefix="!", logger=log):
        super().__init__()

        self.token = token
        self.plugin_dir = plugin_dir

        self.prefix = prefix

        self.log = logger

        self.plugins = self.get_plugins(plugin_dir)

    def run(self):
        self.log.info("starting bot")

        super().run(self.token)

    def get_plugins(self, plugin_dir):
        # import all plugins from directory

        plugins = []

        files = glob.glob(os.path.join(plugin_dir, "*.py"))
        for file in files:
            try:
                self.log.info("importing {}".format(file))

                plugins.append(
                    util.import_file(file).Plugin(self)  # import file and get plugin
                )

            except ImportError as e:
                self.log.error("failed to load {}\n\n{}".format(file, e))

        return plugins

    # # log errors
    #
    # async def on_error(self, event_method, *args, **kwargs):
    #     exc = sys.exc_info()[1]
    #
    #     self.log.error("exception while handling {} event: {!s}".format(event_method, exc))

    # event funneling

    async def on_ready(self):
        self.log.debug("bot ready")

        for plugin in self.plugins:
            await plugin.on_ready()

    async def on_shard_ready(self, shard_id):
        self.log.debug("shard {} ready".format(shard_id))

        for plugin in self.plugins:
            await plugin.on_shard_ready()

    async def on_typing(self, channel, user, when):
        for plugin in self.plugins:
            await plugin.on_typing(channel, user, when)

    async def on_message(self, message):
        for plugin in self.plugins:
            await plugin.__on_message__(message)

    async def on_message_delete(self, message):
        for plugin in self.plugins:
            await plugin.on_message_delete(message)

    async def on_message_edit(self, before, after):
        for plugin in self.plugins:
            await plugin.on_message_edit(before, after)

    async def on_reaction_add(self, reaction, user):
        for plugin in self.plugins:
            await plugin.on_reaction_add(reaction, user)

    async def on_reaction_remove(self, reaction, user):
        for plugin in self.plugins:
            await plugin.on_reaction_remove(reaction, user)

    async def on_reaction_clear(self, message, reactions):
        for plugin in self.plugins:
            await plugin.on_reaction_clear(message, reactions)

    async def on_private_channel_delete(self, channel):
        for plugin in self.plugins:
            await plugin.on_private_channel_delete(channel)

    async def on_private_channel_create(self, channel):
        for plugin in self.plugins:
            await plugin.on_private_channel_create(channel)

    async def on_private_channel_update(self, before, after):
        for plugin in self.plugins:
            await plugin.on_private_channel_update(before, after)

    async def on_guild_channel_create(self, channel):
        for plugin in self.plugins:
            await plugin.on_guild_channel_create(channel)

    async def on_guild_channel_delete(self, channel):
        for plugin in self.plugins:
            await plugin.on_guild_channel_delete(channel)

    async def on_guild_channel_update(self, before, after):
        for plugin in self.plugins:
            await plugin.on_guild_channel_update(before, after)

    async def on_member_join(self, member):
        for plugin in self.plugins:
            await plugin.on_member_join(member)

    async def on_member_remove(self, member):
        for plugin in self.plugins:
            await plugin.on_member_remove(member)

    async def on_member_update(self, before, after):
        for plugin in self.plugins:
            await plugin.on_member_update(before, after)

    async def on_guild_join(self, guild):
        for plugin in self.plugins:
            await plugin.on_guild_join(guild)

    async def on_guild_remove(self, guild):
        for plugin in self.plugins:
            await plugin.on_guild_remove(guild)

    async def on_guild_update(self, before, after):
        for plugin in self.plugins:
            await plugin.on_guild_update(before, after)

    async def on_guild_role_create(self, role):
        for plugin in self.plugins:
            await plugin.on_guild_role_create(role)

    async def on_guild_role_delete(self, role):
        for plugin in self.plugins:
            await plugin.on_guild_role_delete(role)

    async def on_guild_role_update(self, before, after):
        for plugin in self.plugins:
            await plugin.on_guild_role_update(before, after)

    async def on_guild_emojis_update(self, guild, before, after):
        for plugin in self.plugins:
            await plugin.on_guild_emojis_update(guild, before, after)

    async def on_guild_available(self, guild):
        for plugin in self.plugins:
            await plugin.on_guild_available(guild)

    async def on_guild_unavailable(self, guild):
        for plugin in self.plugins:
            await plugin.on_guild_unavailable(guild)

    async def on_member_ban(self, guild, user):
        for plugin in self.plugins:
            await plugin.on_member_ban(guild, user)

    async def on_member_unban(self, guild, user):
        for plugin in self.plugins:
            await plugin.on_member_unban(guild, user)
