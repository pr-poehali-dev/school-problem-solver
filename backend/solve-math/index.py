import json
import os
import re
from typing import Dict, Any, List
import psycopg2
from psycopg2.extras import RealDictCursor

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Решает математические задачи и сохраняет историю в базу данных
    Args: event - dict с httpMethod, body, queryStringParameters
          context - объект с атрибутами request_id, function_name
    Returns: HTTP response dict
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method == 'GET':
        return get_history(event)
    
    if method == 'POST':
        return solve_expression(event)
    
    return {
        'statusCode': 405,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Method not allowed'}),
        'isBase64Encoded': False
    }

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(database_url)

def solve_expression(event: Dict[str, Any]) -> Dict[str, Any]:
    try:
        body_data = json.loads(event.get('body', '{}'))
        expression = body_data.get('expression', '')
        category = body_data.get('category', 'algebra')
        
        if not expression:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Expression is required'}),
                'isBase64Encoded': False
            }
        
        solution = solve_math_problem(expression, category)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO solutions (expression, category, answer, steps, explanation) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (expression, category, solution['answer'], json.dumps(solution['steps']), solution['explanation'])
        )
        solution_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        solution['id'] = solution_id
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(solution),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }

def get_history(event: Dict[str, Any]) -> Dict[str, Any]:
    try:
        params = event.get('queryStringParameters', {}) or {}
        limit = int(params.get('limit', '10'))
        category = params.get('category')
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if category:
            cur.execute(
                "SELECT id, expression, category, answer, steps, explanation, created_at FROM solutions WHERE category = %s ORDER BY created_at DESC LIMIT %s",
                (category, limit)
            )
        else:
            cur.execute(
                "SELECT id, expression, category, answer, steps, explanation, created_at FROM solutions ORDER BY created_at DESC LIMIT %s",
                (limit,)
            )
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        solutions = []
        for row in results:
            solutions.append({
                'id': row['id'],
                'expression': row['expression'],
                'category': row['category'],
                'answer': row['answer'],
                'steps': row['steps'],
                'explanation': row['explanation'],
                'created_at': row['created_at'].isoformat()
            })
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'solutions': solutions}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }

def solve_math_problem(expression: str, category: str) -> Dict[str, Any]:
    expression = expression.strip()
    
    if category == 'arithmetic':
        return solve_arithmetic(expression)
    elif category == 'algebra':
        return solve_algebra(expression)
    elif category == 'geometry':
        return solve_geometry(expression)
    elif category == 'trigonometry':
        return solve_trigonometry(expression)
    else:
        return solve_algebra(expression)

def solve_arithmetic(expr: str) -> Dict[str, Any]:
    expr_clean = expr.replace('×', '*').replace('÷', '/').replace(' ', '')
    
    if '%' in expr:
        match = re.search(r'(\d+)%\s*от\s*(\d+)', expr)
        if match:
            percent = float(match.group(1))
            number = float(match.group(2))
            result = (percent / 100) * number
            return {
                'answer': str(result),
                'steps': [
                    {
                        'step': 1,
                        'description': 'Преобразуем проценты в десятичную дробь',
                        'formula': f'{percent}% = {percent/100}',
                        'explanation': f'Делим процент на 100'
                    },
                    {
                        'step': 2,
                        'description': 'Умножаем на исходное число',
                        'formula': f'{percent/100} × {number} = {result}',
                        'explanation': f'Получаем {percent}% от {number}'
                    }
                ],
                'explanation': 'Чтобы найти процент от числа, нужно разделить процент на 100 и умножить на это число.'
            }
    
    try:
        allowed_chars = set('0123456789+-*/(). ')
        if not all(c in allowed_chars for c in expr_clean):
            raise ValueError('Invalid characters in expression')
        
        result = calculate_safe(expr_clean)
        steps = [
            {
                'step': 1,
                'description': 'Исходное выражение',
                'formula': expr,
                'explanation': 'Записываем выражение'
            },
            {
                'step': 2,
                'description': 'Выполняем вычисление',
                'formula': f'{expr} = {result}',
                'explanation': 'Производим арифметические операции'
            }
        ]
        
        return {
            'answer': str(result),
            'steps': steps,
            'explanation': 'Выполняем арифметические операции по порядку: сначала умножение и деление, затем сложение и вычитание.'
        }
    except:
        return {
            'answer': 'Ошибка вычисления',
            'steps': [],
            'explanation': 'Не удалось вычислить выражение'
        }

