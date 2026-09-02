# Queries FetchXML para la entidad 'appointment' (citas)
# Los placeholders usan la notación {NOMBRE} para sustitución dinámica.

CITAS_SEMANA_EN_CURSO = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />    
        <order attribute="scheduledstart" descending="true" />     
        <filter type="and">            
            <condition attribute="scheduledstart" operator="this-week" />        
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
            </link-entity>        
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

CITAS_12VA_SEMANA_ATRAS = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />   
        <order attribute="scheduledstart" descending="true" />     
        <filter type="and">            
            <condition attribute="scheduledstart" operator="ge" value="{START_DATE}" />
            <condition attribute="scheduledstart" operator="le" value="{END_DATE}" />      
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
            </link-entity>        
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

CITAS_POR_CUENTA = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />
        <order attribute="scheduledstart" descending="true" /> 
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
                <condition attribute="name" operator="eq" value="{NOMBRE_DE_CUENTA}" />          
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
                          
            </link-entity>        
        </link-entity>        
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">            
            <attribute name="domainname" />
        </link-entity>    
    </entity>
</fetch>"""

CITAS_POR_NIF = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />
        <order attribute="scheduledstart" descending="true" /> 
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
                <condition attribute="iav_nif" operator="eq" value="{NIF}" />          
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
                          
            </link-entity>        
        </link-entity>        
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">            
            <attribute name="domainname" /> 
        </link-entity>    
    </entity>
</fetch>"""

CITAS_POR_COMERCIAL = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />
        <order attribute="scheduledstart" descending="true" />
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
            </link-entity>        
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

CITAS_POR_COMERCIAL_SEMANA_EN_CURSO = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />   
        <order attribute="scheduledstart" descending="true" />      
        <filter type="and">            
            <condition attribute="scheduledstart" operator="this-week" />        
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
            </link-entity>        
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

CITAS_POR_COMERCIAL_12VA_SEMANA_ATRAS = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />   
        <order attribute="scheduledstart" descending="true" />         
        <filter type="and">            
            <condition attribute="scheduledstart" operator="ge" value="{START_DATE}" />
            <condition attribute="scheduledstart" operator="le" value="{END_DATE}" />      
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
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">            
            <attribute name="domainname" />       
        </link-entity>    
    </entity>
</fetch>"""

CITAS_POR_GESTOR = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />
        <order attribute="scheduledstart" descending="true" /> 
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
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">            
            <attribute name="domainname" />       
        </link-entity>    
    </entity>
</fetch>"""

CITAS_POR_GESTOR_SEMANA_EN_CURSO = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />   
        <order attribute="scheduledstart" descending="true" />      
        <filter type="and">            
            <condition attribute="scheduledstart" operator="this-week" />        
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
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">            
            <attribute name="domainname" />       
        </link-entity>    
    </entity>
</fetch>"""

CITAS_POR_GESTOR_12VA_SEMANA_ATRAS = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />   
        <order attribute="scheduledstart" descending="true" />         
        <filter type="and">
            <condition attribute="scheduledstart" operator="ge" value="{START_DATE}" />
            <condition attribute="scheduledstart" operator="le" value="{END_DATE}" />
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
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">            
            <attribute name="domainname" />       
        </link-entity>    
    </entity>
</fetch>"""

CITAS_CON_INTERES_FUTURO_POR_COMERCIAL = """<fetch>
    <entity name="appointment">
        <attribute name="scheduledend" />
        <attribute name="iav_resultcomments" />
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user" link-type="inner">
                <attribute name="domainname" />
            </link-entity>
        </link-entity>
        <link-entity name="contact" from="contactid" to="fin_mainmeetingcontactid" alias="contact" link-type="outer">
            <attribute name="fullname" />
        </link-entity>
        <filter type="and">
            <condition attribute="scheduledstart" operator="last-x-months" value="3" />
            <condition attribute="iav_result" operator="eq" value="200000003" />
        </filter>
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
</fetch>    
    """

CITAS_CON_INTERES_FUTURO_POR_GESTOR = """<fetch>
    <entity name="appointment">
        <attribute name="scheduledend" />
        <attribute name="iav_resultcomments" />
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />
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
        <link-entity name="contact" from="contactid" to="fin_mainmeetingcontactid" alias="contact" link-type="outer">
            <attribute name="fullname" />
        </link-entity>
        <filter type="and">
            <condition attribute="scheduledstart" operator="last-x-months" value="3" />
            <condition attribute="iav_result" operator="eq" value="200000003" />
        </filter>
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="created_by" link-type="inner">            
            <attribute name="domainname" />
        </link-entity>
    </entity>
</fetch>    
    """

CITAS_CON_INTERES_FUTURO_POR_CUENTA = """<fetch>
    <entity name="appointment">
        <attribute name="scheduledend" />
        <attribute name="iav_resultcomments" />
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />                 
            <filter type="and">               
                <condition attribute="name" operator="eq" value="{NOMBRE_DE_CUENTA}" />          
            </filter>
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user" link-type="inner">
                <attribute name="domainname" />
            </link-entity>
        </link-entity>
        <link-entity name="contact" from="contactid" to="fin_mainmeetingcontactid" alias="contact" link-type="outer">
            <attribute name="fullname" />
        </link-entity>
        <filter type="and">
            <condition attribute="scheduledstart" operator="last-x-months" value="3" />
            <condition attribute="iav_result" operator="eq" value="200000003" />
        </filter>
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="created_by" link-type="inner">            
            <attribute name="domainname" />
        </link-entity>
    </entity>
</fetch>    
    """

