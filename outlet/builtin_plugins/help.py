import outlet
from outlet import errors

import discord

from inspect import signature, Parameter


class Plugin(outlet.Plugin):
    """
    Builtin help plugin, implementing $help command
    """

    __plugin__ = "Help"

    async def help_embed(self, guild):
        new_embed = discord.Embed(name="Commands",
                                  description="Do **$help <command>** for more information about a command.",
                                  color=await self.bot.my_color(guild))

        new_embed.set_author(name="Commands")

        for plugin in self.bot.plugins:
            commands = []
            for name, command in plugin.commands.items():
                commands.append(self.bot.prefix + name)

            command_list = "\n".join(commands)

            if commands:
                new_embed.add_field(name=plugin.__plugin__, value=command_list)

        return new_embed

    @outlet.command("help")
    async def help(self, ctx, *command):
        """Shows a list of commands, or help for a specific command."""

        if command:
            command = command[0]  # ignore any lingering stuff

            if command.startswith(self.bot.prefix) and command != self.bot.prefix:
                command = command[len(self.bot.prefix):]

            cmd = self.bot.all_commands.get(command)

            if cmd is None:
                raise errors.ArgumentError("`{}` isn't a command".format(command))

            await ctx.send("{}**{}** {}".format(self.bot.prefix, command, cmd.help_message))


        else:
            embed = await self.help_embed(ctx.guild)

            await ctx.send(embed=embed)