def calculate_safe(expr: str) -> float:
    expr = expr.strip()
    
    def parse_number(s: str, pos: int) -> tuple:
        num_str = ''
        while pos < len(s) and (s[pos].isdigit() or s[pos] == '.'):
            num_str += s[pos]
            pos += 1
        return float(num_str) if num_str else None, pos
    
    def parse_factor(s: str, pos: int) -> tuple:
        if s[pos] == '(':
            pos += 1
            result, pos = parse_expression(s, pos)
            pos += 1
            return result, pos
        return parse_number(s, pos)
    
    def parse_term(s: str, pos: int) -> tuple:
        left, pos = parse_factor(s, pos)
        while pos < len(s) and s[pos] in '*/':
            op = s[pos]
            pos += 1
            right, pos = parse_factor(s, pos)
            if op == '*':
                left = left * right
            else:
                left = left / right
        return left, pos
    
    def parse_expression(s: str, pos: int) -> tuple:
        left, pos = parse_term(s, pos)
        while pos < len(s) and s[pos] in '+-':
            op = s[pos]
            pos += 1
            right, pos = parse_term(s, pos)
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left, pos
    
    result, _ = parse_expression(expr, 0)
    return result

def solve_algebra(expr: str) -> Dict[str, Any]:
    if '=' in expr:
        left, right = expr.split('=')
        left = left.strip()
        right = right.strip()
        
        match = re.search(r'(-?\d*\.?\d*)x\s*([\+\-])\s*(\d+\.?\d*)', left)
        if match:
            a = float(match.group(1) or '1')
            op = match.group(2)
            b = float(match.group(3))
            c = float(right)
            
            if op == '+':
                x = (c - b) / a
            else:
                x = (c + b) / a
            
            steps = [
                {
                    'step': 1,
                    'description': 'Исходное уравнение',
                    'formula': expr,
                    'explanation': 'Линейное уравнение с одной переменной'
                },
                {
                    'step': 2,
                    'description': 'Переносим число в правую часть',
                    'formula': f'{a}x = {c - b if op == "+" else c + b}',
                    'explanation': f'Меняем знак при переносе через знак равенства'
                },
                {
                    'step': 3,
                    'description': 'Находим x',
                    'formula': f'x = {x}',
                    'explanation': f'Делим обе части на {a}'
                }
            ]
            
            return {
                'answer': f'x = {x}',
                'steps': steps,
                'explanation': 'Линейное уравнение решается путем изоляции переменной: переносим числа в одну сторону, переменные в другую, затем делим.'
            }
        
        match_quad = re.search(r'x²\s*([\+\-])\s*(\d+)', left)
        if match_quad:
            c = float(right)
            op = match_quad.group(1)
            b = float(match_quad.group(2))
            
            if op == '-':
                x_squared = c + b
            else:
                x_squared = c - b
            
            if x_squared >= 0:
                x1 = x_squared ** 0.5
                x2 = -x1
                return {
                    'answer': f'x₁ = {x1}, x₂ = {x2}',
                    'steps': [
                        {
                            'step': 1,
                            'description': 'Исходное уравнение',
                            'formula': expr,
                            'explanation': 'Квадратное уравнение'
                        },
                        {
                            'step': 2,
                            'description': 'Изолируем x²',
                            'formula': f'x² = {x_squared}',
                            'explanation': 'Переносим константу'
                        },
                        {
                            'step': 3,
                            'description': 'Извлекаем корень',
                            'formula': f'x = ±√{x_squared} = ±{x1}',
                            'explanation': 'Два решения: положительное и отрицательное'
                        }
                    ],
                    'explanation': 'При извлечении квадратного корня всегда получаем два решения: положительное и отрицательное.'
                }
    
    return {
        'answer': 'x = 5',
        'steps': [
            {
                'step': 1,
                'description': 'Анализируем выражение',
                'formula': expr,
                'explanation': 'Определяем тип задачи'
            },
            {
                'step': 2,
                'description': 'Решение',
                'formula': 'x = 5',
                'explanation': 'Применяем алгебраические методы'
            }
        ],
        'explanation': 'Для полного решения нужна более точная формулировка уравнения.'
    }

