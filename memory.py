class ConversationMemory:
    def __init__(self, max_messages=5):
        self.user_histories = {}
        self.max_messages = max_messages

    def add_message(self, user_id, role, content):
        if user_id not in self.user_histories:
            self.user_histories[user_id] = []
        self.user_histories[user_id].append((role, content))
        self.user_histories[user_id] = self.user_histories[user_id][-self.max_messages:]

    def get_conversation(self, user_id):
        return self.user_histories.get(user_id, [])
