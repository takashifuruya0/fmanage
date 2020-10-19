from lancers.functions import mylib_selenium
from lancers.models import Client, Opportunity
from django.contrib.auth import get_user_model


def create_opportunity(proposal_id):
    u = get_user_model().objects.get(pk=1)
    d = mylib_selenium.Lancers()
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
    o.save_from_shell(u)
    return o