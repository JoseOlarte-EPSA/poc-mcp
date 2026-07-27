# Diccionario con el mapeo de columnas para el procesamiento de DataFrames
COLUMNS = {
    "NÚMERO_DE_CUENTA": "account.accountnumber",
    "NIF": "account.iav_nif",
    "NOMBRE_DE_LA_CUENTA": "account.name",
    "SCORE_INICIAL": "account.iav_initialscore@OData.Community.Display.V1.FormattedValue",
    "GROUP_ALIAS": "group.fin_name",
    "FECHA_DE_LA_CITA": "scheduledstart",
    "CONTACTO_PRINCIPAL": "contact.fullname",
    "CARGO_CONTACTO": "contact.jobtitle",
    "TELEFONO_CONTACTO": "contact.telephone1",
    "INDUSTRIA_FI": "industria_fi.fig_name",
    "SECTOR_FI": "sector.fin_name",
    "COMENTARIOS": "iav_resultcomments",
    "CUENTA_ID": "account.accountid",
    "COMERCIAL": "created_by.domainname",
    "GESTOR": "user.domainname"
}

# Diccionario con el mapeo de columnas para el histórico de citas
COLUMNS_HISTORICO = {
    "NOMBRE_DE_LA_CUENTA": "account.name",
    "ASUNTO": "subject",
    "FECHA_DE_LA_CITA": "scheduledstart",
    "CONTACTO_PRINCIPAL": "main_contact.fullname",
    "ASISTENTES": "attendees.fullname",
    "COMENTARIOS": "iav_resultcomments",
    "COMERCIAL": "created_by.domainname",
    "GESTOR": "user.domainname"
}

# Diccionario con el mapeo de columnas para el histórico de llamadas
COLUMNS_HISTORICO_LLAMADAS = {
    "NOMBRE_DE_LA_CUENTA": "account.name",
    "REFERENTE_A": "_regardingobjectid_value@OData.Community.Display.V1.FormattedValue",
    "NÚMERO_TELÉFONO": "phonenumber",
    "ASUNTO": "subject",
    "FECHA_FIN_REAL": "actualend",
    "TIPO": "iav_type@OData.Community.Display.V1.FormattedValue",
    "RESULTADO": "iav_result@OData.Community.Display.V1.FormattedValue",
    "DESCRIPCION": "description",
    "COMERCIAL": "created_by.domainname",
    "GESTOR": "user.domainname"
}

# Diccionario con el mapeo de columnas para el histórico de servicios/oportunidades
COLUMNS_HISTORICO_SERVICIOS = {
    "NOMBRE_DE_LA_CUENTA": "account.name",
    "SERVICIO": "typeofservice.iav_name",
    "FECHA": "createdon",
    "RAZÓN_DEL_ESTADO": "statuscode@OData.Community.Display.V1.FormattedValue",
    "ESTADO": "statecode@OData.Community.Display.V1.FormattedValue",
    "OPORTUNIDAD": "opportunity.name",
    "PROBABILIDAD": "iav_successprobability@OData.Community.Display.V1.FormattedValue",
    "COMPETIDOR": "competitor.name",
    "FECHA_DE_CREACIÓN_COMPETENCIA": "competitor.createdon",
    "ÁREA": "area.fin_name",
    "COMERCIAL": "created_by.domainname",
    "GESTOR": "user.domainname"
}

# Diccionario con el mapeo de columnas para oportunidades en proceso de venta
COLUMNS_LLAMADAS_ESTADO_CALIENTE = {
    "NOMBRE_DE_LA_CUENTA": "account.name",
    "SCORE_INICIAL": "account.iav_initialscore@OData.Community.Display.V1.FormattedValue",
    "GROUP_ALIAS": "group_alias.fin_name",
    "ÚLTIMO_CONTACTO": "account.axz_lastcontactdate",
    "INDUSTRIA_FI": "industria_fi.fig_name",
    "DESCRIPCIÓN": "description",
    "COMERCIAL": "created_by.domainname",
    "GESTOR": "user.domainname"
}

