class ConversationMemory:
    def __init__(self, max_messages=5):
        self.memory = {}
        self.max_messages = max_messages 

    def add_message(self, user_id, role, content):
        if user_id not in self.memory:
            self.memory[user_id] = []
        
        self.memory[user_id].append({"role": role, "content": content})
        
        self.memory[user_id] = self.memory[user_id][-self.max_messages:]

    def get_conversation(self, user_id):
        return self.memory.get(user_id, [])
if __name__ == "__main__":
    conversation = ConversationMemory(max_messages=3)

    conversation.add_message(user_id=1, role="user", content="Привет!")
    conversation.add_message(user_id=1, role="bot", content="Привет, как я могу помочь?")
    conversation.add_message(user_id=1, role="user", content="Как дела?")
    conversation.add_message(user_id=1, role="bot", content="Хорошо, спасибо!")

    print(conversation.get_conversation(user_id=1))
