# -*- coding: utf-8 -*-
"""Часть 4: диагностика, чек-лист, приложения."""

BLOCKS = []
B = BLOCKS.append

# ---------------------------------------------------------------- 9
B(("h1", "9. Диагностика типовых неисправностей"))

B(("p", "Раздел содержит наиболее часто встречающиеся при развёртывании и эксплуатации проблемы. "
        "Перед изменением конфигурации сохраняйте её копию и фиксируйте выполненные действия — это "
        "упрощает обращение в техническую поддержку."))

B(("h2", "9.1. Служба kladminserver_srv не запускается"))
B(("p", "**Симптом.** `systemctl status kladminserver_srv` — `failed`, Web Console недоступна."))
B(("code", [
    "journalctl -u kladminserver_srv -n 100 --no-pager",
    "journalctl -u kliam_srv -n 100 --no-pager",
    "ss -tlnp | grep -E '3306|4444|9050'",
    "mariadb -h 127.0.0.1 -u KSCAdmin -p -e 'SELECT 1;'",
    "mariadb -h 127.0.0.1 -u KSCIAM   -p -e 'SHOW DATABASES;'",
    "systemctl status mariadb --no-pager",
    "ls -l /var/opt/kaspersky/klnagent_srv/iam/",
]))
B(("table", {
    "head": ["Причина", "Признак в журнале", "Действие"],
    "widths": [30, 38, 32],
    "rows": [
        ["СУБД не запущена", "«Can't connect to MySQL server»", "`systemctl start mariadb`, проверить место на диске"],
        ["Неверные учётные данные БД", "«Access denied for user 'KSCAdmin'»",
         "Пересоздать учётную запись и права (раздел 4.7)"],
        ["Неверные параметры MariaDB", "«Конфигурация MySQL: неверное значение переменной…»", "Раздел 9.3"],
        ["Недоступен каталог данных", "«Permission denied» для `/var/opt/kaspersky/...`",
         "Проверить владельца каталога и лимиты `nofile` (раздел 5.2)"],
        ["Расхождение времени", "ошибки TLS/аутентификации", "Раздел 3.10.2"],
    ],
}))

B(("h2", "9.2. Служба kliam_srv не запускается или вход в Web Console невозможен"))
B(("p", "**Симптом.** `systemctl status kliam_srv` — `failed`; при входе в Web Console появляется "
        "сообщение о недоступности службы аутентификации либо учётная запись не принимается."))
B(("table", {
    "head": ["Причина", "Признак в журнале", "Действие"],
    "widths": [30, 38, 32],
    "rows": [
        ["Не создана база `iamdb`", "«Unknown database 'iamdb'»", "Создать базу и права (раздел 4.7)"],
        ["Неверный пароль `KSCIAM`", "«Access denied for user 'KSCIAM'»",
         "`ALTER USER 'KSCIAM'@'localhost' IDENTIFIED BY '<пароль>';` и повторить `postinstall.pl`"],
        ["Не заданы параметры IAM при установке", "в журнале нет строк о запуске службы IAM",
         "Запустить `/opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl` и заполнить пункты 15–22 (раздел 5.5)"],
        ["Заняты порты 4444/9050", "«Address already in use»",
         "`ss -tlnp | grep -E '4444|9050'` — освободить порт"],
        ["Нет прав на каталог IAM", "«Permission denied» для `/var/opt/kaspersky/klnagent_srv/iam`",
         "`chown -R ksciam:kladmins /var/opt/kaspersky/klnagent_srv/iam`, права 700"],
    ],
}))
B(("note", "Служба `kliam_srv` должна быть запущена и включена до первого входа в Web Console: без неё "
           "консоль не сможет аутентифицировать пользователя, даже если `kladminserver_srv` работает."))

B(("h2", "9.3. Ошибка «неверное значение переменной table_open_cache»"))
B(("p", "**Симптом.** Служба не стартует, в журнале: «Конфигурация MySQL: неверное значение "
        "переменной: 'table_open_cache'='...'»."))
