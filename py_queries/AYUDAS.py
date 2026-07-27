DETALLE_DE_AYUDAS = """SELECT 
  fbnds.Beneficiary_NIF AS NIF
  ,fbnds.Beneficiary_Name AS Account
  ,gr_grants.Announcement_Description AS "Announcement Description"
  ,gr_grants.Organism AS "Organism"
  ,SUM(CASE WHEN dinst.Instrument = 'PRÉSTAMO' THEN fbnds.Total_Amount_Concession ELSE 0 END) AS "Total Prestamo"
  ,SUM(CASE WHEN dinst.Instrument = 'SUBVENCIÓN y ENTREGA DINERARIA SIN CONTRAPRESTACIÓN' THEN fbnds.Total_Amount_Concession ELSE 0 END) AS "Total Subvencion"
FROM 
  gold.Fact_BDNS_GS fbnds
INNER JOIN 
  gold.Dim_Grants_Searcher gr_grants ON gr_grants.Grants_Searcher_Id = fbnds.Grants_Searcher_Id
LEFT JOIN
  gold.Dim_Calendar_Reception_Announcement cal_reception ON cal_reception.Date_Id = fbnds.Reception_Announcement_Date_Id
LEFT JOIN
  gold.Dim_Instrument dinst ON dinst.Instrument_Id = fbnds.Instrument_Id
WHERE
  fbnds.Beneficiary_NIF = {ACCOUNT_NIF}
  AND cal_reception.Date BETWEEN DATEADD(YEAR, -3, GETDATE()) AND GETDATE()
GROUP BY
  fbnds.Beneficiary_NIF
  ,fbnds.Beneficiary_Name
  ,gr_grants.Announcement_Description
  ,gr_grants.Organism
;"""