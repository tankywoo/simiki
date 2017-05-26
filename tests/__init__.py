#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement, unicode_literals
import os
import logging

logging.disable(logging.CRITICAL)
os.environ['TEST_MODE'] = "true"  # random string to indicate test mode enabled
