# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.
Create a `.env` file in the current directory where
this `config.py` is and add environment variables that
are required

For examples, see `etc/dev/.env.bash` or `etc/dev/.env.fish`
"""
from environs import Env as Env

env = Env()
env.read_env()

ENV = env.str("FLASK_ENV", default="production")
DEBUG = env.bool("FLASK_DEBUG", default=False)
TESTING = env.bool("FLASK_TESTING", default=False)
CANDIG_UPSTREAM_API = env.str("CANDIG_UPSTREAM_API")
SECRET_KEY = env.str("SECRET_KEY")
DP_EPSILON = env.float("DP_EPSILON")
