class VariableNotFoundException(Exception):
    """
    Environment variable not found.
    """
    variable_name: str

    def __init__(self, variable_name: str):
        self.variable_name = variable_name
        super().__init__(f'Environment variable {variable_name} not found')


class CommandUnauthorizedException(Exception):
    """
    Thrown when user is not authorized to perform a command.
    """
    pass


class OptionNotFoundException(Exception):
    """
    Thrown when the selected option was not present in the Discord interaction.
    """
    pass
