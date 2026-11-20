# -*- coding: utf-8 -*-
"""Часть 2: СУБД MariaDB 11.8 и установка Kaspersky Security Center Linux 17."""

BLOCKS = []
B = BLOCKS.append

# ---------------------------------------------------------------- 4
B(("h1", "4. Установка и настройка СУБД MariaDB"))

B(("p", "Сервер администрирования KSC хранит все данные в СУБД. От корректности её настройки "
        "зависит устойчивость работы KSC, поэтому разделу 4.4 (параметры сервера) следует уделить "
        "особое внимание: параметры рекомендованы производителем и отличаются от значений MariaDB "
        "по умолчанию."))
B(("note", "**Как выполнять команды в разделах 4–8.** Вставляйте в терминал по одной строке из блока "
           "и нажимайте `Enter`; следующую строку — после возврата приглашения (`root@ksc01:~#`). "
           "Строки, начинающиеся с `#`, — комментарии для чтения, их вводить не нужно. Если команда "
           "задаёт вопрос `[Y/n]`, нажмите `Enter` (значение по умолчанию — `Y`). Прервать выполнение — "
           "`Ctrl+C`. Копирование и вставка описаны в разделе 1.8."))

B(("h2", "4.1. Установка MariaDB Server"))
B(("p", "В состав Ubuntu Server 26.10 входит MariaDB 11.8 (пакет 11.8.8), которая входит в список "
        "СУБД, поддерживаемых Kaspersky Security Center Linux 17. Отдельный внешний репозиторий "
        "не требуется."))
B(("code", [
    "sudo -i",
    "apt update",
    "apt -y install mariadb-server",
    "systemctl enable --now mariadb",
    "systemctl status mariadb --no-pager",
]))
B(("p", "Убедитесь, что установлена поддерживаемая версия (MariaDB 11.8):"))
B(("code", [
    "mariadb --version",
    "# ожидается, например: mariadb  Ver 15.1 Distrib 11.8.8-MariaDB, for debian-linux-gnu (x86_64)",
]))
B(("warn", "KSC 17 поддерживает MariaDB 10.11 (сборка 10.11.10 и выше), 11.4, 11.8 и 12.3. Если в "
           "системе по каким-то причинам оказалась другая ветка СУБД, приведите её к 11.8 до установки "
           "KSC: на неподдерживаемой версии установка завершится ошибкой."))

B(("h2", "4.2. Начальная защита СУБД"))
B(("p", "В Ubuntu учётная запись `root` в MariaDB использует аутентификацию `unix_socket`, поэтому "
        "пароль для неё задавать не обязательно — доступ получает только root ОС. Запустите мастер:"))
