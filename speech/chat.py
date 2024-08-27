import asyncio
from concurrent.futures import ProcessPoolExecutor
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from prompt import prompt as base_prompt


model_name = "sberbank-ai/rugpt3large_based_on_gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = AutoModelForCausalLM.from_pretrained(model_name).to(device)


def generate_text(prompt):
    inputs = tokenizer(
        base_prompt + prompt,
        return_tensors="pt",
        truncation=True,
        padding=True
    ).to(device)
    outputs = model.generate(**inputs, max_length=10_000)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


async def add_prompt(prompts):
    loop = asyncio.get_event_loop()
    results = []

    with ProcessPoolExecutor() as executor:
        futures = [
            loop.run_in_executor(executor, generate_text, prompt)
            for prompt in prompts
        ]

        for response in await asyncio.gather(*futures):
            results.append(response)

    return results
