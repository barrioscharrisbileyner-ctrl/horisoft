const cuentasCobro = require("../data/cuentasCobro");
const CuentaCobro = require("../models/cuentaCobro.model");

class CuentasCobroService {

    obtenerTodas() {
        return cuentasCobro;
    }

    obtenerPorId(id_cuenta) {
        const cuenta = cuentasCobro.find(c => c.id_cuenta === Number(id_cuenta));

        if (!cuenta) {
            throw new Error("Cuenta de cobro no encontrada");
        }

        return cuenta;
    }

    obtenerPorResidencia(id_residencia) {
        return cuentasCobro.filter(c => c.id_residencia === Number(id_residencia));
    }

    crear(datos) {

        const { id_residencia, concepto, valor, fecha_vencimiento } = datos;

        if (!id_residencia || !concepto || !valor || !fecha_vencimiento) {
            throw new Error("id_residencia, concepto, valor y fecha_vencimiento son obligatorios");
        }

        if (valor <= 0) {
            throw new Error("El valor de la cuenta debe ser mayor que cero");
        }

        const nuevaCuenta = new CuentaCobro(
            cuentasCobro.length > 0
                ? Math.max(...cuentasCobro.map(c => c.id_cuenta)) + 1
                : 1,
            Number(id_residencia),
            concepto,
            valor,
            fecha_vencimiento
        );

        cuentasCobro.push(nuevaCuenta);

        return nuevaCuenta;
    }

    marcarVencida(id_cuenta) {

        const cuenta = this.obtenerPorId(id_cuenta);

        if (cuenta.estado === "Pagada") {
            throw new Error("No se puede marcar como vencida una cuenta ya pagada");
        }

        cuenta.estado = "Vencida";

        return cuenta;
    }

    eliminar(id_cuenta) {

        const indice = cuentasCobro.findIndex(c => c.id_cuenta === Number(id_cuenta));

        if (indice === -1) {
            throw new Error("Cuenta de cobro no encontrada");
        }

        cuentasCobro.splice(indice, 1);
    }
}

module.exports = new CuentasCobroService();