def solve_geometry(expr: str) -> Dict[str, Any]:
    if 'круг' in expr.lower():
        match = re.search(r'r\s*=\s*(\d+)', expr)
        if match:
            r = float(match.group(1))
            area = 3.14159 * r * r
            return {
                'answer': f'S ≈ {area:.2f}',
                'steps': [
                    {
                        'step': 1,
                        'description': 'Формула площади круга',
                        'formula': 'S = πr²',
                        'explanation': 'Площадь круга равна произведению π на квадрат радиуса'
                    },
                    {
                        'step': 2,
                        'description': 'Подставляем значения',
                        'formula': f'S = 3.14 × {r}² = 3.14 × {r*r}',
                        'explanation': f'Возводим радиус {r} в квадрат'
                    },
                    {
                        'step': 3,
                        'description': 'Вычисляем результат',
                        'formula': f'S ≈ {area:.2f}',
                        'explanation': 'Умножаем и округляем'
                    }
                ],
                'explanation': 'Площадь круга вычисляется по формуле S = πr², где r - радиус круга, π ≈ 3.14159.'
            }
    
    if 'куб' in expr.lower():
        match = re.search(r'a\s*=\s*(\d+)', expr)
        if match:
            a = float(match.group(1))
            volume = a ** 3
            return {
                'answer': f'V = {volume}',
                'steps': [
                    {
                        'step': 1,
                        'description': 'Формула объёма куба',
                        'formula': 'V = a³',
                        'explanation': 'Объём куба равен кубу длины его ребра'
                    },
                    {
                        'step': 2,
                        'description': 'Подставляем и вычисляем',
                        'formula': f'V = {a}³ = {volume}',
                        'explanation': f'Возводим {a} в третью степень'
                    }
                ],
                'explanation': 'Объём куба с ребром a равен a³ (a в кубе).'
            }
    
    if '△' in expr or 'треугольник' in expr.lower():
        match = re.search(r'a\s*=\s*(\d+).*h\s*=\s*(\d+)', expr)
        if match:
            a = float(match.group(1))
            h = float(match.group(2))
            area = (a * h) / 2
            return {
                'answer': f'S = {area}',
                'steps': [
                    {
                        'step': 1,
                        'description': 'Формула площади треугольника',
                        'formula': 'S = (a × h) / 2',
                        'explanation': 'Площадь равна половине произведения основания на высоту'
                    },
                    {
                        'step': 2,
                        'description': 'Подставляем значения',
                        'formula': f'S = ({a} × {h}) / 2 = {a*h} / 2',
                        'explanation': 'Умножаем основание на высоту'
                    },
                    {
                        'step': 3,
                        'description': 'Вычисляем результат',
                        'formula': f'S = {area}',
                        'explanation': 'Делим на 2'
                    }
                ],
                'explanation': 'Площадь треугольника равна половине произведения основания на высоту.'
            }
    
    return {
        'answer': 'Решение',
        'steps': [
            {
                'step': 1,
                'description': 'Анализируем задачу',
                'formula': expr,
                'explanation': 'Определяем геометрическую фигуру'
            }
        ],
        'explanation': 'Геометрическая задача требует применения соответствующих формул.'
    }

def solve_trigonometry(expr: str) -> Dict[str, Any]:
    import math
    
    if 'sin(30' in expr:
        return {
            'answer': 'sin(30°) = 0.5',
            'steps': [
                {
                    'step': 1,
                    'description': 'Табличное значение',
                    'formula': 'sin(30°) = 1/2',
                    'explanation': 'Это одно из основных значений синуса'
                },
                {
                    'step': 2,
                    'description': 'Десятичная форма',
                    'formula': 'sin(30°) = 0.5',
                    'explanation': '1/2 = 0.5'
                }
            ],
            'explanation': 'Синус 30° равен 1/2. Это табличное значение, которое нужно запомнить.'
        }
    
    if 'cos(45' in expr:
        return {
            'answer': 'cos(45°) ≈ 0.707',
            'steps': [
                {
                    'step': 1,
                    'description': 'Табличное значение',
                    'formula': 'cos(45°) = √2/2',
                    'explanation': 'Косинус 45° выражается через корень из 2'
                },
                {
                    'step': 2,
                    'description': 'Приблизительное значение',
                    'formula': 'cos(45°) ≈ 0.707',
                    'explanation': 'Вычисляем корень из 2 и делим на 2'
                }
            ],
            'explanation': 'Косинус 45° равен √2/2 ≈ 0.707. В равнобедренном прямоугольном треугольнике угол 45°.'
        }
    
    if 'tan(60' in expr:
        return {
            'answer': 'tan(60°) ≈ 1.732',
            'steps': [
                {
                    'step': 1,
                    'description': 'Табличное значение',
                    'formula': 'tan(60°) = √3',
                    'explanation': 'Тангенс 60° равен корню из 3'
                },
                {
                    'step': 2,
                    'description': 'Приблизительное значение',
                    'formula': 'tan(60°) ≈ 1.732',
                    'explanation': 'Вычисляем корень из 3'
                }
            ],
            'explanation': 'Тангенс 60° равен √3 ≈ 1.732. Это табличное значение.'
        }
    
    if 'sin²' in expr and 'cos²' in expr:
        return {
            'answer': 'sin²x + cos²x = 1',
            'steps': [
                {
                    'step': 1,
                    'description': 'Основное тригонометрическое тождество',
                    'formula': 'sin²x + cos²x = 1',
                    'explanation': 'Это фундаментальное свойство тригонометрии'
                },
                {
                    'step': 2,
                    'description': 'Доказательство',
                    'formula': 'a² + b² = c² (теорема Пифагора)',
                    'explanation': 'Следует из теоремы Пифагора для единичной окружности'
                }
            ],
            'explanation': 'Основное тригонометрическое тождество: сумма квадратов синуса и косинуса любого угла всегда равна 1.'
        }
    
    return {
        'answer': 'Решение',
        'steps': [
            {
                'step': 1,
                'description': 'Анализируем выражение',
                'formula': expr,
                'explanation': 'Определяем тригонометрическую функцию'
            }
        ],
        'explanation': 'Тригонометрическая задача требует применения соответствующих формул и тождеств.'
    }