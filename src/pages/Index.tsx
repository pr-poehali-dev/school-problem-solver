import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Icon from '@/components/ui/icon';
import { Badge } from '@/components/ui/badge';

const Index = () => {
  const [expression, setExpression] = useState('');
  const [solution, setSolution] = useState<any>(null);
  const [selectedCategory, setSelectedCategory] = useState('algebra');

  const categories = [
    { id: 'arithmetic', name: 'Арифметика', icon: 'Calculator', color: 'from-purple-500 to-pink-500' },
    { id: 'algebra', name: 'Алгебра', icon: 'Variable', color: 'from-blue-500 to-cyan-500' },
    { id: 'geometry', name: 'Геометрия', icon: 'Triangle', color: 'from-orange-500 to-red-500' },
    { id: 'trigonometry', name: 'Тригонометрия', icon: 'Waves', color: 'from-green-500 to-teal-500' },
  ];

  const examples = {
    arithmetic: ['2 + 2', '15 × 8', '144 ÷ 12', '25% от 200'],
    algebra: ['2x + 5 = 15', 'x² - 4 = 0', '(x + 3)(x - 2)', 'x³ + 8'],
    geometry: ['S круга (r=5)', 'V куба (a=3)', 'Площадь △ (a=6, h=4)', 'Теорема Пифагора'],
    trigonometry: ['sin(30°)', 'cos(45°)', 'tan(60°)', 'sin²x + cos²x'],
  };

  const handleSolve = () => {
    const steps = [
      { step: 1, description: 'Упрощаем выражение', formula: expression, explanation: 'Начальное выражение' },
      { step: 2, description: 'Выполняем операции', formula: '2x = 10', explanation: 'Переносим константу вправо' },
      { step: 3, description: 'Находим решение', formula: 'x = 5', explanation: 'Делим обе части на 2' },
    ];
    
    setSolution({
      answer: 'x = 5',
      steps: steps,
      explanation: 'Линейное уравнение решается путем изоляции переменной.',
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12 animate-fade-in">
          <div className="inline-block mb-4">
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-4 rounded-2xl shadow-lg">
              <Icon name="GraduationCap" size={48} />
            </div>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent mb-4">
            МатемаРешка
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Решаем математические задачи с подробными объяснениями
          </p>
        </header>

        <div className="grid md:grid-cols-4 gap-4 mb-8 animate-slide-up">
          {categories.map((category, index) => (
            <Card 
              key={category.id}
              className={`cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-xl ${
                selectedCategory === category.id ? 'ring-2 ring-purple-500 shadow-lg' : ''
              }`}
              style={{ animationDelay: `${index * 100}ms` }}
              onClick={() => setSelectedCategory(category.id)}
            >
              <CardContent className="p-6 text-center">
                <div className={`bg-gradient-to-r ${category.color} w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 text-white shadow-lg`}>
                  <Icon name={category.icon} size={32} />
                </div>
                <h3 className="font-semibold text-lg">{category.name}</h3>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card className="mb-8 shadow-2xl border-0 animate-scale-in overflow-hidden">
          <div className="bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 p-6">
            <CardHeader className="text-white p-0">
              <CardTitle className="text-2xl flex items-center gap-2">
                <Icon name="Sparkles" size={28} />
                Введи задачу
              </CardTitle>
              <CardDescription className="text-purple-100">
                Выбери пример или напиши свой
              </CardDescription>
            </CardHeader>
          </div>
          
          <CardContent className="p-6">
            <div className="flex flex-wrap gap-2 mb-4">
              {examples[selectedCategory as keyof typeof examples].map((example, idx) => (
                <Badge 
                  key={idx}
                  variant="secondary"
                  className="cursor-pointer hover:scale-105 transition-transform px-4 py-2 text-sm"
                  onClick={() => setExpression(example)}
                >
                  {example}
                </Badge>
              ))}
            </div>

            <div className="flex gap-3">
              <Input
                type="text"
                placeholder="Например: 2x + 5 = 15"
                value={expression}
                onChange={(e) => setExpression(e.target.value)}
                className="text-lg py-6 border-2 focus:border-purple-500"
                onKeyPress={(e) => e.key === 'Enter' && handleSolve()}
              />
              <Button 
                onClick={handleSolve}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-6 text-lg shadow-lg"
                disabled={!expression}
              >
                <Icon name="Zap" size={20} className="mr-2" />
                Решить
              </Button>
            </div>
          </CardContent>
        </Card>

        {solution && (
          <Card className="shadow-2xl border-0 animate-fade-in">
            <div className="bg-gradient-to-r from-green-500 to-teal-500 p-6">
              <CardHeader className="text-white p-0">
                <CardTitle className="text-3xl flex items-center gap-2">
                  <Icon name="CheckCircle" size={32} />
                  Решение
                </CardTitle>
              </CardHeader>
            </div>

            <CardContent className="p-6">
              <div className="bg-gradient-to-r from-green-50 to-teal-50 p-6 rounded-xl mb-6 border-2 border-green-200">
                <p className="text-sm text-gray-600 mb-2">Ответ:</p>
                <p className="text-4xl font-bold text-green-700">{solution.answer}</p>
              </div>

              <Tabs defaultValue="steps" className="w-full">
                <TabsList className="grid w-full grid-cols-2 mb-6">
                  <TabsTrigger value="steps" className="text-lg">
                    <Icon name="List" size={20} className="mr-2" />
                    Пошаговое решение
                  </TabsTrigger>
                  <TabsTrigger value="explanation" className="text-lg">
                    <Icon name="Lightbulb" size={20} className="mr-2" />
                    Объяснение
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="steps" className="space-y-4">
                  {solution.steps.map((step: any, idx: number) => (
                    <Card key={idx} className="border-l-4 border-l-purple-500 hover:shadow-lg transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex items-start gap-4">
                          <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold flex-shrink-0">
                            {step.step}
                          </div>
                          <div className="flex-1">
                            <h4 className="font-semibold text-lg mb-2">{step.description}</h4>
                            <div className="bg-gray-50 p-4 rounded-lg mb-2">
                              <code className="text-lg font-mono text-purple-700">{step.formula}</code>
                            </div>
                            <p className="text-gray-600">{step.explanation}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </TabsContent>

                <TabsContent value="explanation">
                  <Card className="border-l-4 border-l-blue-500">
                    <CardContent className="p-6">
                      <div className="flex items-start gap-4">
                        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white p-3 rounded-full flex-shrink-0">
                          <Icon name="BookOpen" size={24} />
                        </div>
                        <div>
                          <h4 className="font-semibold text-lg mb-3">Как это работает?</h4>
                          <p className="text-gray-700 leading-relaxed">{solution.explanation}</p>
                          <div className="mt-4 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                            <p className="text-sm text-blue-800">
                              <Icon name="Info" size={16} className="inline mr-2" />
                              Совет: Всегда проверяй решение, подставив ответ в исходное уравнение!
                            </p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        )}

        {!solution && (
          <div className="text-center py-12 animate-float">
            <div className="bg-gradient-to-r from-purple-100 to-pink-100 w-32 h-32 rounded-full flex items-center justify-center mx-auto mb-6">
              <Icon name="PenTool" size={64} className="text-purple-600" />
            </div>
            <h3 className="text-2xl font-semibold text-gray-700 mb-2">Готов решать задачи!</h3>
            <p className="text-gray-500">Выбери категорию и введи выражение выше</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Index;
