/**
 * Modelo: Proveedor
 * Basado en el rol "Proveedor" del mapa de navegación de Horisoft.
 */
class Proveedor {
    constructor(id_proveedor, nombre, nit, servicio, telefono, estado = "Activo") {
        this.id_proveedor = id_proveedor;
        this.nombre = nombre;
        this.nit = nit;
        this.servicio = servicio; // Ej: Jardinería, Aseo, Mantenimiento eléctrico
        this.telefono = telefono;
        // Estados posibles: Activo | Inactivo
        this.estado = estado;
    }
}

module.exports = Proveedor;
