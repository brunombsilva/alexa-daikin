# -*- coding: latin-1 -*-

from flask import Flask
from daikin import discover
from flask_ask import Ask, statement, question, request, session, version

def create(logger):
    app = Flask(__name__)
    ask = Ask(app, '/daikin')
    units = discover()

    @ask.launch
    def launch():
        logger.debug('launch')
        return question('What would you like to do?') \
                .reprompt("I didn't get that. What can I do for you?")

    @ask.on_session_started
    def new_session():
        logger.debug('session started')

    @ask.session_ended
    def session_end():
        logger.debug('session ended')
        return statement('Something went wrong')
            
    @ask.intent('AMAZON.StopIntent')
    def stop():
        logger.debug('stop')
        return statement('Ok')
            
    @ask.intent('AMAZON.CancelIntent')
    def stop():
        logger.debug('cancel')
        return statement('Ok')
            
    @ask.intent('AMAZON.HelpIntent')
    def help():
        logger.debug('help')
        intro = 'Try something like "switch on living" or "what is the temperature?".'
        message = intro + ' What do you wish to do?'

        card_content = intro + ""

        return question(message) \
                .simple_card(
                    title= 'Things to try',
                    content= card_content
                )

    @ask.intent('Temperature', mapping= {'alias': 'Unit'})
    def temperature(alias):
        logger.debug('temperature')
        result = units.apply(alias, lambda u: u.temperature())
        if not result:
            return question('{} not found. Anything else?'.format(alias))

        message = ''
	content = ''
        for u,t in result.iteritems():
            message += '{} temperature is {} degrees, '.format(u, t.inside)
	    content += '{}: {}°\n'.format(u.capitalize(), t.inside)
        message += 'outside temperature is {} degrees. '.format(t.outside)
	content += 'Outside: {}°\n'.format(t.outside)

        return question('{} Anything else?'.format(message)) \
                .simple_card(
		    title= 'Temperature',
		    content= content
		)

    @ask.intent('Mode', mapping= {'alias': 'Unit'})
    def mode(alias):
        logger.debug('mode')
        result = units.apply(alias, lambda u: u.mode())
        if not result:
            return question('{} not found. Anything else?'.format(alias))

        message = ''
	content = ''
        count_off = 0
        for u,m in result.iteritems():
            if m.power:
                message += '{} is on and set to {} degrees, '.format(u, m.temperature)
		content += '{}: {}°\n'.format(u.capitalize(), m.temperature)
            else:
                count_off += 1
                message += '{} is off, '.format(u)
		content += '{}: off'.format(u.capitalize())

        if count_off == len(result):
            message = 'all off.'
	    content = 'All off'

        return question('{} Anything else?'.format(message)) \
                .simple_card(title= 'Status',
                               content= content)

    @ask.intent('Off', mapping= {'alias': 'Unit'})
    def off(alias):
        logger.debug('off')
        result = units.apply(alias, lambda u: u.off())
        if not result:
            return question('{} not found. Anything else?'.format(alias))

        if len(result) == 1:
            message = '{} is off, '.format(alias)
        else:
            message = 'all off'

        return statement(message)

    @ask.intent('On', mapping= {'alias': 'Unit'})
    def on(alias):
        logger.debug('on')
        result = units.apply(alias, lambda u: u.on())
        if not result:
            return question('{} not found. Anything else?'.format(alias))

        if len(result) == 1:
            message = '{} is on, '.format(alias)
        else:
            message = 'all on'

        return statement(message)

    return app
