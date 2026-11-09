from sqlalchemy.orm import Session


def guardar(db: Session, entidad):
    db.add(entidad)
    db.commit()
    db.refresh(entidad)
    return entidad

