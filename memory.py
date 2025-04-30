class ConversationMemory:
    def __init__(self, max_messages=5):
        self.memory = {}

    def add_message(self, user_id, role, content):
        if user_id not in self.memory:
            self.memory[user_id] = []
        self.memory[user_id].append({"role": role, "content": content})
        self.memory[user_id] = self.memory[user_id][-self.max_messages:]

    def get_conversation(self, user_id):
        return self.memory.get(user_id, [])
