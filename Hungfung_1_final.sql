/*create tables*/
PRAGMA foreign_keys=on;

CREATE TABLE Employee(
    EmployeeID char(7) NOT NULL,
    SIN int(9) NOT NULL,
    DateofBirth DATE NOT NULL,
    DateofHire DATE NOT NULL,
    Fname CHARACTER(100) NOT NULL,
    Mname CHARACTER(100) ,
    Lname CHARACTER(100) NOT NULL,
    Address CHARACTER(100) NOT NULL,
    PRIMARY KEY (EmployeeID)
    );
   
CREATE TABLE exEmployees(
    EmployeeID char(7) NOT NULL,
    SIN int(9) NOT NULL,
    DateofBirth DATE NOT NULL,
    DateofHire DATE NOT NULL,
    Fname CHARACTER(100) NOT NULL,
    Mname CHARACTER(100) ,
    Lname CHARACTER(100) NOT NULL,
    Address CHARACTER(100),
    TerminationDate DATE NOT NULL
    );

CREATE TABLE Vacation (
	ID char(7) NOT NULL,
    TotalVacationEarned int(100) NOT NULL,
    PercentageofGrossPay float NOT NULL,
    YearlyCarryOver int NOT NULL,
    TotalVacationPaid float NOT NULL,
    PRIMARY KEY (TotalVacationEarned, ID),
    FOREIGN KEY (ID) REFERENCES Employee(EmployeeID)
    ON DELETE CASCADE
    );


CREATE TABLE EmergencyContact(
    ContactName CHARACTER(100) NOT NULL,
    PhoneNumber char(20) NOT NULL,
    Relation CHARACTER(100) NOT NULL,
    ID CHARACTER(7) NOT NULL,
    PRIMARY KEY (ContactName, ID),
    FOREIGN KEY (ID) REFERENCES Employee(EmployeeID)
    ON DELETE CASCADE
  );
    
CREATE TABLE Office(
    ID char(7) NOT NULL,
    Salary int(9) NOT NULL,
    PRIMARY KEY (ID),
    FOREIGN KEY (ID) REFERENCES Employee(EmployeeID)
    ON DELETE CASCADE
    );
    
CREATE TABLE Operations(
    ID char(7) NOT NULL,
    WagePerHour float(9) NOT NULL,
    PRIMARY KEY (ID),
    FOREIGN KEY (ID) REFERENCES Employee(EmployeeID)
    ON DELETE CASCADE
    );

CREATE TABLE Payroll(
    ChequeNumber int(10) NOT NULL,
    PayrollDate Date NOT NULL,
    GrossPay float(20) NOT NULL,
    CPP float NOT NULL,
    EI float NOT NULL,
    FederalTax float NOT NULL,
    ProvincialTax float NOT NULL,
    ID char(7) NOT NULL,
    PRIMARY KEY (ChequeNumber),
    FOREIGN KEY (ID) REFERENCES Employee(EmployeeID)
    ON DELETE CASCADE
    );

CREATE TABLE Shift(
	ID char(10) NOT NULL,
    ShiftID char(10) NOT NULL,
    StartTime time NOT NULL,
    EndTime time NOT NULL,
    DateofShift date NOT NULL,
    PRIMARY KEY (ShiftID),
    FOREIGN KEY (ID) REFERENCES Employee(EmployeeID)
    ON DELETE CASCADE
    );




CREATE TABLE Phone(
    PhoneNumber CHAR(20) NOT NULL,
    ID char(7) NOT NULL,
    PRIMARY KEY(PhoneNumber, ID),
    FOREIGN KEY (ID) REFERENCES Employee(EmployeeID)
    ON DELETE CASCADE
);

CREATE TABLE Holiday(
    DateofHoliday date NOT NULL,
    HolidayName varchar(20) NOT NULL,
    PRIMARY KEY (DateofHoliday)

);



/*------------------------------------ Initial Values ------------------------------------------*/

INSERT INTO Holiday (DateofHoliday, HolidayName)
VALUES ('2021-01-01', 'New Year’s Day'),
        ('2021-02-15', 'Family Day'),
        ('2021-04-02', 'Good Friday'),
        ('2021-05-24', 'Victoria Day'),
        ('2021-07-01', 'Canada Day'),
        ('2021-08-02', 'BC Day'),
        ('2021-09-06', 'Labour Day'),
        ('2021-10-11', 'Thanksgiving'),
        ('2021-11-11', 'Remembrance Day'),
        ('2021-12-25', 'Christmas Day');


