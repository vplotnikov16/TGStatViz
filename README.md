# TGStatViz

Инструмент для визуализации статистики Telegram-чатов с использованием Manim.

## Использование

### Установка зависимостей

```bash
poetry install
```

### FFmpeg

#### Windows

Скачать с [ffmpeg.org](https://ffmpeg.org/download.html), распаковать, добавить в PATH.

#### Linux

```bash
sudo apt install ffmpeg
```

#### macOS

```bash
brew install ffmpeg
```

## Использование

### Экспорт чата

1. Telegram Desktop → выбрать чат
2. Меню → Экспорт истории чата
3. Формат: JSON

### Команды

#### Список метрик

```bash
python run.py metrics
```


#### Список рендереров

```bash
python run.py renderers
```


#### Рендеринг видео

```bash
python run.py render <путь_к_экспорту> <путь_к_конфигу> -o <выходной_файл> -q <качество>
```

Параметры:

- `<путь_к_экспорту>` - директория с result.json
- `<путь_к_конфигу>` - YAML-файл раскадровки
- `-o` - путь к выходному файлу (опционально)
- `-q` - качество: low/medium/high (по умолчанию low)

Пример:

```bash
python run.py render exports/ChatExport_2026-01-02 configs/example.yaml -o output.mp4 -q low
```


## Формат конфигурации

```yaml
project:
  title: "Название"
  description: "Описание"

defaults:
  style: "dark"
  transition:
    name: "fade"
    duration: 0.5

slides:
  - metric: "personal.cumulative_messages"
    renderer: "animated_line_chart"
    duration: 10
```

Поля:

- `project.title` — название проекта
- `project.description` — описание (опционально)
- `slides` — список слайдов
    - `metric` — ID метрики
    - `renderer` — ID рендерера
    - `duration` — длительность в секундах
    - `params` — параметры метрики (опционально)

    
## Разработка

### Тесты

```bash
poetry run pytest
```


### Линтинг

```bash
poetry run pylint src/
```
