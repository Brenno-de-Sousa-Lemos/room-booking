import getpass
import config
from werkzeug.security import generate_password_hash
from models.usuario_model import UsuarioModel

nome = input("Nome: ")
email = input("E-mail: ").strip().lower()
senha = getpass.getpass("Senha (mín. 8 caracteres): ")
assert len(senha) >= 8, "Senha muito curta"

uid = UsuarioModel.criar(nome, email, generate_password_hash(senha), "ADMIN", None)
print(f"Administrador criado! id={uid}")