/**
 * Modelo: Pago
 * Registra los abonos/pagos realizados sobre una CuentaCobro.
 */
class Pago {
    constructor(id_pago, id_cuenta, valor_pagado, metodo_pago) {
        this.id_pago = id_pago;
        this.id_cuenta = id_cuenta;
        this.valor_pagado = valor_pagado;
        // Métodos posibles: Efectivo | Transferencia | Tarjeta | PSE
        this.metodo_pago = metodo_pago;
        this.fecha_pago = new Date().toISOString();
    }
}

module.exports = Pago;
