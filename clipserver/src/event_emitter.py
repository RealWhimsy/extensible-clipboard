from flask import url_for
import requests
"""
    This class handles emitting clips to clipboards and hooks
    
    

"""

class ClipEventEmitter:

    def __init__(self, db):
        self.clipboards = []
        self.webhooks = []
        self.recipients = []
        self.db = db
        self.invalidate_listeners()

    def invalidate_listeners(self):
        """
        Refreshes the list of clipboards and hooks
        """
        result = self.db.get_recipients() or []
        self.webhooks = []
        self.clipboards = []
        for r in result:
            if r['is_hook']:
                self.webhooks.append(r)
            else:
                self.clipboards.append(r)
            r['error_count'] = 0
        self.recipients = self.clipboards + self.webhooks


    def send_to_recipients(self, data, recipients=None, force_propagation=False, last_sender=None):
        """
        Passes data to the recipient clipboards
        :param data: The data (text, binary) received by the Resource
        """
        if recipients is None:
            recipients = self.recipients
        parent = data.get('parent')
        # Handle child transmitted to
        if parent and self.db.get_latest_clip()['_id'] != parent:
            # Update was not to current clip
            return
        for c in recipients:
            if force_propagation or (last_sender and last_sender != c['_id']):
                try:
                    # TODO: this runs identical to send to hooks
                    send_data = data.get('data')
                    headers = self.build_headers(data['_id'], data)
                    requests.post(c['url'],
                                  data=send_data,
                                  headers=headers,
                                  timeout=5)
                except Exception as e:
                    print(e)
                    self._send_failed(c)

    def send_to_hooks(self, data):
        """
        Passes data to the Q-Application so it can put them into the clipboard
        :param data: The data (text, binary) received by the Resource
        """
        """
        self.native_hooks.call_hooks(data, self.db.save_clip)
        """
        _id = data.get('parent', data['_id'])
        for c in self.webhooks:
            types = c['preferred_types']
            if data['mimetype'] in types or types == ['*/*']:
                try:
                    send_data = data.pop('data')
                    # URL used for adding a child to the entry
                    headers = self.build_headers(_id, data)
                    requests.post(c['url'],
                                  data=send_data,
                                  headers=headers,
                                  timeout=5)
                except Exception as e:
                    print(e)
                    self._send_failed(c)

    def __on_send_failed__(self, recipient):
        """
        Called when sending data to a recipient failed. Currently ony counts
        errors and prints them. Could be used to remove the recipient after
        a certain number of consecutive failures.
        """
        recipient['error_count'] += 1
        print('Could not send data to {}'.format(recipient['url']))
        print('Errors for {}: {}'.format(
            recipient['url'],
            recipient['error_count']
        ))

    def build_headers(self, data, id):
        response_url = url_for('child_adder',
                               clip_id=id,
                               _external=True)
        headers = {'X-C2-response_url': response_url}
        headers['Content-Type'] = data.pop('mimetype')
        for key, value in data.items():
            headers['X-C2-{}'.format(key)] = value
        return headers