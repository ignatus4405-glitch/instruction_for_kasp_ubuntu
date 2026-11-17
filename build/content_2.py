# -*- coding: utf-8 -*-
"""Часть 2: СУБД MariaDB и установка Kaspersky Security Center Linux."""

BLOCKS = []
B = BLOCKS.append

# ---------------------------------------------------------------- 4
B(("h1", "4. Установка и настройка СУБД MariaDB"))

B(("p", "Сервер администрирования KSC хранит все данные в СУБД. От корректности её настройки "
        "зависит устойчивость работы KSC, поэтому разделу 4.4 (параметры сервера) следует уделить "
        "особое внимание: параметры рекомендованы производителем и отличаются от значений MariaDB "
        "по умолчанию."))

B(("h2", "4.1. Установка MariaDB Server"))
B(("code", [
    "sudo -i",
    "apt update",
    "apt -y install mariadb-server",
    "systemctl enable --now mariadb",
    "systemctl status mariadb --no-pager",
]))
B(("p", "Убедитесь, что версия СУБД поддерживается KSC 15.2 (MariaDB 10.11, сборка не ниже 10.11.10):"))
B(("code", [
    "mariadb --version",
    "# ожидается, например: mariadb  Ver 15.1 Distrib 10.11.14-MariaDB",
]))
B(("warn", "Если установленная сборка ниже 10.11.10 (возможно при установке с необновлённого ISO), "
           "выполните `apt -y full-upgrade` и переустановите пакет либо используйте официальный "
           "репозиторий MariaDB. Проверка версии обязательна: на неподдерживаемой сборке установка "
           "KSC завершится ошибкой."))

B(("h2", "4.2. Начальная защита СУБД"))
B(("p", "В Ubuntu учётная запись `root` в MariaDB использует аутентификацию `unix_socket`, поэтому "
        "пароль для неё задавать не обязательно — доступ получает только root ОС. Запустите мастер:"))
B(("code", [
    "mariadb-secure-installation",
    "# (в старых версиях — mysql_secure_installation)",
]))
B(("p", "Ответы на вопросы мастера:"))
B(("table", {
    "head": ["Вопрос", "Ответ"],
    "widths": [58, 42],
    "rows": [
        ["Enter current password for root", "Enter (пароль не задан)"],
        ["Switch to unix_socket authentication", "n (оставить unix_socket)"],
        ["Change the root password?", "n (не требуется при unix_socket)"],
        ["Remove anonymous users?", "Y"],
        ["Disallow root login remotely?", "Y"],
        ["Remove test database and access to it?", "Y"],
        ["Reload privilege tables now?", "Y"],
    ],
}))

B(("h2", "4.3. Проверка параметров прослушивания и кодировки"))
B(("code", [
    "ss -tlnp | grep 3306          # ожидается 127.0.0.1:3306, а не 0.0.0.0:3306",
    "mariadb -e \"SELECT @@version, @@character_set_server, @@collation_server, @@bind_address;\"",
]))
B(("p", "Если в выводе адрес `0.0.0.0`, ограничьте прослушивание локальным интерфейсом. Создайте файл "
        "`/etc/mysql/mariadb.conf.d/99-ksc-bind.cnf`:"))
B(("code", [
    "[mysqld]",
    "bind-address = 127.0.0.1",
]))
B(("note", "При варианте Б (СУБД на отдельном сервере) вместо `127.0.0.1` укажите внутренний "
           "IP-адрес сервера БД и разрешите подключение только с адреса Сервера администрирования "
           "средствами межсетевого экрана."))

B(("h2", "4.4. Настройка параметров MariaDB для KSC"))
B(("p", "Создайте отдельный файл конфигурации (drop-in), чтобы не изменять штатные файлы пакета:"))
B(("code", [
    "nano /etc/mysql/mariadb.conf.d/99-ksc.cnf",
]))
B(("p", "Содержимое файла (значения соответствуют официальным рекомендациям KSC 15.2; "
        "`innodb_buffer_pool_size` — см. пояснение ниже):"))
