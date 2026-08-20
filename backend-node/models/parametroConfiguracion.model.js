/**
 * Modelo: ParametroConfiguracion
 * Basado en el módulo Administrativo/Configuración de Horisoft.
 * Almacena parámetros globales del conjunto residencial (clave-valor).
 */
class ParametroConfiguracion {
    constructor(clave, valor, descripcion) {
        this.clave = clave;
        this.valor = valor;
        this.descripcion = descripcion;
    }
}

module.exports = ParametroConfiguracion;
