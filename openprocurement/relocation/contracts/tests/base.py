# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from openprocurement.relocation.core.tests.base import BaseWebTest
from datetime import datetime, timedelta
from openprocurement.api.utils import apply_data_patch

test_transfer_data = {}
now = datetime.now()


class OwnershipWebTest(BaseWebTest):

    def setUp(self):
        super(OwnershipWebTest, self).setUp()
        self.create_tender()

    def create_tender(self):
        data = deepcopy(self.initial_data)
        response = self.app.post_json('/tenders', {'data': data})
        tender = response.json['data']
        self.tender_token = response.json['access']['token']
        self.tender_transfer = response.json['access']['transfer']
        self.tender_id = tender['id']

    def set_tendering_status(self):
        data = {
            "status": "active.tendering",
            "enquiryPeriod": {
                "startDate": (now - timedelta(days=10)).isoformat(),
                "endDate": (now).isoformat()
            },
            "tenderPeriod": {
                "startDate": (now).isoformat(),
                "endDate": (now + timedelta(days=7)).isoformat()
            }
        }

        tender = self.db.get(self.tender_id)
        tender.update(apply_data_patch(tender, data))
        self.db.save(tender)

    def set_qualification_status(self):
        data = {
            "status": 'active.qualification',
            "enquiryPeriod": {
                "startDate": (now - timedelta(days=18)).isoformat(),
                "endDate": (now - timedelta(days=8)).isoformat()
            },
            "tenderPeriod": {
                "startDate": (now - timedelta(days=8)).isoformat(),
                "endDate": (now - timedelta(days=1)).isoformat()
            },
            "auctionPeriod": {
                "startDate": (now - timedelta(days=1)).isoformat(),
                "endDate": (now).isoformat()
            },
            "awardPeriod": {
                "startDate": (now).isoformat()
            }
        }

        tender = self.db.get(self.tender_id)
        tender.update(apply_data_patch(tender, data))
        self.db.save(tender)


class ContractOwnershipWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)

    def setUp(self):
        super(ContractOwnershipWebTest, self).setUp()
        self.create_contract()

    def create_contract(self):
        data = deepcopy(self.initial_data)

        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('contracting', ''))
        response = self.app.post_json('/contracts', {'data': data})
        self.contract = response.json['data']
        # self.contract_token = response.json['access']['token']
        self.contract_id = self.contract['id']
        self.app.authorization = orig_auth