# Diccionario con el mapeo de columnas para leads abiertos
COLUMNS_LEADS = {
    "NOMBRE_DE_LA_CUENTA": "account.name",
    "NIF": "account.iav_nif",
    "SCORE_INICIAL": "account.iav_initialscore@OData.Community.Display.V1.FormattedValue",
    "GROUP_ALIAS": "group_alias.fin_name",
    "ÚLTIMO_CONTACTO": "account.axz_lastcontactdate",
    "INDUSTRIA_FI": "industria_fi.fig_name",
    "SOURCE_CHANNEL": "source_channel.fin_name",
    "CAMPAÑA_DE_ORIGEN": "campaign.name",
    "COMENTARIOS_DE_LEAD": "fin_leadcomments",    
    "CREADO": "createdon",
    "COMERCIAL": "created_by.domainname",
    "GESTOR": "user.domainname"
}

# Diccionario con el mapeo de columnas para oportunidades abiertas (servicios)
COLUMNS_OPORTUNIDADES_ABIERTAS = {
    "NOMBRE_DE_LA_CUENTA": "account.name",
    "TIPO_DE_SERVICIO": "typeofservice.iav_name",
    "ÁREA_DE_SERVICIO": "area.fin_name",
    "TIPO_DE_CONTRATO": "iav_typecontract@OData.Community.Display.V1.FormattedValue",
    "PREVISIÓN_DE_HONORARIOS": "iav_totalfeesfiforecast@OData.Community.Display.V1.FormattedValue",
    "FECHA_DE_CREACIÓN": "createdon",
    "PROBABILIDAD": "iav_successprobability@OData.Community.Display.V1.FormattedValue",
    "SECTOR_FI": "sector.fin_name",
    "COMERCIAL": "created_by.domainname",
    "GESTOR": "user.domainname"
}

# Diccionario con el mapeo de columnas para ofertas pendientes
COLUMNS_OFERTAS_PENDIENTES = {
    "NOMBRE_DE_LA_CUENTA": "account.name",
    "FECHA_DE_ÚLTIMA_REUNIÓN": "scheduledend",
    "COMENTARIOS": "iav_resultcomments",
    "CONTACTO_PRINCIPAL": "contact.fullname",
    "COMERCIAL": "created_by.domainname",
    "GESTOR": "user.domainname"
}

# Diccionario con el mapeo de columnas para llamadas en entre fechas
COLUMNS_LLAMADAS_ENTRE_FECHAS = {
    "NÚMERO_DE_CUENTA": "account.accountnumber",
    "CUENTA_ID": "account.accountid",
}

COLUMNS_CUENTAS_LLAMADAS_ANO_EN_CURSO = {
    "NÚMERO_DE_CUENTA": "accountnumber",
    "NIF_DE_CUENTA": "iav_nif",
    "NOMBRE_DE_CUENTA": "name",
}

# Diccionario con el mapeo de columnas para las cuentas en BDNS
COLUMNS_HISTORICO_BDNS = {
  "NIF": "Beneficiary_NIF",
  "BENEFICIARIO": "Beneficiary_Name",
  "ORGANISMO": "Organism",
  "FONDOS_A_PRESTAMO": "Total_Prestamo",
  "FONDOS_A_SUBVENCIÓN": "Total_Subvencion"
}

# Diccionario con el mapeo de columnas para GRANTS
COLUMNS_GRANTS = {
    "SECTOR": "Name",
    "TÍTULO": "Title"
}

# Diccionario con el mapeo de columnas Citas Canceladas Año Actual
COLUMNS_CITAS_CANCELADAS_CURRENT_YEAR = {
    "NÚMERO_DE_CUENTA": "account.accountnumber",
    "NIF": "account.iav_nif",
    "NOMBRE_DE_LA_CUENTA": "account.name",
    "SCORE_INICIAL": "account.iav_initialscore@OData.Community.Display.V1.FormattedValue",
    "GROUP_ALIAS": "group.fin_name",
    "FECHA_DE_LA_CITA": "scheduledstart",
    "CONTACTO_PRINCIPAL": "contact.fullname",
    "CARGO_CONTACTO": "contact.jobtitle",
    "TELEFONO_CONTACTO": "contact.telephone1",
    "INDUSTRIA_FI": "industria_fi.fig_name",
    "SECTOR_FI": "sector.fin_name",
    "COMENTARIOS": "iav_resultcomments",
    "CUENTA_ID": "account.accountid",
    "COMERCIAL": "created_by.domainname",
    "GESTOR": "user.domainname"
}