/**
 * Modelo: Usuario
 * Basado en la entidad "PerfilUsuario" del MER de Horisoft.
 * Roles válidos alineados al mapa de navegación: Administrador, Residente,
 * Vigilante, Administrativo, Proveedor.
 */
class Usuario {
    constructor(id_usuario, nombre, correo, password, rol, estado = "Activo") {
        this.id_usuario = id_usuario;
        this.nombre = nombre;
        this.correo = correo;
        this.password = password; // En un entorno real: almacenar con hash (bcrypt)
        this.rol = rol;
        // Estados posibles: Activo | Inactivo
        this.estado = estado;
    }
}

module.exports = Usuario;
