# -*- coding: utf-8 -*-
import json
import os
import openprocurement.relocation.contracts.tests.base as base_test
from copy import deepcopy
from openprocurement.api.tests.base import (
    PrefixedRequestClass, test_tender_data, test_organization
)
from openprocurement.relocation.contracts.tests.base import OwnershipWebTest, test_transfer_data
from openprocurement.contracting.api.tests.base import test_contract_data, test_tender_token

from webtest import TestApp


class DumpsTestAppwebtest(TestApp):
    def do_request(self, req, status=None, expect_errors=None):
        req.headers.environ["HTTP_HOST"] = "api-sandbox.openprocurement.org"
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            self.file_obj.write(req.as_bytes(True))
            self.file_obj.write("\n")
            if req.body:
                try:
                    self.file_obj.write(
                            'DATA:\n' + json.dumps(json.loads(req.body), indent=2, ensure_ascii=False).encode('utf8'))
                    self.file_obj.write("\n")
                except:
                    pass
            self.file_obj.write("\n")
        resp = super(DumpsTestAppwebtest, self).do_request(req, status=status, expect_errors=expect_errors)
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            headers = [(n.title(), v)
                       for n, v in resp.headerlist
                       if n.lower() != 'content-length']
            headers.sort()
            self.file_obj.write(str('Response: %s\n%s\n') % (
                resp.status,
                str('\n').join([str('%s: %s') % (n, v) for n, v in headers]),
            ))

            if resp.testbody:
                try:
                    self.file_obj.write(json.dumps(json.loads(resp.testbody), indent=2, ensure_ascii=False).encode('utf8'))
                except:
                    pass
            self.file_obj.write("\n\n")
        return resp


class TransferDocsTest(OwnershipWebTest):

    def setUp(self):
        self.app = DumpsTestAppwebtest(
                "config:tests.ini", relative_to=os.path.dirname(base_test.__file__))
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = ('Basic', ('broker', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db

    def test_docs(self):
        data = deepcopy(test_tender_data)
        self.app.authorization = ('Basic', ('broker', ''))

        ########################
        # Contracting transfer #
        ########################

        data = deepcopy(test_contract_data)
        tender_token = data['tender_token']
        self.app.authorization = ('Basic', ('contracting', ''))

        response = self.app.post_json('/contracts', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.contract = response.json['data']
        self.assertEqual('broker', response.json['data']['owner'])
        self.contract_id = self.contract['id']

        self.app.authorization = ('Basic', ('broker', ''))
        with open('docs/source/tutorial/get-contract-transfer.http',
                  'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/contracts/{}/credentials?acc_token={}'.format(self.contract_id,
                                                                tender_token),
                {'data': ''})
            self.assertEqual(response.status, '200 OK')
            token = response.json['access']['token']
            self.contract_transfer = response.json['access']['transfer']

        self.app.authorization = ('Basic', ('broker3', ''))
        with open('docs/source/tutorial/create-contract-transfer.http',
                  'w') as self.app.file_obj:
            response = self.app.post_json('/transfers', {"data": test_transfer_data})
            self.assertEqual(response.status, '201 Created')
            transfer = response.json['data']
            self.assertIn('date', transfer)
            transfer_creation_date = transfer['date']
            new_access_token = response.json['access']['token']
            new_transfer_token = response.json['access']['transfer']

        with open('docs/source/tutorial/change-contract-ownership.http',
                  'w') as self.app.file_obj:
            response = self.app.post_json(
                '/contracts/{}/ownership'.format(self.contract_id),
                {"data": {"id": transfer['id'], 'transfer': self.contract_transfer}})
            self.assertEqual(response.status, '200 OK')
            self.assertNotIn('transfer', response.json['data'])
            self.assertNotIn('transfer_token', response.json['data'])
            self.assertEqual('broker3', response.json['data']['owner'])

        with open('docs/source/tutorial/modify-contract.http',
                  'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/contracts/{}?acc_token={}'.format(self.contract_id,
                                                    new_access_token),
                {"data": {"description": "broker3 now can change the contract"}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['description'],
                             'broker3 now can change the contract')

        with open('docs/source/tutorial/get-used-contract-transfer.http',
                  'w') as self.app.file_obj:
            response = self.app.get('/transfers/{}'.format(transfer['id']))

        # Create Transfer
        with open('docs/source/tutorial/create-contract-transfer-credentials.http',
                  'w') as self.app.file_obj:
            response = self.app.post_json('/transfers', {"data": {}})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            transfer = response.json['data']
            contract_token = response.json['access']['token']
            new_transfer_token = response.json['access']['transfer']

        # Getting access
        with open('docs/source/tutorial/change-contract-credentials.http',
                  'w') as self.app.file_obj:
            response = self.app.post_json(
                '/contracts/{}/ownership'.format(self.contract_id),
                {"data": {"id": transfer['id'], 'tender_token': test_tender_token}})
            self.assertEqual(response.status, '200 OK')
            self.assertNotIn('transfer', response.json['data'])
            self.assertNotIn('transfer_token', response.json['data'])
            self.assertEqual('broker3', response.json['data']['owner'])

        # Check Transfer is used
        with open('docs/source/tutorial/get-used-contract-credentials-transfer.http',
                  'w') as self.app.file_obj:
            response = self.app.get('/transfers/{}'.format(transfer['id']))

        # Modify contract with new credentials
        with open('docs/source/tutorial/modify-contract-credentials.http',
                  'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/contracts/{}?acc_token={}'.format(self.contract_id, contract_token),
                {"data": {"description": "new credentials works"}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['description'],
                             'new credentials works')

