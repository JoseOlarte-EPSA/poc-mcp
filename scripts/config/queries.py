# Diccionario con las consultas XML disponibles
QUERIES = {
    #Listado de reuniones agendadas para la semana en curso / Alerta para el seguimiento de reuniones ya celebradas
    "Reuniones Agendadas entre Fechas": """<fetch>
    <entity name="appointment">
        <attribute name="scheduledstart" />
        <attribute name="iav_resultcomments" />
        <filter type="and">
            <condition attribute="scheduledstart" operator="ge" value="{fechaInicio}T00:00:00.0000000Z" />
            <condition attribute="scheduledstart" operator="le" value="{fechaFin}T23:59:59.9999999Z" />
        </filter>
        <link-entity name="contact" from="contactid" to="fin_mainmeetingcontactid" alias="contact" link-type="outer">
            <attribute name="fullname" />
            <attribute name="jobtitle" />
            <attribute name="telephone1" />
        </link-entity>
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="accountid" />
            <attribute name="accountnumber" />
            <attribute name="name" />
            <attribute name="iav_initialscore" />
            <attribute name="iav_nif" />
            <link-entity name="fig_industriafi" from="fig_industriafiid" to="fig_industriafi" alias="industria_fi" link-type="outer">
                <attribute name="fig_name" />
            </link-entity>
            <link-entity name="fin_group" from="fin_groupid" to="fin_groupaliasid" alias="group" link-type="outer">
                <attribute name="fin_name" />
            </link-entity>
            <link-entity name="fin_majorsector" from="fin_majorsectorid" to="fin_fisectorid" alias="sector" link-type="inner">
                <attribute name="fin_name" />
            </link-entity>
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user" link-type="inner">
                <attribute name="domainname" />
                <filter type="and">
                    <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                    <condition attribute="isdisabled" operator="eq" value="0" />
                    <condition attribute="fig_managementunitid" operator="in">
                        <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                        <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                    </condition>
                </filter>
            </link-entity>
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="createdby" alias="created_by" link-type="inner">
            <attribute name="domainname" />
            <filter type="and">
                <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                <condition attribute="isdisabled" operator="eq" value="0" />
                <condition attribute="fig_managementunitid" operator="in">
                    <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                    <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                </condition>
            </filter>
        </link-entity>
    </entity>
</fetch>""",
    # Resumen de las citas celebradas (incluye competencia)
    "Resumen de Citas Celebradas":"""<fetch>
    <entity name="appointment">
        <attribute name="scheduledstart" />
        <attribute name="subject" />
        <attribute name="iav_resultcomments" />
        <filter type="and">
            <condition attribute="iav_accountid" operator="in">{cuentasIds}</condition>
            <condition attribute="scheduledstart" operator="ge" value="{fechaInicio}" />
            <condition attribute="scheduledstart" operator="le" value="{fechaFin}" />
        </filter>
        <link-entity name="contact" from="contactid" to="fin_mainmeetingcontactid" alias="main_contact" link-type="outer">
            <attribute name="fullname" />
        </link-entity>
        <link-entity name="contact" from="contactid" to="fig_attendeesid" alias="attendees" link-type="outer">
            <attribute name="fullname" />
        </link-entity>
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user" link-type="inner">
                <attribute name="domainname" />
                <filter type="and">
                    <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                    <condition attribute="isdisabled" operator="eq" value="0" />
                    <condition attribute="fig_managementunitid" operator="in">
                        <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                        <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                    </condition>
                </filter>
            </link-entity>
            <attribute name="name" />
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="createdby" alias="created_by" link-type="inner">
            <attribute name="domainname" />
            <filter type="and">
                <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                <condition attribute="isdisabled" operator="eq" value="0" />
                <condition attribute="fig_managementunitid" operator="in">
                    <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                    <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                </condition>
            </filter>
        </link-entity>
    </entity>
</fetch>""",
    # Resumen de las llamadas celebradas
    "Resumen de Llamadas Celebradas": """<fetch>
    <entity name="phonecall">
        <attribute name="actualend" />
        <attribute name="subject" />
        <attribute name="iav_result" />
        <attribute name="regardingobjectid" />
        <attribute name="iav_type" />
        <attribute name="phonenumber" />
        <filter type="and">
            <condition attribute="iav_accountid" operator="in">{cuentasIds}</condition>
            <condition attribute="actualend" operator="ge" value="{fechaInicio}" />
            <condition attribute="actualend" operator="le" value="{fechaFin}" />
        </filter>
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="fin_accountmanagerid" alias="user" link-type="inner">
            <attribute name="domainname" />
            <filter type="and">
                <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                <condition attribute="isdisabled" operator="eq" value="0" />
                <condition attribute="fig_managementunitid" operator="in">
                    <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                    <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                </condition>
            </filter> 
        </link-entity>        
        <link-entity name="systemuser" from="systemuserid" to="createdby" alias="created_by" link-type="inner">
            <attribute name="domainname" />
            <filter type="and">
                <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                <condition attribute="isdisabled" operator="eq" value="0" />
                <condition attribute="fig_managementunitid" operator="in">
                    <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                    <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                </condition>
            </filter>
        </link-entity>
    </entity>
</fetch>""",
    # Resumen de las ofertas lanzadas
    "Resumen de Ofertas Lanzadas":"""<fetch>
    <entity name="iav_opportunityservice">
        <attribute name="createdon" />
        <attribute name="statecode" />
        <attribute name="statuscode" />
        <attribute name="iav_successprobability" />
        <filter type="and">
            <condition attribute="iav_accountid" operator="in">{cuentasIds}</condition>
        </filter>
        <link-entity name="opportunity" from="opportunityid" to="iav_opportunityid" alias="opportunity" link-type="outer">
            <attribute name="name" />
        </link-entity>
        <link-entity name="iav_typeservice" from="iav_typeserviceid" to="iav_typeserviceid" alias="typeofservice" link-type="outer">
            <attribute name="iav_name" />
        </link-entity>
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user" link-type="inner">
                <attribute name="domainname" />
                <filter type="and">
                    <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                    <condition attribute="isdisabled" operator="eq" value="0" />
                    <condition attribute="fig_managementunitid" operator="in">
                        <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                        <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                    </condition>
                </filter>
            </link-entity>
            <attribute name="name" />
        </link-entity>
        <link-entity name="competitor" from="competitorid" to="fin_competitor" alias="competitor" link-type="outer">
            <attribute name="name" />
            <attribute name="createdon" />
        </link-entity>
        <link-entity name="fin_area" from="fin_areaid" to="fin_areaid" alias="area" link-type="outer">
            <attribute name="fin_name" />
        </link-entity>
        
        <link-entity name="systemuser" from="systemuserid" to="createdby" alias="created_by" link-type="inner">
            <attribute name="domainname" />
            <filter type="and">
                <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                <condition attribute="isdisabled" operator="eq" value="0" />
                <condition attribute="fig_managementunitid" operator="in">
                    <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                    <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                </condition>
            </filter>
        </link-entity>
    </entity>
</fetch>
    """,
    # Alertas para el seguimiento a primeras llamadas
        # Llamadas abiertas cuyo propietario sea el usuario en cuestión que contentan en la descripción de la llamada abierta CALIENTE.
    "Llamadas Abiertas": """<fetch>
    <entity name="phonecall">
        <attribute name="description" />
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />
            <attribute name="iav_initialscore" />
            <attribute name="axz_lastcontactdate" />
            <link-entity name="fin_group" from="fin_groupid" to="fin_groupaliasid" alias="group_alias" link-type="outer">
                <attribute name="fin_name" />
            </link-entity>
            <link-entity name="fig_industriafi" from="fig_industriafiid" to="fig_industriafi" alias="industria_fi" link-type="outer">
                <attribute name="fig_name" />
            </link-entity>
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user_account" link-type="outer">
                <attribute name="systemuserid" />
                <attribute name="fullname" />
                <attribute name="domainname" />
                <filter type="and">
                    <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                    <condition attribute="isdisabled" operator="eq" value="0" />
                    <condition attribute="fig_managementunitid" operator="in">
                        <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                        <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                    </condition>
                </filter>
            </link-entity>
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="createdby" alias="created_by" link-type="inner">
            <attribute name="domainname" />
            <filter type="and">
                <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                <condition attribute="isdisabled" operator="eq" value="0" />
                <condition attribute="fig_managementunitid" operator="in">
                    <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                    <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                </condition>
            </filter>
        </link-entity>             
        <filter type="and">
            <condition attribute="actualstart" operator="ge" value="{currentDate}" />
        </filter>
    </entity>
</fetch>""",
    # Recordatorios de leads pendientes de gestión
    "Leads Abiertos":"""<fetch>
    <entity name="lead">
        <attribute name="fin_leadcomments" />
        <attribute name="createdon" />
        <link-entity name="account" from="accountid" to="parentaccountid" alias="account" link-type="inner">
            <attribute name="name" />
            <attribute name="iav_initialscore" />            
            <attribute name="axz_lastcontactdate" />
            <link-entity name="fin_group" from="fin_groupid" to="fin_groupaliasid" alias="group_alias" link-type="outer">
                <attribute name="fin_name" />
            </link-entity>
            <link-entity name="fig_industriafi" from="fig_industriafiid" to="fig_industriafi" alias="industria_fi" link-type="outer">
                <attribute name="fig_name" />
            </link-entity>
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user" link-type="inner">
                <attribute name="domainname" />
                <filter type="and">
                    <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                    <condition attribute="isdisabled" operator="eq" value="0" />
                    <condition attribute="fig_managementunitid" operator="in">
                        <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                        <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                    </condition>
                </filter>
            </link-entity>
        </link-entity>
        <link-entity name="fin_leadchannel" from="fin_leadchannelid" to="fin_leadchannelid" alias="source_channel" link-type="outer">
            <attribute name="fin_name" />
        </link-entity>
        <link-entity name="campaign" from="campaignid" to="campaignid" alias="campaign" link-type="outer">
            <attribute name="name" />
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="createdby" alias="created_by" link-type="inner">
            <attribute name="domainname" />
            <filter type="and">
                <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                <condition attribute="isdisabled" operator="eq" value="0" />
                <condition attribute="fig_managementunitid" operator="in">
                    <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                    <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                </condition>
            </filter>
        </link-entity>
        <filter type="and">
            <condition attribute="statecode" operator="eq" value="0" />
        </filter>
    </entity>
</fetch>""",    
    #Alertas para el seguimiento de ofertas abiertas
    "Oportunidades Abiertas":"""<fetch>
    <entity name="iav_opportunityservice">
        <attribute name="iav_typecontract" />
        <attribute name="iav_totalfeesfiforecast" />
        <attribute name="createdon" />
        <attribute name="iav_successprobability" />
        <link-entity name="opportunity" from="opportunityid" to="iav_opportunityid" alias="opportunity" link-type="inner">
            <filter type="and">
                <condition attribute="fin_stagecategorybpf" operator="eq" value="6" />
                <condition attribute="statecode" operator="eq" value="0" />
            </filter>
        </link-entity>
        <link-entity name="iav_typeservice" from="iav_typeserviceid" to="iav_typeserviceid" alias="typeofservice" link-type="outer">
            <attribute name="iav_name" />
        </link-entity>
        <link-entity name="fin_area" from="fin_areaid" to="fin_areaid" alias="area" link-type="outer">
            <attribute name="fin_name" />
        </link-entity>
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />
            <link-entity name="fin_majorsector" from="fin_majorsectorid" to="fin_fisectorid" alias="sector" link-type="inner">
                <attribute name="fin_name" />
            </link-entity>
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user" link-type="inner">
                <attribute name="domainname" />
                <filter type="and">
                    <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                    <condition attribute="isdisabled" operator="eq" value="0" />
                    <condition attribute="fig_managementunitid" operator="in">
                        <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                        <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                    </condition>
                </filter>
            </link-entity>
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="createdby" alias="created_by" link-type="inner">
            <attribute name="domainname" />
            <filter type="and">
                <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                <condition attribute="isdisabled" operator="eq" value="0" />
                <condition attribute="fig_managementunitid" operator="in">
                    <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                    <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                </condition>
            </filter>
        </link-entity>
    </entity>
</fetch>""",
    #Alertas para el seguimiento de ofertas pendientes
    "Ofertas Pendientes":"""<fetch>
    <entity name="appointment">
        <attribute name="scheduledend" />
        <attribute name="iav_resultcomments" />
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user" link-type="inner">
                <attribute name="domainname" />
                <filter type="and">
                    <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                    <condition attribute="isdisabled" operator="eq" value="0" />
                    <condition attribute="fig_managementunitid" operator="in">
                        <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                        <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                    </condition>
                </filter>
            </link-entity>
        </link-entity>
        <link-entity name="contact" from="contactid" to="fin_mainmeetingcontactid" alias="contact" link-type="outer">
            <attribute name="fullname" />
        </link-entity>
        <filter type="and">
            <condition attribute="scheduledstart" operator="ge" value="{fechaInicio}T00:00:00.0000000Z" />
            <condition attribute="scheduledstart" operator="le" value="{fechaFin}T23:59:59.9999999Z" />
            <condition attribute="iav_result" operator="eq" value="200000003" />
        </filter>
        <link-entity name="systemuser" from="systemuserid" to="createdby" alias="created_by" link-type="inner">
            <attribute name="domainname" />
            <filter type="and">
                <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                <condition attribute="isdisabled" operator="eq" value="0" />
                <condition attribute="fig_managementunitid" operator="in">
                    <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                    <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                </condition>
            </filter>
        </link-entity>
    </entity>
</fetch>    
    """,
    # Detalle de las ayudas
    "Detalle de las Ayudas": """SELECT 
  fbnds.BeneficiaryNif AS NIF
  ,fbnds.BeneficiaryName AS Account
  ,gr_grants.AnnouncementDescription AS AnnouncementDescription
  ,gr_grants.Organism AS "Organism"
  ,SUM(CASE WHEN dinst.Instrument = 'PRÉSTAMO' THEN fbnds.TotalAmountConcession ELSE 0 END) AS TotalPrestamo
  ,SUM(CASE WHEN dinst.Instrument = 'SUBVENCIÓN y ENTREGA DINERARIA SIN CONTRAPRESTACIÓN' THEN fbnds.TotalAmountConcession ELSE 0 END) AS TotalSubvencion
FROM 
  bdns.FactBdnsGs fbnds
INNER JOIN 
  bdns.DimGrantsSearcher gr_grants ON gr_grants.Id = fbnds.IdGrantsSearcher
LEFT JOIN
  bdns.DimInstrument dinst ON dinst.Id = fbnds.IdInstrument
WHERE 
  fbnds.BeneficiaryNif IN ({nifs})
GROUP BY
  fbnds.BeneficiaryNif
  ,fbnds.BeneficiaryName
  ,gr_grants.AnnouncementDescription
  ,gr_grants.Organism
;""",
    #Propuesta de llamadas
    "Llamadas entre Fechas": """<fetch>
    <entity name="phonecall">
        <filter type="and">
            <condition attribute="actualend" operator="ge" value="{fechaInicio}-01-01T00:00:01Z" />
            <condition attribute="actualend" operator="le" value="{fechaFin}" />
        </filter>
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="accountid" />
            <attribute name="accountnumber" />
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user" link-type="inner">
                <filter type="and">
                    <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                    <condition attribute="isdisabled" operator="eq" value="0" />
                    <condition attribute="fig_managementunitid" operator="in">
                        <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                        <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                    </condition>
                </filter>
            </link-entity>
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="createdby" alias="created_by" link-type="inner">
            <attribute name="domainname" />
            <filter type="and">
                <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                <condition attribute="isdisabled" operator="eq" value="0" />
                <condition attribute="fig_managementunitid" operator="in">
                    <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                    <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                </condition>
            </filter>
        </link-entity>
    </entity>
</fetch>
""",
    "Grants por Sector": """SELECT 
    g.Title, 
    s.Name
FROM 
    Sectors s
    INNER JOIN GrantSectors gs ON s.Id = gs.SectorId
    INNER JOIN Grants g ON gs.GrantId = g.Id
    INNER JOIN GrantLocations gl ON gl.GrantId = g.Id
    INNER JOIN Locations lc ON gl.LocationId = lc.Id
WHERE 
    g.Status IN (1, 2)
    AND g.Deleted = 0
    AND lc.CountryId = 'Es'
GROUP BY 
    g.Title, 
    s.Name
ORDER BY 
    MIN(g.OrderByStatusCategory) ASC, 
    MAX(g.CreatedOn) DESC;
""",
    #Poc2: Queries Insides
    #Resumen de las reuniones que ha agendado el operador para realizar la con-firmación. Reuniones abiertas o programadas cuyo autor de la cita sea el usuario en cuestión con fecha de celebración (hora de inicio en CRM) la semana en curso. 
    #-Este no es el mismo de PoC1? No aplicaría el mismo anterior?
    #Detalle de las citas que ha generado durante el año que se encuentran en es-tado cancelado para realizar seguimiento. Reuniones canceladas cuyo autor de la cita sea el usuario en cuestión con fecha de creación de la cita sea el año en curso.
    "Citas Canceladas entre Fechas": """<fetch>
    <entity name="appointment">
        <attribute name="scheduledstart" />
        <attribute name="iav_resultcomments" />
        <filter type="and">
            <condition attribute="scheduledstart" operator="ge" value="{fechaInicio}-01-01T00:00:01Z" />
            <condition attribute="scheduledstart" operator="le" value="{fechaFin}T23:59:59.9999999Z" />
            <condition attribute="statecode" operator="eq" value="2" />
        </filter>
        <link-entity name="contact" from="contactid" to="fin_mainmeetingcontactid" alias="contact" link-type="outer">
            <attribute name="fullname" />
            <attribute name="jobtitle" />
            <attribute name="telephone1" />
        </link-entity>
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="accountid" />
            <attribute name="accountnumber" />
            <attribute name="name" />
            <attribute name="iav_initialscore" />
            <attribute name="iav_nif" />
            <link-entity name="fig_industriafi" from="fig_industriafiid" to="fig_industriafi" alias="industria_fi" link-type="outer">
                <attribute name="fig_name" />
            </link-entity>
            <link-entity name="fin_group" from="fin_groupid" to="fin_groupaliasid" alias="group" link-type="outer">
                <attribute name="fin_name" />
            </link-entity>
            <link-entity name="fin_majorsector" from="fin_majorsectorid" to="fin_fisectorid" alias="sector" link-type="inner">
                <attribute name="fin_name" />
            </link-entity>
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user" link-type="inner">
                <attribute name="domainname" />
                <filter type="and">
                    <condition attribute="isdisabled" operator="eq" value="0" />
                    <condition attribute="fig_managementunitid" operator="in">
                        <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                        <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                    </condition>
                </filter>
            </link-entity>
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="createdby" alias="created_by" link-type="inner">
            <attribute name="domainname" />
            <filter type="and">
                <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                <condition attribute="isdisabled" operator="eq" value="0" />
                <condition attribute="fig_managementunitid" operator="in">
                    <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                    <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                </condition>
            </filter>
        </link-entity>
    </entity>
</fetch>""",
    #Alerta sobre reuniones generadas por el operador celebradas sin llamada pos-terior en los 6 siguientes meses. Reuniones completadas cuyo autor de la cita sea el usuario en cuestión con fecha de celebración seis meses atrás sin activi-dad posterior. Toda la semana de hace 6 meses, podríamos basarnos en la fecha de último contacto
    "Citas de Cuentas con último contacto hace 6 meses": """<fetch>
    <entity name="appointment">
        <attribute name="scheduledstart" />
        <attribute name="iav_resultcomments" />
        <link-entity name="contact" from="contactid" to="fin_mainmeetingcontactid" alias="contact" link-type="outer">
            <attribute name="fullname" />
            <attribute name="jobtitle" />
            <attribute name="telephone1" />
        </link-entity>
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="accountid" />
            <attribute name="accountnumber" />
            <attribute name="name" />
            <attribute name="iav_initialscore" />
            <attribute name="iav_nif" />            
            <filter type="and">
                <condition attribute="axz_lastcontactdate" operator="ge" value="{fechaInicio}T00:00:00.0000000Z" />
                <condition attribute="axz_lastcontactdate" operator="le" value="{fechaFin}T23:59:59.9999999Z" />
            </filter>
            <link-entity name="fig_industriafi" from="fig_industriafiid" to="fig_industriafi" alias="industria_fi" link-type="outer">
                <attribute name="fig_name" />
            </link-entity>
            <link-entity name="fin_group" from="fin_groupid" to="fin_groupaliasid" alias="group" link-type="outer">
                <attribute name="fin_name" />
            </link-entity>
            <link-entity name="fin_majorsector" from="fin_majorsectorid" to="fin_fisectorid" alias="sector" link-type="inner">
                <attribute name="fin_name" />
            </link-entity>
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user" link-type="inner">
                <attribute name="domainname" />
                <filter type="and">
                    <condition attribute="title" operator="like" value="%Inside%" />
                    <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                    <condition attribute="isdisabled" operator="eq" value="0" />
                    <condition attribute="fig_managementunitid" operator="in">
                        <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                        <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                    </condition>
                </filter>
            </link-entity>
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="createdby" alias="created_by" link-type="inner">
            <attribute name="domainname" />
            <filter type="and">
                <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />
                <condition attribute="isdisabled" operator="eq" value="0" />
                <condition attribute="fig_managementunitid" operator="in">
                    <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>
                    <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>
                </condition>
            </filter>
        </link-entity>
    </entity>
</fetch>"""
}

PROMPTS = {
    "summarize_news": (
        "resume la noticia titulada {titulo}, "
        "con el contenido {contenido}. "
        "En caso de error de servidor dejar vacío. "
        "En caso de dato vacío dejar vacío. "
        "No añadir más texto del requerido."
    ),
}