from lancers.functions import mylib_selenium
from lancers.models import Client, Opportunity, Category, OpportunityWork
from django.contrib.auth import get_user_model
import requests
from datetime import datetime
from pprint import pprint


def create_opportunity(opportunity_id):
    u = get_user_model().objects.get(pk=1)
    try:
        d = mylib_selenium.Lancers()
        res = d.get_opportunity(opportunity_id)
    except Exception as e:
        print(e)
    finally:
        d.close()
    res.pop("opportunity_url")
    res.pop("client_url")
    if Client.objects.filter(client_id=res['client_id']).exists():
        c = Client.objects.get(client_id=res.pop('client_id'))
        res.pop('client_name')
    else:
        c = Client()
        c.name = res.pop('client_name')
        c.client_id = res.pop('client_id')
        c.save_from_shell(u)
    o = Opportunity(**res)
    o.client = c
    o.status = "提案中"
    o.save_from_shell(u)
    return o


def create_proposal(proposal_id):
    u = get_user_model().objects.get(pk=1)
    try:
        d = mylib_selenium.Lancers()
        res = d.get_proposal(proposal_id)
    except Exception as e:
        print(e)
    finally:
        d.close()
    res.pop("opportunity_url")
    res.pop("client_url")
    if Client.objects.filter(client_id=res['client_id']).exists():
        c = Client.objects.get(client_id=res.pop('client_id'))
        res.pop('client_name')
    else:
        c = Client()
        c.name = res.pop('client_name')
        c.client_id = res.pop('client_id')
        c.save_from_shell(u)
    o = Opportunity(**res)
    o.client = c
    o.status = "提案中"
    o.type = "提案受注"
    o.save_from_shell(u)
    return o


def create_direct_opportunity(direct_opportunity_id):
    u = get_user_model().objects.get(pk=1)
    try:
        d = mylib_selenium.Lancers()
        res = d.get_direct_opportunity(direct_opportunity_id)
    except Exception as e:
        print(e)
    finally:
        d.close()
    res.pop("opportunity_url")
    res.pop("client_url")
    if Client.objects.filter(client_id=res['client_id']).exists():
        c = Client.objects.get(client_id=res.pop('client_id'))
        res.pop('client_name')
    else:
        c = Client()
        c.name = res.pop('client_name')
        c.client_id = res.pop('client_id')
        c.save_from_shell(u)
    o = Opportunity(**res)
    o.client = c
    o.status = "提案中"
    o.type = "直接受注"
    o.save_from_shell(u)
    return o