B(("code", [
    "mariadb-secure-installation",
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
B(("note", "СУБД установлена на том же сервере, что и Сервер администрирования, поэтому `bind-address = "
           "127.0.0.1` — окончательное значение. Не заменяйте его на внешний IP-адрес сервера: база "
           "должна быть доступна только локально."))

B(("h2", "4.4. Настройка параметров MariaDB для KSC"))
B(("p", "Создайте отдельный файл конфигурации (drop-in), чтобы не изменять штатные файлы пакета:"))
B(("code", [
    "nano /etc/mysql/mariadb.conf.d/99-ksc.cnf",
]))
B(("p", "Содержимое файла (значения соответствуют официальным рекомендациям KSC 17; "
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
                                                           "(в том числе для 11.8)"],
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
    "# в открывшемся редакторе добавьте строки:",
    "[Service]",
    "LimitNOFILE=1048576",
    "# сохраните файл и примените:",
    "systemd-analyze verify mariadb.service",
    "systemctl daemon-reload",
    "systemctl restart mariadb",
]))
B(("note", "**Что происходит после команды** `systemctl edit`. Откроется редактор `nano` с пустым "
           "файлом на весь экран. Введите (или вставьте) две строки `[Service]` и "
           "`LimitNOFILE=1048576`, затем нажмите `Ctrl+O`, `Enter` (сохранить) и `Ctrl+X` (выйти). "
           "После выхода systemd покажет сообщение о создании файла "
           "`/etc/systemd/system/mariadb.service.d/override.conf`. Если редактор не открылся или "
           "открылся `vi`, выполните `EDITOR=nano systemctl edit mariadb.service`."))

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

B(("h2", "4.7. Создание баз данных и учётных записей СУБД"))
B(("p", "KSC 17 использует две базы данных: `kav` — данные Сервера администрирования и `iamdb` — "
        "данные службы IAM (идентификация и аутентификация, появилась в KSC 16). Каждая база "
        "обслуживается отдельной учётной записью СУБД: `KSCAdmin` и `KSCIAM`. Пароли должны содержать "
        "не менее 12 символов; сохраните их в хранилище секретов."))
B(("code", [
    "mariadb",
]))
B(("p", "В консоли MariaDB выполните скрипт (замените `<пароль>` и `<пароль IAM>` на согласованные "
        "пароли):"))
B(("code", [
    "CREATE DATABASE kav",
    "  DEFAULT CHARACTER SET ascii",
    "  DEFAULT COLLATE ascii_general_ci;",
    "CREATE DATABASE iamdb;",
    "",
    "CREATE USER 'KSCAdmin' IDENTIFIED BY '<пароль>';",
    "CREATE USER 'KSCIAM'   IDENTIFIED BY '<пароль IAM>';",
    "",
    "GRANT USAGE ON *.* TO 'KSCAdmin';",
    "GRANT ALL ON kav.* TO 'KSCAdmin';",
    "GRANT SELECT, SHOW VIEW ON mysql.* TO 'KSCAdmin';",
    "GRANT SELECT, SHOW VIEW ON sys.* TO 'KSCAdmin';",
    "GRANT EXECUTE ON PROCEDURE sys.table_exists TO 'KSCAdmin';",
    "GRANT PROCESS, SUPER, SET USER ON *.* TO 'KSCAdmin';",
    "",
    "GRANT ALL ON iamdb.* TO 'KSCIAM';",
    "GRANT PROCESS, SUPER, SET USER ON *.* TO 'KSCIAM';",
    "",
    "FLUSH PRIVILEGES;",
    "SHOW GRANTS FOR 'KSCAdmin';",
    "SHOW GRANTS FOR 'KSCIAM';",
    "EXIT;",
]))
B(("table", {
    "head": ["Право", "Назначение"],
    "widths": [40, 60],
    "rows": [
        ["ALL ON kav.*", "Полный доступ к базе данных Сервера администрирования (кроме GRANT OPTION)"],
        ["ALL ON iamdb.*", "Полный доступ к базе данных службы IAM"],
        ["SELECT, SHOW VIEW ON mysql.*, sys.*", "Чтение системных представлений"],
        ["EXECUTE ON PROCEDURE sys.table_exists", "Проверка существования таблиц (не требуется для MariaDB 10.5 и старше)"],
        ["PROCESS, SUPER", "Глобальные привилегии, необходимые Серверу администрирования"],
        ["SET USER", "Право создавать объекты СУБД с чужим `DEFINER` (обязательно начиная с MariaDB "
                     "10.5.4: начиная с этой версии `SUPER` его не заменяет)"],
    ],
}))
B(("note", "Кодировка базы `kav` задаётся как `ascii` с сопоставлением `ascii_general_ci` — это "
           "требование KSC (данные внутри хранятся в собственном формате приложения), а не ошибка. "
           "База `iamdb` создаётся с кодировкой по умолчанию."))
B(("p", "Проверьте подключение созданных учётных записей по TCP:"))
B(("code", [
    "mariadb -h 127.0.0.1 -P 3306 -u KSCAdmin -p -e \"SHOW DATABASES;\"",
    "mariadb -h 127.0.0.1 -P 3306 -u KSCIAM   -p -e \"SHOW DATABASES;\"",
    "# в первом списке должна присутствовать база kav, во втором — iamdb",
]))

# ---------------------------------------------------------------- 5
B(("h1", "5. Установка Kaspersky Security Center Linux (Сервер администрирования)"))

B(("p", "Установка состоит из трёх шагов: подготовка служебных учётных записей и лимитов, установка "
        "пакета `ksc64`, первичная настройка скриптом `postinstall.pl`. Все действия выполняются "
        "от имени root."))

B(("h2", "5.1. Создание группы и служебных учётных записей"))
B(("p", "KSC 17 использует две непривилегированные учётные записи: `ksc` — для служб Сервера "
        "администрирования и `ksciam` — для службы IAM. Обе должны входить в группу `kladmins`."))
B(("code", [
    "sudo -i",
    "adduser ksc                       # пароли служб; вход по этим учётным записям не требуется",
    "adduser ksciam",
    "groupadd kladmins",
    "gpasswd -a ksc kladmins",
    "gpasswd -a ksciam kladmins",
    "usermod -g kladmins ksc",
    "usermod -g kladmins ksciam",
    "id ksc                            # gid=... (kladmins), groups=... kladmins",
    "id ksciam",
]))
B(("note", "Учётные записи `ksc` и `ksciam` — непривилегированные: от их имени работают службы KSC. "
           "Использовать их для входа в систему и администрирования не следует."))

B(("h2", "5.2. Лимиты файловых дескрипторов"))
B(("p", "Добавьте в `/etc/security/limits.conf` строки (разделитель — табуляция):"))
B(("code", [
    "cat >> /etc/security/limits.conf <<'EOF'",
    "ksc     soft    nofile  32768",
    "ksc     hard    nofile  131072",
    "ksciam  soft    nofile  32768",
    "ksciam  hard    nofile  131072",
    "EOF",
]))
B(("p", "Проверьте результат:"))
B(("code", [
    "tail -5 /etc/security/limits.conf",
]))

B(("h2", "5.3. Размещение дистрибутива на сервере"))
B(("p", "Скопируйте оба установочных файла на сервер (например, через scp с рабочего места):"))
B(("code", [
    "# на рабочем месте (не на сервере):",
    "scp ksc64_17.0.0.<сборка>_amd64.deb \\",
    "    ksc-web-console-17.0.0.<сборка>.x86_64.deb \\",
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
    "apt install ./ksc64_17.0.0.<сборка>_amd64.deb",
]))
B(("p", "Пакет распаковывается в `/opt/kaspersky/ksc64`. Процесс настройки при этом ещё не запускается. "
        "Проверьте результат установки:"))
B(("code", [
    "dpkg -l | grep -i ksc",
    "ls -la /opt/kaspersky/ksc64/sbin | head -20",
]))
B(("note", "Для автоматизированного развёртывания «Лаборатория Касперского» публикует сценарий "
           "быстрой установки (quick installation script). Он выполняет те же шаги, что описаны в "
           "разделах 5.1–5.5, и подходит для типовых конфигураций; ссылка — приложение Д."))

B(("h2", "5.5. Первичная настройка (postinstall.pl)"))
B(("p", "Запустите сценарий настройки:"))
B(("code", [
    "/opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl",
]))
B(("p", "После запуска сценарий выводит текст Лицензионного соглашения и Политики "
        "конфиденциальности: листайте текст клавишей `Space` (страница вперёд) или `Enter` "
        "(строка вперёд), в конце нажмите `q`, если появится приглашение выхода из просмотра. Далее "
        "последовательно задаются вопросы: введите ответ и нажмите `Enter`. Если в вопросе в скобках "
        "указано значение по умолчанию (например, `[127.0.0.1]`), нажатие `Enter` без ввода оставляет "
        "его. Значения для примера из раздела 2.1 приведены в таблице ниже."))
B(("warn", "Вернуться к предыдущему вопросу нельзя: если ответ введён с ошибкой, нажмите `Ctrl+C` и "
           "запустите `postinstall.pl` заново — повторный запуск безопасен и перезаписывает параметры. "
           "Пароли при вводе не отображаются."))
B(("table", {
    "head": ["№", "Запрос установщика", "Значение / действие"],
    "widths": [7, 58, 35],
    "rows": [
        ["1", "Принять условия Лицензионного соглашения (y/n)", "y"],
        ["2", "Принять Политику конфиденциальности (y/n)", "y"],
        ["3", "FQDN или DNS-имя Сервера администрирования", "ksc01.company.local"],
        ["4", "Номер SSL-порта Сервера администрирования", "13000 (Enter)"],
        ["5", "Количество управляемых устройств (1 — до 100, 2 — до 1000, 3 — более 1000)", "1"],
        ["6", "Имя группы безопасности для служб", "kladmins (Enter)"],
        ["7", "Учётная запись для службы Сервера администрирования", "ksc (Enter)"],
        ["8", "Учётная запись для остальных служб KSC", "ksc (Enter)"],
        ["9", "Тип установленной СУБД (1 — MySQL/MariaDB, 2 — PostgreSQL/Postgres Pro)", "1"],
        ["10", "DNS-имя или IP-адрес сервера БД", "127.0.0.1 (Enter)"],
        ["11", "Порт сервера БД", "3306 (Enter)"],
        ["12", "Имя базы данных Сервера администрирования", "kav"],
        ["13", "Учётная запись для доступа к БД", "KSCAdmin"],
        ["14", "Пароль учётной записи БД", "<пароль из раздела 4.7>"],
        ["15", "FQDN или DNS-имя сервера IAM", "ksc01.company.local"],
        ["16", "Учётная запись для запуска службы IAM", "ksciam (Enter)"],
        ["17", "Тип СУБД для службы IAM (1 — MySQL/MariaDB, 2 — PostgreSQL/Postgres Pro)", "1"],
        ["18", "Адрес СУБД для службы IAM", "127.0.0.1 (Enter)"],
        ["19", "Порт СУБД для службы IAM", "3306 (Enter)"],
        ["20", "Имя базы данных IAM", "iamdb"],
        ["21", "Учётная запись БД для службы IAM", "KSCIAM"],
        ["22", "Пароль учётной записи БД IAM", "<пароль IAM из раздела 4.7>"],
        ["23", "Учётная запись администратора KSC (для входа в Web Console)", "ksc"],
        ["24", "Пароль администратора KSC и его подтверждение", "<сложный пароль>"],
    ],
}))
B(("note", "Пункты 15–22 относятся к службе IAM и присутствуют в KSC 16 и новее. Формулировки "
           "запросов могут незначительно отличаться между сборками; ориентируйтесь на смысл вопроса "
           "и приведённые значения, для портов и имён по умолчанию достаточно нажать Enter."))
B(("p", "Требования к паролю администратора KSC: длина от 8 до 256 символов; символы не менее чем "
        "из трёх групп — заглавные латинские буквы, строчные латинские буквы, цифры, специальные "
        "символы. Пароль не должен совпадать с именем учётной записи."))

B(("h2", "5.6. Создание администратора KSC вручную (если требуется)"))
B(("p", "Если на шагах 23–24 учётная запись не создавалась (например, при тихой установке), создайте "
        "администратора утилитой `kladduser`:"))
B(("code", [
    "/opt/kaspersky/ksc64/sbin/kladduser -n ksc -p '<сложный пароль>'",
]))
B(("p", "Проверить список учётных записей администраторов можно в Web Console (раздел 7.1) — "
        "непосредственно после первого входа."))

B(("h2", "5.7. Проверка служб и портов"))
B(("p", "После завершения настройки создаются и запускаются пять служб:"))
B(("table", {
    "head": ["Служба", "Назначение", "Порт(ы)"],
    "widths": [26, 56, 18],
    "rows": [
        ["klnagent_srv", "Серверная часть Агента администрирования (обмен с управляемыми устройствами "
                         "и точками распространения)", "15000/udp, 13000/tcp"],
        ["kladminserver_srv", "Сервер администрирования (ядро KSC)", "13000/tcp+udp, 13299/tcp, 14000/tcp"],
        ["klactprx_srv", "Прокси активации", "внутренний"],
        ["klwebsrv_srv", "Служебный веб-сервер Сервера администрирования (публикация пакетов, OpenAPI)", "внутренний"],
        ["kliam_srv", "Служба IAM (идентификация и аутентификация пользователей KSC)", "внутренний"],
    ],
}))
B(("code", [
    "systemctl status klnagent_srv --no-pager",
    "systemctl status kladminserver_srv --no-pager",
    "systemctl status klactprx_srv --no-pager",
    "systemctl status klwebsrv_srv --no-pager",
    "systemctl status kliam_srv --no-pager",
    "systemctl is-enabled klnagent_srv kladminserver_srv klactprx_srv klwebsrv_srv kliam_srv",
]))
B(("p", "Все службы должны находиться в состоянии `active (running)` и быть включены в автозагрузку "
        "(`enabled`). Проверьте прослушиваемые порты:"))
B(("code", [
    "ss -tulpn | grep -E ':(13000|13299|14000|8080)\\b'",
]))
B(("p", "Запуск служб вручную (при необходимости):"))
B(("code", [
    "systemctl start klnagent_srv kladminserver_srv klactprx_srv klwebsrv_srv kliam_srv",
    "systemctl enable klnagent_srv kladminserver_srv klactprx_srv klwebsrv_srv kliam_srv",
]))
B(("warn", "Если служба `kladminserver_srv` переходит в состояние `failed`, причину ищите в разделе 9.1: "
           "чаще всего это недоступность СУБД, неверные учётные данные БД или неподходящие параметры "
           "`sql_mode`/`table_open_cache`. Если не запускается `kliam_srv`, проверьте базу `iamdb` "
           "и учётную запись `KSCIAM`."))

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
    "apt-get install ./ksc64_17.0.0.<сборка>_amd64.deb",
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
B(("note", "В KSC 16 и новее в файл ответов дополнительно включаются параметры службы IAM "
           "(имя и расположение базы `iamdb`, учётная запись `KSCIAM`, учётная запись `ksciam`). "
           "Полный перечень переменных приведён в справке производителя (раздел «Установка в тихом "
           "режиме», ссылка — приложение Д); при отсутствии переменных установщик запросит эти "
           "значения в интерактивном режиме."))
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
        ["/var/opt/kaspersky/klnagent_srv/iam", "Данные службы IAM: сертификат `main_certificate.pem`, "
                                                "файл токена `initial_token.txt`"],
        ["/var/log/kaspersky", "Журналы и трассировки компонентов"],
        ["/etc/init.d / systemd units", "Службы `kl*_srv`"],
    ],
}))
B(("h2", "5.10. Если postinstall.pl завершился ошибкой"))
B(("p", "Сообщение установщика имеет вид `Fatal error: Server registration failed with code '3': "
        "… '#1950 (1227) KLDB::DB_ERR_GENERAL'`. Здесь два кода: код KSC (`1950`) и в скобках — код "
        "ошибки СУБД (`1227`). Искать причину нужно по коду в скобках: как правило, дело в правах "
        "учётной записи СУБД или в её пароле, а не в самом KSC. Установка при этом не завершена: "
        "службы `kl*_srv` могут быть созданы, но не работать."))
