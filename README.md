# KRB5MAKER
Script en Python diseñado para generar automáticamente un archivo de configuración válido para Kerberos
krb5.conf Generator 

Este es un script en Python diseñado para generar automáticamente un archivo de configuración válido para Kerberos (krb5.conf) en sistemas Linux que necesitan conectarse a un entorno Active Directory (AD). 

El script permite tanto la detección automática del REALM Kerberos como la configuración manual, lo que lo hace útil en una variedad de escenarios, ya sea en entornos automatizados o en redes con configuraciones limitadas. 
Características Principales 

    Detección automática del REALM mediante:
        Conexión LDAP al Controlador de Dominio.
        Consulta DNS inverso sobre la IP del DC.
         
    Configuración manual del REALM si no se dispone de métodos automáticos.
    Generación directa del archivo krb5.conf con parámetros básicos pero funcionales.
    Menú interactivo intuitivo para facilitar su uso.
    No requiere privilegios elevados salvo que se desee escribir en /etc/krb5.conf.
     

Requisitos 

Para ejecutar el script, asegúrate de tener instaladas las siguientes dependencias: `ldap3` `dnspython`

```
pip install -r requirements.txt
```

Uso del Script 
Sintaxis 

```
python3 KRB5MAKER.py <DC_IP>
```

Esto iniciará el menú interactivo donde podrás elegir entre: 

    Detección automática  usando LDAP o DNS inverso.
    Introducir manualmente  el REALM Kerberos.
    Usar solo la IP del DC.
Por defecto, el archivo generado se guardará como ./krb5.conf. Se debe mover a /etc/krb5.conf

Notas de Seguridad 

    Asegúrate de que la máquina tenga conectividad de red con el Controlador de Dominio en los puertos relevantes (LDAP: 389, DNS: 53).
    El archivo generado es básico y puede requerir ajustes adicionales en entornos productivos o complejos.

Licencia 

Este proyecto está bajo la licencia MIT. Puedes usarlo, modificarlo y distribuirlo libremente siempre que se mantenga el reconocimiento correspondiente. 
Contribuciones 

Las contribuciones son bienvenidas. Si deseas mejorar este script o añadir nuevas funcionalidades (como soporte para múltiples KDCs, integración con Samba o pruebas de conexión), no dudes en abrir un PR o informar un issue. 
