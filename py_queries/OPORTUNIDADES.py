# Queries FetchXML para la entidad 'iav_opportunityservices' (servicios de oportunidad)
# Los placeholders usan la notación {NOMBRE} para sustitución dinámica.

SERVICIOS_DE_OPORTUNIDAD_POR_COMERCIAL = """<fetch top="50">
    <entity name="iav_opportunityservice">
        <attribute name="createdon" />
        <attribute name="statecode" />
        <attribute name="statuscode" />
        <attribute name="iav_successprobability" />
        <link-entity name="opportunity" from="opportunityid" to="iav_opportunityid" alias="opportunity" link-type="outer">
            <attribute name="name" />
        </link-entity>
        <link-entity name="iav_typeservice" from="iav_typeserviceid" to="iav_typeserviceid" alias="typeofservice" link-type="outer">
            <attribute name="iav_name" />
        </link-entity>
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user" link-type="inner">
                <attribute name="domainname" />
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
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">            
            <attribute name="domainname" />            
            <filter type="and">               
                <condition attribute="domainname" operator="eq" value="{EMAIL_USUARIO}" />  
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
    """
    
SERVICIOS_DE_OPORTUNIDAD_POR_GESTOR = """<fetch top="50">
    <entity name="iav_opportunityservice">
        <attribute name="createdon" />
        <attribute name="statecode" />
        <attribute name="statuscode" />
        <attribute name="iav_successprobability" />
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
                    <condition attribute="domainname" operator="eq" value="{EMAIL_USUARIO}" />  
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
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">            
            <attribute name="domainname" />      
        </link-entity>
    </entity>
</fetch>
    """

SERVICIOS_DE_OPORTUNIDAD_POR_CUENTA = """<fetch>
    <entity name="iav_opportunityservice">
        <attribute name="createdon" />
        <attribute name="statecode" />
        <attribute name="statuscode" />
        <attribute name="iav_successprobability" />
        <link-entity name="opportunity" from="opportunityid" to="iav_opportunityid" alias="opportunity" link-type="outer">
            <attribute name="name" />
        </link-entity>
        <link-entity name="iav_typeservice" from="iav_typeserviceid" to="iav_typeserviceid" alias="typeofservice" link-type="outer">
            <attribute name="iav_name" />
        </link-entity>
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user" link-type="inner">
                <attribute name="domainname" />
            </link-entity>
            <attribute name="name" />
            <filter type="and">               
                <condition attribute="name" operator="eq" value="{NOMBRE_DE_CUENTA}" />          
            </filter>  
        </link-entity>
        <link-entity name="competitor" from="competitorid" to="fin_competitor" alias="competitor" link-type="outer">
            <attribute name="name" />
            <attribute name="createdon" />
        </link-entity>
        <link-entity name="fin_area" from="fin_areaid" to="fin_areaid" alias="area" link-type="outer">
            <attribute name="fin_name" />
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">            
            <attribute name="domainname" />      
        </link-entity>
    </entity>
</fetch>
    """
    
SERVICIOS_DE_OPORTUNIDAD_ABIERTA_POR_COMERCIAL = """<fetch top="50">
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
            </link-entity>
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="created_by" link-type="inner">
            <attribute name="domainname" />    
            <filter type="and">               
                <condition attribute="domainname" operator="eq" value="{EMAIL_USUARIO}" />  
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

SERVICIOS_DE_OPORTUNIDAD_ABIERTA_POR_GESTOR = """<fetch top="50">
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
                    <condition attribute="domainname" operator="eq" value="{EMAIL_USUARIO}" />  
                    <condition attribute="businessunitid" operator="eq" value="2bf0da8a-6fbc-e611-80ea-c4346badc0e4" />                
                    <condition attribute="isdisabled" operator="eq" value="0" />                
                    <condition attribute="fig_managementunitid" operator="in">                    
                        <value>10b7dd31-74b6-f011-bbd3-7c1e5211af47</value>                    
                        <value>2d40813e-74b6-f011-bbd3-7c1e5211af47</value>                
                    </condition>            
                </filter>
            </link-entity>
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="created_by" link-type="inner">
            <attribute name="domainname" />      
        </link-entity>
    </entity>
</fetch>"""

SERVICIOS_DE_OPORTUNIDAD_ABIERTA_POR_CUENTA = """<fetch>
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
            <filter type="and">               
                <condition attribute="name" operator="eq" value="{NOMBRE_DE_CUENTA}" />          
            </filter>  
            <link-entity name="fin_majorsector" from="fin_majorsectorid" to="fin_fisectorid" alias="sector" link-type="inner">
                <attribute name="fin_name" />
            </link-entity>
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user" link-type="inner">
                <attribute name="domainname" />
            </link-entity>
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="created_by" link-type="inner">
            <attribute name="domainname" />      
        </link-entity>
    </entity>
</fetch>"""