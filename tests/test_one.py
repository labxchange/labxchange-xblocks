#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the `labxchange-xblocks` models module.
"""

from __future__ import absolute_import, unicode_literals

from labxchange_xblocks import one


def test_one():
    assert one() == 1