B(("code", [
    "[mysqld]",
    "sort_buffer_size=10M",
    "join_buffer_size=100M",
    "join_buffer_space_limit=300M",
    "join_cache_level=8",
    "tmp_table_size=512M",
    "max_heap_table_size=512M",
    "key_buffer_size=200M",
    "innodb_buffer_pool_size=6G",
    "innodb_thread_concurrency=20",
    "innodb_flush_log_at_trx_commit=0",
    "innodb_lock_wait_timeout=300",
    "max_allowed_packet=32M",
    "max_connections=151",
    "max_prepared_stmt_count=12800",
    "table_open_cache=60000",
    "table_open_cache_instances=4",
    "table_definition_cache=60000",
    "innodb_file_per_table=1",
    "sql_mode=\"STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION\"",
    "optimizer_prune_level=0",
    "optimizer_search_depth=8",
]))
B(("table", {
    "head": ["Параметр", "Как выбрать значение"],
    "widths": [26, 74],
    "rows": [
        ["innodb_buffer_pool_size", "Не менее 80 % ожидаемого размера БД, но не более 50–60 % ОЗУ сервера, "
                                    "если на нём же работает Сервер администрирования. Для 16 ГБ ОЗУ — 6G, "
                                    "для 8 ГБ — 3G"],
        ["sql_mode", "Значение приведено по документации KSC. Если MariaDB не запускается с ним "
                     "(в некоторых сборках режим `NO_AUTO_CREATE_USER` отсутствует), удалите этот режим "
                     "из списка — остальные значения оставьте без изменений"],
        ["optimizer_prune_level / optimizer_search_depth", "Обязательны для MariaDB 10.6 и новее "
                                                           "(в том числе 10.11)"],
        ["max_connections", "151 достаточно для одного Сервера администрирования; не увеличивайте без "
                            "необходимости — растёт потребление ОЗУ"],
    ],
}))
B(("warn", "Параметр `innodb_flush_log_at_trx_commit=0` рекомендован производителем и повышает "
           "производительность, но при аварийном завершении возможна потеря последних транзакций. "
           "Если это неприемлемо, согласуйте значение `1` и учтите снижение скорости работы."))

B(("h2", "4.5. Увеличение лимита файловых дескрипторов для MariaDB"))
B(("p", "При `table_open_cache=60000` службе MariaDB требуется повышенный лимит открытых файлов."))
B(("code", [
    "systemctl edit mariadb.service",
    "# в открывшемся редакторе добавьте:",
    "[Service]",
    "LimitNOFILE=1048576",
    "# сохраните файл и примените:",
    "systemd-analyze verify mariadb.service",
    "systemctl daemon-reload",
    "systemctl restart mariadb",
]))

B(("h2", "4.6. Перезапуск и проверка применённых параметров"))
B(("code", [
    "systemctl restart mariadb",
    "systemctl status mariadb --no-pager",
    "mariadb -e \"SHOW VARIABLES WHERE Variable_name IN",
    "  ('innodb_buffer_pool_size','table_open_cache','max_connections',",
    "   'sql_mode','innodb_file_per_table');\"",
    "mariadb -e \"SELECT @@optimizer_switch;\" | tr ',' '\\n' | grep -E 'join_cache'",
]))
B(("p", "В выводе `join_cache_incremental`, `join_cache_hashed` и `join_cache_bka` должны иметь "
        "значение `on`. Если какой-либо из них выключен, добавьте в файл `99-ksc.cnf` строки:"))
B(("code", [
    "optimizer_switch='join_cache_incremental=on'",
    "optimizer_switch='join_cache_hashed=on'",
    "optimizer_switch='join_cache_bka=on'",
]))

B(("h2", "4.7. Создание базы данных и учётной записи СУБД"))
B(("p", "Учётная запись СУБД (`KSCAdmin`) используется установщиком и службой Сервера администрирования. "
        "Пароль должен содержать не менее 12 символов; сохраните его в хранилище секретов."))
B(("code", [
    "mariadb",
]))
B(("p", "В консоли MariaDB выполните скрипт (замените `<пароль>` на согласованный пароль):"))
B(("code", [
    "CREATE DATABASE kav",
    "  DEFAULT CHARACTER SET ascii",
    "  DEFAULT COLLATE ascii_general_ci;",
    "",
    "CREATE USER 'KSCAdmin' IDENTIFIED BY '<пароль>';",
    "",
    "GRANT USAGE ON *.* TO 'KSCAdmin';",
    "GRANT ALL ON kav.* TO 'KSCAdmin';",
    "GRANT SELECT, SHOW VIEW ON mysql.* TO 'KSCAdmin';",
    "GRANT SELECT, SHOW VIEW ON sys.* TO 'KSCAdmin';",
    "GRANT EXECUTE ON PROCEDURE sys.table_exists TO 'KSCAdmin';",
    "GRANT PROCESS ON *.* TO 'KSCAdmin';",
    "GRANT SUPER ON *.* TO 'KSCAdmin';",
    "FLUSH PRIVILEGES;",
    "",
    "SHOW GRANTS FOR 'KSCAdmin';",
    "EXIT;",
]))
B(("table", {
    "head": ["Право", "Назначение"],
    "widths": [40, 60],
    "rows": [
        ["ALL ON kav.*", "Полный доступ к базе данных Сервера администрирования (кроме GRANT OPTION)"],
        ["SELECT, SHOW VIEW ON mysql.*, sys.*", "Чтение системных представлений"],
        ["EXECUTE ON PROCEDURE sys.table_exists", "Проверка существования таблиц (не требуется для MariaDB 10.5 и старше)"],
        ["PROCESS, SUPER", "Глобальные привилегии, необходимые Серверу администрирования"],
    ],
}))
B(("note", "Кодировка базы данных задаётся как `ascii` с сопоставлением `ascii_general_ci` — это "
           "требование KSC (данные внутри хранятся в собственном формате приложения), а не ошибка."))
