CREATE USER 'prj_svc' IDENTIFIED WITH AWSAuthenticationPlugin AS 'RDS';
CREATE USER 'jeffrey'@'localhost' IDENTIFIED BY 'password';
CREATE USER 'jeffrey'@'localhost'
  IDENTIFIED BY 'new_password' PASSWORD EXPIRE;
