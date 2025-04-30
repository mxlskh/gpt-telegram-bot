class ConversationMemory:
    def __init__(self, max_messages=5):
        self.memory = {}
        self.max_messages = max_messages  # Инициализируем max_messages

    def add_message(self, user_id, role, content):
        # Проверяем, существует ли уже запись для данного пользователя
        if user_id not in self.memory:
            self.memory[user_id] = []
        
        # Добавляем новое сообщение в память
        self.memory[user_id].append({"role": role, "content": content})
        
        # Ограничиваем количество сообщений до max_messages
        self.memory[user_id] = self.memory[user_id][-self.max_messages:]

    def get_conversation(self, user_id):
        # Возвращаем историю сообщений для данного пользователя
        return self.memory.get(user_id, [])

# Пример использования
if __name__ == "__main__":
    # Создаём объект с максимальным количеством сообщений = 3
    conversation = ConversationMemory(max_messages=3)

    # Добавляем сообщения
    conversation.add_message(user_id=1, role="user", content="Привет!")
    conversation.add_message(user_id=1, role="bot", content="Привет, как я могу помочь?")
    conversation.add_message(user_id=1, role="user", content="Как дела?")
    conversation.add_message(user_id=1, role="bot", content="Хорошо, спасибо!")

    # Получаем последние 3 сообщения
    print(conversation.get_conversation(user_id=1))  # Ожидаем последние 3 сообщения
