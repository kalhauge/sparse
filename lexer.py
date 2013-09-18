"""
:mod:`phile.lexer`
====================

.. currentmodule:: phile.lexer

This module has to main focus is to scan the file for tokens. This modules
only contains a single function:

.. autofunction:: tokenize

"""

import logging
L = logging.getLogger(__name__)

# Partly fro
# http://docs.python.org/3/library/re.html#writing-a-tokenizer

import re
import collections

Token = collections.namedtuple('Token', ['name', 'value', 'line'])


def tokenize(string, token_desc, keywords):
    """
    Tokenize scans a string and yields a sequence of tokens.

    :param string:
        A string representation of a program written in while.

    :param token_desc:
        A list of tuples containing the name, and the regular
        expression needed to parse the token.
        
        5 special keywords is used ``SKIP``, ``NEWLINE``, 
        ``COMMENT_BEGIN``, ``COMMENT_END``, and
        ``ID``. ``SKIP`` skips the token, ``NEWLINE`` adds makes
        the line counter increase (and is skipped). And lastly
        ``ID`` which will return as an ID token except if equal
        to one of the keywords

    :param keywords:
        A list of ID's which should be recognised as words with
        special meaning. Both the name and the value of such tokens
        will be equal to the keyword.

    :yeilds: a sequence of tokens representing the program, 
        like the named tuple :class:`Token`. 
    """
    token_regex = '|'.join('(?P<{}>{})'.format(name, regex)
            for name, regex in token_desc)
    get_token = re.compile(token_regex).match

    line = 1
    token_match = get_token(string)
    skip_all = False
    while token_match is not None:
        name = token_match.lastgroup
        if name != 'COMMENT_END' and skip_all:
            pass
        elif name == 'COMMENT_END':
            skip_all = False;
        elif name == 'COMMENT_BEGIN':
            skip_all = True;
        elif name == 'NEWLINE':
            line += 1
        elif name == 'SKIP':
            pass
        elif name != 'SKIP':
            val = token_match.group(name)
            if name == 'ID' and val in keywords:
                name = val
            yield Token(name, val, line)
        pos = token_match.end()
        token_match = get_token(string, pos)
    if pos != len(string):
        raise RuntimeError('Unexpected character %r on line %d' %
                (string[pos], line))