B(("p", "Проверьте подключение созданной учётной записью по TCP:"))
B(("code", [
    "mariadb -h 127.0.0.1 -P 3306 -u KSCAdmin -p -e \"SHOW DATABASES;\"",
    "# в списке должна присутствовать база kav",
]))

# ---------------------------------------------------------------- 5
B(("h1", "5. Установка Kaspersky Security Center Linux (Сервер администрирования)"))

B(("p", "Установка состоит из трёх шагов: подготовка служебных учётных записей и лимитов, установка "
        "пакета `ksc64`, первичная настройка скриптом `postinstall.pl`. Все действия выполняются "
        "от имени root."))

B(("h2", "5.1. Создание группы и служебной учётной записи"))
B(("code", [
    "sudo -i",
    "adduser ksc                       # пароль для служебной учётной записи; вход по ней не требуется",
    "groupadd kladmins",
    "gpasswd -a ksc kladmins",
    "usermod -g kladmins ksc",
    "id ksc                            # uid=... gid=... (kladmins), groups=... kladmins",
]))
B(("note", "Учётная запись `ksc` — непривилегированная: от её имени работают службы KSC. "
           "Использовать её для входа в систему и администрирования не следует."))

B(("h2", "5.2. Лимиты файловых дескрипторов"))
B(("p", "Добавьте в `/etc/security/limits.conf` строки (разделитель — табуляция):"))
B(("code", [
    "cat >> /etc/security/limits.conf <<'EOF'",
    "ksc     soft    nofile  32768",
    "ksc     hard    nofile  131072",
    "EOF",
]))
B(("p", "Проверьте результат:"))
B(("code", [
    "tail -3 /etc/security/limits.conf",
]))

B(("h2", "5.3. Размещение дистрибутива на сервере"))
B(("p", "Скопируйте оба установочных файла на сервер (например, через scp с рабочего места):"))
B(("code", [
    "# на рабочем месте (не на сервере):",
    "scp ksc64_15.2.0.<сборка>_amd64.deb \\",
    "    ksc-web-console-15.2.<сборка>.x86_64.deb \\",
    "    kscadmin@192.168.10.10:/tmp/ksc_install/",
    "",
    "# на сервере:",
    "mkdir -p /root/ksc_install",
    "mv /tmp/ksc_install/*.deb /root/ksc_install/",
    "ls -lh /root/ksc_install/",
]))

B(("h2", "5.4. Установка пакета Сервера администрирования"))
B(("code", [
    "cd /root/ksc_install",
    "apt install ./ksc64_15.2.0.<сборка>_amd64.deb",
]))
B(("p", "Пакет распаковывается в `/opt/kaspersky/ksc64`. Процесс настройки при этом ещё не запускается. "
        "Проверьте результат установки:"))
B(("code", [
    "dpkg -l | grep -i ksc",
    "ls -la /opt/kaspersky/ksc64/sbin | head -20",
]))

B(("h2", "5.5. Первичная настройка (postinstall.pl)"))
B(("p", "Запустите сценарий настройки:"))
B(("code", [
    "/opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl",
]))
B(("p", "Сценарий выводит текст Лицензионного соглашения и Политики конфиденциальности (прокрутка — "
        "пробел). Далее последовательно вводятся параметры. Значения для примера из раздела 2.1 "
        "приведены в таблице ниже; нажатие Enter оставляет значение по умолчанию."))
