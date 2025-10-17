# SSH Keys для Raspberry Pi

## Ваши SSH ключи готовы! 🔑

### Быстрый способ добавить ключи на Pi:

```bash
# Автоматическое добавление ключей
./scripts/ssh_setup.sh --auto <IP_адрес_Pi>

# Или интерактивный режим
./scripts/ssh_setup.sh
```

### Ручной способ:

1. **Подключитесь к Pi по SSH:**
   ```bash
   ssh pi@<IP_адрес_Pi>
   # Пароль: raspberry
   ```

2. **Создайте SSH директорию:**
   ```bash
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   ```

3. **Добавьте публичный ключ:**
   ```bash
   nano ~/.ssh/authorized_keys
   ```

4. **Скопируйте один из этих ключей:**

   **ED25519 (рекомендуется):**
   ```
   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPjkdBEF7dyQD5I91ADNg94HseefcjtrF4RFl0BpCN+7 raspberry
   ```

   **RSA (резервный):**
   ```
   ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC9U8muvHJMtcDyjrKXaf7nOsL3mOViCt4PI2ziGOWBE1SBdlI+S+UrgqeTvr3JNxZTjn4O5iSgZyu6PDKrRK+w+eda0dF1kEDXIxgIOhE4KdmmwRNN0itkPGdneiMnkveHTga5MNxbYxTuQHqjLv5VzzcPK2D+JpwKGkydICJWi7VBczd7CqtGAAnAL8eadGDWgJ6W8MbfJUGISNUBhnodtcQZXEq7g9L7qhwDwsMg76GjTCCw49jvg3eMfM8Chzx64Rk1oCWMebHd7a/EuUoQBS/HL/oZFSBpkpSE4xSq7ykLzTn7kulTOGMmfrUysEo8sO5icdKWHofJZsImZfSLIkQM6ikaTHKkhajZtowF0aA4Xaq4OhUqo8GGkHJblzXh3XyMhLJubShnPxXJTB/kSDTM0HqNx1IryMQ4AKR409lPSkd5aYIbBP+ae+Qr/g7gSp5qcERtjlN0Oik1/fvRDJbX/4QdmQ1jwSRxrC/D1VE0HZ+DnIQRyKF2D2OiXbOyF8SXBUKu6FAp7gGO1YSIihFRtdwuJxHQwiI6aY0IdGvbonakhUVVDdYL0cJZYU2QkMYiebdjkH5cJerjRSQxJH9cNi467WO8Zso7h91a/wNgS15RxuDr40I0tL2Y3ktlEjvklcD+KXlRssmLxZki29CDDEsMlsh94P9ymq41vQ== raspberry
   ```

5. **Установите правильные права:**
   ```bash
   chmod 600 ~/.ssh/authorized_keys
   chmod 700 ~/.ssh
   ```

6. **Проверьте подключение:**
   ```bash
   ssh pi@<IP_адрес_Pi>
   ```

### Поиск Pi в сети:

```bash
# Автоматический поиск
./scripts/ssh_setup.sh --find

# Или ручной поиск
nmap -sn 192.168.1.0/24 | grep -A2 "Raspberry Pi"
```

### Тестирование подключения:

```bash
./scripts/ssh_setup.sh --test <IP_адрес_Pi>
```

## Безопасность 🔒

- **Используйте ED25519 ключ** - он более безопасный и быстрый
- **Отключите парольную аутентификацию** после настройки ключей:
  ```bash
  sudo nano /etc/ssh/sshd_config
  # Установите: PasswordAuthentication no
  sudo systemctl restart ssh
  ```
- **Измените пароль по умолчанию** перед отключением паролей

## Готово! 🎉

После настройки SSH ключей вы сможете подключаться к Pi без ввода пароля:
```bash
ssh pi@<IP_адрес_Pi>
```