def test3(is_direct=True, is_proposal=True):
    url = "https://script.google.com/macros/s/AKfycbz_SWwkiNpdnWHUOx_WF1i1kRZYu0I-gKo5N_-1wuzHH1yjm2tS/exec"
    r = requests.get(url)
    data = r.json()['data']
    di = {
        "直接受注": [],
        "提案受注": [],
        "else": [],
    }
    for d in data:
        text_splited = d[3].split("/")
        if text_splited.__len__() > 3:
            if text_splited[-2] == "proposal" and is_proposal:
                di["提案受注"].append(
                    {
                        "id": text_splited[-1],
                        "status": d[4],
                        "category": d[5],
                        "working_time": d[13],
                        "is_working": d[15],
                        "memo": d[21],
                        "val": d[9],
                        "add": d[16],
                        "date_proposal": d[1],
                    }
                )
            elif text_splited[-2] == "work_offer" and is_direct:
                di["直接受注"].append(
                    {
                        "id": text_splited[-1],
                        "status": d[4],
                        "category": d[5],
                        "working_time": d[13],
                        "is_working": d[15],
                        "memo": d[21],
                        "val": d[9],
                        "add": d[16],
                        "date_proposal": d[1],
                    }
                )
        else:
            di["else"].append(
                {
                    "id": None,
                    "status": d[4],
                    "category": d[5],
                    "working_time": d[13],
                    "is_working": d[15],
                    "memo": d[21],
                    "date_proposal": d[1],
                    "date_open": d[10],
                    "date_close": d[11],
                    "name": d[2],
                    "val_payment": d[8],
                    "val": d[9],
                    "add": d[16],
                    "date_proposal": d[1],
                }
            )
    pprint(di)
    #
    u = get_user_model().objects.get(pk=1)
    d = mylib_selenium.Lancers()
    errors = 0
    done = 0
    for i in di['直接受注']:
        if Category.objects.filter(name=i['category']).count() == 1:
            category = Category.objects.get(name=i['category'])
        else:
            category = Category(name=i['category'])
            category.save_from_shell(u)
        direct_opportunity_id = i['id']
        print(direct_opportunity_id)
        try:
            res = d.get_direct_opportunity(direct_opportunity_id)
            res.pop("client_url")
            if Client.objects.filter(client_id=res['client_id']).exists():
                c = Client.objects.get(client_id=res.pop('client_id'))
                res.pop('client_name')
            else:
                c = Client()
                c.name = res.pop('client_name')
                c.client_id = res.pop('client_id')
                c.save_from_shell(u)
            o = Opportunity(**res)
            o.client = c
            if i["status"] == "選定" and i['is_working']:
                o.status = "選定/作業中"
            elif i["status"] == "選定" and not i['is_working']:
                o.status = "選定/終了"
            else:
                o.status = i["status"]
            o.type = "直接受注"
            o.category = category
            o.sub_categories.add(category)
            o.memo = i["memo"]
            o.save_from_shell(u)
            # working_time
            if i["working_time"]:
                ow = OpportunityWork()
                ow.opportunity = o
                ow.working_time = i["working_time"] * 60
                ow.save_from_shell(u)
            done += 1
        except Exception as e:
            print(e)
            errors += 1
    for i in di['提案受注']:
        if Category.objects.filter(name=i['category']).count() == 1:
            category = Category.objects.get(name=i['category'])
        else:
            category = Category(name=i['category'])
            category.save_from_shell(u)
        proposal_id = i['id']
        print(proposal_id)
        try:
            res = d.get_proposal(proposal_id)
            res.pop("opportunity_url")
            res.pop("client_url")
            if Client.objects.filter(client_id=res['client_id']).exists():
                c = Client.objects.get(client_id=res.pop('client_id'))
                res.pop('client_name')
            else:
                c = Client()
                c.name = res.pop('client_name')
                c.client_id = res.pop('client_id')
                c.save_from_shell(u)
            o = Opportunity(**res)
            o.client = c
            if i["status"] == "選定" and i['is_working']:
                o.status = "選定/作業中"
            elif i["status"] == "選定" and not i['is_working']:
                o.status = "選定/終了"
            else:
                o.status = i["status"]
            o.type = "提案受注"
            o.category = category
            o.sub_categories.add(category)
            o.memo = i["memo"]
            o.save_from_shell(u)
            # working_time
            if i["working_time"]:
                ow = OpportunityWork()
                ow.opportunity = o
                ow.working_time = i["working_time"] * 60
                ow.save_from_shell(u)
            done += 1
        except Exception as e:
            print(e)
            errors += 1

    # for i in di['else']:
    #     if Category.objects.filter(name=i['category']).count() == 1:
    #         category = Category.objects.get(name=i['category'])
    #     else:
    #         category = Category(name=i['category'])
    #         category.save_from_shell(u)
    #     o = Opportunity()
    #     o.val = i['val']
    #     o.val_payment = i['val_payment']
    #     if i["status"] == "選定" and i['is_working']:
    #         o.status = "選定/作業中"
    #     elif i["status"] == "選定" and not i['is_working']:
    #         o.status = "選定/終了"
    #     else:
    #         o.status = i["status"]
    #     o.type = "直接受注"
    #     o.category = category
    #     o.sub_categories.add(category)
    #     o.memo = i["memo"]
    #     o.date_proposal = datetime.strptime(i['date_proposal'], "%Y-%m-%dT%H:%M").date()
    #     o.datetime_close_opportunity = datetime.strptime(i['date_close'], "%Y-%m-%dT%H:%M")
    #     o.datetime_open_opportunity = datetime.strptime(i['date_open'], "%Y-%m-%dT%H:%M")
    #     o.save_from_shell(u)
    #     # working_time
    #     if i["working_time"]:
    #         ow = OpportunityWork()
    #         ow.opportunity = o
    #         ow.working_time = i["working_time"] * 60
    #         ow.save_from_shell(u)

    d.close()
    return [done, errors, di]


