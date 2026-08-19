/**
 * Modelo: CuentaCobro
 * Basado en el requerimiento RQ01 (Gestión Financiera) de Horisoft.
 */
class CuentaCobro {
    constructor(id_cuenta, id_residencia, concepto, valor, fecha_vencimiento) {
        this.id_cuenta = id_cuenta;
        this.id_residencia = id_residencia;
        this.concepto = concepto;
        this.valor = valor;
        this.valor_pagado = 0;
        this.fecha_vencimiento = fecha_vencimiento; // "YYYY-MM-DD"
        // Estados posibles: Pendiente | Pagada | Vencida
        this.estado = "Pendiente";
    }
}

module.exports = CuentaCobro;
