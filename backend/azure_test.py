"""
Script para probar la conexión a Azure y listar recursos del grupo RSGYAPE001.
Este script se puede usar para verificar que las credenciales son correctas.
"""

import os
import sys
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import ClientAuthenticationError

# Cargar variables de entorno desde archivo .env
load_dotenv()

def test_with_default_credential():
    """Probar conexión usando DefaultAzureCredential"""
    print("\n--- Probando con DefaultAzureCredential ---")
    try:
        # DefaultAzureCredential intenta varios métodos de autenticación
        credential = DefaultAzureCredential()
        subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
        
        resource_client = ResourceManagementClient(credential, subscription_id)
        for group in resource_client.resource_groups.list():
            print(f"Grupo encontrado: {group.name}")
        print("✅ Conexión exitosa con DefaultAzureCredential")
        return True
    except Exception as e:
        print(f"❌ Error con DefaultAzureCredential: {str(e)}")
        return False

def test_azure_connection():
    """Probar la conexión a Azure usando variables de entorno"""
    print("--- Probando conexión a Azure con ClientSecretCredential ---")
    
    # Obtener variables de entorno
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    client_id = os.environ.get("AZURE_CLIENT_ID")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET")
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    
    # Verificar que tenemos todas las variables necesarias
    if not all([tenant_id, client_id, client_secret, subscription_id]):
        print("ERROR: Faltan variables de entorno. Verifique que ha configurado:")
        print("- AZURE_TENANT_ID")
        print("- AZURE_CLIENT_ID")
        print("- AZURE_CLIENT_SECRET")
        print("- AZURE_SUBSCRIPTION_ID")
        return False
    
    print(f"Valores de conexión:")
    print(f"Tenant ID: {tenant_id}")
    print(f"Client ID: {client_id}")
    print(f"Subscription ID: {subscription_id}")
    print(f"Secret: {'*' * 10}")
    
    try:
        # Crear credencial
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Intentar obtener un token para verificar credenciales
        print("Intentando obtener token...")
        token = credential.get_token("https://management.azure.com/.default")
        print(f"✅ Token obtenido correctamente: {token.token[:10]}...")
        
        # Cliente para recursos de Azure
        print("Creando cliente ResourceManagementClient...")
        resource_client = ResourceManagementClient(credential, subscription_id)
        
        # Listar grupos de recursos para verificar acceso
        print("\nListando grupos de recursos disponibles:")
        for group in resource_client.resource_groups.list():
            print(f"- {group.name} (ubicación: {group.location})")
        
        # Intentar listar recursos del grupo específico
        print(f"\nListando recursos en el grupo RSGYAPE001:")
        resources = list(resource_client.resources.list_by_resource_group("RSGYAPE001"))
        
        if not resources:
            print("⚠️ No se encontraron recursos en este grupo o no tiene acceso.")
        else:
            for resource in resources:
                print(f"- {resource.name} (tipo: {resource.type})")
        
        print("\n✅ Conexión exitosa a Azure!")
        return True
        
    except ClientAuthenticationError as auth_error:
        print(f"❌ ERROR de autenticación: {str(auth_error)}")
        print("\nPosibles soluciones:")
        print("1. Verificar que los IDs del tenant, cliente y secreto sean correctos")
        print("2. Asegurarse de que la aplicación tenga los permisos necesarios")
        print("3. Esperar algunos minutos para que se propaguen los permisos")
        return False
    except Exception as e:
        print(f"❌ ERROR general al conectar con Azure: {str(e)}")
        return False

def check_environment():
    """Verificar la configuración del entorno"""
    print("\n--- Verificando variables de entorno ---")
    variables = {
        "AZURE_TENANT_ID": os.environ.get("AZURE_TENANT_ID"),
        "AZURE_CLIENT_ID": os.environ.get("AZURE_CLIENT_ID"),
        "AZURE_CLIENT_SECRET": os.environ.get("AZURE_CLIENT_SECRET", "***CONFIGURADO***"),
        "AZURE_SUBSCRIPTION_ID": os.environ.get("AZURE_SUBSCRIPTION_ID")
    }
    
    for var, value in variables.items():
        status = "✅ CONFIGURADO" if value else "❌ NO CONFIGURADO"
        if var == "AZURE_CLIENT_SECRET" and value:
            print(f"{var}: {status}")
        else:
            print(f"{var}: {status} - Valor: {value}")
    
    return all([v for k, v in variables.items() if k != "AZURE_CLIENT_SECRET"]) and variables["AZURE_CLIENT_SECRET"]

if __name__ == "__main__":
    print("="*60)
    print("PRUEBA DE CONEXIÓN A AZURE")
    print("="*60)
    
    if not check_environment():
        print("\n❌ Falta configurar variables de entorno. No se puede continuar.")
        sys.exit(1)
    
    # Probar ambos métodos de autenticación
    client_secret_result = test_azure_connection()
    default_credential_result = test_with_default_credential()
    
    if client_secret_result or default_credential_result:
        print("\n✅ Al menos un método de autenticación funcionó correctamente")
    else:
        print("\n❌ Ningún método de autenticación funcionó")
        print("Consulte la documentación para más información sobre solución de problemas:") 