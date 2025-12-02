create or replace notification integration if not exists my_notification_int
type = queue
notification_provider = gcp_pubsub
enabled = true
gcp_pubsub_subscription_name = 'projects/project-1234/subscriptions/sub2';

create notification integration my_notification_int
enabled = true
type = queue
notification_provider = azure_storage_queue
azure_storage_queue_primary_uri = 'https://myqueue.queue.core.windows.net/mystoragequeue'
azure_tenant_id = 'a123bcde-1234-5678-abc1-9abc12345678';

create notification integration my_notification_int
enabled = true
type = queue
notification_provider = aws_sns
direction = outbound
aws_sns_topic_arn = 'arn:aws:sns:us-east-2:111122223333:sns_topic'
aws_sns_role_arn = 'arn:aws:iam::111122223333:role/error_sns_role';

create notification integration my_notification_int
type = queue
direction = outbound
notification_provider = gcp_pubsub
enabled = true
gcp_pubsub_topic_name = 'projects/sdm-prod/topics/mytopic';

create notification integration my_notification_int
enabled = true
type = queue
notification_provider = azure_event_grid
direction = outbound
azure_event_grid_topic_endpoint = 'https://myaccount.region-1.eventgrid.azure.net/api/events'
azure_tenant_id = 'mytenantid';
