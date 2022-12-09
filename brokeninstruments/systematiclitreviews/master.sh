#!/usr/bin/env bash
curl 'https://discovery.ebsco.com/api/v4/search' \
-X 'POST' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json, text/plain, */*' \
-H 'Accept-Encoding: gzip, deflate, br' \
-H 'Accept-Language: en;q=0.9, en-US;q=0.8' \
-H 'Host: discovery.ebsco.com' \
-H 'Origin: https://discovery.ebsco.com' \
-H 'Content-Length: 379' \
-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15' \
-H 'Connection: keep-alive' \
-H 'Cookie: amp_e1ea5d_ebsco.com=54276b26-b741-4a81-9f3e-af9e33ba6283...1g9v922k0.1g9v9fo2o.22.2.24; amp_e1ea5d=54276b26-b741-4a81-9f3e-af9e33ba6283..1.1g9v922k0.1g9v94n10.0.0.0; lux_uid=165998081286550928; osano_consentmanager=oxwbjd72GCKsuTVYHkl33BYNPRijfd1XDfg8KsPv2H_Z4iL3jkS_RzmUY-c05468lN_RDFn4OVEKINZkpStk5g4dKrNXW_8g7fIQr5-y-DOLVRSVbKMGlfVaiEdYTa0mjMZb5_Gt7NZ4oLV6UajaGHZYIUR_ShTknBiXlXE06eb8pLlpBCQkP4yacDQpwPTaWpQF1IaSAedPd61EJ1Cwi8rhgydD8Y41fVGNyWhdTXo3KtjY4_04uoUh37xzfCaKbAa3OcxPDesFbpmM1fi_Uz0hGQdwBAjAs_6LJQ==; osano_consentmanager_uuid=0df6e8ef-d5db-4e28-b7f1-f4d67f02e307; LTIUserType=undefined; affiliation=eyJjdXN0b21lciI6InM4ODYwMzM4IiwiZ3JvdXAiOiJtYWluIn0=; locale=en; QSI_HistorySession=https%3A%2F%2Fdiscovery.ebsco.com%2Fc%2F3czfwv%2Fresults%3Fautocorrect%3Dy%26limiters%3DFT1%253AY%26q%3DMarketing%2520Science%2520AND%2520%2528AB%2520hedonic%2520OR%2520AB%2520utilitarian%2529~1659980894397; amp_e1ea5d_discovery.ebsco.com=54276b26-b741-4a81-9f3e-af9e33ba6283...1g9v922k0.1g9v925fe.1.0.1; amp_cookie_test4bBYVljphSxowFbRFM8zVy=1659980810671; amp_cookie_testlM1gSFIomsjowuwvQrPhRE=1659980810663; SESSION_EXPIRATION=1660052808; SESSION_ID=MDk1YjEyMzUtNmIwNy00ZDBhLTg2NmQtMTk3OGYzMWQ5N2M0' \
-H 'x-profile-id: eds' \
-H 'x-current-cgp: eyJjdXN0b21lciI6InM4ODYwMzM4IiwiZ3JvdXAiOiJtYWluIiwicHJvZmlsZSI6ImVkcyJ9' \
-H 'x-initiated-by: typed-in' \
--data-binary '{"query":"(SO Marketing Science) AND (AB hedonic AND AB utilitarian)","queryModel":null,"autoCorrect":true,"profileIdentifier":"3czfwv","expanders":["concept"],"filters":{"databases":null,"minDate":"2010-01","maxDate":"2011-01","publicationIds":[],"peerReviewed":false,"atLibrary":true,"fullText":false,"facets":[]},"offset":0,"count":10,"searchMode":"all","highlightTag":"mark"}'
