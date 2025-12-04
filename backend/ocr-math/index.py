import json
import os
import base64
from typing import Dict, Any

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Распознает математические задачи с изображений используя GPT-4 Vision
    Args: event - dict с httpMethod, body (base64 изображение)
          context - объект с атрибутами request_id, function_name
    Returns: HTTP response dict с распознанным текстом задачи
    '''
    method: str = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }
    
    try:
        body_data = json.loads(event.get('body', '{}'))
        image_data = body_data.get('image')
        
        if not image_data:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Image data is required'}),
                'isBase64Encoded': False
            }
        
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        openai_key = os.environ.get('OPENAI_API_KEY')
        if not openai_key:
            return {
                'statusCode': 500,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'OpenAI API key not configured'}),
                'isBase64Encoded': False
            }
        
        import requests
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {openai_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'text',
                                'text': 'Ты математический ассистент. Внимательно посмотри на изображение и извлеки из него математическую задачу или выражение. Верни ТОЛЬКО текст задачи/выражения, без комментариев и объяснений. Если это уравнение, запиши его в формате "2x + 5 = 15". Если это геометрическая задача, опиши её кратко с указанием данных.'
                            },
                            {
                                'type': 'image_url',
                                'image_url': {
                                    'url': f'data:image/jpeg;base64,{image_data}'
                                }
                            }
                        ]
                    }
                ],
                'max_tokens': 500
            }
        )
        
        if response.status_code != 200:
            return {
                'statusCode': response.status_code,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': f'OpenAI API error: {response.text}'}),
                'isBase64Encoded': False
            }
        
        result = response.json()
        extracted_text = result['choices'][0]['message']['content'].strip()
        
        category = detect_category(extracted_text)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'text': extracted_text,
                'category': category
            }),
            'isBase64Encoded': False
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }

def detect_category(text: str) -> str:
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['sin', 'cos', 'tan', 'тангенс', 'синус', 'косинус', '°']):
        return 'trigonometry'
    
    if any(word in text_lower for word in ['круг', 'квадрат', 'треугольник', 'площадь', 'объем', 'периметр', 'радиус', 'диаметр']):
        return 'geometry'
    
    if any(word in text_lower for word in ['x', 'y', '=', 'уравнение', 'корень', 'переменная']):
        return 'algebra'
    
    return 'arithmetic'