B(("p", "**Причина.** MariaDB не смогла применить `table_open_cache=60000` из-за недостаточного "
        "лимита файловых дескрипторов."))
B(("p", "**Решение.** Увеличьте `LimitNOFILE` для службы MariaDB (рекомендуемое значение — 1048576):"))
B(("code", [
    "systemctl edit mariadb.service      # [Service] LimitNOFILE=1048576",
    "systemd-analyze verify mariadb.service",
    "systemctl daemon-reload",
    "systemctl restart mariadb",
    "mariadb -e \"SHOW VARIABLES LIKE 'table_open_cache';\"   # 60000",
    "systemctl restart klnagent_srv kladminserver_srv klactprx_srv klwebsrv_srv kliam_srv",
]))
B(("note", "Проверить фактический лимит процесса можно командой "
           "`cat /proc/$(pgrep -x mariadbd)/limits | grep 'open files'`."))

B(("h2", "9.4. Web Console не открывается или отвечает ошибкой 502"))
B(("table", {
    "head": ["Проверка", "Команда", "Ожидаемый результат"],
    "widths": [30, 42, 28],
    "rows": [
        ["Службы консоли запущены", "`systemctl list-units 'KSC*'`", "все `active (running)`"],
        ["Порт прослушивается", "`ss -tlnp | grep 8080`", "`node` слушает 8080"],
        ["Доступен порт Сервера администрирования", "`ss -tlnp | grep 13299`", "`klserver` слушает 13299"],
        ["Корректность файла ответов", "`python3 -m json.tool /etc/ksc-web-console-setup.json`", "нет ошибок"],
        ["Межсетевой экран", "`ufw status verbose`", "8080/tcp разрешён"],
        ["Журнал консоли", "`journalctl -u KSCWebConsole.service -n 100`", "нет `EACCES`/`ECONNREFUSED`"],
    ],
}))
B(("p", "Если консоль была установлена с ошибкой в JSON, удалите пакет и установите заново:"))
B(("code", [
    "dpkg -r ksc-web-console",
    "python3 -m json.tool /etc/ksc-web-console-setup.json",
    "dpkg -i /root/ksc_install/ksc-web-console-*.x86_64.deb",
    "systemctl restart 'KSC*'",
]))

B(("h2", "9.5. Устройства не подключаются к Серверу администрирования"))
B(("ol", [
    "Проверьте разрешение имени: на устройстве `getent hosts ksc01.company.local` должен вернуть "
    "IP сервера KSC.",
    "Проверьте доступность порта: `nc -vz ksc01.company.local 13000` (или `telnet`).",
    "Проверьте, что порт 13000/tcp+udp разрешён межсетевым экраном на сервере и в сети.",
    "Убедитесь, что время на устройстве и сервере совпадает (разница не более 5 минут).",
    "Запустите на устройстве `klnagchk` (Linux: `/opt/kaspersky/klnagent64/bin/klnagchk`, "
    "Windows: `C:\\Program Files (x86)\\Kaspersky Lab\\NetworkAgent\\klnagchk.exe`).",
    "При необходимости переключите Агент на другой адрес сервера утилитой `klmover`.",
]))

B(("h2", "9.6. Недостаточно места на диске"))
B(("code", [
    "df -hT",
    "du -sh /var/opt/kaspersky/* /var/lib/mysql /var/log 2>/dev/null | sort -h",
    "journalctl --disk-usage",
    "journalctl --vacuum-time=14d",
    "apt -y clean",
]))
B(("p", "Наиболее быстро растущие каталоги — `/var/opt/kaspersky/klnagent_srv` (данные сервера, "
        "инсталляционные пакеты, карантин) и `/var/lib/mysql`. Освобождайте место удалением устаревших "
        "инсталляционных пакетов и журналов, а не файлов из каталогов данных."))

B(("h2", "9.7. Предупреждение браузера о сертификате"))
B(("p", "Самоподписанный сертификат Web Console вызывает предупреждение — это штатное поведение. "
        "Варианты: каждый раз подтверждать исключение либо заменить сертификат на выданный внутренним "
        "центром сертификации (раздел 6.6). Отключать проверку сертификата в браузере не рекомендуется."))

