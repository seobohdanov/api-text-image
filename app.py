from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, send_file
import io
import requests
import traceback
import os

app = Flask(__name__)

def create_image(text, date, background_url, font_path, width=1792, height=1024):
    response = requests.get(background_url)
    response.raise_for_status()
    background = Image.open(io.BytesIO(response.content))
    background = background.resize((width, height), Image.LANCZOS)
    
    image = background.convert('RGBA')
    draw = ImageDraw.Draw(image)
    
    # Установка фиксированного размера в 250 пунктов
    font_size = 250
    font = ImageFont.truetype(font_path, font_size)
    
    # Преобразуем текст: первая буква заглавная, остальные строчные
    text = text.capitalize()
    
    # Расположение основного текста (вверху с большим отступом)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_position = ((width - text_width) / 2, height * 0.00)  # 0% отступ сверху
    
    # Увеличиваем толщину обводки
    outline_color = "#a47270"
    outline_thickness = 6  # Увеличиваем толщину обводки
    
    # Рисуем более толстую обводку для основного текста
    for x in range(-outline_thickness, outline_thickness + 1):
        for y in range(-outline_thickness, outline_thickness + 1):
            if x == 0 and y == 0:
                continue
            draw.text((text_position[0] + x, text_position[1] + y), text, font=font, fill=outline_color)
    
    # Рисуем основной текст
    draw.text(text_position, text, font=font, fill="white")
    
    # Расположение даты (внизу с большим отступом)
    date_bbox = draw.textbbox((0, 0), date, font=font)
    date_width = date_bbox[2] - date_bbox[0]
    date_position = ((width - date_width) / 2, height * 0.72)  # 28% отступ снизу
    
    # Рисуем более толстую обводку для даты
    for x in range(-outline_thickness, outline_thickness + 1):
        for y in range(-outline_thickness, outline_thickness + 1):
            if x == 0 and y == 0:
                continue
            draw.text((date_position[0] + x, date_position[1] + y), date, font=font, fill=outline_color)
    
    # Рисуем дату
    draw.text(date_position, date, font=font, fill="white")
    
    return image

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Image Generator API"

@app.route('/generate_image', methods=['POST'])
def generate_image():
    try:
        data = request.json
        if not all(key in data for key in ['text', 'date', 'background_url']):
            return 'Missing required parameters: text, date, and background_url are required', 400
        
        text = data['text']
        date = data['date']
        background_url = data['background_url']
        font_path = os.path.join(os.path.dirname(__file__), 'EFCO Brookshire Regular.ttf')
        
        image = create_image(text, date, background_url, font_path, width=1792, height=1024)
        
        img_io = io.BytesIO()
        image = image.convert('RGB')  # Конвертируем в RGB перед сохранением
        image.save(img_io, 'JPEG', quality=85, optimize=True)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/jpeg')
    except Exception as e:
        print(f"Error in generate_image: {str(e)}")
        print(traceback.format_exc())
        return str(e), 500

# Эта строка нужна для локального запуска, но не требуется для Vercel
# if __name__ == '__main__':
#     app.run(debug=True)