# 🥗 Nutrition Tracker - Raspberry Pi Zero 2W Edition

Оптимизированная версия Nutrition Tracker специально для Raspberry Pi Zero 2W с ограниченными ресурсами (512MB RAM).

## 📋 Системные требования

- **Raspberry Pi Zero 2W** (512MB RAM)
- **microSD карта** Class 10 или лучше (минимум 8GB)
- **Raspberry Pi OS** (32-bit)
- **Стабильное WiFi подключение**

## 🚀 Быстрый старт

### 1. Подготовка системы

```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите необходимые пакеты
sudo apt install -y curl git python3-pip

# Клонируйте репозиторий
git clone <repository-url>
cd nutricount
```

### 2. Автоматическая установка

```bash
# Сделайте скрипт исполняемым
chmod +x scripts/pi-zero-setup.sh

# Запустите автоматическую установку
./scripts/pi-zero-setup.sh
```

### 3. Ручная установка

```bash
# Установите Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установите Docker Compose
sudo pip3 install docker-compose

# Создайте .env файл
cp env.example .env

# Соберите и запустите
docker-compose -f docker-compose.pi-zero.yml up -d
```

## ⚙️ Оптимизации для Pi Zero 2W

### Память (300MB лимит)
- **Gunicorn**: 1 воркер вместо 4
- **Nginx**: минимальная конфигурация
- **Docker**: ограничения памяти
- **Логирование**: отключено для экономии места

### CPU (1 ядро)
- **Воркеры**: синхронные вместо асинхронных
- **Таймауты**: увеличены для медленной обработки
- **Сжатие**: минимальный уровень gzip

### Диск
- **Логи**: ограничены размером и количеством
- **Swap**: увеличен до 1GB
- **Кэш**: минимальный размер

## 📊 Мониторинг производительности

```bash
# Запустите мониторинг
chmod +x scripts/pi-zero-monitor.sh
./scripts/pi-zero-monitor.sh

# Непрерывный мониторинг
./scripts/pi-zero-monitor.sh --continuous
```

## 🔧 Управление сервисом

```bash
# Запуск
docker-compose -f docker-compose.pi-zero.yml up -d

# Остановка
docker-compose -f docker-compose.pi-zero.yml down

# Перезапуск
docker-compose -f docker-compose.pi-zero.yml restart

# Просмотр логов
docker-compose -f docker-compose.pi-zero.yml logs -f

# Автозапуск при загрузке
sudo systemctl enable nutrition-tracker
```

## 🌐 Доступ к приложению

- **Веб-интерфейс**: `http://<pi-ip>:80`
- **API**: `http://<pi-ip>:5000`
- **Health check**: `http://<pi-ip>:5000/health`

## 📈 Ожидаемая производительность

### ✅ Что работает отлично:
- Запуск приложения: 30-60 секунд
- API запросы: 50-200ms
- До 5-10 одновременных пользователей
- База данных до 10,000 записей

### ⚠️ Ограничения:
- Медленный запуск (1-2 минуты)
- Задержки при высокой нагрузке
- Рекомендуется SSD карта
- Регулярные перезапуски для очистки памяти

## 🛠️ Устранение неполадок

### Высокое использование памяти
```bash
# Перезапустите контейнеры
docker-compose -f docker-compose.pi-zero.yml restart

# Очистите неиспользуемые образы
docker system prune -f

# Проверьте использование памяти
free -h
```

### Медленная работа
```bash
# Проверьте температуру
vcgencmd measure_temp

# Проверьте CPU нагрузку
top

# Увеличьте swap
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Проблемы с сетью
```bash
# Проверьте статус контейнеров
docker-compose -f docker-compose.pi-zero.yml ps

# Проверьте логи
docker-compose -f docker-compose.pi-zero.yml logs nutrition-tracker-pi
```

## 🔒 Безопасность

- Приложение запускается под непривилегированным пользователем
- Nginx настроен с базовыми заголовками безопасности
- Rate limiting для защиты от DDoS
- Ограничения на размер запросов

## 📝 Логирование

Логи ограничены для экономии места:
- **Размер лога**: максимум 10MB
- **Количество файлов**: 1
- **Уровень логирования**: warning и выше

## 🔄 Обновления

```bash
# Обновите код
git pull origin main

# Пересоберите контейнеры
docker-compose -f docker-compose.pi-zero.yml build --no-cache

# Перезапустите сервис
docker-compose -f docker-compose.pi-zero.yml up -d
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose -f docker-compose.pi-zero.yml logs`
2. Запустите мониторинг: `./scripts/pi-zero-monitor.sh`
3. Проверьте системные ресурсы: `free -h`, `df -h`
4. Создайте issue в репозитории

## 🎯 Рекомендации

- Используйте **Class 10** или лучше microSD карту
- Обеспечьте **хорошую вентиляцию** для предотвращения перегрева
- **Регулярно перезапускайте** приложение для очистки памяти
- **Мониторьте логи** на предмет ошибок
- Используйте **стабильное WiFi** подключение

---

**Примечание**: Эта версия оптимизирована для Pi Zero 2W. Для продакшн использования с множественными пользователями рекомендуется Raspberry Pi 4 (4GB+).