B(("table", {
    "head": ["Код СУБД", "Что означает", "Что делать"],
    "widths": [13, 37, 50],
    "rows": [
        ["1227", "Учётной записи СУБД не хватает глобальной привилегии: `SUPER`, `SET USER`, "
                 "`PROCESS` или `CREATE USER` — KSC создаёт представления и триггеры с собственным "
                 "`DEFINER`", "Выдать права (раздел 5.10.1) и повторить `postinstall.pl`"],
        ["1045", "`Access denied for user 'KSCAdmin'@'localhost'` — неверный пароль, имя учётной "
                 "записи или не совпадает часть `@host`", "Проверить пароль и `SELECT user, host FROM "
                 "mysql.user;`; при необходимости `ALTER USER … IDENTIFIED BY …` (раздел 5.10.1)"],
        ["1044", "`Access denied for user … to database 'kav'` — нет прав на саму базу", "`GRANT ALL ON "
                 "kav.* TO 'KSCAdmin';` и `GRANT ALL ON iamdb.* TO 'KSCIAM';`, затем `FLUSH PRIVILEGES;`"],
        ["1049", "`Unknown database 'kav'` / `'iamdb'` — база не создана", "Создать базы (раздел 4.7)"],
        ["2002 / 2003", "`Can't connect to local MySQL server` — СУБД не запущена или слушает другой "
                        "адрес", "`systemctl status mariadb`, `ss -tlnp | grep 3306`, проверить "
                        "`bind-address` в разделе 4.2"],
        ["1129", "`Host 'localhost' is blocked` — слишком много неудачных попыток входа", "`mariadb-admin "
                 "flush-hosts` (или перезапуск MariaDB), затем проверить пароль"],
        ["1040", "`Too many connections`", "Увеличить `max_connections` (раздел 4.4) или остановить "
                 "лишние подключения"],
    ],
}))
B(("p", "Полезно посмотреть, что именно сообщает служба IAM: в журнале видны и текст SQL-ошибки, "
        "и учётная запись, от имени которой выполнялся запрос."))
