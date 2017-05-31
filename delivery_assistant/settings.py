# -*- coding: utf-8 -*-
"""Application configuration.

See https://github.com/sloria/cookiecutter-flask for configuration options with other flask-extensions
"""
import os


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('DELIVERY_ASSISTANT_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

    # Flask-Assistant Integrations
    ASSIST_ACTIONS_ON_GOOGLE = True
    CLIENT_ACCESS_TOKEN = 'YOUR API.AI AGENT CLIENT ACCESS TOKEN'
    DEV_ACCESS_TOKEN = 'YOUR API.AI AGENT DEVELOPER ACCESS TOKEN'

class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True

class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
