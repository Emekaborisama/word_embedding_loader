# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import numpy as np
import word_embedding_loader.loader.numpy as numpy_module
from numpy.testing import assert_allclose


def test_load(numpy_file):
    arr, vocab = numpy_module.load(numpy_file)
    assert b'</s>' in vocab
    assert b'the' in vocab
    assert '日本語'.encode('utf-8') in vocab
    assert len(vocab) == 3
    assert len(arr) == 3
    assert arr.dtype == np.float32

    assert vocab[b'</s>'] == 0
    assert vocab[b'the'] == 1
    assert vocab['日本語'.encode('utf-8')] == 2

    # Machine epsilon is 5.96e-08 for float32
    assert_allclose(arr[vocab[b'</s>']],
                    np.array([0.08005371, 0.08838806, -0.07660522,
                              -0.06556091, 0.02733154], dtype=np.float32),
                    atol=1e-8)
    assert_allclose(arr[vocab['日本語'.encode('utf-8')]],
                    np.array([-1.67798984, -0.02645044, -0.18966547,
                              1.16504729, -1.39292037], dtype=np.float32),
                    atol=1e-8)
    assert_allclose(arr[vocab[b'the']],
                    np.array([-0.5346821, 1.05223596, -0.24605329,
                              -1.82213438, -0.57173866], dtype=np.float32),
                    atol=1e-8)


def test_check_valid(tmpdir, numpy_file_path):
    assert numpy_module.check_valid(numpy_file_path)
    with open(tmpdir.join('test_check_valid_fail.txt').strpath, 'a+b') as f:
        f.write("""the 0.418 0.24968 -0.41242 0.1217
    , 0.013441 0.23682 -0.16899 0.40951""".encode('utf-8'))
        f.flush()
        assert not numpy_module.check_valid(f.name)


def test_load_with_vocab(numpy_file):
    vocab = dict((
        (b'</s>', 1),
        ('日本語'.encode('utf-8'), 0)
    ))

    arr = numpy_module.load_with_vocab(numpy_file, vocab)
    assert len(arr) == 2
    assert arr.dtype == np.float32
    # Machine epsilon is 5.96e-08 for float32
    assert_allclose(arr[vocab[b'</s>']],
                    np.array([0.08005371, 0.08838806, -0.07660522,
                              -0.06556091, 0.02733154], dtype=np.float32),
                    atol=1e-8)
    assert_allclose(arr[vocab['日本語'.encode('utf-8')]],
                    np.array([-1.67798984, -0.02645044, -0.18966547,
                              1.16504729, -1.39292037], dtype=np.float32),
                    atol=1e-8)
