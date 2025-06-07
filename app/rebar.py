# -*- coding: utf-8 -*-
"""Application rebar registry."""
from __future__ import unicode_literals

from config.secrets_config import DISABLE_SWAGGER
from flask_rebar import Rebar
from flask_rebar import SwaggerV3Generator

rebar = Rebar()
if DISABLE_SWAGGER:
    registry = rebar.create_handler_registry(
        prefix="/api", spec_path=None, swagger_ui_path=None
    )
else:
    registry = rebar.create_handler_registry(
        prefix="/api",
        swagger_generator=SwaggerV3Generator(
            title="Smart Store Api",
            description=" Api docs for Tamayo Smart Store Api",
            version="3.3.1",
        ),
    )
