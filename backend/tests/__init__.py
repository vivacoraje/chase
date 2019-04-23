# -*- coding: utf-8 -*-
import os
import sys
import unittest
import coverage


def run():

    cov = coverage.Coverage(branch=True)
    cov.start()

    tests = unittest.TestLoader().discover('.')
    ok = unittest.TextTestRunner(verbosity=2).run(tests).wasSuccessful()

    cov.stop()

    print('')
    cov.report(omit=['manage.py', 'tests/*', 'venv*/*'])

    sys.exit(0 if ok else 1)
