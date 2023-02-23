# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import cgi
import http.server
import socketserver
import json
import uuid
from datetime import datetime


def uuidMaker():
    return uuid.uuid4().hex


def uuidMakerWithMinus():
    return str(uuid.uuid4())


def xxcheckDBCustId(idcustomer):
    f = open('DB.JSON')
    data = json.load(f)
    for i in data['customer']:
        if i['customer_xid'].strip() == idcustomer.strip():
            resp = i['token']
            return resp

    # create user
    tokenUUID = uuidMaker()
    ownerUUID = uuidMakerWithMinus()
    datanew = {
        'customer_xid': idcustomer,
        "owned_by": uuidMakerWithMinus(),
        'token': tokenUUID,
        'a1': 'asdasd',
        "status": "",
        "enabled_at": "",
        "balance": "0"
    }
    data['customer'].append(datanew)
    print(json.dumps(data['customer'], indent=2))
    with open('DB.JSON', 'w') as f:
        # Write new data to the file
        f.write(json.dumps(data, indent=2))
        f.close

    return tokenUUID


def xprocessInit_POST(data):
    form = cgi.FieldStorage(
        fp=data.rfile,
        headers=data.headers,
        environ={
            'REQUEST_METHOD': 'POST',
        }
    )
    custid = form.getfirst('customer_xid').strip()
    Token = xxcheckDBCustId(custid)

    response = {"data": {"token": Token}, "status": "success"}

    return response


def todayTime():
    return datetime.today().strftime('%Y-%m-%d %H:%M:%S')


def xxenableCustid(auth):
    # normalize the auth
    authNorm = auth.lower().replace('token', '').strip()
    f = open('DB.JSON')
    data = json.load(f)
    for i in data['customer']:
        if i['token'].strip() == authNorm.strip():
            if i['status'] == 'enabled':
                return ""
            else:
                i['status'] = 'enabled'
                i['enabled_at'] = todayTime()

                with open('DB.JSON', 'w') as f:
                    # Write new data to the file
                    f.write(json.dumps(data, indent=2))
                    f.close

                return {
                    'customer_xid': i['customer_xid'],
                    'status': i['status'],
                    'enabled_at': i['enabled_at'],
                    'owned_by': i['owned_by'],
                    'balance': i['balance']

                }
    return ""


def xprocessEnable_POST(auth):
    res = xxenableCustid(auth)
    if res != "":
        response = {
            "status": "success",
            "data": {
                "wallet": {
                    "id": res['customer_xid'],
                    "owned_by": res['owned_by'],
                    "status": res['status'],
                    "enabled_at": res['enabled_at'],
                    "balance": res['balance']
                }
            }
        }
    else:
        response = {
            "status": "fail",
            "data": {
                "error": "Wallet already enabled"
            }
        }
    return response
    pass


def xxCheckbalance(authorization):
    # normalize the auth
    authNorm = authorization.lower().replace('token', '').strip()
    f = open('DB.JSON')
    data = json.load(f)
    for i in data['customer']:
        if i['token'].strip() == authNorm.strip():
            if i['status'] == 'enabled':
                return {
                    'customer_xid': i['customer_xid'],
                    'status': i['status'],
                    'enabled_at': i['enabled_at'],
                    'owned_by': i['owned_by'],
                    'balance': i['balance']

                }

    return ""


def xProcessCheckBalance_GET(authorization):
    res = xxCheckbalance(authorization)

    if res != "":
        response = {
            "status": "success",
            "data": {
                "wallet": {
                    "id": res['customer_xid'],
                    "owned_by": res['owned_by'],
                    "status": res['status'],
                    "enabled_at": res['enabled_at'],
                    "balance": res['balance']
                }
            }
        }
    else:
        response = {
            "status": "fail",
            "data": {
                "error": "Wallet disabled"
            }
        }
    return response
    pass


def xxAddBalance(auth, amount):
    authNorm = auth.lower().replace('token', '').strip()
    f = open('DB.JSON')
    data = json.load(f)
    for i in data['customer']:
        if i['token'].strip() == authNorm.strip():
            i['balance'] = str(int(i['balance']) + int(amount))

            with open('DB.JSON', 'w') as f:
                f.write(json.dumps(data, indent=2))
                f.close

            return


def xxWriteToDeposits(newDeposit):
    with open('DB.JSON') as f:
        data = json.load(f)
        data['deposits'].append(newDeposit)

    with open('DB.JSON', 'w') as f:
        f.write(json.dumps(data, indent=2))
        f.close


def xprocessAddDeposit_POST(data, auth):
    form = cgi.FieldStorage(
        fp=data.rfile,
        headers=data.headers,
        environ={
            'REQUEST_METHOD': 'POST',
        }
    )
    res = xxCheckbalance(auth)
    if res == "":
        return {
            "status": "fail",
            "data": {
                "error": "Wallet disabled"
            }
        }

    owner = res['owned_by']
    amount = form.getfirst('amount').strip()
    reffid = form.getfirst('reference_id').strip()

    xxAddBalance(auth, amount)

    response = {
        "status": "success",
        "data": {
            "deposit": {
                "id": uuidMakerWithMinus(),
                "deposited_by": owner,
                "status": "success",
                "deposited_at": todayTime(),
                "amount": amount,
                "reference_id": reffid
            }
        }
    }
    xxWriteToDeposits(response['data']['deposit'])
    return response


def xxReduceBalance(auth, amount_toWithdraw):
    authNorm = auth.lower().replace('token', '').strip()
    f = open('DB.JSON')
    data = json.load(f)
    for i in data['customer']:
        if i['token'].strip() == authNorm.strip():
            i['balance'] = str(int(i['balance']) - int(amount_toWithdraw))

            with open('DB.JSON', 'w') as f:
                f.write(json.dumps(data, indent=2))
                f.close

            return


