from json import load
from telebot.types import InlineKeyboardMarkup
from telebot.util import quick_markup
from os import path

media_dir = path.join(path.dirname(path.abspath(__file__)), 'storage')

def load_json_data(filename: str):
  with open(filename, encoding='utf-8') as file:
    return load(file) 
  
def dict_to_str(data: dict, indent: int = 0):
  result = []
  for key, value in data.items():
        result.append(' ' * indent + f'<b>{key}</b>: ')            # отступ слева + ключ
        if isinstance(value, dict):                                # если значение это вложенный словарь, то
            result.append('\n' + dict_to_str(value, indent + 2))     # перейти на новую строку,
                                                               # вызвать функцию повторно,
                                                               # увеличить отступ
        else:
            if isinstance(value, int):                               # если значение это целое число, то
                result.append(f'{value}\n')
            elif isinstance(value, str):                             # если значение это строка, то
              if value:                                              # если строка не пустая, то
                result.append(f'{value}\n')
              else:                                                  # если строка пустая, то
                result.append('—\n')
  return ''.join(result)

""" def create_pagination_keyboard(
  current_message: int,
  total_messages: int
):
  return quick_markup({
    '⬅️': {'callback_data': f'prev_{current_message}'},
    f'{current_message} / {total_messages}': {'callback_data': 'ignore'},
    '➡️': {'callback_data': f'next_{current_message}'}
  }, row_width=3) """