import pyjokes
import requests
from translate import Translator
import threading
import time
import flet as ft

ACCESS_TOKEN = ''
VK_API_VERSION = '5.131'
GROUP_ID = ''
cycle_time = 60  # Время по умолчанию в минутах
running = False
translate_jokes = True  # По умолчанию включен перевод

gif_url = "https://media1.tenor.com/m/1JuAyubK6zoAAAAd/bocchi-the-rock-hitori-gotoh.gif"

def post_to_group(message):
    try:
        response = requests.post('https://api.vk.com/method/wall.post', params={
            'access_token': ACCESS_TOKEN,
            'v': VK_API_VERSION,
            'owner_id': -int(GROUP_ID),
            'from_group': 1,
            'message': message
        }).json()
        
        if 'error' in response:
            return f"Error: {response['error']['error_msg']}"
        return "Сообщение успешно отправлено!"
    except Exception as e:
        return f"Произошла ошибка при отправке сообщения: {str(e)}"

def generate_joke_and_post(status_text, countdown_text):
    global running, cycle_time, translate_jokes
    while running:
        joke = pyjokes.get_joke()
        if translate_jokes:
            translated_joke = Translator(to_lang='ru').translate(joke)
        else:
            translated_joke = joke  # Если перевод выключен, используем оригинальный анекдот
        
        post_result = post_to_group(translated_joke)

        status_text.value = f"Оригинальный анекдот: {joke}\nОтправленный анекдот: {translated_joke}\n{post_result}"
        status_text.update()

        for remaining in range(cycle_time * 60, 0, -1):
            countdown_text.value = f"Время до следующего поста: {remaining // 60} мин {remaining % 60} сек"
            countdown_text.update()
            time.sleep(1)

def start_joke_generation(status_text, countdown_text, start_button):
    global running

    if not (ACCESS_TOKEN and GROUP_ID and cycle_time):
        status_text.value = "Пожалуйста, заполните все поля!"
        status_text.update()
        return

    if not running:
        running = True
        threading.Thread(target=generate_joke_and_post, args=(status_text, countdown_text), daemon=True).start()
        status_text.value = "Запускается..."
        status_text.update()

        access_token_input.disabled = True
        group_id_input.disabled = True
        cycle_time_input.disabled = True
        
        access_token_input.update()
        group_id_input.update()
        cycle_time_input.update()

        start_button.visible = False
        start_button.update()

def main(page: ft.Page):
    global access_token_input, group_id_input, cycle_time_input, status_text, translate_switch

    access_token_input = ft.TextField(label="API сообщества")
    group_id_input = ft.TextField(label="ID сообщества")
    cycle_time_input = ft.TextField(label="ПЕРИОДИЧНОСТЬ ПОСТОВ (мин)", value=str(cycle_time))

    def update_settings(e):
        global ACCESS_TOKEN, GROUP_ID, cycle_time
        ACCESS_TOKEN = access_token_input.value
        GROUP_ID = group_id_input.value
        try:
            cycle_time = int(cycle_time_input.value)
        except ValueError:
            cycle_time_input.value = str(cycle_time)
        cycle_time_input.update()

    access_token_input.on_change = update_settings
    group_id_input.on_change = update_settings
    cycle_time_input.on_change = update_settings

    translate_switch = ft.Switch(label="Переводить анекдоты", value=translate_jokes)
    translate_switch.on_change = lambda e: set_translation_status()

    status_text = ft.Text("Готов к работе", text_align=ft.TextAlign.CENTER)
    countdown_text = ft.Text("Время до следующего поста: 52", text_align=ft.TextAlign.CENTER)

    gif_image = ft.Image(src=gif_url, width=1400, height=342)

    start_button = ft.ElevatedButton("Запустить", on_click=lambda e: start_joke_generation(status_text, countdown_text, start_button))

    input_column = ft.Column(
        controls=[
            access_token_input,
            group_id_input,
            cycle_time_input,
            translate_switch,
            start_button
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    output_column = ft.Column(
        controls=[
            status_text,
            countdown_text,
            gif_image
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.add(input_column, output_column)

def set_translation_status():
    global translate_jokes
    translate_jokes = translate_switch.value

ft.app(target=main)
