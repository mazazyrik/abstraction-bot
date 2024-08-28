import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Убедитесь, что у вас есть доступ к GPU, если он доступен
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Загрузка модели и токенизатора для русского языка
model_name = "sberbank-ai/rugpt3large_based_on_gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name).to(device)


def generate_text(prompt, max_length=2000):
    inputs = tokenizer.encode(prompt, return_tensors='pt').to(device)
    outputs = model.generate(inputs, max_length=max_length,
                             num_return_sequences=1)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def add_prompt(text):
    logging.info('add_prompt started')

    prompt = (
        "Ты ассистент который помогает пользователям в написании конспектов.\n"
        "Хорошо я поняла. Ожидаю вводный текст\n"
    )

    text_len = len(text)
    num_chunks = -(-text_len // 2000)  # Округление вверх
    results = []

    for i in range(num_chunks):
        chunk = text[i * 2000:(i + 1) * 2000]
        full_prompt = prompt + chunk
        result = generate_text(full_prompt)
        results.append(result)

    # Объединение результатов
    final_result = "\n".join(results)
    return final_result


print(add_prompt('привет как дела'))
