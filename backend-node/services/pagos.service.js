const pagos = require("../data/pagos");
const Pago = require("../models/pago.model");
const cuentasCobroService = require("./cuentasCobro.service");

const METODOS_VALIDOS = ["Efectivo", "Transferencia", "Tarjeta", "PSE"];

class PagosService {

    obtenerTodos() {
        return pagos;
    }

    obtenerPorCuenta(id_cuenta) {
        return pagos.filter(p => p.id_cuenta === Number(id_cuenta));
    }

    /**
     * Reglas de negocio (equivalentes al clean() de Django):
     *  1. id_cuenta, valor_pagado y metodo_pago son obligatorios.
     *  2. La cuenta de cobro debe existir.
     *  3. La cuenta no puede estar ya "Pagada".
     *  4. valor_pagado debe ser mayor que cero.
     *  5. valor_pagado no puede exceder el saldo pendiente de la cuenta.
     *  6. Si el pago cubre el saldo total, la cuenta pasa a estado "Pagada".
     */
    registrarPago(datos) {

        const { id_cuenta, valor_pagado, metodo_pago } = datos;

        if (!id_cuenta || !valor_pagado || !metodo_pago) {
            throw new Error("id_cuenta, valor_pagado y metodo_pago son obligatorios");
        }

        if (!METODOS_VALIDOS.includes(metodo_pago)) {
            throw new Error(`metodo_pago inválido. Use uno de: ${METODOS_VALIDOS.join(", ")}`);
        }

        const cuenta = cuentasCobroService.obtenerPorId(id_cuenta);

        if (cuenta.estado === "Pagada") {
            throw new Error("Esta cuenta ya se encuentra completamente pagada");
        }

        if (valor_pagado <= 0) {
            throw new Error("valor_pagado debe ser mayor que cero");
        }

        const saldoPendiente = cuenta.valor - cuenta.valor_pagado;

        if (valor_pagado > saldoPendiente) {
            throw new Error(
                `El valor pagado ($${valor_pagado}) excede el saldo pendiente ($${saldoPendiente})`
            );
        }

        const nuevoPago = new Pago(
            pagos.length > 0 ? Math.max(...pagos.map(p => p.id_pago)) + 1 : 1,
            Number(id_cuenta),
            valor_pagado,
            metodo_pago
        );

        pagos.push(nuevoPago);

        // Actualiza el saldo de la cuenta y su estado
        cuenta.valor_pagado += valor_pagado;

        if (cuenta.valor_pagado >= cuenta.valor) {
            cuenta.estado = "Pagada";
        }

        return { pago: nuevoPago, cuenta };
    }
}

module.exports = new PagosService();
