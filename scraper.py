#!/usr/bin/env python                                                                                                                                                                
"""
Python script for scraping http://procesos.ramajudicial.gov.co/consultaprocesos/
"""

__author__ = 'Todd Hayton'

import re
import mechanize

from bs4 import BeautifulSoup, Comment, Tag

URL = 'http://procesos.ramajudicial.gov.co/consultaprocesos/'

class Scraper(object):
    def __init__(self):
        self.br = mechanize.Browser()
        self.br.addheaders = [('User-agent', 
                               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7'),
                              ('X-Requested-With', 'XMLHttpRequest'),
                              ('X-MicrosoftAjax',  'Delta=true')]
        self.url = URL

    def scrape(self):
        def select_form(form):
            return form.attrs.get('id', None) == 'form1'

        self.br.open(self.url)

        s = BeautifulSoup(self.br.response().read())
        saved_form = s.find('form', id='form1').prettify()
        
        self.br.select_form(predicate=select_form)
        self.br.form.new_control('hidden', '__EVENTTARGET',   {'value': ''})
        self.br.form.new_control('hidden', '__EVENTARGUMENT', {'value': ''})
        self.br.form.new_control('hidden', '__ASYNCPOST',     {'value': 'true'})
        self.br.form.new_control('hidden', 'managerScript',   {'value': ''})
        self.br.form.fixup()

        self.br.form.set_all_readonly(False)
        self.br.form['ddlCiudad'] = ['11001']
        self.br.form['managerScript'] = 'upPanelCiudad|ddlCiudad' # div#id value followed by select control name
        self.br.submit()

        # Extract old div and insert new one from ajax response
        d = saved_form.find('div', id='upPanelCiudad')
        s = BeautifulSoup(self.br.response().read())

        r = re.compile(r'VIEWSTATE\|([^|]+)')
        m = re.search(r, str(s))
        view_state = m.group(1)

        r = re.compile(r'upPanelCiudad\|([^|]+)')
        m = re.search(r, str(s))
        new_div = m.group(1)


        html = saved_form.encode('utf8')
        resp = mechanize.make_response(html, [("Content-Type", "text/html")],
                                       self.br.geturl(), 200, "OK")
        self.br.set_response(resp)
        self.br.select_form(predicate=select_form)
        
        print 'scraping...'

if __name__ == '__main__':
    scraper = Scraper()
    scraper.scrape()
