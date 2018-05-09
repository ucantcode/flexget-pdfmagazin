from __future__ import unicode_literals, division, absolute_import
from builtins import *  # noqa pylint: disable=unused-import, redefined-builtin

import logging
import re

from flexget import plugin
from flexget.event import event
from flexget.plugins.internal.urlrewriting import UrlRewritingError
from flexget.utils.soup import get_soup
from flexget.utils.search import normalize_unicode

from requests.exceptions import RequestException

log = logging.getLogger('rlsbb')


class UrlRewriteRlsbb(object):
    """
    pdfmagazin urlrewriter
    Version 0.1
    Configuration
    pdfmagazin:
      filehosters_re:
        - novafile\.com/*
      parse: yes
    filehosters_re: Only add links that match any of the regular expressions 
      listed under filehosters_re.
    For example, to use jdownloader 2 as output, you would use the exec plugin:
    exec:
      - echo "text={{urls}}" >> "/path/to/jd2/folderwatch/{{title}}.crawljob"
    """

    schema = {
        'type': 'object',
        'properties': {
            'filehosters_re': {'type': 'array', 'items': {'format': 'regexp'}, 'default': []},
            'parse': {'type': 'boolean', 'default': False}
        },
        'additionalProperties': False
    }

    # Since the urlrewriter relies on a config, we need to create a default one
    config = {
        'filehosters_re': [],
        'parse': False
    }

    # grab config
    def on_task_start(self, task, config):
        self.config = config

    # urlrewriter API
    def url_rewritable(self, task, entry):
        url = entry['url']
        rewritable_regex = '^https?:\/\/(www.)?pdfmagaz\.in\/.*'
        return re.match(rewritable_regex, url) is not None

    def _get_soup(self, task, url):
        try:
            page = task.requests.get(url)
        except RequestException as e:
            raise UrlRewritingError(str(e))
        try:
            return get_soup(page.text)
        except Exception as e:
            raise UrlRewritingError(str(e))

    @plugin.internet(log)
    # urlrewriter API
    def url_rewrite(self, task, entry):
        soup = self._get_soup(task, entry['url'])
   
        # grab link from filehosters_re
        link_elements = []
        log.debug('Searching %s for a tags where the text matches one of: %s', entry['url'], str(self.config.get('filehosters_re')))  
        regexps = self.config.get('filehosters_re', [])
        if self.config.get('parse'):
            link_elements = soup.find_all('div', class_=re.compile("mag_details"))
            log.debug('filehosters_re parsing enabled: found %d filehosters_re.', len(link_elements))
        log.debug('Original urls: %s', str(entry['urls']))
        if 'urls' in entry:
            urls = list(entry['urls'])
            log.debug('Original urls: %s', str(entry['urls']))
        else:
            urls = []
        log.debug('link_elements parsing enabled: found %d link_elements.', len(link_elements))
        if link_elements and not regexps:
            log.warn('There are not in filehosters_re.')
        for target in link_elements:
            links = target.find_all('a')
            for link in links:
                if re.search('novafile.com', link['href']):
                    urls.append(link['href'])

        # filter urls:
        filtered_urls = []
        for i, url in enumerate(urls):
            urls[i] = normalize_unicode(url)
            for regexp in regexps:
                if re.search(regexp, urls[i]):
                    filtered_urls.append(urls[i])
                    log.debug('Url: "%s" matched filehoster filter: %s', urls[i], regexp)
                    break
            else:
                if regexps:
                    log.debug(
                        'Url: "%s" was discarded because it does not match any of the given filehoster filters: %s', urls[i], str(regexps))
        if regexps:
            log.debug('Using filehosters_re filters: %s', str(regexps))
            urls = filtered_urls
        else:
            log.debug('No filehoster filters configured, using all found links.')
        num_links = len(urls)
        log.verbose('Found %d links at %s.', num_links, entry['url'])
        if num_links:
            entry['urls'] = urls
            entry['url'] = urls[0]
        else:
            raise UrlRewritingError('No useable links found at %s' % entry['url'])


@event('plugin.register')
def register_plugin():
    plugin.register(UrlRewriteRlsbb, 'pdfmagazin', interfaces=['urlrewriter', 'task'], api_ver=2)