B(("table", {
    "head": ["№", "Запрос установщика", "Значение / действие"],
    "widths": [7, 58, 35],
    "rows": [
        ["1", "Принять условия Лицензионного соглашения (y/n)", "y"],
        ["2", "Принять Политику конфиденциальности (y/n)", "y"],
        ["3", "DNS-имя или статический IP-адрес Сервера администрирования",
         "ksc01.company.local"],
        ["4", "Номер SSL-порта Сервера администрирования", "13000 (Enter)"],
        ["5", "Ориентировочное количество управляемых устройств (1 — до 100, 2 — до 1000, 3 — более 1000)", "1"],
        ["6", "Имя группы безопасности для служб", "kladmins (Enter)"],
        ["7", "Учётная запись для службы Сервера администрирования", "ksc (Enter)"],
        ["8", "Учётная запись для остальных служб KSC", "ksc (Enter)"],
        ["9", "Тип установленной СУБД (1 — MySQL/MariaDB, 2 — PostgreSQL/Postgres Pro)", "1"],
        ["10", "DNS-имя или IP-адрес сервера БД", "127.0.0.1"],
        ["11", "Порт сервера БД", "3306 (Enter)"],
        ["12", "Имя базы данных", "kav"],
        ["13", "Учётная запись для доступа к БД", "KSCAdmin"],
        ["14", "Пароль учётной записи БД", "<пароль из раздела 4.7>"],
        ["15", "Учётная запись администратора KSC (для входа в Web Console)", "ksc"],
        ["16", "Пароль администратора KSC и его подтверждение", "<сложный пароль>"],
    ],
}))
B(("note", "Формулировки запросов могут незначительно отличаться между сборками 15.x. Ориентируйтесь "
           "на смысл вопроса и приведённые значения; для вопросов о портах и именах по умолчанию "
           "достаточно нажать Enter."))
B(("p", "Требования к паролю администратора KSC: длина от 8 до 256 символов; символы не менее чем "
        "из трёх групп — заглавные латинские буквы, строчные латинские буквы, цифры, специальные "
        "символы. Пароль не должен совпадать с именем учётной записи."))

B(("h2", "5.6. Создание администратора KSC вручную (если требуется)"))
B(("p", "Если на шаге 15–16 учётная запись не создавалась (например, при тихой установке), создайте "
        "администратора утилитой `kladduser`:"))
B(("code", [
    "/opt/kaspersky/ksc64/sbin/kladduser -n ksc -p '<сложный пароль>'",
]))
B(("p", "Проверить список учётных записей администраторов можно в Web Console (раздел 7.1) — "
        "непосредственно после первого входа."))

B(("h2", "5.7. Проверка служб и портов"))
B(("p", "После завершения настройки создаются и запускаются четыре службы:"))
B(("table", {
    "head": ["Служба", "Назначение", "Порт(ы)"],
    "widths": [30, 52, 18],
    "rows": [
        ["klnagent_srv", "Серверная часть Агента администрирования (обмен с управляемыми устройствами "
                         "и точками распространения)", "15000/udp, 13000/tcp"],
        ["kladminserver_srv", "Сервер администрирования (ядро KSC)", "13000/tcp+udp, 13299/tcp, 14000/tcp"],
        ["klactprx_srv", "Прокси активации", "внутренний"],
        ["klwebsrv_srv", "Служебный веб-сервер Сервера администрирования (публикация пакетов, OpenAPI)", "внутренний"],
    ],
}))
B(("code", [
    "systemctl status klnagent_srv --no-pager",
    "systemctl status kladminserver_srv --no-pager",
    "systemctl status klactprx_srv --no-pager",
    "systemctl status klwebsrv_srv --no-pager",
    "systemctl is-enabled klnagent_srv kladminserver_srv klactprx_srv klwebsrv_srv",
]))
B(("p", "Все службы должны находиться в состоянии `active (running)` и быть включены в автозагрузку "
        "(`enabled`). Проверьте прослушиваемые порты:"))
B(("code", [
    "ss -tulpn | grep -E ':(13000|13299|14000|8080)\\b'",
]))
B(("p", "Запуск служб вручную (при необходимости):"))
B(("code", [
    "systemctl start klnagent_srv kladminserver_srv klactprx_srv klwebsrv_srv",
    "systemctl enable klnagent_srv kladminserver_srv klactprx_srv klwebsrv_srv",
]))
B(("warn", "Если служба `kladminserver_srv` переходит в состояние `failed`, причину ищите в разделе 9.1: "
           "чаще всего это недоступность СУБД, неверные учётные данные БД или неподходящие параметры "
           "`sql_mode`/`table_open_cache`."))

B(("h2", "5.8. Установка в тихом режиме (файл ответов)"))
B(("p", "Для автоматизированного развёртывания используется файл ответов. Формат — обычный текст, "
        "по одной переменной в строке."))
