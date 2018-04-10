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

import asyncio
import importlib.util
import os
from math import ceil as _ceil

import discord

ceil = lambda x: int(_ceil(x))


def import_file(path):
    try:
        spec = importlib.util.spec_from_file_location(os.path.basename(path), path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module
    except Exception as e:
        raise ImportError(e)


async def wait_then(s, coroutine):
    """
    Waits for s seconds before executing coroutine.

    :param str s: Seconds to wait
    :param asyncio.Coroutine coroutine: Coroutine
    :return: Return value of coroutine
    """
    await asyncio.sleep(s)

    return await coroutine


class PagedEmbed(object):
    """
    Utility class used to create paged embeds, which use reactions to go to other pages.

    :param discord.Embed embed: Embed to page. You should create your embed beforehand, this class
                                will simply paginate it.
    :param discord.Client client: Discord client to use when sending the paged embed.
    :param int per_page: (Keyword) Number of fields to show per page. Must be <= 25
    """

    __slots__ = ["_client", "_embed", "per_page", "author", "title", "description", "fields", "footer",
                 "pages", "current_page"]

    def __init__(self, client, embed, *, per_page=10):
        if not 1 <= per_page <= 25:
            raise ValueError("fields per page must be in range [1, 25]")

        self._client = client
        self._embed = embed

        self.per_page = per_page

        self.author = embed.author

        self.title = embed.title
        self.description = embed.description

        self.fields = embed.fields

        self.footer = embed.footer

        self.pages = self.make_pages()

        self.current_page = 0

    def make_pages(self):
        if len(self.fields) < self.per_page:
            return [self._embed]
        else:
            n_pages = ceil(len(self.fields) / self.per_page)

            embeds = []
            for page in range(n_pages):
                this_page = self.fields[:self.per_page]

                page_embed = discord.Embed(title=self.title, description=self.description)

                if self.author.name is not discord.Embed.Empty:
                    page_embed.set_author(**self.author)

                footer_text = self.footer.text + " | " if self.footer.text is not discord.Embed.Empty else ""
                page_embed.set_footer(text=footer_text + "Page {}/{}".format(page + 1, n_pages),
                                      icon_url=self.footer.icon_url)

                for field in this_page:
                    page_embed.add_field(name=field.name, value=field.value, inline=False)

                embeds.append(page_embed)

                del self.fields[:self.per_page]

            return embeds

    async def next_page(self, message):
        if self.current_page < len(self.pages):
            self.current_page += 1
            await message.edit(embed=self.pages[self.current_page])

    async def previous_page(self, message):
        if self.current_page > 0:
            self.current_page -= 1
            await message.edit(embed=self.pages[self.current_page])

    reactions = {
        "⬅": previous_page,
        "➡": next_page,
    }

    async def run(self, channel, user_for, *, timeout=120):
        """
        Runs the paged embed in specified channel.

        :param channel: Channel to run the embed in.
        :param user_for: Which user can use the page buttons.
        :param timeout: (Keyword) If no reaction is added in timeout seconds, the embed will stop responding."""

        def check(reaction_, user_):
            if user_ == self._client.user:  # bot added reaction
                return False

            if str(reaction_.emoji) not in self.reactions:  # check if reaction has any function
                return False

            return True

        message = await channel.send(embed=self.pages[self.current_page])

        for emoji in self.reactions:
            await message.add_reaction(emoji)

        while True:
            try:
                reaction, user = await self._client.wait_for("reaction_add", check=check, timeout=timeout)

                if user == user_for:
                    await self.reactions[str(reaction.emoji)](self, message)

                await message.remove_reaction(reaction, user)

            except asyncio.TimeoutError:
                await message.clear_reactions()
                break
