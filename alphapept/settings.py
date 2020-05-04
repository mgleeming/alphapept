# AUTOGENERATED! DO NOT EDIT! File to edit: nbs\11_settings.ipynb (unless otherwise specified).

__all__ = ['print_settings', 'load_settings', 'save_settings']

# Cell
import yaml

def print_settings(settings):
    """
    Print settings
    """
    print(yaml.dump(settings, default_flow_style=False))


def load_settings(path):
    """
    Print settings
    """
    with open(path, "r") as settings_file:
        SETTINGS_LOADED = yaml.load(settings_file, Loader=yaml.FullLoader)
        return SETTINGS_LOADED

def save_settings(settings, path):
    """
    Save settings
    """
    with open(path, "w") as file:
        yaml.dump(settings, file)