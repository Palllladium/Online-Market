#!/usr/bin/env python3

import os
from pathlib import Path

def main():
    current_dir = Path(".").resolve()
    output_file = "PROJECT_STRUCTURE.txt"
    
    print(f"📁 Сканируем: {current_dir}")
    print(f"💾 Сохраняем в: {output_file}")
    
    # Игнорируемые элементы
    ignored = {'.git', '__pycache__', '.pytest_cache', '.vscode', 
               '.idea', 'node_modules', 'venv',
               output_file, '.DS_Store', 'Thumbs.db'}
    
    # Собираем структуру
    structure = []
    contents = []
    
    # Функция для чтения с правильной кодировкой
    def read_file_smart(filepath):
        filename = filepath.name.lower()
        
        # Особые файлы - сначала пробуем UTF-16 LE
        if filename in ['requirements.txt', 'readme.md']:
            for encoding in ['utf-16-le', 'utf-16', 'utf-8', 'cp1251']:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        content = f.read()
                        if content.startswith('\ufeff'):
                            content = content[1:]
                        print(f"  ✓ {filepath.name} ({encoding})")
                        return content
                except:
                    continue
            return f"[Не удалось прочитать {filename} ни в одной кодировке]"
        
        # Остальные текстовые файлы
        text_exts = {'.py', '.txt', '.md', '.json', '.yml', '.yaml', 
                    '.html', '.css', '.js', '.xml', '.ini', '.cfg'}
        if filepath.suffix.lower() in text_exts:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                try:
                    with open(filepath, 'r', encoding='cp1251') as f:
                        return f.read()
                except:
                    return f"[Бинарный файл или ошибка кодировки]"
        
        return "[Бинарный файл]"
    
    # Строим дерево
    def build_tree(dir_path, prefix=""):
        try:
            items = sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except:
            return
        
        dirs = [i for i in items if i.is_dir() and i.name not in ignored]
        files = [i for i in items if i.is_file() and i.name not in ignored]
        
        for i, item in enumerate(dirs + files):
            is_last = (i == len(dirs + files) - 1)
            is_dir = item.is_dir()
            
            if is_dir:
                structure.append(f"{prefix}{'└── ' if is_last else '├── '}📁 {item.name}/")
                build_tree(item, prefix + ("    " if is_last else "│   "))
            else:
                structure.append(f"{prefix}{'└── ' if is_last else '├── '}📄 {item.name}")
                
                # Собираем содержимое файла
                rel_path = item.relative_to(current_dir)
                content = read_file_smart(item)
                contents.append({
                    'path': rel_path,
                    'content': content[:50000] + "\n[... обрезано ...]" if len(content) > 50000 else content
                })
    
    # Собираем данные
    structure.append(f"📁 {current_dir.name}/")
    build_tree(current_dir)
    
    # Записываем в файл
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"ПОЛНАЯ СТРУКТУРА ПРОЕКТА\n")
        f.write(f"Директория: {current_dir}\n")
        f.write("=" * 100 + "\n\n")
        
        f.write("ДРЕВОВИДНАЯ СТРУКТУРА:\n")
        f.write("-" * 50 + "\n")
        for line in structure:
            f.write(line + "\n")
        
        f.write("\n" + "=" * 100 + "\n\n")
        f.write("СОДЕРЖИМОЕ ФАЙЛОВ:\n")
        f.write("=" * 100 + "\n\n")
        
        for item in contents:
            f.write(f"\n📄 {item['path']}\n")
            f.write("-" * 50 + "\n")
            f.write(item['content'])
            f.write(f"\n" + "=" * 50 + "\n")
    
    print(f"\n✅ Готово! Файл сохранен: {output_file}")
    print(f"📊 Строк структуры: {len(structure)}")
    print(f"📄 Файлов обработано: {len(contents)}")

if __name__ == "__main__":
    main()