B(("code", [
    "journalctl -u kliam_srv -n 100 --no-pager | grep -i -E 'error|denied|1227'",
    "journalctl -u kladminserver_srv -n 100 --no-pager | grep -i -E 'error|denied|1227'",
    "journalctl -u mariadb -n 50 --no-pager",
    "tail -n 50 /var/log/kaspersky/kladminserver/klserver.log",
]))

B(("h3", "5.10.1. Ошибка 1227: выдача недостающих прав"))
B(("p", "Сначала посмотрите, какие права уже выданы и под какой частью `@host` созданы учётные записи:"))
B(("code", [
    "mariadb -e \"SELECT user, host FROM mysql.user WHERE user IN ('KSCAdmin','KSCIAM');\"",
    "mariadb -e \"SHOW GRANTS FOR 'KSCAdmin';\"",
    "mariadb -e \"SHOW GRANTS FOR 'KSCIAM';\"",
]))
B(("p", "Убедитесь, что каждая учётная запись подключается по TCP и видит свою базу (пароли "
        "запрашиваются интерактивно):"))
B(("code", [
    "mariadb -h 127.0.0.1 -u KSCAdmin -p -e \"USE kav; SELECT DATABASE();\"",
    "mariadb -h 127.0.0.1 -u KSCIAM   -p -e \"USE iamdb; SELECT DATABASE();\"",
]))
B(("p", "Затем выдайте обеим учётным записям недостающие глобальные привилегии и повторите проверку:"))
B(("code", [
    "mariadb",
    "GRANT ALL ON kav.* TO 'KSCAdmin';",
    "GRANT SELECT, SHOW VIEW ON mysql.* TO 'KSCAdmin';",
    "GRANT SELECT, SHOW VIEW ON sys.* TO 'KSCAdmin';",
    "GRANT EXECUTE ON PROCEDURE sys.table_exists TO 'KSCAdmin';",
    "GRANT PROCESS, SUPER, SET USER ON *.* TO 'KSCAdmin';",
    "GRANT ALL ON iamdb.* TO 'KSCIAM';",
    "GRANT PROCESS, SUPER, SET USER ON *.* TO 'KSCIAM';",
    "FLUSH PRIVILEGES;",
    "SHOW GRANTS FOR 'KSCAdmin';",
    "SHOW GRANTS FOR 'KSCIAM';",
    "EXIT;",
]))
B(("note", "`SET USER` появилась в MariaDB 10.5.4: начиная с этой версии привилегия `SUPER` больше не "
           "позволяет создавать объекты с чужим `DEFINER`, а KSC создаёт такие объекты при инициализации "
           "базы. Отсюда типичная ошибка `1227` на установках с MariaDB 11.x. В MySQL такой привилегии "
           "нет — при использовании MySQL строку с `SET USER` пропустите."))
