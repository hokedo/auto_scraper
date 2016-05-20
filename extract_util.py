#-*- coding:utf-8 -*-
import HTMLParser
import logging
import re
# TODO: do not remove the unused imports, until they can be specified
# in the extraction templates. they are used in some eval expressions
import datetime
import json
import lxml
import sys

from pyquery import PyQuery as pq

hp = HTMLParser.HTMLParser()
logger = logging.getLogger("extract.util")


def extract(doc, template, url=None):
	if doc is None or not isinstance(doc, pq) or len(doc) == 0:
		return None

	doc = pq(doc, parser=template.get('format'))

	output = {}

	for prop, rules in template.get('requires', {}).items():
		logger.debug("  check: %r", prop)
		if prop == 'url' and url is not None:
			if not any([re.search(url_re, url) for url_re in rules]):
				return None

		else:
			for rule in rules:
				if not apply_rule(doc, rule):
					# don't apply any other rules, if one of the conditions
					# are not met
					return None

	for prop, rules in template.get('properties').items():
		logger.debug("extract: %r", prop)

		if type(rules) == list:
			for rule in rules:
				result = apply_rule(doc, rule)
				logger.debug("      -> %r", result)

				if result:
					output[prop] = result
					# stop evaluating the extraction rules as soon as we
					# get a truish value
					break

		else:
			rule = dict(path=rules.get('path'), pp=rules.get('pp', []))
			if 'items' in rules:
				results = []
				for item in apply_rule(doc, rule):
					result = extract(
						item if isinstance(item, pq) else pq(item),
						rules.get('items')
						)
					results.append(result)

				output[prop] = results

			else:
				item = apply_rule(doc, rule)
				output[prop] = extract(
					item if isinstance(item, pq) else pq(item),
					rules
					)

	return output


def apply_rule(doc, rule):
	this = None
	if not rule.get('path'):
		this = doc
	else:
		logger.debug("   path: %r", rule['path'])
		this = doc(rule['path'])

	if 'pp' in rule:
		for pp in rule['pp']:
			logger.debug("   post process: %r", pp)
			pp_name = pp[0] if type(pp) == list else pp

			if pp_name == 'attr':
				this = this.attr(pp[1]) if this and pp[1] else None

			elif pp_name == 'match':
				if this:
					match = re.search(pp[1], this)
					if match and len(match.groups()) >= pp[2]:
						this = match.group(pp[2])
						this = this.strip() if this else this
					else:
						this = None
				else:
					this = None

			elif pp_name == 'sub':
				this = re.sub(pp[1], pp[2], this) if this else this

			elif pp_name == 'float':
				this = float(this) if this else None

			elif pp_name == 'int':
				this = int(this) if this else None

			elif pp_name == 'eval':
				this = eval(pp[1])

			elif pp_name == 'csspath':
				this = this(pp[1]) if isinstance(this, pq) else pq([])

			elif pp_name == 'scale':
				this = scale(this, pp[1], pp[2] if len(pp) > 2 else 0)

			elif pp_name == 'date_format':
				return date_format(
					this,
					pp[1],
					pp[2],
					from_locale=pp[3] if len(pp) > 3 else 'en_US.utf8',
					to_locale=pp[4] if len(pp) > 4 else 'C'
					)

			elif pp_name == 'decode_html':
				return decode_html(this)

			elif pp_name == 'url_abs':
				return url_abs(pp[1], this) if this is not None else this

			elif pp_name == 'text':
				this = this.text() or None if this is not None else this

			elif pp_name == 'text_contents':
				this = this.contents().map(
					lambda i, e: pq(e).text()
						if isinstance(e, basestring) else None
					) or None if this is not None else this

			elif pp_name == 'strip':
				this = this.strip() or None if this is not None else this

			elif pp_name == 'str':
				this = str(this) if this is not None else ''

			else:
				raise ValueError("Unsupported post process %r", pp)

			logger.debug("              -> %r", this)

	else:
		this = pq(this) if not isinstance(this, pq) else this

	return this


def scale(val, max_val, min_val=0):
	import math

	if min_val < max_val:
		if val >= min_val and val <= max_val:
			return int(round(val / float(max_val) * 100))

	else:
		if val <= min_val and val >= max_val:
			return int(round((min_val + max_val - val) * 100 / float(min_val)))

	return None


def decode_html(txt):
	return hp.unescape(txt) if txt is not None else None


def url_abs(base_url, url):
	import urlparse
	return urlparse.urljoin(base_url, url)


def date_format(txt, from_format, to_format, from_locale='en_US.utf8', to_locale='C'):
	"""
	For available formats, see:
	https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
	"""
	import locale

	if txt is None:
		return None

	_locale = locale.getlocale()
	try:
		locale.setlocale(locale.LC_ALL, from_locale)
		dt = datetime.datetime.strptime(txt, from_format)
		result = None
		if to_format == 'utc_ms':
			result = int((dt - datetime.datetime(1970, 1, 1)).total_seconds()) * 1000

		elif to_format == 'utc_s':
			result = int((dt - datetime.datetime(1970, 1, 1)).total_seconds())

		else:
			locale.setlocale(locale.LC_ALL, to_locale)
			result = dt.strftime(to_format)

		return result

	finally:
		locale.setlocale(locale.LC_ALL, _locale)

def remove_nones(o):
	if isinstance(o, int) or isinstance(o, float):
		return o
	elif o:
		if isinstance(o, dict):
			return {k: remove_nones(v) for k, v in o.iteritems() if v is not None}
		elif isinstance(o, list):
			return [remove_nones(v) for v in o if v is not None]
		else:
			return o
	else:
		return {}

def text_parts_concat(parts, sep):
	sep = sep if sep and type(sep) is str else u" "
	ret = u""
	if type(parts) is not list:
		return ret
	for elem in parts:
		if ret and elem:
			if not re.search(ur"[\.\?\!:;,。]$", ret):
				ret += u"." + sep
			else:
				ret += sep
		ret += elem

	return ret

def filter_reviews(reviews, review_filter, category_score_filter=None):
	for i in reversed(xrange(len(reviews))):
		review = reviews[i]
		# ignore reviews if the filter function says so
		if review_filter(review):
			continue
		if category_score_filter is not None:
			# ignore score elements if the filter function says so
			category_list = review.pop('category_list', [])
			filtered_category_list = [
				cs for cs in category_list
				if not category_score_filter(cs)]
			if filtered_category_list:
				review['category_list'] = filtered_category_list
		yield review