B(("h2", "9.8. Сбор данных для обращения в поддержку"))
B(("code", [
    "mkdir -p /tmp/ksc_diag",
    "systemctl --no-pager status 'kl*_srv' 'KSC*' > /tmp/ksc_diag/services.txt 2>&1",
    "journalctl -u 'kl*_srv' -u 'KSC*' --since '-2 days' > /tmp/ksc_diag/journal.txt",
    "ss -tulpn > /tmp/ksc_diag/ports.txt",
    "df -hT > /tmp/ksc_diag/disk.txt; free -h >> /tmp/ksc_diag/disk.txt",
    "dpkg -l | grep -Ei 'ksc|kaspersky|mariadb' > /tmp/ksc_diag/packages.txt",
    "cp -r /var/log/kaspersky /tmp/ksc_diag/logs 2>/dev/null",
    "tar -czf /tmp/ksc_diag_$(date +%F).tar.gz -C /tmp ksc_diag",
]))
B(("warn", "Перед передачей архива в поддержку проверьте, что в журналах нет паролей и иных "
           "конфиденциальных данных; при необходимости удалите такие строки."))

# ---------------------------------------------------------------- 10
B(("h1", "10. Чек-лист приёмки"))

B(("p", "Развёртывание считается завершённым, когда выполнены все пункты таблицы. "
        "Отметьте результат и укажите ответственного."))
B(("checklist", {
    "head": ["№", "Проверка", "Критерий", "Отметка"],
    "widths": [5, 42, 38, 15],
    "rows": [
        ["1", "Ubuntu Server 26.10 установлена", "`cat /etc/os-release` возвращает 26.10", ""],
        ["2", "FQDN и DNS настроены", "`hostname -f` = `ksc01.company.local`, имя разрешается", ""],
        ["3", "Время синхронизировано", "`timedatectl` — `System clock synchronized: yes`", ""],
        ["4", "Swap не менее 1,5 × ОЗУ", "`swapon --show`", ""],
        ["5", "Межсетевой экран настроен", "`ufw status` — открыты 22, 8080, 13000, 13299 "
    "наружу публикуются только 8080 и 13000; 3306, 13299, 4444, 9050 — только локально", ""],
        ["6", "MariaDB 11.8 установлена и настроена", "`mariadb --version` — 11.8.x, параметры из `99-ksc.cnf` применены", ""],
        ["7", "Базы `kav` и `iamdb`, учётные записи `KSCAdmin` и `KSCIAM` созданы", "подключение по TCP под обеими учётными записями успешно", ""],
        ["8", "Пакет `ksc64` установлен, postinstall выполнен", "все 5 служб `kl*_srv` (включая `kliam_srv`) — `active`, `enabled`", ""],
        ["9", "Порты 13000, 13299, 4444, 9050, 8080 прослушиваются", "`ss -tulpn`", ""],
        ["10", "Web Console установлена и доступна", "вход по `https://<FQDN>:8080` выполнен", ""],
        ["11", "Лицензия активирована", "срок действия и количество объектов отображаются", ""],
        ["12", "Инсталляционный пакет Агента создан", "статус пакета «Готов»", ""],
        ["13", "Первое устройство подключено", "устройство в статусе «Защищено»/«OK»", ""],
        ["14", "Задача обновления выполнена", "дата баз актуальна", ""],
        ["15", "Резервное копирование настроено и проверено", "дампы `kav` и `iamdb` создаются, восстановление проверено", ""],
        ["16", "Пароли и параметры стенда внесены в хранилище секретов", "запись создана", ""],
    ],
}))

