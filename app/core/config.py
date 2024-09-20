from dotenv import load_dotenv, dotenv_values


class AppConfig:
    """
    A class to encapsulate application configuration.
    """

    def __init__(self, env_file='./.env'):
        """
        Initializes the AppConfig with default values for configuration settings.
        """
        self.env_file = env_file
        load_dotenv(self.env_file)
        self.configs = dotenv_values(self.env_file)

    def load_configs(self):
        """
        Loads configuration settings from the .env file into the current environment.
        """
        self.configs = dotenv_values(self.env_file)

    def save_config(self):
        """
        Saves the current configuration settings to the .env file.
        """
        with open(self.env_file, 'w') as configfile:
            for key, value in self.configs.items():
                configfile.write(f"{key}={value}\n")

    def set(self, option, value):
        """
        Sets a configuration value and saves it to the .env file.
        """
        self.configs[option.upper()] = str(value)
        self.save_config()
        self.load_configs()

    @property
    def db_name(self):
        return self.configs.get('DB_NAME')


# Example usage:
# Instantiate the AppConfig class
config = AppConfig()
# Now, configuration settings can be accessed as properties of the `config` object
