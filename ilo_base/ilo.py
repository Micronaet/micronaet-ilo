# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


import os
import sys
import logging
import openerp
import hpilo
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID#, api
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class IloServer(orm.Model):
    """ Model name: IloServer
    """
    
    _name = 'ilo.server'
    _description = 'HP iLo Server'
    _order = 'name'

    def ilo_connect(self, cr, uid, ids, context=None):
        ''' Connect to server passed
        '''    
        assert len(ids) == 1, 'Works only with one record a time'
        server_proxy = self.browse(cr, uid, ids, context=context)[0]
        ilo = hpilo.Ilo(
            hostname=server_proxy.hostname, 
            login=server_proxy.username, 
            password=server_proxy.password, 
            timeout=server_proxy.timeout, 
            port=server_proxy.port,
            #protocol=None,
            #delayed=False, 
            #ssl_version=None
            )
        return ilo    

    def ilo_temperature_info(self, cr, uid, ids, context=None):
        ''' Environment temperature info
        '''
        #print ilo.get_fw_version()
        #print ilo.get_uid_status()
        #print ilo.get_embedded_health()
        import pdb; pdb.set_trace()
        ilo = self.ilo_connect(cr, uid, ids, context=context)
        temperature = ilo.get_embedded_health()['temperature']

        # Echo temperature check:
        
        status = temperature['01-Inlet Ambient']['status']
        degree = temperature['01-Inlet Ambient']['currentreading'][0]
        if status != 'OK': 
            raise osv.except_osv(
                _('Temperature error'), 
                _('Error temperature passed level: %s' % degree),
                )
        return True
        
    _columns = {
        'name': fields.char('Server description', size=64, required=True),
        'hostname': fields.char('Hostname', size=64, required=True),
        'port': fields.integer('Port', required=True),
        'timeout': fields.integer('Timeout', required=True),
        'username': fields.char('Username', size=64, required=True),
        'password': fields.char('Password', size=64, required=True),
        
        'info_temperature': fields.text('Info Temperature'),
        #protocol
        #delayed
        #ssl_version
        }
    
    _defaults = {
        'username': lambda *x: 'Administrator',
        'timeout': lambda *x: 120,
        'port': lambda *x: 443,
        }