CITAS_CON_INTERES_FUTURO_POR_NIF = """<fetch>
    <entity name="appointment">
        <attribute name="scheduledend" />
        <attribute name="iav_resultcomments" />
        <link-entity name="account" from="accountid" to="iav_accountid" alias="account" link-type="inner">
            <attribute name="name" />                 
            <filter type="and">               
                <condition attribute="iav_nif" operator="eq" value="{NIF}" />          
            </filter>
            <link-entity name="systemuser" from="systemuserid" to="iav_accountmanager" alias="user" link-type="inner">
                <attribute name="domainname" />
            </link-entity>
        </link-entity>
        <link-entity name="contact" from="contactid" to="fin_mainmeetingcontactid" alias="contact" link-type="outer">
            <attribute name="fullname" />
        </link-entity>
        <filter type="and">
            <condition attribute="scheduledstart" operator="last-x-months" value="3" />
            <condition attribute="iav_result" operator="eq" value="200000003" />
        </filter>
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="created_by" link-type="inner">            
            <attribute name="domainname" />
        </link-entity>
    </entity>
</fetch>    
    """

CITAS_ABIERTAS_POR_COMERCIAL_SEMANA_EN_CURSO = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />   
        <order attribute="scheduledstart" descending="false" />      
        <filter type="and">            
            <condition attribute="scheduledstart" operator="this-week" />        
            <condition attribute="actualend" operator="null" />        
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
            </link-entity>        
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

CITAS_ABIERTAS_POR_GESTOR_SEMANA_EN_CURSO = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />   
        <order attribute="scheduledstart" descending="true" />      
        <filter type="and">            
            <condition attribute="scheduledstart" operator="this-week" />        
            <condition attribute="actualend" operator="null" />        
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
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">            
            <attribute name="domainname" />       
        </link-entity>    
    </entity>
</fetch>"""

CITAS_CANCELADAS_POR_COMERCIAL_ANO_EN_CURSO = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />   
        <order attribute="scheduledstart" descending="false" />      
        <filter type="and">            
            <condition attribute="statecode" operator="eq" value="2" />     
            <condition attribute="createdon" operator="this-year" />     
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
            </link-entity>        
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

CITAS_CANCELADAS_POR_GESTOR_ANO_EN_CURSO = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />   
        <order attribute="scheduledstart" descending="false" />      
        <filter type="and">            
            <condition attribute="statecode" operator="eq" value="2" />     
            <condition attribute="createdon" operator="this-year" />     
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
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">            
            <attribute name="domainname" />
        </link-entity>    
    </entity>
</fetch>"""

CITAS_CANCELADAS_POR_CUENTA_ANO_EN_CURSO = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />   
        <order attribute="scheduledstart" descending="false" />      
        <filter type="and">            
            <condition attribute="statecode" operator="eq" value="2" />     
            <condition attribute="createdon" operator="this-year" />     
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
            <filter type="and">               
                <condition attribute="name" operator="eq" value="{NOMBRE_DE_CUENTA}" />          
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
            </link-entity>        
        </link-entity>        
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">            
            <attribute name="domainname" />
        </link-entity>    
    </entity>
</fetch>"""

CITAS_CANCELADAS_POR_NIF_ANO_EN_CURSO = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />   
        <order attribute="scheduledstart" descending="false" />      
        <filter type="and">            
            <condition attribute="statecode" operator="eq" value="2" />     
            <condition attribute="createdon" operator="this-year" />     
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
            <filter type="and">               
                <condition attribute="iav_nif" operator="eq" value="{NIF}" />          
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
            </link-entity>        
        </link-entity>        
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">            
            <attribute name="domainname" />
        </link-entity>    
    </entity>
</fetch>"""

CITAS_POR_COMERCIAL_SIN_LLAMADA_POSTERIOR_6_MESES = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />
        <order attribute="scheduledstart" descending="true" />
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
            </link-entity>
            <filter type="and">
                <condition attribute="axz_lastcontactdate" operator="olderthan-x-months" value="6" />                
            </filter>
            <order attribute="axz_lastcontactdate" descending="true" />
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

CITAS_POR_GESTOR_SIN_LLAMADA_POSTERIOR_6_MESES = """<fetch>    
    <entity name="appointment">        
        <attribute name="scheduledstart" />        
        <attribute name="iav_resultcomments" />
        <order attribute="scheduledstart" descending="true" />
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
            <order attribute="axz_lastcontactdate" descending="true" />
            <filter type="and">
                <condition attribute="axz_lastcontactdate" operator="olderthan-x-months" value="6" />                
            </filter>
        </link-entity>        
        <link-entity name="systemuser" from="systemuserid" to="ownerid" alias="owner" link-type="inner">            
            <attribute name="domainname" />      
        </link-entity>    
    </entity>
</fetch>"""