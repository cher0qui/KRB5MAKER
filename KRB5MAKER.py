#!/usr/bin/env python3

import sys
import socket
import dns.resolver
from ldap3 import Server, Connection, ALL


def print_banner():
    banner = r"""
██╗  ██╗██████╗ ██████╗ ███████╗███╗   ███╗ █████╗ ██╗  ██╗███████╗██████╗ 
██║ ██╔╝██╔══██╗██╔══██╗██╔════╝████╗ ████║██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
█████╔╝ ██████╔╝██████╔╝███████╗██╔████╔██║███████║█████╔╝ █████╗  ██████╔╝
██╔═██╗ ██╔══██╗██╔══██╗╚════██║██║╚██╔╝██║██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗
██║  ██╗██║  ██║██████╔╝███████║██║ ╚═╝ ██║██║  ██║██║  ██╗███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                                                                           
"""
    print(banner)

def get_realm_from_ldap(dc_ip):
    try:
        server = Server(dc_ip, get_info=ALL)
        with Connection(server) as conn:
            if not server.info:
                return None
            default_naming_context = server.info.other.get('defaultNamingContext', [])
            if not default_naming_context:
                return None
            realm = '.'.join(
                part.split('=')[1].upper()
                for part in default_naming_context[0].split(',')
                if part.startswith('DC')
            )
            return realm
    except Exception as e:
        print(f"[-] LDAP: {e}")
        return None

def get_realm_from_dns_srv(domain):
    try:
        answers = dns.resolver.resolve(f'_kerberos._tcp.{domain}', 'SRV')
        for rdata in answers:
            target = str(rdata.target).rstrip('.')
            if domain.lower() in target.lower():
                return domain.upper()
        return domain.upper()
    except Exception as e:
        print(f"[-] DNS SRV: {e}")
        return None

def get_realm_from_reverse_dns(dc_ip):
    try:
        hostname = socket.gethostbyaddr(dc_ip)[0]
        parts = hostname.split('.')
        if len(parts) > 1:
            return '.'.join(p.upper() for p in parts)
        else:
            return None
    except socket.herror:
        return None

def choose_method(dc_ip):
    print("[!] Menu interactivo \n")
    print("Selecciona una opción:\n")
    print("1. Deteccion automatica (LDAP)")
    print("2. Introducir REALM manualmente")
    print("3. Solo usar IP como KDC (modo básico)")

    choice = input("Opción: ").strip()
    while choice not in ['1', '2', '3']:
        choice = input("Opción inválida. Elige 1, 2 o 3: ").strip()

    if choice == "1":
        #  LDAP
        realm = get_realm_from_ldap(dc_ip)
        if realm:
            print(f"[+] Realm encontrado por LDAP: {realm}")
            generate_krb5_conf(realm, dc_ip)
            return
        
        # DNS INVERSO
        realm = get_realm_from_reverse_dns(dc_ip)
        if realm:
            print(f"[+] Realm encontrado por DNS inverso: {realm}")
            generate_krb5_conf(realm, dc_ip)
            return
        
        print("[-] No se pudo detectar automáticamente. Volviendo al menú...")
        return choose_method(dc_ip)
        
    elif choice == "2":
        realm = input("Introduce el REALM (ej: comtoso.com): ").strip().upper()
        while not realm:
            realm = input("[-] REALM no puede estar vacio; Introduce el REALM: ").strip().upper()
        kdc = dc_ip
        generate_krb5_conf(realm, dc_ip)
    elif choice == "3":
        realm = f"REALM.{dc_ip.replace('.', '_')}"
        kdc = dc_ip
        generate_krb5_conf(realm, dc_ip)

    return realm, kdc

def generate_krb5_conf(realm, kdc, output="./krb5.conf"):
    krb5_config = f"""[libdefaults]
    default_realm = {realm}
    dns_lookup_realm = false
    dns_lookup_kdc = false
    ticket_lifetime = 24h
    renew_lifetime = 7d
    forwardable = true

[realms]
    {realm} = {{
        kdc = {kdc}
        admin_server = {kdc}
    }}

[domain_realm]
    .{realm} = {realm}
    {realm} = {realm}

[logging]
    default = FILE:/var/log/krb5libs.log
    kdc = FILE:/var/log/krb5kdc.log
    admin_server = FILE:/var/log/kadmind.log
"""
    try:
        with open(output, "w") as f:
            f.write(krb5_config)
        print(f"\n[+] Archivo generado correctamente en: {output}")
    except PermissionError:
        print(f"[-] No tienes permisos para escribir en {output}. Ejecuta con sudo.")
        sys.exit(1)



## Main 
def main():
    print_banner()

    if len(sys.argv) != 2:
        print(f"Uso:{sys.argv[0]} <IP_DEL_DC>")
        sys.exit(1)
    
    

    dc_ip = sys.argv[1]

    print(f"\n[!] IP del Controlador de Dominio : [{dc_ip}]\n")

    choose_method(dc_ip)

if __name__ == "__main__":
    main()
