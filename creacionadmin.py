from getpass import getpass
from app.database import SessionLocal
from app.models.usuario import Usuario
from app.security import hash_password


sesion = SessionLocal()

try:
    correo = input("Correo del administrador: ").strip()
    nombre = input("Nombre del administrador: ").strip()
    contrasena = getpass("Contraseña: ")

    longitud = len(contrasena.encode("utf-8"))
    if longitud < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if longitud > 72:
        raise ValueError("La contraseña no puede superar los 72 bytes")

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