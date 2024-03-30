## Налаштування оточення
1. **Створення та запуск Multipass контейнера:**
   - Скачайте та встановіть [Multipass](https://multipass.run/download/windows) та [VirtualBox](https://www.virtualbox.org/wiki/Downloads), якщо у вас Windows Home.
   - Запустіть PowerShell від імені адміна.
   - Створіть новий контейнер за допомогою команди:
     ```bash
     multipass launch 22.04 --name nc-ftp
     ```
   - Запустіть контейнер:
     ```bash
     multipass start nc-ftp
     ```
2. **Налаштування мережі для Windows Home:**
   - Зупиніть контейнер:
     ```bash
     multipass stop nc-ftp
     ```
   - [Завантажте](https://discourse.ubuntu.com/t/how-to-use-virtualbox-in-multipass-on-windows/16626#heading--finding-multipass-instances-in-virtualbox) та розпакуйте PSTools.zip у папку Downloads.
   - Виконайте команду:
     ```bash
     $env:USERPROFILE\Downloads\PSTools\PsExec.exe -s -i $env:VBOX_MSI_INSTALL_PATH\VirtualBox.exe
     ```
   - Відкрийте DHCP сервер і встановіть нижню межу адрес на 192.168.56.2.
   - Зайдіть в контейнер:
     ```bash
     multipass shell nc-ftp
     ```
   - Відкрийте файловий редактор:
     ```bash
     sudo nano /etc/netplan/60-extra-interfaces.yaml
     ```
   - Додайте наступний блок з належними відступами та пустим рядком знизу:
     ```yaml
     network:
       version: 2
       renderer: networkd
       ethernets:
         enp0s8:
           dhcp4: yes
     ```
   - Застосуйте зміни:
     ```bash
     sudo netplan apply
     ```
   - Встановіть net-tools:
     ```bash
     sudo apt install net-tools
     ```
   - Запустіть ```ifconfig```, щоб подивитись на новий ip адрес контейнера в enp0s8 інтерфейсі
3. **Налаштування SSH доступу:**
   - Відкрийте SSH конфіг:
     ```bash
     notepad C:\<User>\.ssh\config
     ```
   - Створіть конфігурацію для контейнера з пустим рядком знизу:
     ```bash
     Host nc-ftp
       Hostname CONTAINER_IP
       User ubuntu
     ```
   - Створіть:
     ```bash
     ssh-keygen -t ed25519
     ```
     та дістаньте публічний ключ:
     ```bash
     cat ~/.ssh/id_ed25519.pub
     ```
   - Додайте публічний ключ до контейнера:
     ```bash
     multipass exec nc-ftp -- bash -c "echo 'YOUR_PUBLIC_KEY' >> ~/.ssh/authorized_keys"
     ```
## Запуск Скрипта
   - Клонуйте репозиторій:
     ```bash
     git clone https://github.com/justmiroslav/nc-ftp.git
     ```
   - Перейдіть у каталог nc-ftp:
     ```bash
     cd nc-ftp/
     ```
   - Запустіть chmod_files.sh:
     ```bash
     bash chmod_files.sh
     ```
   - Запустіть скрипт setup_node.py, при бажанні вкажіть довірені IP-адреси як sys.argv:
     ```bash
     ./setup_node.py "192.168.0.5, 192.168.56.5"
     ```
   - Запустіть скрипт update_iptables.py за допомогою socat на порту 7777:
     ```bash
     socat TCP-LISTEN:7777,reuseaddr,fork EXEC:"./update_iptables.py"
     ```
## Реалізація скриптів
- **setup_node.py:** Приймає IP-адресу хоста та розгортає на ній FTP сервер, налаштовує правила iptables для вхідних пакетів, блокує всі вхідні TCP та ICMP echo-requests пакети, окрім тих, що передані як sys. А потім створює нового користувача ftp_user із домашньою директорією /home/ftp_user, додає 2 файли з вмістом “Hello World!” в директорію /home/ftp_user/ftp і надає всім користувачам повний доступ до цієї директорії.
- **update_iptables.py:** Автоматично дістає IP-адресу клієнта, перевіряє, чи є вона в файлі credentials.txt якщо так – просить ввести відповідний ключ, якщо ні – встановлює дію DROP для цієї IP-адреси, На основі введеного ключа скрипт також встановлює дію iptables - "ACCEPT" або "DROP".