INSERT INTO Employee (EmployeeID, SIN, DateofBirth, DateofHire, Fname, Mname, Lname, Address)
VALUES (0001, 897586446, '1987-01-09', '2018-04-26', 'Jack', 'Young', 'Ma', '8990 Alpha Street'),
	   (0002, 397486256, '1987-04-28', '2010-03-23', 'Emma', 'Yye', 'Zhang', '8990 Beta Street'),
	   (0003, 296586884, '1980-09-01', '2012-05-16', 'Alan', 'Zhu', 'Kit', '1990 Nova Street'),
	   (0004, 697086464, '1970-03-21', '2013-01-04', 'Wilson', 'Stephan', 'Kit', '3090 Crew Street'),
       (0005, 197526335, '1990-02-09', '2015-07-07', 'Sharon', 'Yao', 'Wang', '1990 Walter Street');


INSERT INTO EmergencyContact  (ContactName, PhoneNumber, Relation, ID)
VALUES ('Belle Lu', '(889) 908-1728','Sister',0001),
       ('Wang Zhu', '(883) 902-1123','Wife',0002),
       ('Ling Che', '(183) 202-1098','Cousin',0003),
       ('Lee Hwang','(113) 204-1323','Friend',0004),
       ('Christopher Wayne','(522) 041-3623','Father',0005);


INSERT INTO Office (ID, Salary)
VALUES (0001, 60000),
       (0002, 50000);

INSERT INTO Operations(ID, WagePerHour)
VALUES (0003, 20),
       (0004, 18),
       (0005, 17);


INSERT INTO Phone(PhoneNumber, ID)
VALUES ('(778) 789-5645', 0001),
       ('(604) 512-3695', 0002),
	   ('(778) 956-1234', 0003),
	   ('(778) 456-1293', 0004),
	   ('(778) 236-1290', 0005);

INSERT INTO Vacation(ID, TotalVacationEarned, PercentageofGrossPay, YearlyCarryOver, TotalVacationPaid)
VALUES(0001,2000,0.4,2000,0),
	  (0002,5200,0.6,2200,3000),
	  (0003,5060,0.6,2060,3000),
	  (0004,5100,0.6,2100,3000);

INSERT INTO Shift(ID, ShiftID, StartTime, EndTime, DateofShift)
VALUES(0003,100,12,18,'2021-01-01'),
      (0003,101,11,15,'2021-02-15'),
      (0003,102,9,14,'2021-04-02'),
      (0003,103,12,16,'2021-05-24'),
      (0003,105,12,16,'2021-07-01'),
      (0003,106,12,18,'2021-08-02'),
      (0003,104,12,18,'2021-09-06'),
      (0003,107,12,18,'2021-10-11'),
      (0003,108,12,18,'2021-11-11'),
      (0003,109,12,18,'2021-12-25');



CREATE TRIGGER adding_to_exEmployess
   AFTER DELETE ON Employee
BEGIN
    INSERT INTO exEmployees 
    VALUES (old.EmployeeID, old.SIN, old.DateofBirth, old.DateofHire, old.Fname, old.Mname, old.Lname, old.Address,DATETIME('NOW'));
       
END;

CREATE TRIGGER update_vacation_pay
    AFTER UPDATE OF PercentageofGrossPay ON vacation
    FOR EACH ROW 
BEGIN 
    UPDATE vacation
    SET TotalVacationEarned = 1.2*(TotalVacationEarned);
END;



/*Division query*/


/*
CREATE TABLE EmployeeWithTwoYearsExperience AS 
SELECT employee.EmployeeID, employee.Fname, employee.Lname, DATEDIFF(SYSDATE, employee.DateofHire)/365 
FROM employee
WHERE DATEDIFF(SYSDATE, employee.DateofHire)/365 >2;

SELECT * FROM EmployeeWithTwoYearsExperience WHERE NOT EXISTS 
(SELECT * FROM Office WHERE EmployeewithTwoYearsExperience.EmployeeID = Office.ID )
);
*/


