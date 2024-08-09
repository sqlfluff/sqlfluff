ALTER TABLE example_dataset.example_table2
ADD CONSTRAINT my_fk_name FOREIGN KEY (x)
REFERENCES example_dataset.example_table(x) NOT ENFORCED;

ALTER TABLE `example_dataset.example_table`
ADD PRIMARY KEY (`x`) NOT ENFORCED;

ALTER TABLE fk_table
ADD PRIMARY KEY (x,y) NOT ENFORCED,
ADD CONSTRAINT fk FOREIGN KEY (u, v) REFERENCES pk_table(x, y) NOT ENFORCED,
ADD CONSTRAINT `fk2` FOREIGN KEY (`i`, `j`) REFERENCES `pk_table`(`x`, `y`) NOT ENFORCED;
