from lancers.functions import mylib_selenium
from lancers.models import Client, Opportunity
from django.contrib.auth import get_user_model


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


def test():
    u = get_user_model().objects.get(pk=1)
    opps = [
        "https://www.lancers.jp/work/detail/2407503",
        "https://www.lancers.jp/work/detail/2429450",
        "https://www.lancers.jp/work/detail/2452668",
        "https://www.lancers.jp/work/detail/2440293",
        "https://www.lancers.jp/work/detail/2420065",
        "https://www.lancers.jp/work/detail/2419566",
        "https://www.lancers.jp/work/detail/2414393",
        "https://www.lancers.jp/work/detail/2418068",
        "https://www.lancers.jp/work/detail/2407889",
        "https://www.lancers.jp/work/detail/2259534",
        "https://www.lancers.jp/work/detail/2453635",
        "https://www.lancers.jp/work/detail/2459384",
        "https://www.lancers.jp/work/detail/2474906",
        "https://www.lancers.jp/work/detail/2478681",
        "https://www.lancers.jp/work/detail/2479074",
        "https://www.lancers.jp/work/detail/2496537",
        "https://www.lancers.jp/work/detail/2519039",
        "https://www.lancers.jp/work/detail/2525492",
        "https://www.lancers.jp/work/detail/2524208",
        "https://www.lancers.jp/work/detail/2557282",
        "https://www.lancers.jp/work/detail/2576411",
        "https://www.lancers.jp/work/detail/2581271",
        "https://www.lancers.jp/work/detail/2598296",
        "https://www.lancers.jp/work/detail/2612439",
        "https://www.lancers.jp/work/detail/2631199",
        "https://www.lancers.jp/work/detail/2639620",
        "https://www.lancers.jp/work/detail/2690840",
    ]
    offers = [
        "https://www.lancers.jp/work_offer/12057",
        "https://www.lancers.jp/work_offer/15496",
        "https://www.lancers.jp/work_offer/17517",
        "https://www.lancers.jp/work_offer/30214",
        "https://www.lancers.jp/work_offer/122775",
        "https://www.lancers.jp/work_offer/128941",
        "https://www.lancers.jp/work_offer/145240",
    ]
    proposals = [
        "https://www.lancers.jp/work/proposal/13568113",
        "https://www.lancers.jp/work/proposal/14504320",
        "https://www.lancers.jp/work/proposal/14504345",
        "https://www.lancers.jp/work/proposal/15417729",
        "https://www.lancers.jp/work/proposal/15418275",
        "https://www.lancers.jp/work/proposal/15455496",
        "https://www.lancers.jp/work/proposal/15465271",
        "https://www.lancers.jp/work/proposal/15599411",
        "https://www.lancers.jp/work/proposal/15729105",
        "https://www.lancers.jp/work/proposal/15897890",
        "https://www.lancers.jp/work/proposal/15939361",
        "https://www.lancers.jp/work/proposal/16028315",
        "https://www.lancers.jp/work/proposal/16233079",
        "https://www.lancers.jp/work/proposal/16233016",
        "https://www.lancers.jp/work/proposal/16447669",
        "https://www.lancers.jp/work/proposal/16473569",
        "https://www.lancers.jp/work/proposal/16588101",
        "https://www.lancers.jp/work/proposal/16665174",
        "https://www.lancers.jp/work/proposal/16873554",
        "https://www.lancers.jp/work/proposal/16876989",
        "https://www.lancers.jp/work/proposal/16981836",
        "https://www.lancers.jp/work/proposal/17002628",
        "https://www.lancers.jp/work/proposal/17043330",
        "https://www.lancers.jp/work/proposal/17093480",
    ]
    d = mylib_selenium.Lancers()
    errors = 0
    done = 0
    for prop in proposals:
        proposal_id = prop.split("/")[-1]
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
            o.status = "提案中"
            o.type = "提案受注"
            o.save_from_shell(u)
            done += 1
        except Exception as e:
            print(e)
            errors += 1
    for do in offers:
        direct_opportunity_id = do.split("/")[-1]
        print(direct_opportunity_id)
        try:
            res = d.get_direct_opportunity(direct_opportunity_id)
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
            done += 1
        except Exception as e:
            print(e)
            errors += 1
    d.close()
    return [done, errors]

