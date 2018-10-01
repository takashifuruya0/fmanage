from django.shortcuts import render

# Create your views here.
import requests
from datetime import date, datetime
from django.conf import settings


def dashboard(request):
    boardids = {
        "Private": "5a8c05d2a0ae077733249613",
        "Task": "5a8a19124ba2f6c961ff9393",
    }

    key = "b003b9b25dbd2f9bfe6420262ae9a1c8"
    token = "748c7d5622f3c04e4803ad49aa35c1d6be209203bdd532878f4919e06f38678a"
    params = {
        "key": key,
        "token": token,
    }

    output = dict()
    output["name"] = [bname for bname in boardids.keys()]
    output["today"] = date.today()
    tdata = dict()
    datalist = list()
    for bname, bid in boardids.items():
        url = "https://trello.com/1/lists/"
        url2 = "https://trello.com/1/boards/" + bid + "/lists"
        url3 = "https://trello.com/1/boards/" + bid + "/labels"

        # label
        r = requests.get(url3, params=params)
        listid = r.json()
        labels = [i["name"] for i in listid]
        resl = {i: 0 for i in labels}

        # lists
        r = requests.get(url2, params=params)
        listid = r.json()

        # cards
        res = dict()
        for i in range(listid.__len__()):
            r = requests.get(url + listid[i]["id"] + "/cards", params=params)
            data = r.json()
            res[listid[i]["name"]] = len(data)
            for d in data:
                print("======================")
                if d['due'] is not None:
                    s = d['due']
                    d['due'] = datetime(
                        int(s[0:4]),
                        int(s[5:7]),
                        int(s[8:10]),
                        int(s[11:13]),
                        int(s[14:16])
                    )
                datalist.append(d)
                for label in d["labels"]:
                    if label["name"] in labels:
                        resl[label["name"]] += 1
        tdata[bname] = {"status": res, "label": resl}
    output["data"] = tdata
    output["datalist"] = datalist

    return render(request, 'trello/dashboard.html', output)

# sample = {
#     'name': '滝口先生に結婚報告',
#     'idLabels': ['5a8c05d3aac09e0a92e3b3e5'],
#     'idShort': 24,
#     'dateLastActivity': '2018-09-13T05:29:02.929Z',
#     'badges': {
#         'comments': 0,
#         'description': True,
#         'attachments': 0,
#         'checkItems': 0,
#         'Complete': False,
#         'attachmentsByType': {
#             'trello': {'board': 0, 'card': 0}
#         },
#         'checkItemsChecked': 0,
#         'votes': 0,
#         'subscribed': False,
#         'due': None,
#         'fogbugz': '',
#         'viewingMemberVoted': False
#     },
#     'pos': 425984, 'dueComplete': False,
#     'idMembersVoted': [],
#     'idChecklists': [],
#     'shortUrl': 'https://trello.com/c/0PWBWmjI',
#     'due': None,
#     'id': '5a9806afd5618509ed3096e0',
#     'manualCoverAttachment': False,
#     'idAttachmentCover': None,
#     'idMembers': [],
#     'desc': 'estiman.taki@docomo.ne.jp\n変わってなければこれだと思う\nケータイだけど',
#     'labels': [],
#     'url': 'https://trello.com%9D%E5%8F%A3%E5%85%88%E7%94%9F%E3%81%AB%E7%B5%90%E5%A9%9A%E5%A0%B1%E5%91%8A',
#     'idBoard': '5a8c05d2a0ae077733249613',
#     'descData': {
#         'emoji': {}
#     },
#     'closed': False,
#     'subscribed': False,
#     'idList': '5a8c074085c5cfe1a6c5bcd9',
#     'shortLink': '0PWBWmjI',
#     'checkItemStates': None
# }