B(("warn", "Не ограничивайте права «минимально необходимым» наугад: если урезать `PROCESS`/`SUPER`/`SET USER` "
           "после успешной установки, Сервер администрирования перестанет запускаться или потеряет "
           "возможность обслуживать базу. Возвращайте права к документированной схеме (раздел 4.7)."))

B(("h3", "5.10.2. Чистый повтор установки"))
B(("p", "Если после исправления прав установка всё равно завершается ошибкой, начните с пустых баз: "
        "данных в них ещё нет, повторная настройка безопасна."))
B(("code", [
    "systemctl stop klnagent_srv kladminserver_srv klactprx_srv klwebsrv_srv kliam_srv 2>/dev/null",
    "mariadb -e \"DROP DATABASE IF EXISTS kav; DROP DATABASE IF EXISTS iamdb;\"",
    "mariadb -e \"CREATE DATABASE kav DEFAULT CHARACTER SET ascii DEFAULT COLLATE ascii_general_ci;\"",
    "mariadb -e \"CREATE DATABASE iamdb;\"",
    "mariadb -e \"SHOW DATABASES;\"",
    "/opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl",
]))
B(("note", "Вопросы установщика повторяются с самого начала (раздел 5.5): лицензия, параметры Сервера "
           "администрирования, затем параметры IAM. Повторный запуск перезаписывает ранее введённые "
           "значения, поэтому удобно заранее подготовить ответы в файле (раздел 5.8)."))
B(("warn", "Базу `iamdb` нельзя удалять на работающем сервере: в ней хранятся учётные записи и токены "
           "службы IAM. При деинсталляции KSC она также не удаляется автоматически — это нужно делать "
           "вручную и осознанно."))