def xxWriteToWithdrawals(newwithdrawal):
    with open('DB.JSON') as f:
        data = json.load(f)
        data['withdrawals'].append(newwithdrawal)

    with open('DB.JSON', 'w') as f:
        f.write(json.dumps(data, indent=2))
        f.close


def xprocessAddWithdrawal_POST(data, authorization):
    form = cgi.FieldStorage(
        fp=data.rfile,
        headers=data.headers,
        environ={
            'REQUEST_METHOD': 'POST',
        }
    )
    res = xxCheckbalance(authorization)
    if res == "":
        return {
            "status": "fail",
            "data": {
                "error": "Wallet disabled"
            }
        }

    owner = res['owned_by']
    amount_current = res['balance']
    amount_toWithdraw = form.getfirst('amount').strip()
    reffid = form.getfirst('reference_id').strip()

    if int(amount_current) < int(amount_toWithdraw):
        return {
            "status": "fail",
            "data": {
                "error": "Balance Not Enough"
            }
        }

    xxReduceBalance(authorization, amount_toWithdraw)

    response = {
        "status": "success",
        "data": {
            "withdrawal": {
                "id": uuidMakerWithMinus(),
                "withdrawn_by": owner,
                "status": "success",
                "withdrawn_at": todayTime(),
                "amount": amount_toWithdraw,
                "reference_id": reffid
            }
        }
    }
    xxWriteToWithdrawals(response['data']['withdrawal'])
    return response


def xxWriteToDisableAcc(auth):
    authNorm = auth.lower().replace('token', '').strip()
    f = open('DB.JSON')
    data = json.load(f)
    for i in data['customer']:
        if i['token'].strip() == authNorm.strip():
            i['status'] = "disabled"

            with open('DB.JSON', 'w') as f:
                f.write(json.dumps(data, indent=2))
                f.close

            return


def xProcessDisableACC_PATCH(auth):
    # normalize the auth

    authNorm = auth.lower().replace('token', '').strip()
    f = open('DB.JSON')
    data = json.load(f)
    for i in data['customer']:
        if i['token'].strip() == authNorm.strip():
            if i['status'] == 'enabled':
                xxWriteToDisableAcc(auth)
                return {
                    "status": "success",
                    "data": {
                        "wallet": {
                            "id": uuidMakerWithMinus(),
                            "owned_by": i['owned_by'],
                            "status": "disabled",
                            "disabled_at": todayTime(),
                            "balance": i['balance']
                        }
                    }
                }
            if i['status'] == 'disabled':
                return {
                    "status": "fail",
                    "data": {
                        "error": "already disabled"
                    }
                }

    return {
        "status": "fail",
        "data": {
            "error": "user not found"
        }
    }

    pass


def xProcessSeeAllTrx_GET(authorization):
    alltrx = {'withdrawals': [], 'deposits': []}
    # normalize the auth
    authNorm = authorization.lower().replace('token', '').strip()
    f = open('DB.JSON')
    data = json.load(f)
    for i in data['customer']:
        if i['token'].strip() == authNorm.strip():
            ownerid = i['owned_by']

    for i in data['withdrawals']:
        if i['withdrawn_by'] == ownerid:
            alltrx['withdrawals'].append(i)

    for i in data['deposits']:
        if i['deposited_by'] == ownerid:
            alltrx['deposits'].append(i)

    if (alltrx['withdrawals'] == "") and (alltrx['deposits'] == ""):
        return {
            'status': 'fail',
            'data': {
                'error': 'No Transaction'
            }
        }

    return alltrx

class RequestHandler(http.server.BaseHTTPRequestHandler):

    def do_PATCH(self):
        if self.path.replace("%0A", "") == '/api/v1/wallet':
            print("disabling acc")
            authorization = self.headers.get('Authorization')
            response = xProcessDisableACC_PATCH(authorization)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            return

    def do_GET(self):
        if self.path.replace("%0A", "") == '/api/v1/wallet':
            print("enable wallet")
            authorization = self.headers.get('Authorization')
            response = xProcessCheckBalance_GET(authorization)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            return

        if self.path.replace("%0A", "") == '/api/v1/wallet/transactions':
            print("see all trx")
            authorization = self.headers.get('Authorization')
            response = xProcessSeeAllTrx_GET(authorization)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            return

        else:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'fail', 'data': {'message': 'check url!'}}
            self.wfile.write(json.dumps(response).encode())
            return

    def do_POST(self):
        x = self.path.strip()
        if self.path.replace("%0A", "") == '/api/v1/init':
            print("init create user")
            response = xprocessInit_POST(self)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            return

        if self.path.replace("%0A", "") == '/api/v1/wallet':
            print("enable wallet")
            authorization = self.headers.get('Authorization')
            response = xprocessEnable_POST(authorization)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        if self.path.replace("%0A", "") == '/api/v1/wallet/deposits':
            print("add deposit")
            authorization = self.headers.get('Authorization')
            response = xprocessAddDeposit_POST(self, authorization)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        if self.path.replace("%0A", "") == '/api/v1/wallet/withdrawals':
            print("add withdrawals")
            authorization = self.headers.get('Authorization')
            response = xprocessAddWithdrawal_POST(self, authorization)
            xxx = json.dumps(response)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())


def createServer():
    PORT = 8989
    Handler = RequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()


if __name__ == '__main__':
    createServer()
    # xxcheckDBCustId("ASDasdads")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
