# -*- charset: utf8 -*-

import json

from helpers import *

class Member(object):
    pass

class Visitor(object):
    pass

class AuthExpired(object):
    pass

class Storage(object):
    """docstring for Storage"""
    def __init__(self, storage_path):
        super(Storage, self).__init__()
        self.storage_path = storage_path
        self.storage_obj  = readJSONFile(self.storage_path)

    def add(self, data):
        if isinstance(data, dict):
            if not self.getRecordByMobile(data['user-mobile']):
                self.storage_obj.append(data)
                return True
            else:
                return False

    def rm(self, mobile_no):
        for idx in range(len(self.storage_obj)):
            if mobile_no == self.storage_obj[idx]['user-mobile']:
                return self.storage_obj.pop(idx)
        return None

    def disable(self, mobile_id):
        return self.addFieldForRecord(mobile_id, 'disabled', True)

    def enable(self, mobile_id):
        return self.addFieldForRecord(mobile_id, 'disabled', False)


    def addFieldForRecord(self, mobile_id, field, value):
        for idx in range(len(self.storage_obj)):
            if mobile_id == self.storage_obj[idx]['user-mobile']:
                self.storage_obj[idx][field] = value
                self.save()
                return True
        return False

    def addAndSave(self, data):
        if self.add(data):
            self.save()
            return True
        return False

    def save(self):
        writeJSONFile(self.storage_path, self.storage_obj)

    def dump(self):
        return json.dumps(self.storage_obj)

    def getObject(self):
        return self.storage_obj

    def getRecordByMobile(self, q):
        for usr_rec in self.storage_obj:
            q = q.replace('-','')
            usr_mobile = usr_rec['user-mobile'].replace('-','')
            if usr_mobile == q:
                return usr_rec
        return None

    def lookup_visitor(self, q):
        for usr_rec in self.storage_obj:
            q = q.replace('-','')
            usr_mobile = usr_rec['user-mobile'].replace('-','')
            print ">> lookup_visitor", " :: ".join([usr_mobile, q])
            if usr_mobile == q:
                if usr_rec['user-rfid']:
                    return Member()
                if 'disabled' in usr_rec.keys() and usr_rec['disabled']:
                    print ">> disabled"
                    return AuthExpired()
                return usr_rec
        return None

    def lookup_members(self, q):
        for usr_rec in self.storage_obj:
            if usr_rec['user-rfid']:
                if usr_rec['user-rfid'] == q:
                    if 'disabled' in usr_rec.keys() and usr_rec['disabled']:
                        return AuthExpired()
                    return usr_rec
        return None






