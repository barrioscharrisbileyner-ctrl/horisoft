/**
 * Modelo: Vehiculo
 * Complementa el módulo de Seguridad (Vigilantes/Visitantes) de Horisoft,
 * registrando los vehículos autorizados de cada residencia.
 */
class Vehiculo {
    constructor(id_vehiculo, placa, id_residencia, tipo, color, estado = "Activo") {
        this.id_vehiculo = id_vehiculo;
        this.placa = placa.toUpperCase();
        this.id_residencia = id_residencia;
        // Tipos posibles: Carro | Moto | Bicicleta
        this.tipo = tipo;
        this.color = color;
        // Estados posibles: Activo | Inactivo
        this.estado = estado;
    }
}

module.exports = Vehiculo;
