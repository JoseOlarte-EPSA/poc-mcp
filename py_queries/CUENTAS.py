CUENTAS_LLAMADAS_ANO_EN_CURSO = """<fetch distinct='true'>
    <entity name="account">
        <attribute name="accountnumber" />
        <attribute name="name" />
        <order attribute="name" descending="false" />
        <link-entity name="phonecall" from="iav_accountid" to="accountid" alias="pc" link-type="inner">
            <filter type="and">
                <condition attribute="actualend" operator="this-year" />
            </filter>
            <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">
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
    </entity>
</fetch>"""