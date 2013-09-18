"""
:mod:`phile.parser`
===================


This module can parse a string representaion of a while program into a
AST (see. :mod:`phile.ast`).  The simple usage is just to use the function:

.. autofunction:: parse_program


:class:`Parser` class
---------------------

.. autoclass:: Parser
    :members:

Exceptions
----------

.. autoclass:: CouldNotParseToken

"""
import collections
import functools
import string

import logging
L = logging.getLogger(__name__)

class CouldNotParseToken(Exception):
    """ The token reached was unexpected """
    def __init__(self, token, expected):
        super(CouldNotParseToken, self).__init__(
                'Failed parsing {expected}\n Reason: {token}'\
                        .format(token=token, expected=expected)
                        )

def reflex(data):
    """ Mark that data should be parsed on as is"""
    return data

def precedence(prec, factory):
    """
    This is a factory function able to make a function
    that checks that the precedence is correct for binary
    operators.

    :param prec: The precedence table, higger is worse:
        * -> 3

    :param factory: Returns a tree node when called with
        tree values (first, operator, second). The tree node
        *must* have an attribute called ``operator``, which
        can be used to find the precedence
    """
    def internal (first, operator, second):
        """
        The ensures precedence of the operators
        """
        if (hasattr(second,'operator') and
                prec[operator] < prec[second.operator]):
            new_node = internal(first, operator, second.first)
            return factory(new_node, second.operator, second.second)
        else:
            return factory(first, operator, second)
    return internal


VALUE_TEST = frozenset(string.ascii_uppercase).union('_')

def is_token(name, token_id):
    """
    Returns true if name is all uppercase letters
    """
    return (any(not char in VALUE_TEST for char in name)
            or name.startswith(token_id))

Context = collections.namedtuple('Context', ['tokens', 'matches'])

def parse_rule(rule, tokens, gramma, token_id):
    """
    parses a rule using tokens and a gramma
    """
    def parse_name(context, name):
        """
        parses a single name using the context
        """
        if not context.tokens:
            raise CouldNotParseToken(None, name)

        if is_token(name, token_id):
            token, *rest = context.tokens
            if token_id + token.name == name:
                return Context(rest, [token.value])
            elif token.value == name:
                return Context(rest, context.matches)
            else:
                raise CouldNotParseToken(token, name)
        else:
            error = None
            for function, srule in gramma.get(name, [(str, token_id+name)]):
                try:
                    result = parse_rule(srule, context.tokens, gramma, token_id)
                    matches = context.matches + [function(*result.matches)]
                    return Context(result.tokens, matches)
                except CouldNotParseToken as exception:
                    error = exception
            raise CouldNotParseToken(error, name)

    return functools.reduce(parse_name, rule.split(), Context(tokens, []))

def parse(rule, tokens, gramma, token_id='#'):
    """
    Parses a while rule, using tokens
    """
    return parse_rule(rule, list(tokens), gramma, token_id).matches[0]

