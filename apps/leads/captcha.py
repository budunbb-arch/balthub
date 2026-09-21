import secrets


SESSION_KEY = "slider_captcha_challenges"
MAX_CHALLENGES = 20
CAPTCHA_TOLERANCE = 3


def create_challenge(request):
    challenge_id = secrets.token_urlsafe(18)
    target = secrets.randbelow(61) + 20
    challenges = request.session.get(SESSION_KEY, {})
    challenges[challenge_id] = str(target)
    request.session[SESSION_KEY] = dict(list(challenges.items())[-MAX_CHALLENGES:])
    request.session.modified = True
    return {"id": challenge_id, "target": target}


def verify_challenge(request, challenge_id, value):
    challenges = request.session.get(SESSION_KEY, {})
    expected = challenges.pop(str(challenge_id), None)
    request.session[SESSION_KEY] = challenges
    request.session.modified = True
    if not expected or value is None:
        return False
    try:
        return abs(int(value) - int(expected)) <= CAPTCHA_TOLERANCE
    except (TypeError, ValueError):
        return False