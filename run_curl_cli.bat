@echo off
setlocal enabledelayedexpansion

set BASE_URL=http://127.0.0.1:8080
set TMP_BODY=%TEMP%\api_body.json

:menu
cls
echo   Server: %BASE_URL%
echo ==================================================
echo   1. POST  /add-client               -- create client
echo   2. GET   /collect-client           -- list clients
echo   3. PUT   /revise-client/:uid       -- revise client
echo   4. POST  /add-message              -- create message
echo   5. GET   /collect-message/:client  -- list messages
echo   6. PUT   /revise-message/:uid      -- revise message
echo   7. GET   /collect-feedback/:msg    -- list feedbacks
echo   8. GET   /collect-report           -- report
echo   9. Ping the server
echo   0. Exit
echo ==================================================
set /p choice="Choice: "

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

echo Invalid choice.
pause
goto menu

:add_client
cls
echo --- 1. Create client ---
set /p ua="User-Agent [unknown]: "
if "%ua%"=="" set ua=unknown
echo.
echo ^>^> POST %BASE_URL%/rest/api/v2/add-client
echo.
curl -s -X POST -H "Accept-Language: ru-RU" -H "Content-Type: application/json" ^
    --get "%BASE_URL%/rest/api/v2/add-client" ^
    --data-urlencode "user_agent=%ua%" | python -m json.tool --no-ensure-ascii
echo.
pause
goto menu

:collect_client
cls
echo --- 2. List clients ---
set /p uid="UID (empty = all): "
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
echo --- 3. Revise client ---
set /p uid="Client UID: "
echo Example body: {"user_agent":"NewAgent"}
set /p body="JSON: "
echo %body%> "%TMP_BODY%"
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
echo --- 4. Create message ---
set /p client="client (client UID): "
if "%client%"=="" (
    echo [ERROR] client is required.
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
    --get "%BASE_URL%/rest/api/v2/add-message" ^
    --data-urlencode "data=%data%" ^
    --data-urlencode "client=%client%" ^
    --data-urlencode "description=%desc%" ^
    --data-urlencode "tags=%tags%" ^
    --data-urlencode "stage=%stage%" ^
    | python -m json.tool --no-ensure-ascii
echo.
pause
goto menu

:collect_message
cls
echo --- 5. List messages ---
set /p client="Client UID: "
set /p stage="stage (empty = all): "
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
echo --- 6. Revise message ---
set /p uid="Message UID: "
echo Example body: {"stage":"done"}
set /p body="JSON: "
echo %body%> "%TMP_BODY%"
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
echo --- 7. List feedbacks ---
set /p msg="Message UID: "
echo.
echo ^>^> GET %BASE_URL%/rest/api/v2/collect-feedback/%msg%
echo.
curl -s -H "Accept-Language: ru-RU" "%BASE_URL%/rest/api/v2/collect-feedback/%msg%" | python -m json.tool --no-ensure-ascii
echo.
pause
goto menu

:collect_report
cls
echo --- 8. Report ---
echo ^>^> GET %BASE_URL%/rest/api/v2/collect-report
echo.
curl -s -H "Accept-Language: ru-RU" "%BASE_URL%/rest/api/v2/collect-report" | python -m json.tool --no-ensure-ascii
echo.
pause
goto menu

:ping
cls
echo --- 9. Check server ---
curl -s -o nul -w "HTTP %%{http_code}\n" -H "Accept-Language: ru-RU" "%BASE_URL%/rest/api/v2/collect-client"
if errorlevel 1 (
    echo [ERROR] Server is not reachable at %BASE_URL%.
    echo Run run_server.bat first.
) else (
    echo [OK] Server responds.
)
pause
goto menu
