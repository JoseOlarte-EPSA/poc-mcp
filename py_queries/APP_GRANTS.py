GRANTS_BY_SECTOR = """SELECT
    TOP 15
    g.Title, 
    s.Name
FROM 
    Sectors s
    INNER JOIN GrantSectors gs ON s.Id = gs.SectorId
    INNER JOIN Grants g ON gs.GrantId = g.Id
    INNER JOIN GrantLocations gl ON gl.GrantId = g.Id
    INNER JOIN Locations lc ON gl.LocationId = lc.Id
WHERE 
    s.Name = {SECTOR_GRANTS}
    AND g.Status IN (1, 2)
    AND g.Deleted = 0
    AND lc.CountryId = 'Es'
GROUP BY 
    g.Title, 
    s.Name
ORDER BY 
    MIN(g.OrderByStatusCategory) ASC, 
    MAX(g.CreatedOn) DESC;
"""