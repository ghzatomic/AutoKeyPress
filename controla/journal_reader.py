import os
import glob
import ctypes
from ctypes import wintypes
import win32file
import win32con
import win32security
import win32api
import ntsecuritycon

def enable_privilege(privilege_name):
    """
    Habilita o privilégio especificado (ex.: 'SeBackupPrivilege' ou 'SeRestorePrivilege')
    para o processo atual. Necessário executar como Administrador.
    """
    flags = ntsecuritycon.TOKEN_ADJUST_PRIVILEGES | ntsecuritycon.TOKEN_QUERY
    token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)
    privilege_id = win32security.LookupPrivilegeValue(None, privilege_name)
    new_privileges = [(privilege_id, win32security.SE_PRIVILEGE_ENABLED)]
    win32security.AdjustTokenPrivileges(token, False, new_privileges)

# Definição do UNICODE_STRING conforme a NT API
class UNICODE_STRING(ctypes.Structure):
    _fields_ = [
        ("Length", wintypes.USHORT),
        ("MaximumLength", wintypes.USHORT),
        ("Buffer", ctypes.c_wchar_p)  # Especificamos c_wchar_p para evitar incompatibilidades
    ]

def init_unicode_string(string):
    """
    Converte uma string Python para um UNICODE_STRING.
    """
    u_str = UNICODE_STRING()
    # Cria um buffer de caracteres Unicode para o caminho
    buffer = ctypes.create_unicode_buffer(string)
    # Converte o buffer para c_wchar_p explicitamente
    u_str.Buffer = ctypes.cast(buffer, ctypes.c_wchar_p)
    u_str.Length = len(string) * 2
    u_str.MaximumLength = (len(string) + 1) * 2
    return u_str

# Definição da estrutura OBJECT_ATTRIBUTES
class OBJECT_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("Length", wintypes.ULONG),
        ("RootDirectory", wintypes.HANDLE),
        ("ObjectName", ctypes.POINTER(UNICODE_STRING)),
        ("Attributes", wintypes.ULONG),
        ("SecurityDescriptor", wintypes.LPVOID),
        ("SecurityQualityOfService", wintypes.LPVOID)
    ]

# Estrutura IO_STATUS_BLOCK
class IO_STATUS_BLOCK(ctypes.Structure):
    _fields_ = [
        ("Status", wintypes.ULONG),
        ("Information", ctypes.c_void_p)
    ]

# Carrega a ntdll e define o protótipo de NtOpenFile
ntdll = ctypes.WinDLL("ntdll")
NtOpenFile = ntdll.NtOpenFile
NtOpenFile.argtypes = [
    ctypes.POINTER(wintypes.HANDLE),      # FileHandle
    wintypes.ULONG,                       # DesiredAccess
    ctypes.POINTER(OBJECT_ATTRIBUTES),    # ObjectAttributes
    ctypes.POINTER(IO_STATUS_BLOCK),      # IoStatusBlock
    wintypes.ULONG,                       # ShareAccess
    wintypes.ULONG                        # OpenOptions
]
NtOpenFile.restype = wintypes.ULONG

class JournalReader:
    def __init__(self, directory):
        self.directory = directory

    def get_latest_text_file(self):
        """Retorna o caminho do arquivo de texto mais recente na pasta."""
        files = glob.glob(os.path.join(self.directory, "*.txt"))
        if not files:
            return None  # Nenhum arquivo encontrado
        latest_file = max(files, key=os.path.getctime)
        return latest_file

    def read_latest_file(self):
        """Tenta ler o arquivo usando NtOpenFile com FILE_OPEN_FOR_BACKUP_INTENT."""
        latest_file = self.get_latest_text_file()
        if not latest_file:
            return None
        return self.read_file_with_nt_open(latest_file)

    def read_file_with_nt_open(self, filepath):
        """
        Tenta abrir o arquivo utilizando NtOpenFile com FILE_OPEN_FOR_BACKUP_INTENT,
        habilitando os privilégios de backup. Essa abordagem tenta contornar bloqueios
        exclusivos aplicados pelo processo ClassicUO.
        """
        try:
            # Habilita privilégios de backup e restore
            enable_privilege(win32security.SE_BACKUP_NAME)
            enable_privilege(win32security.SE_RESTORE_NAME)
            
            # Inicializa o UNICODE_STRING com o caminho do arquivo
            u_path = init_unicode_string(filepath)
            obj_attr = OBJECT_ATTRIBUTES()
            obj_attr.Length = ctypes.sizeof(OBJECT_ATTRIBUTES)
            obj_attr.RootDirectory = None
            obj_attr.ObjectName = ctypes.pointer(u_path)
            obj_attr.Attributes = 0x00000040  # OBJ_CASE_INSENSITIVE
            obj_attr.SecurityDescriptor = None
            obj_attr.SecurityQualityOfService = None

            io_status = IO_STATUS_BLOCK()
            file_handle = wintypes.HANDLE()

            desired_access = win32con.GENERIC_READ
            # Permite compartilhamento total
            share_access = win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE
            FILE_OPEN_FOR_BACKUP_INTENT = 0x00004000  # Flag para backup

            status = NtOpenFile(
                ctypes.byref(file_handle),
                desired_access,
                ctypes.byref(obj_attr),
                ctypes.byref(io_status),
                share_access,
                FILE_OPEN_FOR_BACKUP_INTENT
            )
            if status != 0:
                print(f"Falha ao abrir o arquivo. Status: {status}")
                return None

            # Lê o conteúdo do arquivo em chunks
            content_bytes = b""
            while True:
                chunk, _ = win32file.ReadFile(file_handle, 4096)
                if not chunk:
                    break
                content_bytes += chunk

            win32file.CloseHandle(file_handle)
            return content_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"Erro ao tentar ler com NtOpenFile: {e}")
            return None

# Exemplo de uso
if __name__ == "__main__":
    pasta = r"C:\Program Files (x86)\Ultima Online Outlands\ClassicUO\Data\Client\JournalLogs"
    reader = JournalReader(pasta)
    
    latest = reader.get_latest_text_file()
    if latest:
        print(f"Último arquivo encontrado: {latest}")
        content = reader.read_latest_file()
        if content:
            print("Conteúdo do arquivo:\n", content)
        else:
            print("Falhou ao ler o arquivo usando NtOpenFile.")
    else:
        print("Nenhum arquivo de texto encontrado.")
