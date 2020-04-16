"""
    This class handles emitting clips to clipboards and hooks

    Ideas:
    - handle current clip by broadcast functions
    - prebuild response-url in views

"""

class ClipEventEmitter:

    def __init__(self, db):
        self.clipboards = []
        self.post_hooks = []
        self.db = db
        self.current_clip = None

        self.invalidate_listeners()

    def invalidate_listeners(self):
        """
        Refreshes the list of clipboards and hooks
        """
        result = self.db.get_recipients() or []
        self.post_hooks = []
        self.clipboards = []
        for r in result:
            if r['is_hook']:
                self.post_hooks.append(r)
            else:
                self.clipboards.append(r)
            r['error_count'] = 0

    def __build_request__(self, data):

    # TODO Since this method is part of the save_in_database method, which is used across multiple
    def send_to_clipboards(self, data, force_propagation=False):
        """
        Passes data to the recipient clipboards
        :param data: The data (text, binary) received by the Resource
        """
        parent = data.get('parent')
        # Handle child transmitted to
        if parent and self.current_clip != parent:
            # Update was not to current clip
            return

        for c in self.clipboards:
            if force_propagation or self.last_sender != c['_id']:
                try:
                    # TODO: this runs identical to send to hooks
                    send_data = data.get('data')
                    # TODO: build this somewhere else
                    response_url = url_for('child_adder',
                                           clip_id=data['_id'],
                                           _external=True)
                    print(response_url)
                    headers = {'X-C2-response_url': response_url}
                    headers['Content-Type'] = data.get('mimetype')
                    # TODO: this mapping can also be
                    for key, value in data.items():
                        if key != 'data' and key != 'mimetype':
                            headers['X-C2-{}'.format(key)] = value

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

        for c in self.post_hooks:
            types = c['preferred_types']
            if data['mimetype'] in types or types == ['*/*']:
                try:
                    send_data = data.pop('data')
                    # URL used for adding a child to the entry
                    response_url = url_for('child_adder',
                                           clip_id=_id,
                                           _external=True)
                    headers = {'X-C2-response_url': response_url}
                    headers['Content-Type'] = data.pop('mimetype')
                    for key, value in data.items():
                        headers['X-C2-{}'.format(key)] = value
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