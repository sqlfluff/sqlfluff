RAISERROR(15600, -1, -1, 'mysp_CreateCustomer');

RAISERROR('This is message %s %d.', 10, 1, 'number');

RAISERROR('Error raised in TRY block.', 16, 1);

RAISERROR (N'Unicode error', 16, 1);

RAISERROR ('WITH option', 16, 1) WITH LOG;


RAISERROR ('Error with lots of arguments %a %b %c %d %e %f %g %h %i %j %k %l %m %n %o %p %q %r %s %t', 16, 1,
		'a',
		N'b',
		@c,
		4,
		5,
		6,
		7,
		8,
		9,
		10,
		11,
		12,
		13,
		14,
		15,
		16,
		17,
		18,
		19,
		20);
