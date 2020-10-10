class FawkesConfig:
    """ The configuation file for running Fawkes.

        Attributes:
            apps: A list of file paths to AppConfigs for respective apps onboarded to Fawkes.
    """

    def __init__(self, config):
        self.apps = config["apps"]