def test4(is_direct=True, is_proposal=True):
    url = "https://script.google.com/macros/s/AKfycbz_SWwkiNpdnWHUOx_WF1i1kRZYu0I-gKo5N_-1wuzHH1yjm2tS/exec"
    r = requests.get(url)
    data = r.json()['data']
    di = {
        "直接受注": [],
        "提案受注": [],
        "else": [],
    }
    for d in data:
        text_splited = d[3].split("/")
        if text_splited.__len__() > 3:
            if text_splited[-2] == "proposal" and is_proposal:
                target = "提案受注"
            elif text_splited[-2] == "work_offer" and is_direct:
                target = "直接受注"
            di[target].append(
                {
                    "id": text_splited[-1],
                    "status": d[4],
                    "category": d[5],
                    "working_time": d[13],
                    "is_working": d[15],
                    "memo": d[21],
                    "date_open": d[10],
                    "date_close": d[11],
                    "val_payment": d[8],
                    "val": d[9],
                    "add": d[16],
                    "date_proposal": d[1],
                }
            )
        else:
            di["else"].append(
                {
                    "id": None,
                    "status": d[4],
                    "category": d[5],
                    "working_time": d[13],
                    "is_working": d[15],
                    "memo": d[21],
                    "date_proposal": d[1],
                    "date_open": d[10],
                    "date_close": d[11],
                    "name": d[2],
                    "val_payment": d[8],
                    "val": d[9],
                    "add": d[16],
                    "date_proposal": d[1],
                }
            )
    pprint(di)
    #
    u = get_user_model().objects.get(pk=1)
    d = mylib_selenium.Lancers()
    errors = 0
    done = 0
    for i in di['直接受注']:
        if Category.objects.filter(name=i['category']).count() == 1:
            category = Category.objects.get(name=i['category'])
        else:
            category = Category(name=i['category'])
            category.save_from_shell(u)
        direct_opportunity_id = i['id']
        print(direct_opportunity_id)
        try:
            res = d.get_direct_opportunity(direct_opportunity_id)
            res.pop("client_url")
            if Client.objects.filter(client_id=res['client_id']).exists():
                c = Client.objects.get(client_id=res.pop('client_id'))
                res.pop('client_name')
            else:
                c = Client()
                c.name = res.pop('client_name')
                c.client_id = res.pop('client_id')
                c.save_from_shell(u)
            o = Opportunity(**res)
            o.client = c
            o.date_open = datetime.strptime(i['date_proposal'][0:15], "%Y-%m-%dT%H:%M").date()
            o.date_close = datetime.strptime(i['date_close'][0:15], "%Y-%m-%dT%H:%M").date()
            if i["status"] == "選定" and i['is_working']:
                o.status = "選定/作業中"
            elif i["status"] == "選定" and not i['is_working']:
                o.status = "選定/終了"
            else:
                o.status = i["status"]
            o.type = "直接受注"
            o.category = category
            o.memo = i["memo"]
            o.save_from_shell(u)
            # sub category
            o.sub_categories.add(category)
            o.save_from_shell(u)
            # working_time
            if i["working_time"]:
                ow = OpportunityWork()
                ow.opportunity = o
                ow.working_time = i["working_time"] * 60
                ow.save_from_shell(u)
            done += 1
            # related_opportunity
            if i['add'] > 0:
                ro = Opportunity(
                    name="【追加受注】{}".format(o.name), type="追加受注",
                    val=i['val']-o.val, val_payment=i['val_payment']-o.val_payment,
                    status=o.status, category=o.category,
                    client=o.client, date_open=o.date_open, date_close=o.date_close,
                )
                ro.save_from_shell(u)
                # ManyToMany
                ro.related_opportunity.add(o)
                ro.sub_categories.add(category)
                ro.save_from_shell(u)
        except Exception as e:
            print(e)
            errors += 1
    for i in di['提案受注']:
        if Category.objects.filter(name=i['category']).count() == 1:
            category = Category.objects.get(name=i['category'])
        else:
            category = Category(name=i['category'])
            category.save_from_shell(u)
        proposal_id = i['id']
        print(proposal_id)
        try:
            res = d.get_proposal(proposal_id)
            res.pop("opportunity_url")
            res.pop("client_url")
            if Client.objects.filter(client_id=res['client_id']).exists():
                c = Client.objects.get(client_id=res.pop('client_id'))
                res.pop('client_name')
            else:
                c = Client()
                c.name = res.pop('client_name')
                c.client_id = res.pop('client_id')
                c.save_from_shell(u)
            o = Opportunity(**res)
            o.client = c
            o.date_open = datetime.strptime(i['date_proposal'][0:15], "%Y-%m-%dT%H:%M").date()
            o.date_close = datetime.strptime(i['date_close'][0:15], "%Y-%m-%dT%H:%M").date()
            if i["status"] == "選定" and i['is_working']:
                o.status = "選定/作業中"
            elif i["status"] == "選定" and not i['is_working']:
                o.status = "選定/終了"
            else:
                o.status = i["status"]
            o.type = "提案受注"
            o.category = category
            o.memo = i["memo"]
            o.save_from_shell(u)
            # manytomany
            o.sub_categories.add(category)
            o.save_from_shell(u)
            # working_time
            if i["working_time"]:
                ow = OpportunityWork()
                ow.opportunity = o
                ow.working_time = i["working_time"] * 60
                ow.save_from_shell(u)
            done += 1
            # related_opportunity
            if i['add'] > 0:
                ro = Opportunity(
                    name="【追加受注】{}".format(o.name), type="追加受注",
                    val=i['val'] - o.val, val_payment=i['val_payment'] - o.val_payment,
                    status=o.status, category=o.category,
                    client=o.client, date_open=o.date_open, date_close=o.date_close,
                )
                ro.save_from_shell(u)
                #ManyToMany
                ro.related_opportunity.add(o)
                ro.sub_categories.add(category)
                ro.save_from_shell(u)
        except Exception as e:
            print(e)
            errors += 1

    for i in di['else']:
        if Category.objects.filter(name=i['category']).count() == 1:
            category = Category.objects.get(name=i['category'])
        else:
            category = Category(name=i['category'])
            category.save_from_shell(u)
        o = Opportunity()
        o.val = i['val']
        o.val_payment = i['val_payment']
        if i["status"] == "選定" and i['is_working']:
            o.status = "選定/作業中"
        elif i["status"] == "選定" and not i['is_working']:
            o.status = "選定/終了"
        else:
            o.status = i["status"]
        o.type = "直接受注"
        o.category = category
        o.memo = i["memo"]
        o.date_proposal = datetime.strptime(i['date_proposal'][0:15], "%Y-%m-%dT%H:%M").date()
        o.datetime_close_opportunity = datetime.strptime(i['date_close'][0:15], "%Y-%m-%dT%H:%M")
        o.datetime_open_opportunity = datetime.strptime(i['date_open'][0:15], "%Y-%m-%dT%H:%M")
        o.save_from_shell(u)
        # ManyToMany
        o.sub_categories.add(category)
        o.save_from_shell(u)
        # working_time
        if i["working_time"]:
            ow = OpportunityWork()
            ow.opportunity = o
            ow.working_time = i["working_time"] * 60
            ow.save_from_shell(u)

    d.close()
    return [done, errors, di]


