import typing
import json
from pathlib import Path
import logging
import os
import copy
from datetime import datetime

class ConfigurationManager:
    """
    Manages system-wide configurations with support for different environments
    and dynamic configuration updates.
    """
    
    def __init__(self, config_dir: str = 'config'):
        """
        Initialize ConfigurationManager with a specific configuration directory.
        
        :param config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.logger = logging.getLogger('configuration_manager')
        self._configurations: dict[str, dict] = {}
        self._config_history: dict[str, list[dict]] = {}
        self._load_configurations()
    
    def _load_configurations(self):
        """
        Load all JSON configuration files from the config directory.
        """
        for config_file in self.config_dir.glob('*.json'):
            try:
                with open(config_file, 'r') as f:
                    config_name = config_file.stem
                    config_data = json.load(f)
                    self._configurations[config_name] = config_data
                    self._config_history[config_name] = [copy.deepcopy(config_data)]
                    self.logger.info(f"Loaded configuration: {config_name}")
            except json.JSONDecodeError:
                self.logger.error(f"Invalid JSON in configuration file: {config_file}")
            except IOError as e:
                self.logger.error(f"Error reading configuration file {config_file}: {e}")
    
    def get_configuration(self, config_name: str) -> typing.Optional[dict]:
        """
        Retrieve a specific configuration.
        
        :param config_name: Name of the configuration to retrieve
        :return: Configuration dictionary or None
        """
        return self._configurations.get(config_name)
    
    def update_configuration(self, config_name: str, updates: dict) -> bool:
        """
        Update a specific configuration with new values.
        
        :param config_name: Name of the configuration to update
        :param updates: Dictionary of updates to apply
        :return: True if update successful, False otherwise
        """
        if config_name not in self._configurations:
            self.logger.error(f"Configuration {config_name} not found")
            return False
        
        # Create a deep copy of the current configuration
        current_config = copy.deepcopy(self._configurations[config_name])
        
        # Recursively update the configuration
        def deep_update(original, update):
            for key, value in update.items():
                if isinstance(value, dict):
                    original[key] = deep_update(original.get(key, {}), value)
                else:
                    original[key] = value
            return original
        
        updated_config = deep_update(current_config, updates)
        
        # Store the update in configuration history
        self._configurations[config_name] = updated_config
        self._config_history[config_name].append({
            'timestamp': datetime.now().isoformat(),
            'configuration': copy.deepcopy(updated_config)
        })
        
        # Optionally, save the updated configuration to file
        self._save_configuration(config_name)
        
        self.logger.info(f"Updated configuration: {config_name}")
        return True
    
    def _save_configuration(self, config_name: str):
        """
        Save a configuration to its corresponding JSON file.
        
        :param config_name: Name of the configuration to save
        """
        config_path = self.config_dir / f"{config_name}.json"
        try:
            with open(config_path, 'w') as f:
                json.dump(self._configurations[config_name], f, indent=2)
            self.logger.info(f"Saved configuration to {config_path}")
        except IOError as e:
            self.logger.error(f"Error saving configuration {config_name}: {e}")
    
    def get_configuration_history(self, config_name: str, limit: int = 10) -> list[dict]:
        """
        Retrieve configuration change history.
        
        :param config_name: Name of the configuration
        :param limit: Maximum number of historical entries to return
        :return: List of configuration history entries
        """
        return self._config_history.get(config_name, [])[-limit:]
    
    def rollback_configuration(self, config_name: str, steps: int = 1) -> bool:
        """
        Rollback a configuration to a previous state.
        
        :param config_name: Name of the configuration
        :param steps: Number of steps to rollback
        :return: True if rollback successful, False otherwise
        """
        if config_name not in self._config_history:
            self.logger.error(f"No history found for configuration: {config_name}")
            return False
        
        history = self._config_history[config_name]
        if len(history) <= steps:
            self.logger.error(f"Cannot rollback {steps} steps for {config_name}")
            return False
        
        # Rollback to the specified previous configuration
        rolled_back_config = history[-steps - 1]
        self._configurations[config_name] = copy.deepcopy(rolled_back_config)
        
        # Save the rolled back configuration
        self._save_configuration(config_name)
        
        self.logger.info(f"Rolled back configuration {config_name} by {steps} steps")
        return True
    
    def list_configurations(self) -> list[str]:
        """
        List all available configurations.
        
        :return: List of configuration names
        """
        return list(self._configurations.keys())

def main():
    """Example usage of ConfigurationManager."""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize ConfigurationManager
    config_manager = ConfigurationManager()
    
    # List available configurations
    print("Available Configurations:", config_manager.list_configurations())
    
    # Get a specific configuration
    compliance_config = config_manager.get_configuration('compliance_config')
    print("Compliance Configuration:", compliance_config)
    
    # Update a configuration
    update_result = config_manager.update_configuration('compliance_config', {
        'new_rule': {
            'name': 'Additional Privacy Rule',
            'description': 'Enhanced privacy protection',
            'severity': 'high'
        }
    })
    
    # Get configuration history
    history = config_manager.get_configuration_history('compliance_config')
    print("Configuration History:", history)

if __name__ == '__main__':
    main()
