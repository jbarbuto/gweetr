"""controllers.py"""

from flask import json, request, session, url_for
import twilio
import twilio.rest
import twilio.twiml

from gweetr import app, db
from gweetr.exceptions import GweetrError
from gweetr.models import Greeting, Track
from gweetr.utils import fetch_track, is_valid_url

twilio_client = twilio.rest.TwilioRestClient(
    app.config['TWILIO_ACCOUNT_SID'],
    app.config['TWILIO_AUTH_TOKEN'],
)

ALLOWED_ACTIONS = ('set',)


@app.route('/receive-voice', methods=['POST'])
def receive_voice():
    """
    Receive incoming voice call.

    Forward the call to the configured number.
    If it doesn't go through, play greeting and go to voicemail.
    """
    resp = twilio.twiml.Response()
    resp.dial(
        app.config['YOUR_PHONE_NUMBER'],
        timeout=app.config['YOUR_PHONE_TIMEOUT']
    )
    greeting = Greeting.query.filter_by(
        phone=app.config['TWILIO_PHONE_NUMBER']
    ).first()
    if greeting is None:
        for message in app.config['NO_SONG_MESSAGES']:
            if is_valid_url(message):
                resp.play(message)
            else:
                resp.say(message)
    else:
        for message in app.config['PRE_SONG_MESSAGES']:
            if is_valid_url(message):
                resp.play(message)
            else:
                resp.say(message)
        resp.play(greeting.track.url)
        for message in app.config['POST_SONG_MESSAGES']:
            if is_valid_url(message):
                resp.play(message)
            else:
                resp.say(message)
    resp.record()
    return str(resp)


@app.route('/receive-message', methods=['POST'])
def receive_message():
    """
    Receive incoming SMS message.

    Determine if a command was sent and act accordingly.
    We only support setting a greeting track for now.
    """
    msg_from = request.values.get('From')
    msg_body = request.values.get('Body')
    sms_command_prefix = app.config['SMS_COMMAND_PREFIX'].lower()

    resp = twilio.twiml.Response()
    try:
        prefix, args = msg_body.split(None, 1)
    except ValueError:
        if msg_body.lower() == sms_command_prefix:
            resp.message("No action provided, must be one of the following: %s"
                         % ','.join(ALLOWED_ACTIONS))
        return str(resp)
    else:
        # TODO: provide a way to handle non-command texts
        if prefix.lower() != sms_command_prefix:
            return str(resp)

    try:
        action, args = args.split(None, 1)
    except ValueError:
        resp.message("No arguments provided for action '%s'" % args)
        return str(resp)

    if action == 'set':
        args = args.split()
        track_params = {}
        for arg in args:
            try:
                key, value = arg.split(':')
            except ValueError:
                resp.message("Param '%s' has no corresponding value, must be "
                             "specified as key:value" % key)
                return str(resp)
            else:
                track_params[key] = value.replace('_', ' ')

        # Check if tracks exist with the given parameters before calling
        try:
            track_data = fetch_track(track_params)
        except GweetrError as exc:
            resp.message(str(exc))
            return str(resp)
        else:
            if not track_data:
                resp.message("No tracks match the parameters given")
                return str(resp)

        try:
            twilio_client.calls.create(
                to=msg_from,
                from_=app.config['TWILIO_PHONE_NUMBER'],
                url=url_for(
                    'set_greeting_track',
                    _external=True,
                    track_params=json.dumps(track_params)
                )
            )
        except twilio.TwilioRestException as exc:
            app.logger.error(str(exc))
            resp.message('An error has occurred, '
                         'please see server log for details')
        else:
            resp.message('You should receive a call shortly')
    else:
        resp.message("Action '%s' unknown, must be one of the following: %s"
                     % (action, ','.join(ALLOWED_ACTIONS)))

    return str(resp)


@app.route("/set-greeting-track", methods=['POST'])
def set_greeting_track():
    """Set greeting track based on provided parameters."""
    session['msg_from'] = request.values.get('To')

    try:
        track_params = session['track_params']
        first_run = False
    except KeyError:
        track_params = json.loads(request.values.get('track_params'))
        session['track_params'] = track_params
        first_run = True

    track_data = session['track_data'] = fetch_track(track_params)

    resp = twilio.twiml.Response()
    if first_run:
        resp.say("You requested a song with the following parameters.")
        for key, value in track_params.items():
            resp.say("%s=%s" % (key, value))
            resp.pause()
    resp.say("This song by %(artist)s is called %(title)s" % track_data)
    resp.play(track_data['url'])

    with resp.gather(
            numDigits=1,
            action=url_for('handle_key'),
            method='POST') as gatherer:
        gatherer.say("To accept %(title)s by %(artist)s as your voicemail "
                     "song, press 1. Press 2 to hear another song."
                     % track_data)
    return str(resp)


@app.route("/handle-key", methods=['POST'])
def handle_key():
    """Handle key press from a user."""
    digit_pressed = request.values.get('Digits')
    resp = twilio.twiml.Response()
    if digit_pressed == '1':
        track_data = session['track_data']
        track = Track.query.filter_by(
            url=track_data['url']
        ).first()
        if track is None:
            track = Track(
                track_data['title'],
                track_data['artist'],
                track_data['url']
            )
            db.session.add(track)
            db.session.commit()

        greeting = Greeting.query.filter_by(
            phone=app.config['TWILIO_PHONE_NUMBER']
        ).first()
        if greeting is None:
            greeting = Greeting(
                app.config['TWILIO_PHONE_NUMBER'],
                track
            )
            db.session.add(greeting)
        else:
            greeting.track = track
        db.session.commit()

        resp.say('Your voicemail greeting has been set successfully. Goodbye.')
    elif digit_pressed == '2':
        resp.redirect(url_for('set_greeting_track'))
    else:
        resp.say("%s is an invalid option. Please try again." % digit_pressed)
        # TODO: reprompt for a different key instead of replaying track
        resp.redirect(url_for('set_greeting_track'))

    return str(resp)
