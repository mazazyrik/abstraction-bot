import logging
from gigachat import GigaChat


def add_prompt(text):
    logging.info('add_prompt started')
    error_text = ('К сожалению, нейросеть не смогла расшифровать этот текст. '
                  'Попробуйте ещё раз.')
    prompt = (
        f'Напиши кракткий конспект этого текста.'
        f'Этот текст расшифрован другой '
        f'нейросетью из аудиозаписи, могут быть погрешности учти это.'
        f'Если текст похож на что-то по типу уууу или просто мычания, '
        f'то напиши {error_text}. Попробуй написать тезисный конспект, '
        f'даже если текст крайне короткий'
    )
    with GigaChat(
        credentials=(
            'YWFiOWJmZGItNzU2YS00NzBlLTkxOTUtYzc4ZjQwMDg3ZDljOmE2NGQ2NDVmLTNmMjItNDZhOS1iODY4LTY0ZGVmMjllYjZlYw=='
        ),
        verify_ssl_certs=False
    ) as giga:
        response = giga.chat(
            f'Текст: "{text}"' + prompt)
    logging.info('text is ready')
    return response.choices[0].message.content
