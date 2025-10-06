"""
Configuration loader for Google Ads Multi-Agent System
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
from dotenv import load_dotenv


class ConfigLoader:
    """Configuration loader for Google Ads settings"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader

        Args:
            config_path: Optional path to config file
        """
        # Load environment variables
        load_dotenv()

        # Determine config path
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Look for config in multiple locations
            possible_paths = [
                Path(__file__).parent.parent.parent / "config" / "google_ads_config.yaml",
                Path.cwd() / "google-ads-multiagent" / "config" / "google_ads_config.yaml",
                Path.cwd() / "google-ads.yaml",
                Path.cwd() / ".google-ads.yaml"
            ]

            for path in possible_paths:
                if path.exists():
                    self.config_path = path
                    break
            else:
                logger.warning("No config file found, using environment variables only")
                self.config_path = None

        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file and environment"""
        config = {}

        # Load from YAML file if exists
        if self.config_path and self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        config.update(file_config)
                logger.info(f"Loaded config from {self.config_path}")
            except Exception as e:
                logger.error(f"Error loading config file: {e}")

        # Override with environment variables
        env_mapping = {
            'developer_token': 'GOOGLE_ADS_DEVELOPER_TOKEN',
            'client_id': 'GOOGLE_ADS_CLIENT_ID',
            'client_secret': 'GOOGLE_ADS_CLIENT_SECRET',
            'refresh_token': 'GOOGLE_ADS_REFRESH_TOKEN',
            'login_customer_id': 'GOOGLE_ADS_LOGIN_CUSTOMER_ID',
            'use_proto_plus': 'GOOGLE_ADS_USE_PROTO_PLUS'
        }

        for key, env_var in env_mapping.items():
            env_value = os.getenv(env_var)
            if env_value:
                # Handle boolean values
                if key == 'use_proto_plus':
                    config[key] = env_value.lower() in ('true', '1', 'yes')
                else:
                    config[key] = env_value

        # Validate required fields
        required_fields = ['developer_token', 'client_id', 'client_secret', 'refresh_token']
        missing_fields = [field for field in required_fields if not config.get(field)]

        if missing_fields:
            logger.warning(f"Missing required config fields: {missing_fields}")

        return config

    def get_google_ads_client(self):
        """
        Create and return a Google Ads client

        Returns:
            GoogleAdsClient instance
        """
        try:
            from google.ads.googleads.client import GoogleAdsClient

            # Create client configuration
            client_config = {
                'developer_token': self.config.get('developer_token'),
                'client_id': self.config.get('client_id'),
                'client_secret': self.config.get('client_secret'),
                'refresh_token': self.config.get('refresh_token'),
                'use_proto_plus': self.config.get('use_proto_plus', True)
            }

            # Add login customer ID if present
            login_customer_id = self.config.get('login_customer_id')
            if login_customer_id:
                client_config['login_customer_id'] = str(login_customer_id)

            # Create client
            client = GoogleAdsClient.load_from_dict(client_config)
            logger.info("Successfully created Google Ads client")
            return client

        except Exception as e:
            logger.error(f"Error creating Google Ads client: {e}")
            raise

    def get_config(self, key: str = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key (optional)

        Returns:
            Configuration value or entire config dict
        """
        if key:
            return self.config.get(key)
        return self.config

    def validate_config(self) -> bool:
        """
        Validate configuration

        Returns:
            True if config is valid
        """
        required_fields = ['developer_token', 'client_id', 'client_secret', 'refresh_token']

        for field in required_fields:
            if not self.config.get(field):
                logger.error(f"Missing required field: {field}")
                return False

            # Check for placeholder values
            value = self.config.get(field)
            if value and ('YOUR_' in value or value == 'PLACEHOLDER'):
                logger.error(f"Placeholder value found for {field}")
                return False

        logger.info("Configuration validation passed")
        return True

    def get_openai_config(self) -> Dict[str, Any]:
        """
        Get OpenAI configuration for agents

        Returns:
            OpenAI configuration dictionary
        """
        return {
            'api_key': os.getenv('OPENAI_API_KEY'),
            'model': os.getenv('OPENAI_MODEL', 'gpt-4'),
            'temperature': float(os.getenv('OPENAI_TEMPERATURE', '0.7')),
            'max_tokens': int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
        }

    def get_database_config(self) -> Dict[str, Any]:
        """
        Get database configuration

        Returns:
            Database configuration dictionary
        """
        return {
            'type': os.getenv('DB_TYPE', 'sqlserver'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '1433')),
            'name': os.getenv('DB_NAME', 'MarketingIQ'),
            'user': os.getenv('DB_USER', 'sa'),
            'password': os.getenv('DB_PASSWORD', '')
        }

    def get_api_config(self) -> Dict[str, Any]:
        """
        Get API configuration

        Returns:
            API configuration dictionary
        """
        return {
            'host': os.getenv('API_HOST', '0.0.0.0'),
            'port': int(os.getenv('API_PORT', '8000')),
            'debug': os.getenv('API_DEBUG', 'False').lower() == 'true',
            'cors_origins': os.getenv('CORS_ORIGINS', '*').split(',')
        }


# Singleton instance
_config_loader = None


def get_config_loader() -> ConfigLoader:
    """
    Get singleton config loader instance

    Returns:
        ConfigLoader instance
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


def get_google_ads_client():
    """
    Convenience function to get Google Ads client

    Returns:
        GoogleAdsClient instance
    """
    loader = get_config_loader()
    return loader.get_google_ads_client()


def get_config(key: str = None) -> Any:
    """
    Convenience function to get configuration

    Args:
        key: Configuration key (optional)

    Returns:
        Configuration value or entire config dict
    """
    loader = get_config_loader()
    return loader.get_config(key)