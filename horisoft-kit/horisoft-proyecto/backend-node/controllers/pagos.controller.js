const pagosService = require("../services/pagos.service");

class PagosController {

    listar(req, res) {
        if (req.query.id_cuenta) {
            return res.json(pagosService.obtenerPorCuenta(req.query.id_cuenta));
        }
        res.json(pagosService.obtenerTodos());
    }

    registrar(req, res) {
        try {
            const resultado = pagosService.registrarPago(req.body);
            res.status(201).json({ mensaje: "Pago registrado correctamente", ...resultado });
        } catch (error) {
            const codigo = error.message.includes("no encontrada") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }
}

module.exports = new PagosController();
