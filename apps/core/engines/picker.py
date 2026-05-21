# /opt/balthub/apps/core/engines/picker.py

def normalize_querydict(request):

    state = {}

    for key in request.GET.keys():

        clean_key = key.replace("[]", "")

        values = request.GET.getlist(key)

        state[clean_key] = values

    return state