LISTEN virtual;
NOTIFY virtual;
UNLISTEN virtual;

LISTEN "virtual listener";
NOTIFY "virtual listener";
UNLISTEN "virtual listener";

LISTEN listener_a;
LISTEN listener_b;
NOTIFY listener_a, 'payload_a';
NOTIFY listener_b, 'payload_b';
UNLISTEN *
