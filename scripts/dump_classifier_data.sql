(select name as token, 'HOTEL_NAME' as label from hotel4x.source where char_length(name) > 5 limit 1000)
UNION
(select address as token, 'HOTEL_ADDRESS' as label from hotel4x.source where char_length(address) > 5 limit 1000)
UNION
(select array_to_string(token_array, '') as token, 'REVIEW_TEXT' as label from hotel4x.review limit 1000);