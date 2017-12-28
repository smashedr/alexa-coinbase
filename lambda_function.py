import requests

TXT_UNKNOWN = 'I did not understand that request, please try something else.'
TXT_ERROR = 'Error looking up {}, please try something else.'

KEYS = {
    'bitcoin': 'BTC',
    'bitcoin cash': 'BCH',
    'litecoin': 'LTC',
    'ethereum': 'ETH',
}


def build_speech_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def alexa_response(session_attributes, speech_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speech_response
    }


def alexa_error(error='Unknown error, please try something else', title='UE'):
    alexa = alexa_response(
        {}, build_speech_response(title, error, None, True)
    )
    return alexa


def get_accounts(token):
    url = 'https://api.coinbase.com/v2/accounts'
    headers = {
        'Authorization': 'Bearer {}'.format(token)
    }
    r = requests.get(url, headers=headers)
    j = r.json()
    return j


def acct_overview(event):
    resp = ''
    a = get_accounts(event['session']['user']['accessToken'])
    s = 's' if len(a['data']) > 1 else ''
    resp += 'I found {} account{}. '.format(len(a['data']), s)
    for d in a['data']:
        resp += '{} contains {}. '.format(d['name'], d['balance']['amount'])

    alexa = alexa_response(
        {},
        build_speech_response(
            'Accounts Overview', resp, None, True
        )
    )
    return alexa


def coin_overview(event):
    alexa = alexa_response(
        {},
        build_speech_response(
            'WIP', 'Overview not yet finished.', None, True
        )
    )
    return alexa


def lookup_coinbase(currency_code):
    url = 'https://api.coinbase.com/v2/exchange-rates'
    params = {
        'currency': currency_code,
    }
    r = requests.get(url, params=params, timeout=3)
    d = r.json()
    return d['data']['rates']['USD']


def coin_lookup(event):
    try:
        value = event['request']['intent']['slots']['currency']['value']
        value = value.lower().replace('define', '').strip()
        value = value.lower().replace('lookup', '').strip()
        value = value.lower().replace('look up', '').strip()
        value = value.lower().replace('search', '').strip()
        value = value.lower().replace('find', '').strip()
        print('value: {}'.format(value))
    except Exception as error:
        print('error: {}'.format(error))
        alexa = alexa_response(
            {}, build_speech_response('Error', TXT_UNKNOWN, None, True)
        )
        return alexa
    definition = lookup_coinbase(KEYS[value])
    speech = 'The current price of {} is {} dollars'.format(
        value, definition
    )
    alexa = alexa_response(
        {}, build_speech_response('Price', speech, None, True)
    )
    return alexa


def lambda_handler(event, context):
    print('event: {}'.format(event))
    try:
        intent = event['request']['intent']['name']
        if intent == 'CoinLookup':
            return coin_lookup(event)
        elif intent == 'CoinOverview':
            return coin_overview(event)
        elif intent == 'AccountOverview':
            return acct_overview(event)
        else:
            raise ValueError('Unknown Intent')
    except ValueError:
        return alexa_error()
    except Exception as error:
        print('error: {}'.format(error))
        return alexa_error()
