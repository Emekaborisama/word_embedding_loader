# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import io

import numpy as np
import pytest
from numpy.testing import assert_array_equal

import word_embedding_loader.loader.glove as glove
from word_embedding_loader import ParseError, ParseWarning


def test_load(glove_file):
    arr, vocab = glove.load(glove_file, dtype=np.float32)
    assert b'the' in vocab
    assert b',' in vocab
    assert '日本語'.encode('utf-8') in vocab
    assert len(vocab) == 3
    assert len(arr) == 3
    assert arr.dtype == np.float32

    assert vocab[b'the'] == 0
    assert vocab[b','] == 1
    assert vocab['日本語'.encode('utf-8')] == 2

    assert_array_equal(arr[vocab[b'the']],
                       np.array([0.418, 0.24968, -0.41242, 0.1217],
                                dtype=np.float32))
    assert_array_equal(arr[vocab[b',']],
                       np.array([0.013441, 0.23682, -0.16899, 0.40951],
                                dtype=np.float32))
    assert_array_equal(arr[vocab['日本語'.encode('utf-8')]],
                       np.array([0.15164, 0.30177, -0.16763, 0.17684],
                                dtype=np.float32))


def test_check_valid(tmpdir):
    with open(tmpdir.join('test_check_valid.txt').strpath, 'a+b') as f:
        f.write("""the 0.418 0.24968 -0.41242 0.1217
    , 0.013441 0.23682 -0.16899 0.40951""".encode('utf-8'))
        f.flush()
        assert glove.check_valid(f.name)
    with open(tmpdir.join('test_check_valid_fail.txt').strpath, 'a+b') as f:
        f.write("""2 4\nthe 0.418 0.24968 -0.41242 0.1217""".encode('utf-8'))
        f.flush()
        assert not glove.check_valid(f.name)


def test_load_fail():
    f = io.BytesIO("""the 0.418 0.24968 -0.41242 0.1217
, 0.013441 0.23682 0.40951
日本語 0.15164 0.30177 -0.16763 0.17684""".encode('utf-8'))
    with pytest.raises(ParseError):
        glove.load(f)


def test_load_with_vocab(glove_file):
    vocab = dict((
        (b'the', 1),
        ('日本語'.encode('utf-8'), 0)
    ))

    arr = glove.load_with_vocab(glove_file, vocab)
    assert len(arr) == 2
    assert arr.dtype == np.float32
    # Machine epsilon is 5.96e-08 for float32
    assert_array_equal(arr[vocab[b'the']],
                       np.array([0.418, 0.24968, -0.41242, 0.1217],
                                dtype=np.float32))
    assert_array_equal(arr[vocab['日本語'.encode('utf-8')]],
                       np.array([0.15164, 0.30177, -0.16763, 0.17684],
                                dtype=np.float32))


def test_load_warn_duplicate(tmpdir):
    with open(tmpdir.join('glove.txt').strpath, 'a+b') as glove_file:
        glove_file.write("""the 0.418 0.24968 -0.41242 0.1217
    , 0.013441 0.23682 -0.16899 0.40951
    日本語 0.15164 0.30177 -0.16763 0.17684
    , 0.013441 -0.16763 0.17684 0.40951""".encode('utf-8'))
        glove_file.flush()
        glove_file.seek(0)
        with pytest.warns(ParseWarning):
            glove.load(glove_file, dtype=np.float32)
