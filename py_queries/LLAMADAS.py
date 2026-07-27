# Queries FetchXML para la entidad 'phonecall' (llamadas)
# Los placeholders usan la notación {NOMBRE} para sustitución dinámica.

LLAMADAS_SEMANA_EN_CURSO = """<fetch>
    <entity name="phonecall">
        <attribute name="actualend" />
        <attribute name="subject" />
        <attribute name="iav_result" />
        <attribute name="regardingobjectid" />
        <attribute name="iav_type" />
        <attribute name="phonenumber" />
        <attribute name="scheduledstart" />
        <attribute name="description" />
        <order attribute="actualend" descending="true" />   
        <filter type="and">
            <condition attribute="scheduledstart" operator="this-week" />
        </filter>
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="fin_accountmanagerid" alias="user" link-type="inner">
            <attribute name="domainname" />
        </link-entity>        
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">
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

LLAMADAS_POR_CUENTA = """<fetch top="50">
    <entity name="phonecall">
        <attribute name="actualend" />
        <attribute name="subject" />
        <attribute name="iav_result" />
        <attribute name="regardingobjectid" />
        <attribute name="iav_type" />
        <attribute name="phonenumber" />
        <attribute name="description" />
        <order attribute="actualend" descending="true" />
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />    
            <filter type="and">               
                <condition attribute="name" operator="eq" value="{NOMBRE_DE_CUENTA}" />          
            </filter>      
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="fin_accountmanagerid" alias="user" link-type="inner">
            <attribute name="domainname" />
        </link-entity>        
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">
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

LLAMADAS_POR_NIF = """<fetch top="50">
    <entity name="phonecall">
        <attribute name="actualend" />
        <attribute name="subject" />
        <attribute name="iav_result" />
        <attribute name="regardingobjectid" />
        <attribute name="iav_type" />
        <attribute name="phonenumber" />
        <attribute name="description" />
        <order attribute="actualend" descending="true" />
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />    
            <filter type="and">               
                <condition attribute="iav_nif" operator="eq" value="{NIF}" />          
            </filter>      
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="fin_accountmanagerid" alias="user" link-type="inner">
            <attribute name="domainname" />
        </link-entity>        
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">
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

LLAMADAS_POR_COMERCIAL = """<fetch top="50">
    <entity name="phonecall">
        <attribute name="actualend" />
        <attribute name="subject" />
        <attribute name="iav_result" />
        <attribute name="regardingobjectid" />
        <attribute name="iav_type" />
        <attribute name="phonenumber" />
        <attribute name="description" />
        <order attribute="actualend" descending="true" />   
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="fin_accountmanagerid" alias="user" link-type="inner">
            <attribute name="domainname" />
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
</fetch>"""

LLAMADAS_POR_COMERCIAL_SEMANA_EN_CURSO = """<fetch> 
    <entity name="phonecall">
        <attribute name="actualend" />
        <attribute name="subject" />
        <attribute name="iav_result" />
        <attribute name="regardingobjectid" />
        <attribute name="iav_type" />
        <attribute name="phonenumber" />        
        <attribute name="description" />
        <order attribute="actualend" descending="true" />   
        <filter type="and">
            <condition attribute="scheduledstart" operator="this-week" />
        </filter>
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="fin_accountmanagerid" alias="user" link-type="inner">
            <attribute name="domainname" />
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
</fetch>"""

LLAMADAS_POR_GESTOR = """<fetch top="50">
    <entity name="phonecall">
        <attribute name="actualend" />
        <attribute name="subject" />
        <attribute name="iav_result" />
        <attribute name="regardingobjectid" />
        <attribute name="iav_type" />
        <attribute name="phonenumber" />
        <attribute name="description" />
        <order attribute="actualend" descending="true" />   
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="fin_accountmanagerid" alias="user" link-type="inner">
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
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">
            <attribute name="domainname" />
        </link-entity>
    </entity>