def create_opportunity(i, res, category, u):
    try:
        res.pop("opportunity_url")
        res.pop("client_url")
        if Client.objects.filter(client_id=res['client_id']).exists():
            c = Client.objects.get(client_id=res.pop('client_id'))
            res.pop('client_name')
        else:
            c = Client()
            c.name = res.pop('client_name')
            c.client_id = res.pop('client_id')
            c.save_from_shell(u)
        o = Opportunity(**res)
        o.client = c
        o.date_open = datetime.strptime(i['date_proposal'][0:15], "%Y-%m-%dT%H:%M").date()
        o.date_close = datetime.strptime(i['date_close'][0:15], "%Y-%m-%dT%H:%M").date()
        if i["status"] == "選定" and i['is_working']:
            o.status = "選定/作業中"
        elif i["status"] == "選定" and not i['is_working']:
            o.status = "選定/終了"
        else:
            o.status = i["status"]
        o.type = "提案受注"
        o.category = category
        o.memo = i["memo"]
        o.save_from_shell(u)
        # manytomany
        o.sub_categories.add(category)
        o.save_from_shell(u)
        # working_time
        if i["working_time"]:
            ow = OpportunityWork()
            ow.opportunity = o
            ow.working_time = i["working_time"] * 60
            ow.save_from_shell(u)
        # related_opportunity
        if i['add'] > 0:
            ro = Opportunity(
                name="【追加受注】{}".format(o.name), type="追加受注",
                val=i['val'] - o.val, val_payment=i['val_payment'] - o.val_payment,
                status=o.status, category=o.category,
                client=o.client, date_open=o.date_open, date_close=o.date_close,
            )
            ro.save_from_shell(u)
            # ManyToMany
            ro.related_opportunity.add(o)
            ro.sub_categories.add(category)
            ro.save_from_shell(u)
        result = True
    except Exception as e:
        print(e)
        result = False
    finally:
        return result
