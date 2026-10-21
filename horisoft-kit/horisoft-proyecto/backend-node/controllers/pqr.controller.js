const pqrService = require("../services/pqr.service");

class PqrController {

    listar(req, res) {
        if (req.query.id_residencia) {
            return res.json(pqrService.obtenerPorResidencia(req.query.id_residencia));
        }
        res.json(pqrService.obtenerTodas());
    }

    obtener(req, res) {
        try {
            res.json(pqrService.obtenerPorId(req.params.id));
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }

    crear(req, res) {
        try {
            const pqr = pqrService.crear(req.body);
            res.status(201).json({ mensaje: "PQR registrada correctamente", pqr });
        } catch (error) {
            res.status(400).json({ mensaje: error.message });
        }
    }

    responder(req, res) {
        try {
            const pqr = pqrService.responder(req.params.id, req.body.respuesta);
            res.json({ mensaje: "Respuesta registrada, PQR cerrada", pqr });
        } catch (error) {
            const codigo = error.message.includes("no encontrada") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    cambiarEstado(req, res) {
        try {
            const pqr = pqrService.cambiarEstado(req.params.id, req.body.estado);
            res.json(pqr);
        } catch (error) {
            const codigo = error.message.includes("no encontrada") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    eliminar(req, res) {
        try {
            pqrService.eliminar(req.params.id);
            res.json({ mensaje: "PQR eliminada" });
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }
}

module.exports = new PqrController();