# ---------------------------------------------------------------- Приложения
B(("h1", "Приложение А. Порты Kaspersky Security Center Linux"))
B(("table", {
    "head": ["Порт", "Протокол", "Процесс", "Назначение", "Где открывать"],
    "widths": [9, 12, 17, 42, 20],
    "rows": [
        ["13000", "TCP (TLS)", "klserver", "Приём подключений Агентов администрирования и подчинённых серверов",
         "Сервер KSC (наружу)"],
        ["13000", "UDP", "klserver", "Уведомления о выключении устройств", "Сервер KSC (наружу)"],
        ["13299", "TCP (TLS)", "klserver", "Подключения Web Console, OpenAPI", "Только 127.0.0.1"],
        ["14000", "TCP", "klserver", "Незащищённый порт Сервера администрирования", "Только 127.0.0.1"],
        ["13291", "TCP (TLS)", "klserver", "Утилита автоматизации `klakaut`; по умолчанию закрыт", "По необходимости"],
        ["4444", "TCP (TLS)", "kliam_srv", "OAuth-сервис IAM: аутентификация пользователей KSC",
         "Только 127.0.0.1"],
        ["9050", "TCP (TLS)", "kliam_srv", "Прокси-сервис IAM (обмен данными с Web Console)",
         "Только 127.0.0.1"],
        ["8080", "TCP (TLS)", "node", "Веб-интерфейс KSC Web Console", "Рабочие места администраторов"],
        ["15000", "UDP", "klnagent", "Сигналы управления от сервера к агентам", "Управляемые устройства"],
        ["13000", "TCP (TLS)", "klnagent", "Работа Агента в роли точки распространения", "Точки распространения"],
        ["3306", "TCP", "mariadbd", "Доступ к СУБД", "Только 127.0.0.1"],
    ],
}))

B(("h1", "Приложение Б. Параметры и пути по умолчанию"))
B(("table", {
    "head": ["Объект", "Значение по умолчанию"],
    "widths": [44, 56],
    "rows": [
        ["SSL-порт Сервера администрирования", "13000"],
        ["Порт Сервера администрирования", "14000"],
        ["Порт OpenAPI / Web Console", "13299"],
        ["Порт утилиты klakaut", "13291 (закрыт)"],
        ["Порт Web Console", "8080"],
        ["Порт OAuth-сервиса IAM", "4444"],
        ["Порт прокси-сервиса IAM", "9050"],
        ["Порт СУБД MySQL/MariaDB", "3306"],
        ["Порт СУБД PostgreSQL", "5432"],
        ["Имя базы данных Сервера администрирования", "kav"],
        ["Имя базы данных службы IAM", "iamdb"],
        ["Группа безопасности служб", "kladmins"],
        ["Служебная учётная запись", "ksc"],
        ["Служебная учётная запись службы IAM", "ksciam"],
        ["Каталог установки KSC", "/opt/kaspersky/ksc64"],
        ["Данные Сервера администрирования", "/var/opt/kaspersky/klnagent_srv"],
        ["Данные Web Console", "/var/opt/kaspersky/ksc-web-console"],
        ["Файл ответов Web Console", "/etc/ksc-web-console-setup.json"],
        ["Сертификат Сервера администрирования", "/var/opt/kaspersky/klnagent_srv/1093/cert/klserver.cer"],
        ["Данные службы IAM", "/var/opt/kaspersky/klnagent_srv/iam"],
        ["Сертификат IAM", "/var/opt/kaspersky/klnagent_srv/iam/main_certificate.pem"],
        ["Журналы", "/var/log/kaspersky, journalctl"],
        ["Скрипт настройки KSC", "/opt/kaspersky/ksc64/lib/bin/setup/postinstall.pl"],
        ["Утилита создания администратора", "/opt/kaspersky/ksc64/sbin/kladduser"],
        ["Утилита резервного копирования", "/opt/kaspersky/ksc64/sbin/klbackup"],
    ],
}))

B(("h1", "Приложение В. Полный пример файла ответов (тихая установка)"))
B(("code", [
    "# /root/ksc_install/answers.txt — KSC Linux 17, все компоненты на одном сервере",
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
]))
B(("note", "Для KSC 17 в файл ответов добавляются переменные службы IAM (адрес и порт СУБД, база "
           "`iamdb`, учётная запись `KSCIAM` и её пароль, учётная запись `ksciam`). Если эти переменные "
           "не указаны, установщик запросит соответствующие значения в интерактивном режиме — это "
           "нормальный путь для первого развёртывания (раздел 5.5)."))
