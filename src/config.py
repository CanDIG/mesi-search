# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a `etc/.env.bash` or `etc/.env.bash.fish`
file to set environment variables.
"""
from environs import Env as Env

env = Env()
env.read_env()

ENV = env.str("FLASK_ENV", default="production")
DEBUG = env.bool("FLASK_DEBUG", default=False)
TESTING = env.bool("FLASK_TESTING", default=False)
SECRET_KEY = env.str("SECRET_KEY")
