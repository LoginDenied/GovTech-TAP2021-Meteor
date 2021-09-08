CREATE DATABASE meteor;
USE meteor;

/* Lookup table for HouseHold */
CREATE TABLE HousingType (
	HousingType VARCHAR(255),
    PRIMARY KEY (HousingType)
);
INSERT INTO HousingType (
	HousingType
) VALUES 
	("Landed"),
    ("Condomunium"),
    ("HDB")
;

/* Household table */
CREATE TABLE HouseHold (
	HouseID INT AUTO_INCREMENT,
    HousingType VARCHAR(255),
    PRIMARY KEY (HouseID),
    FOREIGN KEY (HousingType) REFERENCES HousingType (HousingType) ON UPDATE CASCADE ON DELETE NO ACTION
);

/* Lookup tables for MemberLivesIn */
CREATE TABLE Gender (
	Gender VARCHAR(255),
    PRIMARY KEY (Gender)
 );
 INSERT INTO Gender (
	Gender
) VALUES
	("Male"),
    ("Female")
;
CREATE TABLE MaritalStatus (
	MaritalStatus VARCHAR(255),
    PRIMARY KEY (MaritalStatus)
);
INSERT INTO MaritalStatus (
	MaritalStatus
) VALUES
	("Single"),
	("Married"),
    ("Divorced")
;
CREATE TABLE OccupationType (
	OccupationType VARCHAR(255),
    PRIMARY KEY (OccupationType)
);
INSERT INTO OccupationType (
	OccupationType
) VALUES 
	("Unemployed"),
    ("Student"),
    ("Employed")
;

/* MemberLivesIn table */
CREATE TABLE MemberLivesIn (
	Name VARCHAR(255),
    Gender VARCHAR(255) NOT NULL,
    MaritalStatus VARCHAR(255) NOT NULL,
    Spouse VARCHAR(255) DEFAULT NULL,
    OccupationType VARCHAR(255) NOT NULL,
    AnnualIncome FLOAT NOT NULL,
    DOB DATE NOT NULL,
    PRIMARY KEY (Name),
    FOREIGN KEY (Gender) REFERENCES Gender (Gender) ON UPDATE CASCADE ON DELETE NO ACTION,
    FOREIGN KEY (MaritalStatus) REFERENCES MaritalStatus (MaritalStatus) ON UPDATE CASCADE ON DELETE NO ACTION,
    FOREIGN KEY (OccupationType) REFERENCES OccupationType (OccupationType) ON UPDATE CASCADE ON DELETE NO ACTION,
    FOREIGN KEY (Spouse) REFERENCES MemberLivesIn (Name) ON UPDATE CASCADE ON DELETE SET NULL
);