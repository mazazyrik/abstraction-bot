# SpeechAI Telegram Bot

[English](#english) | [Русский](#русский)

## English

### Overview
SpeechAI is an advanced Telegram bot that combines voice recognition and AI capabilities to provide an intelligent conversational experience. The bot can process voice messages, understand natural language, and provide meaningful responses.

### Features
- Voice message processing and transcription
- Natural language understanding
- AI-powered responses
- Secure payment integration
- Asynchronous architecture

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/speechai.git
cd speechai
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with the following variables:
```
TELEGRAM_BOT_TOKEN=your_bot_token
OPENAI_API_KEY=your_openai_key
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key
```

5. Start the application:
```bash
python -m speech
```

### Docker Setup
```bash
docker-compose up -d
```

## Русский

### Обзор
SpeechAI - это продвинутый Telegram бот, объединяющий возможности распознавания голоса и искусственного интеллекта для создания интеллектуального диалогового опыта. Бот может обрабатывать голосовые сообщения, понимать естественный язык и предоставлять осмысленные ответы.

### Возможности
- Обработка и транскрибация голосовых сообщений
- Понимание естественного языка
- AI-ответы
- Безопасная интеграция платежей
- Асинхронная архитектура

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/speechai.git
cd speechai
```

2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # В Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения:
Создайте файл `.env` со следующими переменными:
```
TELEGRAM_BOT_TOKEN=your_bot_token
OPENAI_API_KEY=your_openai_key
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key
```

5. Запустите приложение:
```bash
python -m speech
```

### Установка через Docker
```bash
docker-compose up -d
```