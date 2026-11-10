@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set BASE_URL=http://127.0.0.1:8080
set TMP_BODY=%TEMP%\api_body.json

:menu
cls
echo   Сервер: %BASE_URL%
echo ==================================================
echo   1. POST  /add-client               -- создать клиента
echo   2. GET   /collect-client           -- список клиентов
echo   3. PUT   /revise-client/:uid       -- изменить клиента
echo   4. POST  /add-message              -- создать сообщение
echo   5. GET   /collect-message/:client  -- список сообщений
echo   6. PUT   /revise-message/:uid      -- изменить сообщение
echo   7. GET   /collect-feedback/:msg    -- список фидбеков
echo   8. GET   /collect-report           -- отчёт
echo   9. Пингануть сервер
echo   0. Выход
echo ==================================================
set /p choice="Выбор: "

if "%choice%"=="1" goto add_client
if "%choice%"=="2" goto collect_client
if "%choice%"=="3" goto revise_client
if "%choice%"=="4" goto add_message
if "%choice%"=="5" goto collect_message
if "%choice%"=="6" goto revise_message
if "%choice%"=="7" goto collect_feedback
if "%choice%"=="8" goto collect_report
if "%choice%"=="9" goto ping
if "%choice%"=="0" exit /b 0

echo Неверный выбор.
pause
goto menu

:add_client
cls
echo --- 1. Создать клиента ---
set /p ua="User-Agent [unknown]: "
if "%ua%"=="" set ua=unknown
echo.
echo ^>^> POST %BASE_URL%/rest/api/v2/add-client
echo.
curl -s -X POST -H "Accept-Language: ru-RU" -H "Content-Type: application/json" ^
    "%BASE_URL%/rest/api/v2/add-client?user_agent=%ua%" | python -m json.tool --no-ensure-ascii
echo.
pause
goto menu

:collect_client
cls
echo --- 2. Список клиентов ---
set /p uid="UID (пусто = все): "
if "%uid%"=="" (
    set "url=%BASE_URL%/rest/api/v2/collect-client"
) else (
    set "url=%BASE_URL%/rest/api/v2/collect-client?uid=%uid%"
)
echo.
echo ^>^> GET !url!
echo.
curl -s -H "Accept-Language: ru-RU" "!url!" | python -m json.tool --no-ensure-ascii
echo.
pause
goto menu

:revise_client
cls
echo --- 3. Изменить клиента ---
set /p uid="UID клиента: "
echo Пример тела: {"user_agent":"NewAgent"}
set /p body="JSON: "
echo %body% > "%TMP_BODY%"
echo.
echo ^>^> PUT %BASE_URL%/rest/api/v2/revise-client/%uid%
echo.
curl -s -X PUT -H "Accept-Language: ru-RU" -H "Content-Type: application/json" ^
    -d @"%TMP_BODY%" "%BASE_URL%/rest/api/v2/revise-client/%uid%" | python -m json.tool --no-ensure-ascii
echo.
pause
goto menu

:add_message
cls
echo --- 4. Создать сообщение ---
set /p client="client (UID клиента): "
if "%client%"=="" (
    echo [ERROR] client обязателен.
    pause
    goto menu
)
set /p data="data: "
if "%data%"=="" set data=hello
set /p desc="description [none]: "
set /p tags="tags [none]: "
set /p stage="stage [none]: "
echo.
echo ^>^> POST %BASE_URL%/rest/api/v2/add-message
echo.
curl -s -X POST -H "Accept-Language: ru-RU" -H "Content-Type: application/json" ^
    "%BASE_URL%/rest/api/v2/add-message?data=%data%&client=%client%&description=%desc%&tags=%tags%&stage=%stage%" ^
    | python -m json.tool --no-ensure-ascii
echo.
pause
goto menu

:collect_message
cls
echo --- 5. Список сообщений ---
set /p client="UID клиента: "
set /p stage="stage (пусто = все): "
if "%stage%"=="" (
    set "url=%BASE_URL%/rest/api/v2/collect-message/%client%"
) else (
    set "url=%BASE_URL%/rest/api/v2/collect-message/%client%?stage=%stage%"
)
echo.
echo ^>^> GET !url!
echo.
curl -s -H "Accept-Language: ru-RU" "!url!" | python -m json.tool --no-ensure-ascii
echo.
pause
goto menu

:revise_message
cls
echo --- 6. Изменить сообщение ---
set /p uid="UID сообщения: "
echo Пример тела: {"stage":"done"}
set /p body="JSON: "
echo %body% > "%TMP_BODY%"
echo.
echo ^>^> PUT %BASE_URL%/rest/api/v2/revise-message/%uid%
echo.
curl -s -X PUT -H "Accept-Language: ru-RU" -H "Content-Type: application/json" ^
    -d @"%TMP_BODY%" "%BASE_URL%/rest/api/v2/revise-message/%uid%" | python -m json.tool --no-ensure-ascii
echo.
pause
goto menu

:collect_feedback
cls
echo --- 7. Список фидбеков ---
set /p msg="UID сообщения: "
echo.
echo ^>^> GET %BASE_URL%/rest/api/v2/collect-feedback/%msg%
echo.
curl -s -H "Accept-Language: ru-RU" "%BASE_URL%/rest/api/v2/collect-feedback/%msg%" | python -m json.tool --no-ensure-ascii
echo.
pause
goto menu

:collect_report
cls
echo --- 8. Отчёт ---
echo ^>^> GET %BASE_URL%/rest/api/v2/collect-report
echo.
curl -s -H "Accept-Language: ru-RU" "%BASE_URL%/rest/api/v2/collect-report" | python -m json.tool --no-ensure-ascii
echo.
pause
goto menu

:ping
cls
echo --- 9. Проверка сервера ---
curl -s -o nul -w "HTTP %%{http_code}\n" -H "Accept-Language: ru-RU" "%BASE_URL%/rest/api/v2/collect-client"
if errorlevel 1 (
    echo [ERROR] Сервер недоступен по адресу %BASE_URL%.
    echo Запустите run_server.bat.
) else (
    echo [OK] Сервер отвечает.
)
pause
goto menu