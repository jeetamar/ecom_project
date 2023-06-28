import requests
import json

# import checksum generation utility
# You can get this utility from https://developer.paytm.com/docs/checksum/
from paytmchecksum import PaytmChecksum

paytmParams = dict()

paytmParams["body"] = {
    "mid"           : "GOODEA80339035627893",
    "orderId"       : "OREDRID98663",
    "amount"        : "1323.00",
    "businessType"  : "UPI_QR_CODE",
    "posId"         : "S12_123"
}

# Generate checksum by parameters we have in body
# Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), "Izjmn#M5#BMlBX2L")

paytmParams["head"] = {
    "clientId"	        : "C11",
    "version"	        : "v1",
    "signature"         : checksum
}

post_data = json.dumps(paytmParams)

# for Staging
url = "https://securegw-stage.paytm.in/paymentservices/qr/create"

# for Production
# url = "https://securegw.paytm.in/paymentservices/qr/create"
response = requests.post(url, data = post_data, headers = {"Content-type": "application/json"}).json()
print(response)
# print(response['body']['resultInfo']['resultStatus'])
# print(response['body']['resultInfo']['resultMsg'])
# print(response['body']['resultInfo']['resultMsg'])
# print(response['body']['qrCodeId'])
# print(response['body']['qrData'])
# print(response['body']['image'])










# import requests
# import json
#
# # import checksum generation utility
# # You can get this utility from https://developer.paytm.com/docs/checksum/
# from paytmchecksum import PaytmChecksum
#
# paytmParams = dict()
#
# paytmParams["body"] = {
#     "mid"           : "GOODEA80339035627893",
#     "orderId"       : "OREDRID98767",
#     "amount"        : "1303.00",
#     "businessType"  : "UPI_QR_CODE",
#     "posId"         : "P004"
# }
#
# # Generate checksum by parameters we have in body
# # Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
# checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), "Izjmn#M5#BMlBX2L")
#
# paytmParams["head"] = {
#     "clientId"	        : "C11",
#     "version"	        : "v1",
#     "signature"         : checksum
# }
#
# post_data = json.dumps(paytmParams)
#
# # for Staging
# url = "https://securegw-stage.paytm.in/paymentservices/qr/create"
#
#
# # for Production
# # url = "https://securegw.paytm.in/paymentservices/qr/create"
# response = requests.post(url, data = post_data, headers = {"Content-type": "application/json"}).json()
# print(response)
#
