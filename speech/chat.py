from gigachat import GigaChat


def add_prompt(text):
    with GigaChat(
        credentials='YWFiOWJmZGItNzU2YS00NzBlLTkxOTUtYzc4ZjQwMDg3ZDljOmE2NGQ2NDVmLTNmMjItNDZhOS1iODY4LTY0ZGVmMjllYjZlYw==',
        verify_ssl_certs=False
    ) as giga:
        response = giga.chat(
            text + 'Напиши кракткий конспект этого текста. Этот текст расшифрован нейросетью, учти это.')
    return response.choices[0].message.content
