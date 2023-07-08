select employee_id, manager_id, title
from employees
start with title = 'President'
connect by
    manager_id = prior employee_id
order by employee_id;

select sys_connect_by_path(title, ' -> '), employee_id, manager_id, title
from employees
start with title = 'President'
connect by
    manager_id = prior employee_id
order by employee_id;

select
  description,
  quantity,
  component_id,
  parent_component_id,
  sys_connect_by_path(component_id, ' -> ') as path
from components
start with component_id = 1
connect by
    parent_component_id = prior component_id
order by path;

select
employee_id, manager_id, title,
connect_by_root title as root_title
from employees
start with title = 'President'
connect by
    manager_id = prior employee_id
order by employee_id;
