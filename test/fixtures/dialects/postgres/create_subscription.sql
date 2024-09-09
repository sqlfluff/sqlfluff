CREATE SUBSCRIPTION my_subscription
CONNECTION 'publishers_uri'
PUBLICATION my_publication
WITH (
    binary = true,
    copy_data = true,
    create_slot = true,
    run_as_owner = false,
    slot_name = 'my_slot_name',
    streaming = 'parallel'
);

CREATE SUBSCRIPTION mysub
CONNECTION 'host=192.168.1.50 port=5432 user=foo dbname=foodb'
PUBLICATION mypublication, insert_only;


CREATE SUBSCRIPTION mysub
CONNECTION 'host=192.168.1.50 port=5432 user=foo dbname=foodb'
PUBLICATION insert_only
WITH (enabled = false);
