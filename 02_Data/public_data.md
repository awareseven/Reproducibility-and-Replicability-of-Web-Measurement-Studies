# Measurement Results 
We provide our measurement results (all requests, responses, and visit logs) as `BigQuery` tables public. You can simply run SQL statements on our tables via [BigQuery web dashboard](https://console.cloud.google.com/bigquery). 

Please be careful before running SQL statements on our dataset. Our dataset is about 1.1TB; running SQL statements on our table may cause additional costs in your billing account.


* Table **requests** is accesibla via `compare-web-measurements.shared_data.requests` or [click here](https://console.cloud.google.com/bigquery?project=compare-web-measurements&p=compare-web-measurements&d=shared_data&page=table&t=requests) to access the table on dashboard.
* Table **responses** is accesibla via `compare-web-measurements.shared_data.requests` or [click here](https://console.cloud.google.com/bigquery?project=compare-web-measurements&p=compare-web-measurements&d=shared_data&page=table&t=responses) to access the table on dashboard.
* Table **visits** is accesibla via `compare-web-measurements.shared_data.requests` or [click here](https://console.cloud.google.com/bigquery?project=compare-web-measurements&p=compare-web-measurements&d=shared_data&page=table&t=visits) to access the table on dashboard.


The following code provides an example, how you can call our tables. This statement doesn't cost since it processes 0B of data.:

`SELECT count(*) FROM ``compare-web-measurements.shared_data.requests`` `