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
        saved_form = s.find('form', id='form1')
        saved_form.extract()

        # 
        # 1 - POST to get select options for <select name=ddlEntidadEspecialidad>
        # 2 - Replace <table class="contenedor"> with table in AJAX response
        # 3 - Select option for <select name=ddlEntidadEspecialidad>
        # 4 - Enter filing number
        # 5 - Click button btnConsultarNum
        # 6 - Replace <div id="divActuaciones"> with div in AJAX response

        # 1
        self.br.select_form(predicate=select_form)
        self.br.form.new_control('hidden', '__EVENTTARGET',   {'value': ''})
        self.br.form.new_control('hidden', '__EVENTARGUMENT', {'value': ''})
        self.br.form.new_control('hidden', '__ASYNCPOST',     {'value': 'true'})
        self.br.form.new_control('hidden', 'managerScript',   {'value': ''})
        self.br.form.fixup()

        self.br.form.set_all_readonly(False)
        self.br.form['ddlCiudad'] = ['11001'] # Bogata, D.C.
        self.br.form['managerScript'] = 'upPanelCiudad|ddlCiudad' # div#id value followed by select control name
        self.br.submit()

        # 2
        d = saved_form.find('div', id='upPanelCiudad')
        r = self.br.response().read()

        it = iter(r.split('|'))
        kv = dict(zip(it, it))

        import pprint 
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(kv)

        new_table = BeautifulSoup(kv['upPanelCiudad'])
        old_table = d.table
        old_table.replace_with(new_table)

        html = saved_form.encode('utf8')
        resp = mechanize.make_response(html, [("Content-Type", "text/html")],
                                       self.br.geturl(), 200, "OK")

        self.br.set_response(resp)
        self.br.select_form(predicate=select_form)
        self.br.form.new_control('hidden', '__ASYNCPOST',     {'value': 'true'})
        self.br.form.new_control('hidden', 'managerScript',   {'value': ''})
        self.br.form.set_all_readonly(False)

        self.br.form['__VIEWSTATE'] = kv['__VIEWSTATE'] # update viewstate
        self.br.form['managerScript'] = 'managerScript|btnConsultarNum' 

        # 3
        ctl = self.br.form.find_control('ddlEntidadEspecialidad')
        ctl.get(label='JUZGADOS CIVILES DEL CIRCUITO DE BOGOTA').selected = True

        self.br.form['rblConsulta'] = ['1']
        def select_control(ctl):
            return ctl.attrs['maxlength'] == '23'

        # tqsurrp4n5dcbu2dtnnzjkur
        ctl = self.br.form.find_control(predicate=select_control)
        self.br.form[ctl.name] = '11001310300220140043000'

        self.br.submit(name='btnConsultarNum')

        print 'scraping...'

if __name__ == '__main__':
    scraper = Scraper()
    scraper.scrape()
