@echo off
chcp 65001 >nul
setlocal

set "BASE_URL=http://127.0.0.1:8080"

echo 1. GET collect-client (200 OK)
curl -v -H "Accept-Language: ru-RU" %BASE_URL%/rest/api/v2/collect-client
echo .
echo .

echo 2. POST add-client (200 OK)
curl -v -X POST -H "Accept-Language: ru-RU" -H "Content-Type: application/json" "%BASE_URL%/rest/api/v2/add-client?user_agent=curl%2F8.16.0"
echo .
echo .

echo 3. PUT revise-client/1 (200 OK)
curl -v -X PUT -H "Accept-Language: ru-RU" -H "Content-Type: application/json" -d "{\"user_agent\":\"new-agent\"}" %BASE_URL%/rest/api/v2/revise-client/1
echo .
echo .

echo 4. POST add-message (200 OK)
curl -v -X POST -H "Accept-Language: ru-RU" -H "Content-Type: application/json" "%BASE_URL%/rest/api/v2/add-message?data=hello&client=1&description=desc&tags=tag1&stage=ready"
echo .
echo .

echo 5. GET collect-message/1 (200 OK)
curl -v -H "Accept-Language: ru-RU" %BASE_URL%/rest/api/v2/collect-message/1
echo .
echo .

echo 6. GET collect-feedback/1 (200 OK)
curl -v -H "Accept-Language: ru-RU" %BASE_URL%/rest/api/v2/collect-feedback/1
echo .
echo .

echo 7. GET collect-report (200 OK)
curl -v -H "Accept-Language: ru-RU" %BASE_URL%/rest/api/v2/collect-report
echo .
echo .

echo 8. ОШИБКА 415: POST без Content-Type
curl -i -X POST -H "Accept-Language: ru-RU" "%BASE_URL%/rest/api/v2/add-client?user_agent=x"
echo .
echo .

echo 9. ОШИБКА 406: GET без Accept-Language
curl -i %BASE_URL%/rest/api/v2/collect-client
echo .
echo .

echo 10. ОШИБКА 406: GET с Accept-Language: en
curl -i -H "Accept-Language: en" %BASE_URL%/rest/api/v2/collect-client

pause