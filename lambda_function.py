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


def lookup_coinbase(currency_code):
    url = 'https://api.coinbase.com/v2/exchange-rates'
    params = {
        'currency': currency_code,
    }
    r = requests.get(url, params=params, timeout=3)
    d = r.json()
    return d['data']['rates']['USD']


def lambda_handler(event, context):
    print('event: {}'.format(event))

    try:
        if event['request']['intent']['name'] == 'CoinLookup':
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
        elif event['request']['intent']['name'] == 'CoinOverview':
            alexa = alexa_response(
                {},
                build_speech_response('WIP', 'This section is not finished.', None, True)
            )
            return alexa
        else:
            raise ValueError('Unknown Intent')
    except Exception as error:
        print('error: {}'.format(error))
        alexa = alexa_response(
            {},
            build_speech_response('Error', TXT_ERROR.format(value), None, True)
        )
        return alexa
