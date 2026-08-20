const cuentasCobroService = require("../services/cuentasCobro.service");

class CuentasCobroController {

    listar(req, res) {
        if (req.query.id_residencia) {
            return res.json(cuentasCobroService.obtenerPorResidencia(req.query.id_residencia));
        }
        res.json(cuentasCobroService.obtenerTodas());
    }

    obtener(req, res) {
        try {
            res.json(cuentasCobroService.obtenerPorId(req.params.id));
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }

    crear(req, res) {
        try {
            const cuenta = cuentasCobroService.crear(req.body);
            res.status(201).json({ mensaje: "Cuenta de cobro creada correctamente", cuenta });
        } catch (error) {
            res.status(400).json({ mensaje: error.message });
        }
    }

    marcarVencida(req, res) {
        try {
            const cuenta = cuentasCobroService.marcarVencida(req.params.id);
            res.json(cuenta);
        } catch (error) {
            const codigo = error.message.includes("no encontrada") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    eliminar(req, res) {
        try {
            cuentasCobroService.eliminar(req.params.id);
            res.json({ mensaje: "Cuenta de cobro eliminada" });
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }
}

module.exports = new CuentasCobroController();
