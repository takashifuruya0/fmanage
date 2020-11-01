from lancers.functions import mylib_selenium
from lancers.models import Client, Opportunity, Category, OpportunityWork
from django.contrib.auth import get_user_model
import requests
from datetime import datetime, date
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


def _migrate_opportunity(i, res, u, type_opp, is_linked_to_client=True):
    try:
        # category
        if Category.objects.filter(name=i['category']).count() == 1:
            category = Category.objects.get(name=i['category'])
        else:
            category = Category(name=i['category'])
            category.save_from_shell(u)
        # client
        if is_linked_to_client:
            if Client.objects.filter(client_id=res['client_id']).exists():
                c = Client.objects.get(client_id=res.pop('client_id'))
                res.pop('client_name')
            else:
                c = Client()
                c.name = res.pop('client_name')
                c.client_id = res.pop('client_id')
                c.save_from_shell(u)
        else:
            c = Client(name="tmp{}".format(i["row"]), client_id="tmp{}".format(i["row"]))
            c.save_from_shell(u)
        o = Opportunity(**res)
        o.client = c
        # opportunity
        o.date_open = datetime.strptime(i['date_proposal'][0:15], "%Y-%m-%dT%H:%M").date()
        o.date_close = datetime.strptime(i['date_close'][0:15], "%Y-%m-%dT%H:%M").date()
        if i["status"] == "選定" and i['is_working']:
            o.status = "選定/作業中"
        elif i["status"] == "選定" and not i['is_working']:
            o.status = "選定/終了"
        else:
            o.status = i["status"]
        o.type = type_opp
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
        if isinstance(i['add'], int) and i['add'] > 0:
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


def migrate_from_ss(is_direct=True, is_proposal=True, is_else=True):
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
            if text_splited[-2] == "proposal":
                target = "提案受注"
                oppid = text_splited[-1]
            elif text_splited[-2] == "work_offer":
                target = "直接受注"
                oppid = text_splited[-1]
        else:
            target = "else"
            oppid = None
        di[target].append(
            {
                "id": oppid,
                "row": d[0],
                "name": d[2],
                "status": d[4],
                "category": d[5],
                "working_time": d[13],
                "is_working": d[15],
                "memo": d[21],
                "date_proposal": d[1],
                "date_open": d[10],
                "date_close": d[11],
                "val_payment": d[8],
                "val": d[9],
                "add": d[16],

            }
        )
    pprint(di)
    #
    u = get_user_model().objects.get(pk=1)
    if is_proposal or is_direct:
        d = mylib_selenium.Lancers()
    errors = list()
    done = list()
    if is_direct:
        for i in di['直接受注']:
            direct_opportunity_id = i['id']
            print(direct_opportunity_id)
            if Opportunity.objects.filter(direct_opportunity_id=direct_opportunity_id).exists():
                print("PASS")
                continue
            try:
                res = d.get_direct_opportunity(direct_opportunity_id)
            except Exception as e:
                print("Failed to get_direct_opportunity({})".format(direct_opportunity_id))
                print(e)
                continue
            res.pop("client_url")
            result = _migrate_opportunity(i, res, u, "直接受注")
            if result:
                done.append(("直接受注", direct_opportunity_id))
            else:
                errors.append(("直接受注", direct_opportunity_id))
    if is_proposal:
        for i in di['提案受注']:
            proposal_id = i['id']
            print(proposal_id)
            if Opportunity.objects.filter(proposal_id=proposal_id).exists():
                print("PASS")
                continue
            try:
                res = d.get_proposal(proposal_id)
            except Exception as e:
                print("Failed to get_proposal({})".format(proposal_id))
                print(e)
                continue
            res.pop("opportunity_url")
            res.pop("client_url")
            result = _migrate_opportunity(i, res, u, "提案受注")
            if result:
                done.append(("提案受注", proposal_id))
            else:
                errors.append(("提案受注", proposal_id))
    if is_else:
        for i in di['else']:
            res = {
                "name": i['name'],
                "val": i['val'],
                "val_payment": i['val_payment'],
                "date_proposal": datetime.strptime(i['date_proposal'][0:15], "%Y-%m-%dT%H:%M").date(),
                "datetime_close_opportunity": datetime.strptime(i['date_close'][0:15], "%Y-%m-%dT%H:%M"),
                "datetime_open_opportunity": datetime.strptime(i['date_proposal'][0:15], "%Y-%m-%dT%H:%M"),
            }
            result = _migrate_opportunity(i, res, u, "直接受注", is_linked_to_client=False)
            if result:
                done.append(("else", i['name']))
            else:
                errors.append(("else", i['name']))
    if is_proposal or is_direct:
        d.close()
    context = {
        "done": done,
        "errors": errors,
        "di": di
    }
    return context


def create_opportunity2(oppid, u, type_opp, category_name, status, memo, is_linked_to_client=True):
    try:
        d = mylib_selenium.Lancers()
        if type_opp == "直接受注":
            res = d.get_direct_opportunity(oppid)
            res.pop('client_url')
        elif type_opp == "提案受注":
            res = d.get_proposal(oppid)
            res.pop("opportunity_url")
            res.pop("client_url")
        d.close()
    except Exception as e:
        print("Failed to get data by selenium")
        print(e)
        d.close()
        return False
    try:
        # category
        if Category.objects.filter(name=category_name).count() == 1:
            category = Category.objects.get(name=category_name)
        else:
            category = Category(name=category_name)
            category.save_from_shell(u)
        # client
        if is_linked_to_client:
            if Client.objects.filter(client_id=res['client_id']).exists():
                c = Client.objects.get(client_id=res.pop('client_id'))
                res.pop('client_name')
            else:
                c = Client()
                c.name = res.pop('client_name')
                c.client_id = res.pop('client_id')
                c.save_from_shell(u)
        else:
            c = Client(name="tmp{}".format(res['name']), client_id="tmp{}".format(res['name']))
            c.save_from_shell(u)
        o = Opportunity(**res)
        o.client = c
        # opportunity
        o.date_open = date.today()
        o.status = status
        o.type = type_opp
        o.category = category
        o.memo = memo
        o.save_from_shell(u)
        # manytomany
        o.sub_categories.add(category)
        o.save_from_shell(u)
        result = True
    except Exception as e:
        print(e)
        result = False
    finally:
        return result
