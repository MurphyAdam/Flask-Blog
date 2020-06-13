from collections import Counter
import sys
import time
import re
import bleach
import random
from validator_collection import validators, checkers, errors
import datetime


def format_time(datetime_obj):
    if datetime_obj:
        date = datetime.datetime.strftime(
            datetime_obj, '%A the %d of %B, %Y'
            )
        return date
    return None

def clean_text(text):
    tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong','ul']
    attributes={'a': ['href', 'title'], 'abbr': ['title'], 'acronym': ['title']}
    styles=[]
    protocols=['http', 'https', 'mailto']
    # Nuke all html, scripts, etc
    text = bleach.clean(text, tags, strip=False, strip_comments=True)
    return text


def is_empty(text):
    return False if text and checkers.is_string(text) and not text.isspace() and len(text) > 0 else True

def spread(arg):
	ret = []
	for i in arg:
		if isinstance(i, list):
			ret.extend(i)
		else:
			ret.append(i)
	return ret


def deep_flatten(xs):
	flat_list = []
	[flat_list.extend(deep_flatten(x)) for x in xs] if isinstance(xs, list) else flat_list.append(xs)
	return flat_list


def has_duplicates(lst):
	return len(lst) != len(set(lst))


def merge_dictionaries(a, b):
	return {**a, **b}

def to_dictionary(keys, values):
	return dict(zip(keys, values))

def most_frequent(lst):
	return max(set(lst), key = lst.count)


def shortentags(tag):
    # Lets loop and map each char (v) against its equavalent char (k)
    for k, v in TO_SHORT_TAGS.items():
        tag = tag.replace(k, v)
    return(tag)


def str2tuple(s, sep='/'):
    """ 
        >>> str2tuple('fly/NN')
        ('fly', 'NN')
    """
    loc = s.rfind(sep)
    if loc >= 0:
        return (s[:loc], s[loc + len(sep) :].upper())
    else:
        return (s, None)


def tuple2str(tagged_token, sep='/'):
    """
        >>> tagged_token = ('fly', 'NN')
        >>> tuple2str(tagged_token)
        'fly/NN'
    """
    word, tag = tagged_token
    if tag is None:
        return word
    else:
        assert sep not in tag, 'tag may not contain sep!'
        return '%s%s%s' % (word, sep, tag)


def is_one_token(token):
    return len(re.split("\s+", token)) == 1


def is_one_token_adv(data):
    if isinstance(data, str):
        if data != "":
            return len(re.split("\s+", data)) == 1
        else:
            return "Empty string"
    return "Invalid data {}".format(type(data))


def contains_swear_words(input):
    swear_words = ('some inappropriate word', 'mouthbreather', 'other inappropriate word')
    for word in swear_words:
        if word in input:
            return True