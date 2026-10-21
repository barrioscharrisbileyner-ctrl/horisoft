/**
 * Modelo: Usuario
 * Basado en la entidad "PerfilUsuario" del MER de Horisoft.
 * Roles válidos alineados al mapa de navegación: Administrador, Residente,
 * Vigilante, Administrativo, Proveedor.
 */
class Usuario {
    constructor(id_usuario, nombre, correo, password, rol, estado = "Activo", id_residencia = null) {
        this.id_usuario = id_usuario;
        this.nombre = nombre;
        this.correo = correo;
        this.password = password; // En un entorno real: almacenar con hash (bcrypt)
        this.rol = rol;
        // Estados posibles: Activo | Inactivo
        this.estado = estado;
        // Residencia a la que pertenece el usuario (solo aplica a Residentes).
        // null = el usuario no está asociado a una residencia (ej. Administrador).
        this.id_residencia = id_residencia;
    }
}

module.exports = Usuario;
