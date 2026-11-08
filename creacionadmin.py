from getpass import getpass
from app.database import SessionLocal
from app.models.usuario import Usuario
from app.security import hash_password


sesion = SessionLocal()

try:
    correo = input("Correo del administrador: ").strip()
    nombre = input("Nombre del administrador: ").strip()
    contrasena = getpass("Contraseña: ")

    if len(contrasena) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")

    if not nombre or not correo:
        raise ValueError("El nombre y correo son obligatorios")

    existente = sesion.query(Usuario).filter(
        Usuario.correo == correo
    ).first()

    if existente:
        raise ValueError("Este correo ya está registrado")

    administrador = Usuario(
        nombre=nombre,
        correo=correo,
        contrasena_encriptada=hash_password(contrasena),
        rol="admin"
    )

    sesion.add(administrador)
    sesion.commit()

    print("Administrador creado correctamente")

except Exception as error:
    sesion.rollback()
    print("Error:", error)

finally:
    sesion.close()