B(("code", [
    "# применение файла ответов",
    "export KLAUTOANSWERS=/root/ksc_install/answers.txt",
    "cd /root/ksc_install",
    "apt-get install ./ksc64_17.0.0.<сборка>_amd64.deb",
    "/opt/kaspersky/ksc64/sbin/kladduser -n ksc -p '<пароль администратора KSC>'",
]))

B(("h1", "Приложение Г. Полезные команды"))
B(("table", {
    "head": ["Задача", "Команда"],
    "widths": [38, 62],
    "rows": [
        ["Состояние всех служб KSC", "`systemctl status 'kl*_srv' 'KSC*' --no-pager`"],
        ["Перезапуск KSC", "`systemctl restart klnagent_srv kladminserver_srv klactprx_srv klwebsrv_srv kliam_srv`"],
        ["Создать администратора KSC", "`/opt/kaspersky/ksc64/sbin/kladduser -n <имя> -p '<пароль>'`"],
        ["Резервная копия настроек", "`/opt/kaspersky/ksc64/sbin/klbackup -path /backup/ksc -savepwd`"],
        ["Восстановление настроек", "`/opt/kaspersky/ksc64/sbin/klbackup -restore -path /backup/ksc`"],
        ["Дамп БД", "`mariadb-dump --single-transaction --databases kav iamdb > ksc.sql`"],
        ["Проверка портов", "`ss -tulpn | grep -E '13000|13299|4444|9050|8080'`"],
        ["Проверка подключения агента", "`/opt/kaspersky/klnagent64/bin/klnagchk`"],
        ["Смена адреса сервера у агента", "`/opt/kaspersky/klnagent64/bin/klmover -address <FQDN>`"],
        ["Версия MariaDB", "`mariadb --version`"],
        ["Свободное место", "`df -hT; du -sh /var/opt/kaspersky/*`"],
        ["Журнал Сервера администрирования", "`journalctl -u kladminserver_srv -f`"],
    ],
}))

B(("h1", "Приложение Д. Источники и ссылки"))
B(("ul", [
    "Kaspersky Security Center Linux 17. Аппаратные и программные требования: "
    "https://support.kaspersky.ru/ksc-linux/17/255791",
    "Kaspersky Security Center Linux 17. Требования к Web Console: "
    "https://support.kaspersky.ru/ksc-linux/17/255792",
    "Kaspersky Security Center Linux 17. Установка (оглавление раздела): "
    "https://support.kaspersky.com/ksc-linux/17/176383",
    "Kaspersky Security Center Linux. Пошаговая установка Сервера администрирования (KSC 16, "
    "порядок действий сохраняется в 17): https://support.kaspersky.ru/ksc-linux/16/166764",
    "Kaspersky Security Center Linux. Настройка сервера MariaDB: "
    "https://support.kaspersky.com/ksc-linux/16/210277",
    "Kaspersky Security Center Linux. Параметры файла ответов и обновление Web Console: "
    "https://support.kaspersky.ru/ksc-linux/16/271767",
    "Kaspersky Security Center Linux. Порты: https://support.kaspersky.ru/ksc-linux/15/158830",
    "Ubuntu Server. Официальная документация: https://ubuntu.com/server/docs",
    "Ubuntu 26.10. Release notes: https://documentation.ubuntu.com/release-notes/26.10/",
]))
B(("note", "Ссылки актуальны на дату выпуска документа. При изменении структуры сайта поддержки "
           "воспользуйтесь поиском по идентификатору статьи (например, 166764)."))

B(("pagebreak", None))
B(("h1nb", "Лист изменений документа"))
B(("table", {
    "head": ["Версия", "Дата", "Изменения", "Автор"],
    "widths": [12, 18, 50, 20],
    "rows": [
        ["1.0", "17.11.2026", "Первая редакция: установка Ubuntu Server 26.10, СУБД MariaDB 11.8, "
                              "KSC Linux 17 (с базой IAM) и Web Console 17",
         "Служба технической поддержки"],
    ],
}))
