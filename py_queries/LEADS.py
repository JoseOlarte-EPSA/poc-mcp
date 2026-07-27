# Queries FetchXML para la entidad 'leads' (leads)
# Los placeholders usan la notación {NOMBRE} para sustitución dinámica.

#LEADS_POR_COMERCIAL
#LEADS_POR_GESTOR
#LEADS_POR_CUENTA

LEADS_ABIERTOS_POR_COMERCIAL = """<fetch top="50">
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
            </link-entity>
        </link-entity>
        <link-entity name="fin_leadchannel" from="fin_leadchannelid" to="fin_leadchannelid" alias="source_channel" link-type="outer">
            <attribute name="fin_name" />
        </link-entity>
        <link-entity name="campaign" from="campaignid" to="campaignid" alias="campaign" link-type="outer">
            <attribute name="name" />
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
        <filter type="and">
            <condition attribute="statecode" operator="eq" value="0" />
        </filter>
    </entity>
</fetch>"""

LEADS_ABIERTOS_POR_GESTOR = """<fetch top="50">
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
        <link-entity name="fin_leadchannel" from="fin_leadchannelid" to="fin_leadchannelid" alias="source_channel" link-type="outer">
            <attribute name="fin_name" />
        </link-entity>
        <link-entity name="campaign" from="campaignid" to="campaignid" alias="campaign" link-type="outer">
            <attribute name="name" />
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="created_by" link-type="inner">
            <attribute name="domainname" />
        </link-entity>
        <filter type="and">
            <condition attribute="statecode" operator="eq" value="0" />
        </filter>
    </entity>
</fetch>"""

LEADS_ABIERTOS_POR_CUENTA = """<fetch top="50">
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
            </link-entity>
            <filter type="and">               
                <condition attribute="name" operator="eq" value="{NOMBRE_DE_CUENTA}" />          
            </filter> 
        </link-entity>
        <link-entity name="fin_leadchannel" from="fin_leadchannelid" to="fin_leadchannelid" alias="source_channel" link-type="outer">
            <attribute name="fin_name" />
        </link-entity>
        <link-entity name="campaign" from="campaignid" to="campaignid" alias="campaign" link-type="outer">
            <attribute name="name" />
        </link-entity>
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="created_by" link-type="inner">
            <attribute name="domainname" />
        </link-entity>
        <filter type="and">
            <condition attribute="statecode" operator="eq" value="0" />
        </filter>
    </entity>
</fetch>"""