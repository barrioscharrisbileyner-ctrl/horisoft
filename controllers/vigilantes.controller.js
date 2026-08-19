const vigilantesService = require("../services/vigilantes.service");

class VigilantesController {

    listar(req, res) {
        res.json(vigilantesService.obtenerTodas());
    }

    obtener(req, res) {
        try {
            const vigilante = vigilantesService.obtenerPorId(req.params.id);
            res.json(vigilante);
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }

    crear(req, res) {
        try {
            const vigilante = vigilantesService.crear(req.body);

            res.status(201).json({
                mensaje: "Vigilante creado correctamente",
                vigilante
            });
        } catch (error) {
            res.status(400).json({ mensaje: error.message });
        }
    }

    actualizarEstado(req, res) {
        try {
            const vigilante = vigilantesService.actualizarEstado(
                req.params.id,
                req.body.estado
            );
            res.json(vigilante);
        } catch (error) {
            const codigo = error.message.includes("no encontrado") ? 404 : 400;
            res.status(codigo).json({ mensaje: error.message });
        }
    }

    eliminar(req, res) {
        try {
            vigilantesService.eliminar(req.params.id);
            res.json({ mensaje: "Vigilante eliminado" });
        } catch (error) {
            res.status(404).json({ mensaje: error.message });
        }
    }
}

module.exports = new VigilantesController();
