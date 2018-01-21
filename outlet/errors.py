class CommandError(Exception):
    pass


class MissingPermission(CommandError):
    pass


class ArgumentError(CommandError):
    pass


class MissingArguments(ArgumentError):
    pass


class TooManyArguments(ArgumentError):
    pass


class WrongType(ArgumentError):
    pass

