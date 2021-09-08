CREATE DATABASE meteor;
USE meteor;

CREATE TABLE HousingType (
	HousingType varchar(255),
    PRIMARY KEY (HousingType)
);
INSERT INTO HousingType (
	HousingType
) VALUES 
	("Landed"),
    ("Condomunium"),
    ("HDB")
;

CREATE TABLE HouseHold (
	HouseID INT AUTO_INCREMENT,
    HousingType varchar(255),
    PRIMARY KEY (HouseID),
    FOREIGN KEY (HousingType) REFERENCES HousingType (HousingType) ON UPDATE CASCADE ON DELETE NO ACTION
);
    