</fetch>"""

LLAMADAS_POR_GESTOR_SEMANA_EN_CURSO = """<fetch>
    <entity name="phonecall">
        <attribute name="actualend" />
        <attribute name="subject" />
        <attribute name="iav_result" />
        <attribute name="regardingobjectid" />
        <attribute name="iav_type" />
        <attribute name="phonenumber" />
        <attribute name="description" />
        <order attribute="scheduledstart" descending="true" />   
        <filter type="and">
            <condition attribute="scheduledstart" operator="this-week" />
        </filter>
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="fin_accountmanagerid" alias="user" link-type="inner">
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
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">
            <attribute name="domainname" />
        </link-entity>
    </entity>
</fetch>"""

LLAMADAS_ABIERTAS = """<fetch top="50">
    <entity name="phonecall">
        <attribute name="actualend" />
        <attribute name="subject" />
        <attribute name="iav_result" />
        <attribute name="regardingobjectid" />
        <attribute name="iav_type" />
        <attribute name="phonenumber" />
        <attribute name="description" />
        <order attribute="actualend" descending="true" />
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="fin_accountmanagerid" alias="user" link-type="inner">
            <attribute name="domainname" />
        </link-entity>        
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">
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
            <condition attribute="scheduledstart" operator="ge" value="{CURRENT_DATE}" />
        </filter>
    </entity>
</fetch>"""

LLAMADAS_ABIERTAS_POR_CUENTA = """<fetch>
    <entity name="phonecall">
        <attribute name="actualend" />
        <attribute name="subject" />
        <attribute name="iav_result" />
        <attribute name="regardingobjectid" />
        <attribute name="iav_type" />
        <attribute name="phonenumber" />
        <attribute name="description" />
        <order attribute="actualend" descending="true" /> 
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />    
            <filter type="and">               
                <condition attribute="name" operator="eq" value="{NOMBRE_DE_CUENTA}" />          
            </filter>      
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="fin_accountmanagerid" alias="user" link-type="inner">
            <attribute name="domainname" />
        </link-entity>        
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">
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
            <condition attribute="scheduledstart" operator="ge" value="{CURRENT_DATE}" />
        </filter>
    </entity>
</fetch>"""

LLAMADAS_ABIERTAS_POR_NIF = """<fetch>
    <entity name="phonecall">
        <attribute name="actualend" />
        <attribute name="subject" />
        <attribute name="iav_result" />
        <attribute name="regardingobjectid" />
        <attribute name="iav_type" />
        <attribute name="phonenumber" />
        <attribute name="description" />
        <order attribute="actualend" descending="true" /> 
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />    
            <filter type="and">               
                <condition attribute="iav_nif" operator="eq" value="{NIF}" />          
            </filter>      
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="fin_accountmanagerid" alias="user" link-type="inner">
            <attribute name="domainname" />
        </link-entity>        
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">
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
            <condition attribute="scheduledstart" operator="ge" value="{CURRENT_DATE}" />
        </filter>
    </entity>
</fetch>"""

LLAMADAS_ABIERTAS_POR_COMERCIAL = """<fetch top="50">
    <entity name="phonecall">
        <attribute name="actualend" />
        <attribute name="subject" />
        <attribute name="iav_result" />
        <attribute name="regardingobjectid" />
        <attribute name="iav_type" />
        <attribute name="phonenumber" />
        <attribute name="description" />
        <order attribute="actualend" descending="true" />   
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="fin_accountmanagerid" alias="user" link-type="inner">
            <attribute name="domainname" />
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
        <filter type="and">
            <condition attribute="scheduledstart" operator="ge" value="{CURRENT_DATE}" />
        </filter>
    </entity>
</fetch>"""

LLAMADAS_ABIERTAS_POR_GESTOR = """<fetch top="50">
    <entity name="phonecall">
        <attribute name="actualend" />
        <attribute name="subject" />
        <attribute name="iav_result" />
        <attribute name="regardingobjectid" />
        <attribute name="iav_type" />
        <attribute name="phonenumber" />
        <attribute name="description" />
        <order attribute="actualend" descending="true" />   
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="fin_accountmanagerid" alias="user" link-type="inner">
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
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">
            <attribute name="domainname" />
        </link-entity>
        <filter type="and">
            <condition attribute="scheduledstart" operator="ge" value="{CURRENT_DATE}" />
        </filter>
    </entity>
</fetch>"""