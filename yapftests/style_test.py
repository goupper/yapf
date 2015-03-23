# -*- coding: utf-8 -*-
# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for yapf.style"""

import contextlib
import shutil
import tempfile
import textwrap
import unittest

from yapf.yapflib import style


class UtilsTest(unittest.TestCase):

  def test_StringListConverter(self):
    self.assertEqual(style._StringListConverter('foo, bar'), ['foo', 'bar'])
    self.assertEqual(style._StringListConverter('foo,bar'), ['foo', 'bar'])
    self.assertEqual(style._StringListConverter('  foo'), ['foo'])
    self.assertEqual(style._StringListConverter('joe  ,foo,  bar'),
                     ['joe', 'foo', 'bar'])

  def test_BoolConverter(self):
    self.assertEqual(style._BoolConverter('true'), True)
    self.assertEqual(style._BoolConverter('1'), True)
    self.assertEqual(style._BoolConverter('false'), False)
    self.assertEqual(style._BoolConverter('0'), False)


def _LooksLikeGoogleStyle(cfg):
  return (cfg['INDENT_WIDTH'] == 2 and
          cfg['BLANK_LINE_BEFORE_NESTED_CLASS_OR_DEF'])


def _LooksLikePEP8Style(cfg):
  return (cfg['INDENT_WIDTH'] == 4 and
          not cfg['BLANK_LINE_BEFORE_NESTED_CLASS_OR_DEF'])
  

class PredefinedStylesByNameTest(unittest.TestCase):

  def test_Default(self):
    # default is PEP8
    cfg = style.CreateStyleFromConfig(None)
    self.assertTrue(_LooksLikePEP8Style(cfg))

  def test_GoogleByName(self):
    for google_name in ('google', 'Google', 'GOOGLE'):
      cfg = style.CreateStyleFromConfig(google_name)
      self.assertTrue(_LooksLikeGoogleStyle(cfg))

  def test_PEP8ByName(self):
    for pep8_name in ('PEP8', 'pep8', 'Pep8'):
      cfg = style.CreateStyleFromConfig(pep8_name)
      self.assertTrue(_LooksLikePEP8Style(cfg))


@contextlib.contextmanager
def _TempFileContents(dir, contents):
  with tempfile.NamedTemporaryFile(dir=dir, mode='w') as f:
    f.write(contents)
    f.flush()
    yield f
  

class StyleFromFileTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.test_tmpdir = tempfile.mkdtemp()

  @classmethod
  def tearDownClass(cls):
    shutil.rmtree(cls.test_tmpdir)

  def test_DefaultBasedOnStyle(self):
    cfg = textwrap.dedent('''\
        [style]
        tab_width = 20
        ''')
    with _TempFileContents(self.test_tmpdir, cfg) as f:
      cfg = style.CreateStyleFromConfig(f.name)
      self.assertTrue(_LooksLikePEP8Style(cfg))
      self.assertEqual(cfg['TAB_WIDTH'], 20)

  def test_DefaultBasedOnPEP8Style(self):
    cfg = textwrap.dedent('''\
        [style]
        based_on_style = pep8
        tab_width = 40
        ''')
    with _TempFileContents(self.test_tmpdir, cfg) as f:
      cfg = style.CreateStyleFromConfig(f.name)
      self.assertTrue(_LooksLikePEP8Style(cfg))
      self.assertEqual(cfg['TAB_WIDTH'], 40)

  def test_DefaultBasedOnGoogleStyle(self):
    cfg = textwrap.dedent('''\
        [style]
        based_on_style = google
        split_penalty_matching_bracket = 33
        ''')
    with _TempFileContents(self.test_tmpdir, cfg) as f:
      cfg = style.CreateStyleFromConfig(f.name)
      self.assertTrue(_LooksLikeGoogleStyle(cfg))
      self.assertEqual(cfg['SPLIT_PENALTY_MATCHING_BRACKET'], 33)

  def test_BoolOptionValue(self):
    cfg = textwrap.dedent('''\
        [style]
        based_on_style = google
        SPLIT_BEFORE_NAMED_ASSIGNS = False
        split_before_logical_operator = true
        ''')
    with _TempFileContents(self.test_tmpdir, cfg) as f:
      cfg = style.CreateStyleFromConfig(f.name)
      self.assertTrue(_LooksLikeGoogleStyle(cfg))
      self.assertEqual(cfg['SPLIT_BEFORE_NAMED_ASSIGNS'], False)
      self.assertEqual(cfg['SPLIT_BEFORE_LOGICAL_OPERATOR'], True)

  def test_StringListOptionValue(self):
    cfg = textwrap.dedent('''\
        [style]
        based_on_style = google
        I18N_FUNCTION_CALL = N_, V_, T_
        ''')
    with _TempFileContents(self.test_tmpdir, cfg) as f:
      cfg = style.CreateStyleFromConfig(f.name)
      self.assertTrue(_LooksLikeGoogleStyle(cfg))
      self.assertEqual(cfg['I18N_FUNCTION_CALL'], ['N_', 'V_', 'T_'])


def suite():
  result = unittest.TestSuite()
  result.addTests(unittest.makeSuite(UtilsTest))
  result.addTests(unittest.makeSuite(PredefinedStylesByNameTest))
  result.addTests(unittest.makeSuite(StyleFromFileTest))
  return result


if __name__ == '__main__':
  unittest.main()