B(("code", [
    "mkdir -p /root/ksc_install",
    "cat > /root/ksc_install/answers.txt <<'EOF'",
    "EULA_ACCEPTED=1",
    "PP_ACCEPTED=1",
    "KLSRV_UNATT_SERVERADDRESS=ksc01.company.local",
    "KLSRV_UNATT_PORT_SRV_SSL=13000",
    "KLSRV_UNATT_NETRANGETYPE=1",
    "KLSRV_UNATT_DBMS_TYPE=mysql",
    "KLSRV_UNATT_DBMS_INSTANCE=127.0.0.1",
    "KLSRV_UNATT_DBMS_PORT=3306",
    "KLSRV_UNATT_DB_NAME=kav",
    "KLSRV_UNATT_DBMS_LOGIN=KSCAdmin",
    "KLSRV_UNATT_DBMS_PASSWORD=<пароль БД>",
    "KLSRV_UNATT_KLADMINSGROUP=kladmins",
    "KLSRV_UNATT_KLSRVUSER=ksc",
    "KLSRV_UNATT_KLSVCUSER=ksc",
    "EOF",
    "",
    "export KLAUTOANSWERS=/root/ksc_install/answers.txt",
    "apt-get install ./ksc64_15.2.0.<сборка>_amd64.deb",
    "/opt/kaspersky/ksc64/sbin/kladduser -n ksc -p '<сложный пароль>'",
]))
B(("table", {
    "head": ["Переменная", "Обязательна", "Назначение", "Значение в примере"],
    "widths": [38, 12, 32, 18],
    "rows": [
        ["EULA_ACCEPTED", "Да", "Принятие Лицензионного соглашения", "1"],
        ["PP_ACCEPTED", "Да", "Принятие Политики конфиденциальности", "1"],
        ["KLSRV_UNATT_SERVERADDRESS", "Да", "DNS-имя или IP-адрес Сервера администрирования", "ksc01.company.local"],
        ["KLSRV_UNATT_PORT_SRV_SSL", "Нет", "SSL-порт Сервера администрирования (по умолчанию 13000)", "13000"],
        ["KLSRV_UNATT_PORT_SRV", "Нет", "Порт Сервера администрирования (по умолчанию 14000)", "—"],
        ["KLSRV_UNATT_PORT_KLOAPI", "Нет", "Порт OpenAPI/Web Console (по умолчанию 13299)", "—"],
        ["KLSRV_UNATT_NETRANGETYPE", "Нет", "Количество устройств (1/2/3)", "1"],
        ["KLSRV_UNATT_DBMS_TYPE", "Да", "Тип СУБД: `mysql` или `postgres`", "mysql"],
        ["KLSRV_UNATT_DBMS_INSTANCE", "Да", "Адрес сервера БД", "127.0.0.1"],
        ["KLSRV_UNATT_DBMS_PORT", "Да", "Порт БД (3306 / 5432)", "3306"],
        ["KLSRV_UNATT_DB_NAME", "Да", "Имя базы данных", "kav"],
        ["KLSRV_UNATT_DBMS_LOGIN", "Да", "Учётная запись БД", "KSCAdmin"],
        ["KLSRV_UNATT_DBMS_PASSWORD", "Да", "Пароль учётной записи БД", "<пароль>"],
        ["KLSRV_UNATT_KLADMINSGROUP", "Да", "Группа безопасности служб", "kladmins"],
        ["KLSRV_UNATT_KLSRVUSER", "Да", "Учётная запись службы Сервера администрирования", "ksc"],
        ["KLSRV_UNATT_KLSVCUSER", "Да", "Учётная запись остальных служб", "ksc"],
    ],
}))
B(("note", "При установке от имени обычного пользователя используйте `sudo -E apt-get install ...`, "
           "чтобы переменная `KLAUTOANSWERS` сохранилась в окружении."))

B(("h2", "5.9. Размещение файлов после установки"))
B(("table", {
    "head": ["Путь", "Содержимое"],
    "widths": [40, 60],
    "rows": [
        ["/opt/kaspersky/ksc64", "Программные файлы Сервера администрирования"],
        ["/opt/kaspersky/ksc64/sbin", "Утилиты управления (`kladduser`, `klbackup`, `klscflag` и др.)"],
        ["/opt/kaspersky/ksc64/lib/bin/setup", "Скрипты установки и настройки (`postinstall.pl`)"],
        ["/var/opt/kaspersky/klnagent_srv", "Данные Сервера администрирования (требуется не менее 10 ГБ)"],
        ["/var/opt/kaspersky/klnagent_srv/1093/cert", "Сертификаты Сервера администрирования (`klserver.cer`)"],
        ["/var/log/kaspersky", "Журналы и трассировки компонентов"],
        ["/etc/init.d / systemd units", "Службы `kl*_srv`"],
    ],
}))
